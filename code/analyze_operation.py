from pybroker import *
from operation import Operation
from anomaly import OperationAnomaly
from inc_mean_std import ExpMeanSTD
import numpy as np 
import math

TIME_NORM = 180.0
COUNT_NORM = 100.0
COUNT_EACH_NORM = 100.0
PERIODIC_CHECK_TIME = 600
CONFI_TH = 0.6

def sigmoid(x):
    return 2 * (1 / (1 + math.exp(-x)) - 0.5)


def generate_anomaly(ts,
                     desp,
                     confi,
                     index,
                     anomaly_queue,
                     operation=None,
                     iat=None,
                     mean=None,
                     std=None):
    if confi >= CONFI_TH:
        anomaly = OperationAnomaly(ts,
                                   desp,
                                   confi,
                                   index,
                                   operation,
                                   iat,
                                   mean,
                                   std)
        anomaly_queue.put_nowait(anomaly)


class FunctionStats:
    def __init__(self, index, operation, anomaly_queue):
        self.index = index
        self.anomaly_queue = anomaly_queue            
        self.last_seen = operation.ts
        self.iat = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 


    def update(self, operation):
        iat = operation.ts - self.last_seen
        #print(iat)
        #print(self.iat)
        rst, confi, mean, std = self.iat.update(iat)

        if rst != 0:
            if rst == 1:
                desp = "OPERATION_TOO_LATE"
            else:
                desp = "OPERATION_TOO_EARLY"
            generate_anomaly(operation.ts,
                             desp,
                             confi,
                             self.index,
                             self.anomaly_queue,
                             operation,
                             iat,
                             mean,
                             std) 
            
        self.last_seen = operation.ts


    def check(self, ts):
        iat = ts-self.last_seen
        rst, confi, mean, std = self.iat.check(iat)
        if rst == 1:
            desp = "OPERATION_MISSING"
            generate_anomaly(ts,
                             desp,
                             confi,
                             self.index,
                             self.anomaly_queue,
                             iat=iat,
                             mean=mean,
                             std=std)


class OperationModel:
    def __init__(self, index, operation, anomaly_queue):
        self.index = index
        self.fc_dict = dict() 
        self.anomaly_queue = anomaly_queue
        self.first_seen = operation.ts
        self.total_seen = 0 


    def update(self, operation):
        index = self.index + ";" + str(operation.fc)
        if operation.service == "DNP3":
            if operation.fc < 0 or operation.fc > 255:
                generate_anomaly(operation.ts,
                                 "INVALID_FUNCTION_CODE",
                                 1,
                                 index,
                                 self.anomaly_queue,
                                 operation)
                return
            if operation.fc == 129 or operation.fc == 130:
                if operation.is_orig:
                    generate_anomaly(operation.ts,
                                     "RESPONSE_FROM_ORIG",
                                     1,
                                     index,
                                     self.anomaly_queue,
                                     operation)
                    return
            else:
                if not operation.is_orig:
                    generate_anomaly(operation.ts,
                                     "REQUEST_FROM_RESP",
                                     1,
                                     index,
                                     self.anomaly_queue,
                                     operation)
                    return
        elif operation.service == "Modbus":
            if operation.fc < 1 or operation.fc > 127:
                generate_anomaly(operation.ts,
                                 "INVALID_FUNCTION_CODE",
                                 1,
                                 index,
                                 self.anomaly_queue,
                                 operation)
                return

        if operation.fc not in self.fc_dict:
            #print("sigmoid: " + str(sigmoid(self.total_seen/COUNT_NORM)))
            confi = sigmoid(self.total_seen/COUNT_NORM) * sigmoid((operation.ts-self.first_seen)/TIME_NORM)
            generate_anomaly(operation.ts,
                             "NEW_OPERATION",
                             confi,
                             index,
                             self.anomaly_queue,
                             operation)
            self.fc_dict[operation.fc] = FunctionStats(index, operation, self.anomaly_queue)
        else:
            self.fc_dict[operation.fc].update(operation)

        self.total_seen += 1


    def check(self, ts):
        for fc in self.fc_dict:
            self.fc_dict[fc].check(ts)


class OperationAnalyzer():
    def __init__(self, anomaly_queue):
        self.last_check = None
        self.operation_dict = dict()
        self.anomaly_queue = anomaly_queue


    def analyze(self, operation):
        #print(operation)
        key = operation.orig_ip + ";" + operation.resp_ip + ";" + operation.service + ";" + operation.uid
        #print(key)
        if key not in self.operation_dict:
            self.operation_dict[key] = OperationModel(key, operation, self.anomaly_queue);
        self.operation_dict[key].update(operation)

        if self.last_check == None:
            self.last_check = operation.ts
        elif operation.ts > self.last_check + PERIODIC_CHECK_TIME:
            self.check(operation.ts)
            self.last_check += PERIODIC_CHECK_TIME


    def check(self, ts):
        for key in self.operation_dict:
            self.operation_dict[key].check(ts)
