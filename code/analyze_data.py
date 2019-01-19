from data_value import DataValue 
from collections import deque
from anomaly import MeasurementAnomaly
from inc_mean_std import Analog
import numpy as np 
import math

COUNT_EACH_NORM = 100.0
CONFI_TH = 0.6
PERIOD_LEN = 60 * 60 * 24
SLOT_LEN = 60 * 20 


def getVariability(x):
    if x == 0 or x == 1:
        return 0
    return -x*math.log(x, 2) - (1-x)*math.log(1-x, 2)


def sigmoid(x):
    return 2 / (1 + math.exp(-x)) - 1


def generate_anomaly(ts,
                     desp,
                     confi,
                     index,
                     anomaly_queue,
                     measurement=None,
                     measurement_type=None,
                     type_confi=0,
                     current=None,
                     mean=None,
                     std=None):
    if confi >= CONFI_TH:
        anomaly = MeasurementAnomaly(ts,
                                     desp,
                                     confi,
                                     index,
                                     measurement,
                                     measurement_type,
                                     type_confi,
                                     current,
                                     mean,
                                     std)
        anomaly_queue.put_nowait(anomaly)


class BinaryValue:
    def __init__(self, key, data_value, anomaly_queue):
        self.index = key
        self.count_total = 0
        self.count_true = 0
        self.normal_status = None
        self.anomaly_queue = anomaly_queue


    def detect(self, data_value):
        value = data_value.value
        confi = 0 
        if self.normal_status != None and self.normal_status * value < 0:
            ratio = self.count_true*1.0/self.count_total
            confi = sigmoid(self.count_total/COUNT_EACH_NORM) * (1-getVariability(ratio))
            desp = "BINARY_FAULT"
            generate_anomaly(data_value.ts,
                             desp,
                             confi,
                             self.index,
                             self.anomaly_queue,
                             data_value,
                             "Binaray",
                             1,
                             value,
                             self.normal_status,
                             max(ratio, 1-ratio))
 
        if not data_value.is_event and confi < 0.95: 
            self.count_total += 1
            if value > 0:
                self.count_true += 1
            ratio = self.count_true*1.0/self.count_total
            if ratio >= 0.5:
                self.normal_status = 1
            else:
                self.normal_status = -1


class AnalogValue:
    def __init__(self, key, data_value, anomaly_queue):
        self.index = key
        self.analog_model = Analog(COUNT_EACH_NORM, PERIOD_LEN, SLOT_LEN)
        self.anomaly_queue = anomaly_queue


    def detect(self, data_value):
        #print(data_value.index)
        #print(self.analog_model.getType())
        value = data_value.value
        ts = data_value.ts
        if not data_value.is_event:
            rst, confi, mean, diff = self.analog_model.update(value, ts)
        else:
            rst, confi, mean, diff = self.analog_model.detect(value, ts)

        if rst != 0:
            if rst == 1:
                desp = "ANALOG_TOO_LARGE"
            else: 
                desp = "ANALOG_TOO_SMALL"
            generate_anomaly(ts,
                             desp,
                             confi,
                             self.index,
                             self.anomaly_queue,
                             data_value,
                             self.analog_model.getType(),
                             self.analog_model.getTypeConfi(),
                             value,
                             mean,
                             diff)
 

class DataValueModel:
    def __init__(self, key, data_value, anomaly_queue):
        self.type = "Unknown"
        self.data = None

        if data_value.protocol == "MODBUS":
            if data_value.data_type == "Coil":
                self.type = "Modbus_Coil"
                self.data = BinaryValue(key, data_value, anomaly_queue)
            elif data_value.data_type == "HoldingRegister":
                self.type = "Modbus_HoldingRegister"
            elif data_value.data_type == "InputRegister":
                self.type = "Modbus_InputRegister"
            elif data_value.data_type == "DiscreteInput":
                self.type = "Modbus_DiscreteInput"
            else:
                self.type = "Modbus_Other"
        elif data_value.protocol == "DNP3":
            if data_value.data_type == "Analog":
                self.type = "DNP3_Analog"
                self.data = AnalogValue(key, data_value, anomaly_queue)
            elif data_value.data_type == "Binary":
                self.type = "DNP3_Binary"
                self.data = BinaryValue(key, data_value, anomaly_queue)
            elif data_value.data_type == "Counter":
                self.type = "DNP3_Counter"
            else:
                self.type = "DNP3_Other"


    def update(self, data_value):
        if self.type == "DNP3_Binary" or self.type == "DNP3_Analog":
            self.data.detect(data_value)
        #else:
        #    print(3, self.type) 


class DataAnalyzer():
    def __init__(self, anomaly_queue):
        self.data_dict = dict() 
        self.anomaly_queue = anomaly_queue


    def analyze(self, data_value):
        #print(data_value)
        key = data_value.holder_ip + ";" + data_value.protocol + ";" + data_value.uid + ";" + data_value.data_type + ";" + str(data_value.index)
        #print(key)
        if key not in self.data_dict:
            self.data_dict[key] = DataValueModel(key, data_value, self.anomaly_queue);
        self.data_dict[key].update(data_value)
