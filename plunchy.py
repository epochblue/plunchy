import os
import sys
import shutil
import argparse
from glob import glob
from subprocess import call, Popen, PIPE

try:
    import pygments
    import pygments.lexers
    import pygments.formatters
except ImportError:
    pygments = None

VERSION = '1.1.0'
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
        self.pattern = kwargs.get('pattern')
        self.path = kwargs.get('path')
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
        plists = {}

        # Get all the paths out of the PLUNCHY_FILE first
        with open(PLUNCHY_FILE, 'r') as f:
            for f in f.read().splitlines():
                agent = os.path.basename(f).rpartition('.')[0]
                if not pattern or (pattern and pattern in agent):
                    plists.update({agent: f})

        # Then get all the files in the directories
        for d in self.__dirs():
            search = '{}/*.plist'.format(d)
            for f in glob(search):
                agent = os.path.basename(f).rpartition('.')[0]
                if not pattern or (pattern and pattern in agent):
                    plists.update({agent: f})

        return plists

    def execute(self):
        getattr(self, self.cmd)()

    def start(self):
        plists = self.__plists(self.pattern)
        for path in plists.values():
            call(['launchctl', 'load', path], stdout=DEVNULL, stderr=DEVNULL)

        print('\n'.join(['Started %s' % p for p in plists.keys()]))

    def stop(self):
        plists = self.__plists(self.pattern)
        for path in plists.values():
            call(['launchctl', 'unload', path], stdout=DEVNULL, stderr=DEVNULL)

        print('\n'.join(['Stopped %s' % p for p in plists.keys()]))

    def restart(self):
        self.stop()
        self.start()

    def list(self):
        services = sorted(self.__plists(self.pattern).keys())
        print('\n'.join(services))

    def ls(self):
        self.list()

    def status(self):
        launch = Popen(['launchctl', 'list'], stdout=PIPE)

        if self.OPTIONS['verbose']:
            if self.pattern:
                call(['grep', '-i', '-e', self.pattern], stdin=launch.stdout)
            else:
                shutil.copyfileobj(launch.stdout, sys.stdout)
        else:
            cmd = ['grep', '-i']
            for key in self.__plists(None).keys():
                agent = key.replace('.', '\.')
                cmd.extend(['-e', agent])

            filtered = Popen(cmd, stdin=launch.stdout, stdout=PIPE)
            if self.pattern:
                call(['grep', '-i', '-e', self.pattern], stdin=filtered.stdout)
            else:
                shutil.copyfileobj(filtered.stdout, sys.stdout)

    def install(self):
        with open(PLUNCHY_FILE, 'a+') as f:
            f.write('{}\n'.format(self.path))

        print('Added {}'.format(self.path))

    def link(self):
        for d in self.__dirs():
            base = os.path.basename(self.path)
            os.symlink(self.path, os.path.join(d, base))
            print('Installed {} into {} via symlink'.format(self.path, d))
            break

    def copy(self):
        for d in self.__dirs():
            base = os.path.basename(self.path)
            shutil.copy(self.path, os.path.join(d, base))
            print('Installed {} into {} via copy'.format(self.path, d))
            break

    def show(self):
        for base, path in self.__plists(self.pattern).items():
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
        for path in self.__plists(self.pattern).values():
            call([os.getenv('VISUAL', os.getenv('EDITOR', 'vi')), path])


def main():
    """A simpler interface into launchctl."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog='Command-specific help is available by running `%(prog)s command --help`')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        dest='verbose', help='Enable verbose output')
    parser.add_argument('--version', action='version', version="%(prog)s {}".format(VERSION))

    subp = parser.add_subparsers(dest='cmd', metavar='command', title='Available Commands')

    list_p = subp.add_parser('list', help='List all launch agents, or only ones matching the given pattern.')
    list_p.add_argument('pattern', type=str, nargs='?', help='The (optional) pattern to match')

    ls_p = subp.add_parser('ls', help='List all launch agents, or only ones matching the given pattern.')
    ls_p.add_argument('pattern', type=str, nargs='?', help='The (optional) pattern to match')

    start_p = subp.add_parser('start', help='Start the launch agent(s) matching the given pattern.')
    start_p.add_argument('pattern', type=str, help='The pattern to match')

    stop_p = subp.add_parser('stop', help='Stop the launch agent(s) matching the given pattern.')
    stop_p.add_argument('pattern', type=str, help='The pattern to match')

    restart_p = subp.add_parser('restart', help='Restart the launch(s) agent matching the given pattern.')
    restart_p.add_argument('pattern', type=str, help='The pattern to match')

    status_p = subp.add_parser('status', help='Status the launch agent(s) matching the given pattern.')
    status_p.add_argument('pattern', type=str, help='The pattern to match')

    show_p = subp.add_parser('show', help='Show the launch agent matching(s) the given pattern.')
    show_p.add_argument('pattern', type=str, help='The pattern to match')

    edit_p = subp.add_parser('edit', help='Edit the launch agent(s) matching the given pattern.')
    edit_p.add_argument('pattern', type=str, help='The file to edit with $VISUAL (falls back to $EDITOR)')

    install_p = subp.add_parser('install', help='Add the agent to ~/.plunchy to be started/stopped manually.')
    install_p.add_argument('path', type=str, help='The path to the launch agent to be installed.')

    link_p = subp.add_parser('link', help='Install the agent into ~/Library/LaunchAgents via symlink')
    link_p.add_argument('path', type=str, help='The path to the launch agent to be linked.')

    copy_p = subp.add_parser('copy', help='Install the agent into ~/Library/LaunchAgents via copy')
    copy_p.add_argument('path', type=str, help='The path to the launch agent to be copied.')

    args = vars(parser.parse_args())
    p = Plunchy(**args)
    p.execute()

