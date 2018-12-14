class Anomaly:
    def __init__(self,
                ts=None,  
                desp=None,
                confi=0,
                anomaly_type=None,
                index=None,
                current=None,
                mean=None,
                dev=None
                ):
        self.ts = ts
        self.desp = desp 
        self.confi = confi 
        self.anomaly_type = anomaly_type
        self.index = index
        self.current = current
        self.mean = mean
        self.dev = dev

    def getTS(self):
        return self.ts


    def getDesp(self):
        return self.desp


    def getConfi(self):
        return self.confi

    
    def getAnomalyType(self):
        return self.anomaly_type


    def getIndex(self):
        return self.index


    def getCurrent(self):
        return self.current


    def getMean(self):
        return self.mean


    def getDict(self):
        rst = {"ts": self.ts,
               "desp": self.desp,
               "confi": self.confi,
               "anomaly_type":  self.anomaly_type,
               "index": self.index,
               "current": self.current,
               "mean": self.mean,
               "dev": self.dev}
        return rst


    def getDev(self):
        return self.dev


    def __str__(self):
        return '''
    ts = {0} 
    desp = {1} 
    confi = {2} 
    anomaly_type = {3}
    index = {4}
    current = {5}
    mean = {6}
    dev = {7}
'''.format(
            self.ts,
            self.desp,
            self.confi,
            self.anomaly_type,
            self.index,
            self.current,
            self.mean,
            self.dev
            ) 


class PacketAnomaly(Anomaly):
    def __init__(self,
                ts=None,  
                desp=None,
                confi=0,
                index=None,
                packet=None,
                current=None,
                normal_mean=None,
                normal_diff=None
                ):
        Anomaly.__init__(self, ts, desp, confi, "packet", index, current, normal_mean, normal_diff)
        self.packet = packet


    def getPacket(self):
        return self.packet


    def getDict(self):
        rst = Anomaly.getDict(self)
        type_specific = {"packet": self.packet.getDict()}
        rst.update(type_specific)
        return rst


    def __str__(self):
        return Anomaly.__str__(self)[:-1] + '''
    packet = {0}'''.format("    ".join(str(self.packet).splitlines(True)))


class FlowAnomaly(Anomaly):
    def __init__(self,
                ts=None,  
                desp=None,
                confi=0,
                index=None,
                flow=None,
                current=None,
                mean=None,
                std=None
                ):
        Anomaly.__init__(self, ts, desp, confi, "flow", index, current, mean, std)
        self.flow = flow 


    def getFlow(self):
        return self.flow


    def getDict(self):
        rst = Anomaly.getDict(self)
        type_specific = {"flow": self.flow.getDict()}
        rst.update(type_specific)
        return rst


    def __str__(self):
        return Anomaly.__str__(self)[:-1] + '''
    flow = {0}'''.format("    ".join(str(self.flow).splitlines(True)))


class OperationAnomaly(Anomaly):
    def __init__(self,
                ts=None,  
                desp=None,
                confi=0,
                index=None,
                operation=None,
                iat=None,
                mean=None,
                std=None
                ):
        Anomaly.__init__(self, ts, desp, confi, "operation", index, iat, mean, std)
        self.operation = operation 


    def getOperation(self):
        return self.operation


    def getDict(self):
        rst = Anomaly.getDict(self)
        if self.operation != None:
            type_specific = {"operation": self.operation.getDict()}
            rst.update(type_specific)
        return rst


    def __str__(self):
        return Anomaly.__str__(self)[:-1] + '''
    operation = {0}'''.format("    ".join(str(self.operation).splitlines(True)))


class MeasurementAnomaly(Anomaly):
    def __init__(self,
                ts=None,  
                desp=None,
                confi=0,
                index=None,
                measurement=None,
                measurement_type=None,
                type_confi=0,
                current=None,
                mean=None,
                std=None
                ):
        Anomaly.__init__(self, ts, desp, confi, "measurement", index, current, mean, std)
        self.measurement = measurement 
        self.measurement_type = measurement_type
        self.type_confi = type_confi


    def getMeasurement(self):
        return self.measurement


    def getMeasurementType(self):
        return self.measurement_type


    def getTypeConfi(self):
        return self.type_confi


    def getDict(self):
        rst = Anomaly.getDict(self)
        type_specific = {"measurement_type": self.measurement_type,
                         "type_confi": self.type_confi,
                         "measurement": self.measurement.getDict()}
        rst.update(type_specific)
        return rst


    def __str__(self):
        return Anomaly.__str__(self)[:-1] + '''
    measurement_type = {0}
    type_confi = {1}'''.format(self.measurement_type, self.type_confi) + '''
    measurement = {0}'''.format("    ".join(str(self.measurement).splitlines(True)))
