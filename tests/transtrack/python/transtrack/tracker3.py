from collections import defaultdict
from logging import DEBUG
import functools
from time import time
from typing import Any
from dataclasses import dataclass
from .log import Logger
import trace


@dataclass
class Lookup:
    tracker: defaultdict(list)
    results: defaultdict()

    def report(self):
        for method, times in self.tracker.items():
            self.results[method] = (
                len(times),
                sum(times),
                self.tracker[method],
            )
        return self.results


@dataclass
class Proxy(Lookup):
    log = Logger(DEBUG).log


class Tracker:
    proxy = Proxy(defaultdict(list), defaultdict())

    @staticmethod
    def service(fn):
        @functools.wraps(fn)
        def wrapper(self, tctx, root, service, proplist):
            tracer = trace.Trace(countfuncs=True, timing=True, outfile='kkotari_track_results.log')
            output = tracer.runctx(
                'fn(self, tctx, root, service, proplist)',
                locals={
                    'self': self,
                    'fn': fn,
                    'tctx': tctx,
                    'root': root,
                    'service': service,
                    'proplist': proplist
                }
            )
            self.log.info("kkotari :: {}".format(output))
            # fn(self, tctx, root, service, proplist)
        return wrapper

    @staticmethod
    def report():
        return Tracker.proxy.report()
