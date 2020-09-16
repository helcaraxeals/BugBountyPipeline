import configparser
import luigi
import re

from ..helpers.local_command import *

config = configparser.ConfigParser()


class SubfinderExecutor(luigi.Task):
    """
    This luigi task is responsible for running the 'subfinder' binary with options
    """
    config.read('src/tasks/config/command.ini')
    command_tpl = config.get('subfinder', 'command')
    config_file = config.get('subfinder', 'config_file')

    def requires(self):
        raise NotImplemented

    def store(self, data: dict):
        pass

    def run(self):
        _domains: list = []
        _subdomains: list = []

        with self.input().open('r') as fp:
            [_domains.append(line.rstrip()) for line in fp]

        for _domain in _domains:
            _command = self.command_tpl.replace('**DOMAIN**', _domain)
            _command = _command.replace('**CONFIG**', self.config_file)
            proc_out = chain(_command.rstrip())
            if proc_out:
                [_subdomains.append(_subdomain) for _subdomain in proc_out
                 if re.findall(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', _subdomain)]

        if _subdomains:
            _subdomains = list(set(_subdomains))
            self.store({'subdomain': _subdomains})

        with self.output().open('w') as fp:
            [fp.write(_sub.rstrip() + '\n') for _sub in _subdomains]

    def output(self):
        raise NotImplemented
