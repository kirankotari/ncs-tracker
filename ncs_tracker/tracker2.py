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
                len(self.tracker[method]),
                sum(self.tracker[method]),
                self.tracker[method],
            )

@dataclass
class Proxy(Lookup):
    def method(self, obj):
        return obj

class Base:
    tracker = defaultdict(list)
    results = defaultdict()

    def update(self, method, tt):
        self.tracker[method].append(tt)

    def report(self):
        """
        This method will update the results in following format
        method: (times-called, total-time-taken, list-of-taken-times)
        """
        for method, times in self.tracker.items():
            self.results[method] = (len(self.tracker[method]), sum(self.tracker[method]), self.tracker[method])

class ProxyMetaClass(type):
    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return super().__str__()

    def __type__(self) -> str:
        return type(super())

    def __instancecheck__(self, __instance: Any) -> bool:
        return super().__instancecheck__(__instance)

class Proxy(Base):
    def __init__(self, obj):
        super().__init__()
        self.name = f"{obj.__class__.__name__} class"
        self.obj = obj
        print(f"{self.name} wrapped")

    def __name__(self):
        self.obj.__name__

    # def __type__(self):
    #     return self.obj.__type__()

    def __str__(self):
        return self.obj.__str__()

    def __repr__(self):
        return self.obj.__repr__()
    def __getattr__(self, method):
        def mwrap(*args, **kwargs):
            print(f"{self.name} calling `{method}` with params {args}, {kwargs}")
            st = time()
            res = getattr(self.obj, method)(*args, **kwargs)
            self.update(method, time() - st)
            return res

        print(f"{self.name} checking for `{method}`")
        if hasattr(self.obj, method):
            return mwrap
        else:
            # TODO: don't know how field works
            msg = f"ERR: {self.name}, no such field/method found"
            print(msg)
            raise AttributeError(msg)

class Tracker:
    @staticmethod
    def service(fn):
        @functools.wraps(fn)
        def wrapper(self, tctx, root, service, proplist):
            tctx = Proxy(tctx)
            root = Proxy(root)
            service = Proxy(service)
            proplist = Proxy(proplist)
            fn(self, tctx, root, service, proplist)

        return wrapper