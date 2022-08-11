from collections import defaultdict
import functools
from time import time
from typing import Any
from dataclasses import dataclass


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
    def object(self, obj):
        each: str
        for each in obj.__dir__():
            if each.startswith('__'):
                continue
            exec("obj.%s = self.method(%s)"%(each, each))
        return obj

    def method(self, m):
        @functools.wraps(m)
        def wrapped(*args, **kwargs):
            print('{!r} executing'.format(m.__name__))
            st = time()
            res = m(*args, **kwargs)
            self.tracker[m].append(time() - st)
            return res
        return wrapped


class Tracker:
    proxy = Proxy(defaultdict(list), defaultdict())

    @staticmethod
    def service(fn):
        @functools.wraps(fn)
        def wrapper(self, tctx, root, service, proplist):
            tctx = Tracker.proxy.object(tctx)
            root = Tracker.proxy.object(root)
            service = Tracker.proxy.object(service)
            proplist = Tracker.proxy.object(proplist)
            fn(self, tctx, root, service, proplist)
        return wrapper

    @staticmethod
    def report():
        return Tracker.proxy.report()
