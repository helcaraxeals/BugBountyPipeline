import shlex
from luigi.contrib.ssh import RemoteContext, RemoteCalledProcessError


def return_ssh_context(host: str, username: str, key_file: str):
    try:
        return RemoteContext(host=host, username=username, key_file=key_file, no_host_key_check=True)
    except RemoteCalledProcessError as e:
        print(f"context error: {e.__str__()}")


def execute_command(context: RemoteContext, command: str):
    try:
        output = context.check_output(shlex.split(command))
        return output
    except RemoteCalledProcessError as e:
        print(f"execute error: {e.__str__()}")
