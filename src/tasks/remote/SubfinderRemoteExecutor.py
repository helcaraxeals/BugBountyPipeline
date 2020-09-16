import configparser
import luigi
import re

from ..helpers.remote_command import *
from ..helpers.create_instance import *

config = configparser.ConfigParser()


class SubfinderRemoteExecutor(luigi.Task):
    """
    This luigi task is responsible for running the 'subfinder' binary with options
    """
    config.read('src/tasks/config/command.ini')
    command_tpl = config.get('subfinder', 'command')
    config_file = config.get('subfinder', 'config_file')

    # Remote Task Variables
    template = luigi.Parameter()
    provider_token = luigi.Parameter()

    def requires(self):
        raise NotImplemented

    def store(self, data: dict):
        pass

    def run(self):
        _domains: list = []
        _subdomains: list = []

        # Create VM Instance
        instance_ip = return_new_instance(
            self.provider_token.__str__(),
            self.template.__str__()
        )

        # Log into Server
        conn = return_ssh_context(instance_ip, username='root', key_file="src/tasks/remote/keys/terraform_rsa")

        with self.input().open('r') as fp:
            [_domains.append(line.rstrip()) for line in fp]

        for _domain in _domains:
            _command = self.command_tpl.replace('**DOMAIN**', _domain)
            _command = _command.replace('**CONFIG**', self.config_file)
            proc_out = execute_command(conn, _command.rstrip())
            if proc_out:
                items = proc_out.decode('utf8').split('\n')
                [_subdomains.append(_subdomain) for _subdomain in items
                 if re.findall(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', _subdomain)]

        # Destroy VM Instance
        destroy_instance(
            self.provider_token.__str__(),
            self.template.__str__()
        )

        if _subdomains:
            _subdomains = list(set(_subdomains))
            self.store({'subdomain': _subdomains})

        with self.output().open('w') as fp:
            [fp.write(_sub.rstrip() + '\n') for _sub in _subdomains]

    def output(self):
        raise NotImplemented
