import datetime

class Operation:
    def __init__(self,
                ts=None,  
                orig_ip=None,
                resp_ip=None,
                service=None,
                uid=None,
                fc=None,
                fn=None,
                is_orig=False
                ):
        self.ts = ts
        self.orig_ip = orig_ip 
        self.resp_ip = resp_ip 
        self.service = service 
        self.uid = uid 
        self.fc = fc 
        self.fn = fn 
        self.is_orig = is_orig


    def getDict(self):
        rst = {"ts": self.ts,
               "orig_ip": self.orig_ip,
               "resp_ip": self.resp_ip,
               "service": self.service,
               "uid": self.uid,
               "fc": self.fc,
               "fn": self.fn,
               "is_orig": self.is_orig}
        return rst


    def __str__(self):
        return '''
    ts = {0} 
    orig_ip = {1} 
    resp_ip = {2} 
    service = {3}
    uid = {4} 
    fc = {5} 
    fn = {6}
    is_orig = {7}
'''.format(
            datetime.datetime.fromtimestamp(self.ts),
            self.orig_ip,
            self.resp_ip,
            self.service,
            self.uid,
            self.fc,
            self.fn,
            self.is_orig
            ) 
