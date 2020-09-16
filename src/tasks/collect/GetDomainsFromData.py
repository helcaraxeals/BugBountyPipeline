import luigi
import re


class GetDomainsFromData(luigi.Task):
    """
    This luigi task is responsible for parsing out valid domains from provided data
    """

    def requires(self):
        raise NotImplemented

    def store(self, data: dict):
        pass

    def run(self):
        _domains: list = []

        with self.input().open('r') as _file:
            [_domains.append(line) for line in _file if re.findall(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', line)]

        if _domains:
            _domains = list(set(_domains))
            self.store({'domain': _domains})

        with self.output().open('w') as outfile:
            [outfile.write(domain) for domain in _domains]

    def output(self):
        raise NotImplemented
