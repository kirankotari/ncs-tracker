from collections import defaultdict
from logging import DEBUG
import functools
from time import time
from typing import Any
from dataclasses import dataclass
from .log import Logger


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
    def object(self, obj):
        each: str
        self.log.info(obj.__dir__())
        for each in obj.__dir__():
            # self.log.info('%s' %(each))
            if each.startswith('__'):
                # self.log.info('skipped')
                continue
            if not callable(each):
                if exec("type(%s) == builtin_function_or_method" %each):
                    self.log.info('%s is built in callable' %(each))
                    pass
                self.log.info('%s is not a built in method or object..!' %(each))
                # self.log.info('%s is not callable' %(each))
                # exec("obj.%s = self.variable(%s)"%(each, each))
                continue
            self.log.info('%s wrapped..!' %(each))
            try:
                # self.log.info('exec %s' %(each))
                exec("obj.%s = self.method(%s)"%(each, each))
            except NameError:
                self.log.info('exec failed %s' %(each))
            except Exception:
                self.log.info('exec failed %s - Exception' %(each))
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
            self.log.info("tctx wrapped")
            root = Tracker.proxy.object(root)
            self.log.info("root wrapped")
            service = Tracker.proxy.object(service)
            self.log.info("service wrapped")
            proplist = Tracker.proxy.object(proplist)
            self.log.info("proplist wrapped")
            fn(self, tctx, root, service, proplist)
        return wrapper

    @staticmethod
    def report():
        return Tracker.proxy.report()
