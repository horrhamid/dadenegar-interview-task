# import dotenv
from dotenv import load_dotenv
import os
import django
import sys
import importlib
import warnings

warnings.filterwarnings("ignore")

commands = {
    "superuser": {
        "file": "create_superuser",
        "kwargs": ["username", "password"],
        "about": "creates a super user with given username and password",
    }
}


def print_command(command_name):
    command = commands.get(command_name)
    print(f"{command_name}:")
    about = command.get("about")
    command_file = command.get("file")
    kwargs = command.get("kwargs")
    print(f"\tabout: {about}")
    if len(kwargs) > 0:
        print(f"\tinputs: {kwargs}")
    else:
        print(f"\tinputs: no args")

    print(f"\truns: scripts.shell.{command_file}.run")


def print_commands():
    for command_name in commands.keys():
        print_command(command_name)


def main():
    load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sejam_service.settings")
    django.setup()
    if len(sys.argv) < 2:
        print_commands()
    else:
        command_name = sys.argv[1]
        command = commands.get(command_name, None)
        if not command:
            print_commands()
        else:
            input_args = sys.argv[2:]

            command_kwargs = command.get("kwargs")

            if len(input_args) != len(command_kwargs):
                print_command(command_name)
            else:
                kwargs = {}
                for index, key in enumerate(command_kwargs):
                    kwargs.update(**{key: input_args[index]})
                command_file = command.get("file")
                scripts = importlib.__import__(f"scripts.shell.{command_file}")
                shell = getattr(scripts, "shell")
                command = getattr(shell, command_file)
                run = getattr(command, "run")
                run(**kwargs)


if __name__ == "__main__":
    main()
