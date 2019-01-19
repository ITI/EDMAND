import datetime

class DataValue:
    def __init__(self,
                ts=None,  
                holder_ip=None,
                protocol=None,
                uid=None,
                data_type=None,
                index=None,
                value=None,
                is_event=False
                ):
        self.ts = ts
        self.holder_ip = holder_ip 
        self.protocol = protocol 
        self.uid = uid 
        self.data_type = data_type 
        self.index = index 
        self.value = value
        self.is_event = is_event


    def getDict(self):
        rst = {"ts": self.ts,
               "holder_ip": self.holder_ip,
               "service": self.protocol,
               "uid": self.uid,
               "data_type": self.data_type,
               "index": self.index,
               "value": self.value,
               "is_event": self.is_event}
        return rst
            

    def __str__(self):
        return '''
    ts = {0} 
    holder_ip = {1} 
    protocol = {2}
    uid = {3} 
    data_type = {4} 
    index = {5} 
    value = {6}
    is_event = {7}
'''.format(
            datetime.datetime.fromtimestamp(self.ts),
            self.holder_ip,
            self.protocol,
            self.uid,
            self.data_type,
            self.index,
            self.value,
            self.is_event
            ) 
