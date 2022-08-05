
from ncs_tracker.tracker import track

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