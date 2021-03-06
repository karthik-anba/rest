#
# in our rest architecture we want to interface to the backend systems while
# using a secure rest service. I
# Internally we will use the many fnctions that cloudmesh_client provides.
# Before we use them we need to implement some elementary functions
# lets first do administrative functions in an admin commond

# pseudo code: task implement

from __future__ import print_function

import importlib
import pkgutil
import pydoc
import sys
import textwrap
from cmd import Cmd

from cloudmesh_client.shell.command import PluginCommand
from cloudmesh_client.shell.command import command

import cloudmesh
from cloudmesh.rest.server. mongo import Mongo
import inspect
from cloudmesh_client.common.dotdict import dotdict

def print_list(elements):
    for name in elements:
        print("*", name)

class plugin(object):
    @classmethod
    def modules(cls):
        module_list = []
        package = cloudmesh
        for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                              prefix=package.__name__ + '.',
                                                              onerror=lambda x: None):
            module_list.append(modname)
        return module_list

    @classmethod
    def classes(cls):
        module_list = cls.modules()
        commands = []
        for module in module_list:
            if module.startswith('cloudmesh.ext.command.'):
                commands.append(module)
        return commands

    @classmethod
    def name(cls, command):
        command_name = "do_" + command

        class_name = "cloudmesh.ext.command." + command + "." \
                     + command.capitalize() + "Command"

        return class_name, command_name

    @classmethod
    def class_name(cls, command):
        return "cloudmesh.ext.command." + command + "." \
               + command.capitalize() + "Command"

    @classmethod
    def load(cls, commands=None):
        """

        :param commands: If None the commands will be found from import cloudmesh
                         Otherwise the commands can be explicitly specified with

                          commands = [
                            'cloudmesh.ext.command.bar.BarCommand',
                            'cloudmesh.ext.command.foo.FooCommand',
                            ]
                          A namespace packege must exists. Foo and Bar ar just examples

        :return: the classes of the command
        """

        if commands is None:
            commands = [c.split('.')[-1] for c in cls.classes()]

        # print_list(commands)

        COMMANDS = [cls.class_name(c) for c in commands]
        commands = [getattr(importlib.import_module(mod), cls) for (mod, cls) in
                    (commands.rsplit(".", 1) for commands in COMMANDS)]
        return commands


plugin.load()

PluginCommandClasses = type(
    'CommandProxyClass',
    tuple(PluginCommand.__subclasses__()),
    {})


class CMShell(Cmd, PluginCommandClasses):

    prompt = 'cms> '
    banner = textwrap.dedent("""
              +=======================================================+
              .   ____ _                 _                     _      .
              .  / ___| | ___  _   _  __| |_ __ ___   ___  ___| |__   .
              . | |   | |/ _ \| | | |/ _` | '_ ` _ \ / _ \/ __| '_ \  .
              . | |___| | (_) | |_| | (_| | | | | | |  __/\__ \ | | | .
              .  \____|_|\___/ \__,_|\__,_|_| |_| |_|\___||___/_| |_| .
              +=======================================================+
                                Cloudmesh Rest Shell
              """)

    #
    # List all commands that start with do
    #
    @command
    def do_help(self, args, arguments):
        """
        ::
           Usage:
                help

           Description:
                help - List of all registered commands

        """
        print("Help")
        print("====")
        methodList = [n for n, v in inspect.getmembers(self, inspect.ismethod)]
        functionList = [n for n, v in inspect.getmembers(self, inspect.isfunction)]

        commands = methodList + functionList

        for c in sorted(commands):
            if c.startswith("do_"):
                print(c.replace("do_", ""), end=' ')
        print ()
        return ""

    @command
    def do_info(self, args, arguments):
        """
        ::

          Usage:
                info [commands|package|help]

          Description:
                info
                    provides internal info about the shell and its packages

        """
        arguments = dotdict(arguments)

        module_list = plugin.modules()

        if arguments.commands:
            commands = plugin.classes()
            print_list(commands)
        elif arguments.help:
            for name in module_list:
                p = "cloudmesh." + name
                strhelp = p + " not found."
                try:
                    strhelp = pydoc.render_doc(p, "Help on %s" + "\n" + 79 * "=")
                except Exception, e:
                    pass
                print(strhelp)

        else:
            print_list(module_list)

    @command
    def do_admin(self, args, arguments):
        """
        ::

          Usage:
                admin [db|rest] start
                admin [db|rest] stop
                admin db backup
                admin db reset
                admin status

          Description:
                db start
                    starts the database service

                db stop
                    stops the database service

                db backup
                    creates abackup of the database

                db reset
                    resets the database

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """
        arguments = dotdict(arguments)
        print(arguments)
        if arguments.db and arguments.stop:

            print("PLEASE stop db")
            m = Mongo()
            m.stop()
        elif arguments.db and arguments.start:

            print("PLEASE start db")
            m = Mongo()
            m.start()

        elif arguments.rest and arguments.start:

            print("PLEASE start rest")
            # m = Eve()
            # m.start()

        elif arguments.rest and arguments.stop:

            print("PLEASE stop rest")
            # m = Eve()
            # m.stop()


        elif arguments.start:
            m = Mongo()
            r = m.start()
            print(r)

            # start mong, start eve
            pass
        elif arguments.stop:
            m = Mongo()
            r = m.stop()
            print(r)

            # stop eve
            pass

        elif arguments.status:
            m = Mongo()
            r = m.status()
            print(r)

    def preloop(self):
        """adds the banner to the preloop"""


        lines = textwrap.dedent(self.banner).split("\n")
        for line in lines:
            # Console.cprint("BLUE", "", line)
            print(line)

    # noinspection PyUnusedLocal
    def do_EOF(self, args):
        """
        ::

            Usage:
                EOF

            Description:
                Command to the shell to terminate reading a script.
        """
        return True

    # noinspection PyUnusedLocal
    def do_quit(self, args):
        """
        ::

            Usage:
                quit

            Description:
                Action to be performed whne quit is typed
        """
        return True

    do_q = do_quit

    def emptyline(self):
        return

#def main():
#    CMShell().cmdloop()

def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def do_gregor(line):
    print("gregor")

# noinspection PyBroadException
def main():
    """cms.

    Usage:
      cms --help
      cms [--echo] [--debug] [--nosplash] [-i] [COMMAND ...]

    Arguments:
      COMMAND                  A command to be executed

    Options:
      --file=SCRIPT  -f  SCRIPT  Executes the script
      -i                 After start keep the shell interactive,
                         otherwise quit [default: False]
      --nosplash    do not show the banner [default: False]
    """

    def manual():
        print(main.__doc__)

    args = sys.argv[1:]

    arguments = {
        '--echo': '--echo' in args,
        '--help': '--help' in args,
        '--debug': '--debug' in args,
        '--nosplash': '--nosplash' in args,
        '-i': '-i' in args}

    echo = arguments["--echo"]
    if arguments['--help']:
        manual()
        sys.exit()

    for a in args:
        if a in arguments:
            args.remove(a)

    arguments['COMMAND'] = [' '.join(args)]

    commands = arguments["COMMAND"]
    if len(commands) > 0:
        if ".cm" in commands[0]:
            arguments["SCRIPT"] = commands[0]
            commands = commands[1:]
        else:
            arguments["SCRIPT"] = None

        arguments["COMMAND"] = ' '.join(commands)
        if arguments["COMMAND"] == '':
            arguments["COMMAND"] = None

    # noinspection PySimplifyBooleanCheck
    if arguments['COMMAND'] == []:
        arguments['COMMAND'] = None

    splash = not arguments['--nosplash']
    debug = arguments['--debug']
    interactive = arguments['-i']
    script = arguments["SCRIPT"]
    command = arguments["COMMAND"]

    #context = CloudmeshContext(
    #    interactive=interactive,
    #    debug=debug,
    #    echo=echo,
    #    splash=splash)




    cmd = CMShell()


#    if script is not None:
#        cmd.do_exec(script)

    try:
        if echo:
            print(cmd.prompt, command)
        if command is not None:
            cmd.precmd(command)
            stop = cmd.onecmd(command)
            cmd.postcmd(stop, command)
    except Exception as e:
        print("ERROR: executing command '{0}'".format(command))
        print(70 * "=")
        print(e)
        print(70 * "=")

    if interactive or (command is None and script is None):
        cmd.cmdloop()





if __name__ == '__main__':
    main()


