from collections import defaultdict
from logging import INFO, DEBUG
from .log import Logger


class Tracker:
    tracker = defaultdict()
    result = defaultdict()

    def update(self, method, tt):
        # TODO: need to add/update tracker
        pass
    def report(self):
        # TODO: generate result
        pass


class ClassWrapper(Tracker):
    tracker = {} # method: [operaton-time, ]
    tracker_result = {} # method: (no of times called, total time, [operaton-time, ])
    def __init__(self, obj, log):
        super().__init__()
        self.name = f"{obj.__class__.__name__} class"

        self.obj = obj
        self.log = log
        self.log.debug(f"{self.name} wrapped")

    def __getattr__(self, method):
        def mwrap(*args, **kwargs):
            self.log.debug(f"{self.name} calling `{method}` with params {args}, {kwargs}")
            return getattr(self.obj, method)(*args, **kwargs)
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


def track(*targs, timeit=False, verbose=False, before=None, after=None):
    def wrapper(fun):
        def wrapfun(fun_self, *args, **kwargs):
            log = get_logger(verbose)
            sequence_recorder = [] # TODO: add seq recorder
            for arg in targs:
                """
                TODO:
                need to check the arg is part of fun_self class
                need to check the arg is an argument to fun_self
                """
                exec('fun_self.%s' %(arg))
                exec("fun_self.%s = ClassWrapper(fun_self.%s, log)" %(arg, arg))
                log.debug(f"wrapped {arg}")
            if before:
                log.info(before)
            # TODO: method time start
            res = fun(fun_self, *args, **kwargs)
            # TODO: method time end
            if after:
                log.info(after)
            for arg in targs:
                exec("fun_self.%s = fun_self.%s.obj" %(arg, arg))
                log.debug(f"un-wrapped {arg}")
            return res
        return wrapfun
    return wrapper


class Trans:
    def open(self):
        print("Transaction opened")
    def close(self):
        print("Transaction close")
    def commit(self):
        print("Transaction commit")


class ncs:
    root = None
    service = None
    trans = Trans()


class newService(ncs):
    def __init__(self):
        self.root = "/"
        self.service = "/services/service/dummy"
        self.trans = Trans()

    @track('trans', verbose=True)
    def applyService(self):
        print(f"self.root: {self.root}")
        print(f"self.service: {self.service}")
        print(f"self.trans: {self.trans}")
        self.trans.open()
        self.trans.commit()
        self.trans.close()

if __name__ == "__main__":
    s = newService()
    print(s.root, s.service, s.trans)
    s.applyService()