import os
import shutil
import sys
from glob import glob
from subprocess import call, Popen, PIPE

try:
    import pygments
    import pygments.lexers
    import pygments.formatters
except ImportError:
    pygments = None

PLUNCHY_FILE = os.path.expanduser('~/.plunchy')
DIRS = ['~/Library/LaunchAgents']
ROOT_DIRS = [
    '/Library/LaunchAgents',
    '/Library/LaunchDaemons',
    '/System/Library/LaunchDaemons'
]

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'w')


class Plunchy(object):
    def __init__(self, **kwargs):
        self.cmd = kwargs.get('cmd')
        self.arg = kwargs.get('arg')
        self.is_root = (os.geteuid() == 0)
        self.OPTIONS = kwargs

        # Make sure the PLUNCHY_FILE exists
        if not os.path.isfile(PLUNCHY_FILE):
            open(PLUNCHY_FILE, 'a').close()

    def __dirs(self):
        dirs = [os.path.expanduser(d) for d in DIRS]

        if self.is_root:
            dirs.extend([os.path.expanduser(d) for d in ROOT_DIRS])

        return dirs

    def __plists(self, pattern):
        if hasattr(self, '_plists'):
            return self._plists
        plists = {}

        # Get all the paths out of the PLUNCHY_FILE first
        with open(PLUNCHY_FILE, 'r') as f:
            for f in f.read().splitlines():
                agent = os.path.basename(f).rpartition('.')[0]
                plists.update({agent: f})

        # Then get all the files in the directories
        for d in self.__dirs():
            search = '{}/*.plist'.format(d)
            for f in glob(search):
                agent = os.path.basename(f).rpartition('.')[0]
                plists.update({agent: f})

        # Then filter if necessary
        if pattern:
            for k in plists.keys():
                if pattern not in k:
                    del plists[k]

        self._plists = plists
        return plists

    def execute(self):
        getattr(self, self.cmd)()

    def start(self):
        if not self.arg:
            raise ValueError('start [pattern]')

        plists = self.__plists(self.arg)
        for path in plists.values():
            call(['launchctl', 'load', path], stdout=DEVNULL, stderr=DEVNULL)

        print('\n'.join(['Started %s' % p for p in plists.keys()]))

    def stop(self):
        if not self.arg:
            raise ValueError('stop [pattern]')

        plists = self.__plists(self.arg)
        for path in plists.values():
            call(['launchctl', 'unload', path], stdout=DEVNULL, stderr=DEVNULL)

        print('\n'.join(['Stopped %s' % p for p in plists.keys()]))

    def restart(self):
        self.stop()
        self.start()

    def list(self):
        services = sorted(self.__plists(self.arg).keys())
        print('\n'.join(services))

    def ls(self):
        self.list()

    def status(self):
        launch = Popen(['launchctl', 'list'], stdout=PIPE)

        if self.OPTIONS['verbose']:
            if self.arg:
                call(['grep', '-i', '-e', self.arg], stdin=launch.stdout)
            else:
                shutil.copyfileobj(launch.stdout, sys.stdout)
        else:
            cmd = ['grep', '-i']
            for key in self.__plists(None).keys():
                agent = key.replace('.', '\.')
                cmd.extend(['-e', agent])

            filtered = Popen(cmd, stdin=launch.stdout, stdout=PIPE)
            if self.arg:
                call(['grep', '-i', '-e', self.arg], stdin=filtered.stdout)
            else:
                shutil.copyfileobj(filtered.stdout, sys.stdout)

    def add(self):
        if not self.arg:
            raise ValueError('add [file]')

        with open(PLUNCHY_FILE, 'a+') as f:
            f.write('{}\n'.format(self.arg))

        print('Added {}'.format(self.arg))

    def install(self):
        return self.add()

    def link(self):
        if not self.arg:
            raise ValueError('link [file]')

        for d in self.__dirs():
            base = os.path.basename(self.arg)
            os.symlink(self.arg, os.path.join(d, base))
            print('Installed {} into {} via symlink'.format(self.arg, d))
            break

    def copy(self):
        if not self.arg:
            raise ValueError('copy [file]')

        for d in self.__dirs():
            base = os.path.basename(self.arg)
            shutil.copy(self.arg, os.path.join(d, base))
            print('Installed {} into {} via copy'.format(self.arg, d))
            break

    def show(self):
        if not self.arg:
            raise ValueError('show [pattern]')

        for base, path in self.__plists(self.arg).items():
            f = open(path, 'r')
            output = f.read()
            if pygments:
                output = pygments.highlight(
                    output,
                    pygments.lexers.XmlLexer(),
                    pygments.formatters.Terminal256Formatter())
            print(output)
            f.close()

    def edit(self):
        if not self.arg:
            raise ValueError('edit [pattern]')

        for path in self.__plists(self.arg).values():
            call([os.getenv('VISUAL', os.getenv('EDITOR', 'vi')), path])
