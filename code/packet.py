import datetime

class Packet:
    def __init__(self,
                ts=None,  
                sender=None,
                receiver=None,
                protocol_type=None,
                tcp_flag=-1,
                service=None,
                packet_len=None,
                conn=None
                ):
        self.ts = ts
        self.sender = sender
        self.receiver = receiver
        self.protocol_type=protocol_type
        self.tcp_flag = tcp_flag
        self.service = service 
        self.packet_len = packet_len
        self.conn = conn


    def getDict(self):
        rst = {"ts": self.ts,
               "sender": self.sender,
               "receiver": self.receiver,
               "protocol_type": self.protocol_type,
               "service": self.service,
               "packet_len": self.packet_len,
               "conn": self.conn}
        return rst


    def __str__(self):
        return '''
    ts = {0} 
    sender = {1} 
    receiver = {2} 
    protocol_type = {3}
    tcp_flag = {4} 
    service = {5} 
    packet_len = {6} 
    conn = {7}
'''.format(
            datetime.datetime.fromtimestamp(self.ts),
            self.sender,
            self.receiver,
            self.protocol_type,
            self.tcp_flag,
            self.service,
            self.packet_len,
            self.conn
            ) 
