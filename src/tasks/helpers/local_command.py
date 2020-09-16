import subprocess


def execute_command_chain(command: str):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = process.communicate()
    if output:
        return output.decode('utf8').split('\n')
    if errors:
        raise Exception(f'[x] Command failed: {errors}')


def chain(command):
    return execute_command_chain(command)
