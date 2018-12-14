class Flow:
    def __init__(self,
                start=None,
                end=None,
                orig=None,
                resp=None,
                protocol_type=None,
                service=None,
                count_pkt_ab=0,
                count_pkt_ba=0,
                mean_bytes_ab=None,
                std_bytes_ab=None,
                mean_bytes_ba=None,
                std_bytes_ba=None,
                mean_iat_ab=None,
                std_iat_ab=None,
                mean_iat_ba=None,
                std_iat_ba=None,
                ):
        self.start = start 
        self.end = end 
        self.orig = orig 
        self.resp = resp 
        self.protocol_type = protocol_type
        self.service = service
        self.count_pkt_ab = count_pkt_ab
        self.count_pkt_ba = count_pkt_ba
        self.mean_bytes_ab = mean_bytes_ab
        self.std_bytes_ab = std_bytes_ab
        self.mean_bytes_ba = mean_bytes_ba
        self.std_bytes_ba = std_bytes_ba
        self.mean_iat_ab = mean_iat_ab
        self.std_iat_ab = std_iat_ab
        self.mean_iat_ba = mean_iat_ba
        self.std_iat_ba = std_iat_ba


    def getDict(self):
        rst = {"start": self.start,
               "end": self.end,
               "orig": self.orig,
               "resp": self.resp,
               "protocol_type": self.protocol_type,
               "serivce": self.service,
               "count_pkt_ab": self.count_pkt_ab,
               "count_pkt_ba": self.count_pkt_ba,
               "mean_bytes_ab": self.mean_bytes_ab,
               "std_bytes_ab": self.std_bytes_ab,
               "mean_bytes_ba": self.mean_bytes_ba,
               "std_bytes_ba": self.std_bytes_ba,
               "mean_iat_ab": self.mean_iat_ab,
               "std_iat_ab": self.mean_iat_ab,
               "mean_iat_ba": self.mean_iat_ba,
               "std_iat_ba": self.std_iat_ba}
        return rst


    def __str__(self):
        return '''
    start = {0}
    end = {1}
    orig = {2}
    resp = {3}
    protocol_type = {4}
    service = {5}
    count_pkt_ab = {6}
    count_pkt_ba = {7}
    mean_bytes_ab = {8}
    std_bytes_ab = {9}
    mean_bytes_ba = {10}
    std_bytes_ba = {11}
    mean_iat_ab = {12}
    std_iat_ab = {13}
    mean_iat_ba = {14}
    std_iat_ba = {15}
'''.format(
            self.start,
            self.end,
            self.orig,
            self.resp,
            self.protocol_type,
            self.service,
            self.count_pkt_ab,
            self.count_pkt_ba,
            self.mean_bytes_ab,
            self.std_bytes_ab,
            self.mean_bytes_ba,
            self.std_bytes_ba,
            self.mean_iat_ab,
            self.std_iat_ab,
            self.mean_iat_ba,
            self.std_iat_ba,
            ) 
