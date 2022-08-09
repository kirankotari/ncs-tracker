from time import time
from logging import INFO, DEBUG
from collections import defaultdict
from .log import Logger


# TODO: need to record sequence of methods called on tracker objects

class Tracker:
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


class Proxy(Tracker):
    def __init__(self, obj, log):
        super().__init__()
        self.name = f"{obj.__class__.__name__} class"
        self.log, self.obj = log, obj
        self.log.debug(f"{self.name} wrapped")

    def __getattr__(self, method):
        def mwrap(*args, **kwargs):
            self.log.debug(f"{self.name} calling `{method}` with params {args}, {kwargs}")
            st = time()
            res = getattr(self.obj, method)(*args, **kwargs)
            self.update(method, time() - st)
            return res

        self.log.debug(f"{self.name} checking for `{method}`")
        if hasattr(self.obj, method):
            return mwrap
        else:
            # TODO: don't know how field works
            msg = f"{self.name}, no such field/method found"
            self.log.error(msg)
            raise AttributeError(msg)


def get_logger(verbose):
    print("setting logger")
    level = INFO
    if verbose:
        level = DEBUG
    log = Logger(level=level).log
    return log


def proxyWrapper(self, arg, log):
    try:
        log.debug(f"kkotari: {self.__dir__()}")
        if arg in self.__dir__():
            exec("self.%s = Proxy(self.%s, log)" %(arg, arg))
        else:
            exec("%s = Proxy(%s, log)" %(arg, arg))
    except Exception:
        raise AttributeError('no variable `%s` found' %(arg))


def proxyUnWrapper(self, arg, log):
    try:
        if arg in self.__dir__():
            exec("self.%s = self.%s.obj" %(arg, arg))
        else:
            exec("%s = %s.obj" %(arg, arg))
    except Exception:
        raise AttributeError('no variable `%s` found' %(arg))


def track(*targs, timeit=False, verbose=False): # before=None, after=None
    def wrapper(fun):
        def wrapfun(self, *args, **kwargs):
            log = get_logger(verbose)
            log.info("I am in track..!")
            log.info(f"kkotari: {args}")
            for arg in targs:
                proxyWrapper(self, arg, log)
                log.debug(f"wrapped {arg}")

            st = time()
            res = fun(self, *args, **kwargs)
            tt = time() - st

            for arg in targs:
                proxyUnWrapper(self, arg, log)
                log.debug(f"un-wrapped {arg}")
            return res
        return wrapfun
    return wrapper

def track_service(*targs, timeit=False, verbose=False):
    log = get_logger(verbose)
    log.info("kkotari: track_service, started")
    def wrapper(fun):
        log.info("kkotari: wrapper fun, started")
        def wrapfun(self, *args, **kwargs):
            log = get_logger(verbose)
            log.info("kkotari: wrapfun, started")
            tctx = 10
            st = time()
            log.info(f"kkotari: fun is {fun} with {args}")
            res = fun(self, *args, **kwargs)
            tt = time() - st
            if timeit:
                log.info(f"kkotari: timetaken: {tt}")
                log.info(f"kkotari: res: {res}")

            return res
        return wrapfun
    return wrapper
