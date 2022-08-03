from logging import INFO, DEBUG


def track(*targs, verbose=False, before=None, after=None):
    def wrapper(fun):
        level = INFO
        if verbose:
            level = DEBUG
        log = Logger(level).log

        def wrapfun(fun_self, *args, **kwargs):
            class Dynamic:
                def __init__(self, obj):
                    self.obj = obj
                    log.debug(f"{self.obj.__class__} wrapped")

                def __getattr__(self, method):
                    def mwrap(*args, **kwargs):
                        log.debug(f"{self.obj.__class__} calling {method} with args {args}, {kwargs}")
                        return getattr(self.obj, method)(*args, **kwargs)
                    log.debug(f"{self.obj.__class__} checking for method")
                    if hasattr(self.obj, method):
                        return mwrap
                    else:
                        # TODO: don't know how field works
                        msg = f"{self.obj.__class__}, no such field/method found"
                        log.error(msg)
                        raise AttributeError(msg)
            for arg in targs:
                # TODO: call Dynamic on objects
                exec('fun_self.%s' %(arg))
                exec("fun_self.%s = Dynamic(fun_self.%s)" %(arg, arg))
                log.debug(f"wrapped {arg}")
            if before:
                log.info(before)
            res = fun(fun_self, *args, **kwargs)
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