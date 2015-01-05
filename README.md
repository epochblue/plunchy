# plunchy

[![Latest Version](https://pypip.in/version/plunchy/badge.svg)](https://pypi.python.org/pypi/plunchy/)

`plunchy` is a simple interface into OS X's `launchctl`. It is based on the idea
behind Mike Perham's [`lunchy`](https://github.com/mperham/lunchy) Ruby script,
though there are a few small differences between the two:

1. By default, `plunchy` does not install items into the system's `LaunchAgents`
folders. Unless you jump through hoops, items in those folders are automatically
started at system boot, defeating the purpose of managing startup and
shutdown for your launch agents.

2. Also by default, if you do want a file to be installed in a `LaunchAgents`
folder, `plunchy` will symlink the file, rather than copy it. This allows you
to automatically receive updates if the launch agent is updated.


`plunchy` does want to maintain the simplicity of the original, however, so the
available commands largely mirror `lunchy`'s:

    * ls [pattern]        List all launch agents, or only ones matching the given pattern.
    * list [pattern]      Alias for ls
    * start {pattern}     Start the launch agent matching the given pattern.
    * stop {pattern}      Stop the launch agent matching the given pattern.
    * restart {pattern}   Restart the launch agent matching the given pattern.
    * status {pattern}    Display the status of all launch agents matching the pattern.
    * show {pattern}      See the launch agent with the specified pattern
    * edit {pattern}      Edit the launch agent with the specified pattern

The main area where `plunchy` differs, however, is in the installation of scripts. `plunchy`
provides the following commands for installing scripts:

    * add {path}          Add the agent to `~/.plunchy` to be started/stopped manually
    * install {path}      Alias for `add`
    * link {path}         Install the agent into `~/Library/LaunchAgents` via symlink (\*)
    * copy {path}         Install the agent into `~/Library/LaunchAgents` via file copy (\*)


<small>\* Doing this means the launch agent will be loaded/started when the system boots up.</small>


## Installation

The easiest way to install `plunchy` is via `pip`:

    pip install plunchy

## License

`plunchy` is MIT licensed. Please see the included `LICENSE` file.

## Author

Bill Israel - [@epochblue](https://twitter.com/epochblue) - [http://billisrael.info/](http://billisrael.info/)

