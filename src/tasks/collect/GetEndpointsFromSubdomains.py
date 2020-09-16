import luigi


class GetEndpointsFromSubdomains(luigi.Task):
    """
    This luigi task will sort and collect endpoints for further processing
    """

    def requires(self):
        raise NotImplemented

    def store(self, data: dict):
        pass

    def run(self):
        _unique_results: list = []

        for task in self.input():
            with self.input()[task].open('r') as fp:
                [_unique_results.append(line.rstrip()) for line in fp if line not in _unique_results]

        if _unique_results:
            _unique_results = list(set(_unique_results))
            self.store({'endpoint': _unique_results})

        with self.output().open('w') as fp:
            [fp.write(domain + '\n') for domain in _unique_results]

    def output(self):
        raise NotImplemented
