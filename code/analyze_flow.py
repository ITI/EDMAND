from flow import Flow 
from anomaly import FlowAnomaly
from inc_mean_std import ExpMeanSTD
import numpy as np 
import math

COUNT_EACH_NORM = 100.0
CONFI_TH = 0.666666

def sigmoid(x):
    return 2 * (1 / (1 + math.exp(-x)) - 0.5)


def generate_anomaly(ts,
                     desp,
                     confi,
                     index,
                     anomaly_queue,
                     flow=None,
                     iat=None,
                     mean=None,
                     std=None):
    if confi >= CONFI_TH:
        anomaly = FlowAnomaly(ts,
                              desp,
                              confi,
                              index,
                              flow,
                              iat,
                              mean,
                              std)
        anomaly_queue.put_nowait(anomaly)


class FlowModel:
    def __init__(self, index, anomaly_queue):
        self.index = index
        self.anomaly_queue = anomaly_queue            
        self.count_pkt_ab = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 
        self.count_pkt_ba = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 
        self.mean_bytes_ab = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 
        self.mean_bytes_ba = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 


    def update(self, flow):
        self.update_each(flow, flow.count_pkt_ab, self.count_pkt_ab, "PACKET_AB_TOO_MANY", "PACKET_AB_TOO_FEW")
        self.update_each(flow, flow.count_pkt_ba, self.count_pkt_ba, "PACKET_BA_TOO_MANY", "PACKET_BA_TOO_FEW")
        self.update_each(flow, flow.mean_bytes_ab, self.mean_bytes_ab, "MEAN_BYTES_AB_TOO_LARGE", "MEAN_BYTES_AB_TOO_SMALL")
        self.update_each(flow, flow.mean_bytes_ba, self.mean_bytes_ba, "MEAN_BYTES_BA_TOO_LARGE", "MEAN_BYTES_BA_TOO_SMALL")


    def update_each(self, flow, current, stats, desp_g=None, desp_l=None):
        rst, confi, mean, std = stats.update(current, True)
        if rst != 0:
            if rst == 1 and desp_g != None:
                generate_anomaly(flow.end,
                                 desp_g,
                                 confi,
                                 self.index,
                                 self.anomaly_queue,
                                 flow,
                                 current,
                                 mean,
                                 std) 
            if rst == -1 and desp_l != None:
                generate_anomaly(flow.end,
                                 desp_l,
                                 confi,
                                 self.index,
                                 self.anomaly_queue,
                                 flow,
                                 current,
                                 mean,
                                 std) 


class FlowAnalyzer():
    def __init__(self, anomaly_queue):
        self.flow_dict = dict()
        self.anomaly_queue = anomaly_queue


    def analyze(self, flow):
        #print(flow)
        key = flow.orig + ";" + flow.resp + ";" + flow.protocol_type + ";" + flow.service 
        #print(key)
        if key not in self.flow_dict:
            self.flow_dict[key] = FlowModel(key, self.anomaly_queue);
        self.flow_dict[key].update(flow)
