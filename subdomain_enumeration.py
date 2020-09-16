import tldextract
import luigi

from luigi.util import inherits
from src.tasks.local import *
from src.tasks.remote import *
from src.tasks.collect import *
from src.tasks.helpers.token import generate_token
from src.tasks.helpers.database import return_database_handler

_provider_token = "<digital_ocean_token_here>"


class _GetDataFromSource(GetDataFromSource.GetDataFromSource):

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-get_data_from_source-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _GetDomainsFromData(GetDomainsFromData.GetDomainsFromData):

    def requires(self):
        return _GetDataFromSource(nonce_token=self.nonce_token, data_source=self.data_source)

    def store(self, data: dict):
        my_db = return_database_handler()
        my_cursor = my_db.cursor()
        for _domain in data['domain']:
            sql = f"INSERT IGNORE INTO domains (id, domain) VALUES (NULL, '{_domain}')"
            my_cursor.execute(sql)
            my_db.commit()

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-get_domains_from_data-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _ChaosExecutorTask(ChaosExecutor.ChaosExecutor):

    provider_token = _provider_token
    template = "src/tasks/remote/templates/digitalocean/chaos"

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-chaos_executor-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _AmassExecutorTask(AmassRemoteExecutor.AmassRemoteExecutor):

    provider_token = _provider_token
    template = "src/tasks/remote/templates/digitalocean/amass"

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-amass_remote_executor-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _SubfinderExecutorTask(SubfinderRemoteExecutor.SubfinderRemoteExecutor):

    provider_token = _provider_token
    template = "src/tasks/remote/templates/digitalocean/subfinder"

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-subfinder_remote_executor-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _GetSubdomainsFromData(GetSubdomainsFromDomains.GetSubdomainsFromDomains):

    def requires(self):
        return {
            'task_a': _ChaosExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source),
            'task_b': _AmassExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source),
            'task_d': _SubfinderExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source)
        }

    def store(self, data: dict):
        my_db = return_database_handler()
        my_cursor = my_db.cursor()
        for _subdomain in data['subdomain']:
            domain_parts = tldextract.extract(_subdomain)
            domain = f'{domain_parts.domain}.{domain_parts.suffix}'
            sql = f"INSERT IGNORE INTO subdomains (id, domain, subdomain) VALUES (NULL, '{domain}', '{_subdomain}')"
            my_cursor.execute(sql)
            my_db.commit()

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-collect_and_sort_domains-{self.nonce_token}.complete')


if __name__ == '__main__':
    token: str = generate_token()
    data_source: str = '/tmp/targets.txt'
    luigi.build([_GetSubdomainsFromData(nonce_token=token, data_source=data_source)], local_scheduler=True, workers=3)
