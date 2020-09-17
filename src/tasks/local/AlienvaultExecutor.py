import configparser
import luigi
import re

from ..helpers.local_command import *

config = configparser.ConfigParser()


class AlienvaultExecutor(luigi.Task):
    """
    This luigi task is responsible for running the 'alienvault' binary with options
    """
    config.read('src/tasks/config/command.ini')
    command_tpl = config.get('alienvault', 'command')
    api_key = config.get('alienvault', 'api_key')

    def requires(self):
        raise NotImplemented

    def store(self, data: dict):
        pass

    def run(self):
        _domains: list = []
        _endpoints: list = []

        with self.input().open('r') as fp:
            [_domains.append(line.rstrip()) for line in fp]

        for _domain in _domains:
            _command = self.command_tpl.replace('**DOMAIN**', _domain)
            _command = _command.replace('**APIKEY**', self.api_key)
            proc_out = chain(_command.rstrip())
            if proc_out:
                [_endpoints.append(_endpoint) for _endpoint in proc_out if _endpoint.startswith('http')]

        if _endpoints:
            _endpoints = list(set(_endpoints))
            self.store({'endpoint': _endpoints})

        with self.output().open('w') as fp:
            [fp.write(_sub.rstrip() + '\n') for _sub in _endpoints]

    def output(self):
        raise NotImplemented
