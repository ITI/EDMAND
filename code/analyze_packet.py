from packet import Packet 
from flow import Flow
from anomaly import PacketAnomaly
from den_stream import DenStream1D 
from inc_mean_std import IncMeanSTD, ExpMeanSTD
import datetime
import numpy as np 
import math

COUNT_NORM = 100.0
COUNT_EACH_NORM = 100.0
CONFI_TH = 0.9
PERIOD = 60*10 

def sigmoid(x):
    return 2 * (1 / (1 + math.exp(-x)) - 0.5)


def generate_flow(start, end, orig, resp, protocol, service, service_stats, flow_queue):
    flow = Flow(
                start,
                end,
                orig,
                resp,
                protocol,
                service,
                service_stats.bytes_flow_ab.getTotal(),
                service_stats.bytes_flow_ba.getTotal(), 
                service_stats.bytes_flow_ab.getMean(),
                service_stats.bytes_flow_ab.getSTD(),
                service_stats.bytes_flow_ba.getMean(),
                service_stats.bytes_flow_ba.getSTD(),
                service_stats.iat_flow_ab.getMean(),
                service_stats.iat_flow_ab.getSTD(),
                service_stats.iat_flow_ba.getMean(),
                service_stats.iat_flow_ba.getSTD()
                )
    flow_queue.put_nowait(flow)


def generate_anomaly(ts,
                     desp,
                     confi,
                     index,
                     anomaly_queue,
                     packet=None,
                     current=None,
                     normal_mean=None,
                     normal_std=None):
    if confi >= CONFI_TH:
        anomaly = PacketAnomaly(ts,
                                desp,
                                confi,
                                index,
                                packet,
                                current,
                                normal_mean,
                                normal_std)
        anomaly_queue.put_nowait(anomaly)


class OrigStats():
    def __init__(self):
        self.resp_dict = dict()
        self.total = 0


class RespStats():
    def __init__(self):
        self.protocol_dict = dict()
        self.total = 0


class ProtocolStats(): 
    def __init__(self):
        self.service_dict = dict()
        self.total = 0


class ServiceStats():
    def __init__(self, index, anomaly_queue):
        self.index = index
        self.anomaly_queue = anomaly_queue

        self.total_ab = 0
        self.total_ba = 0

        self.last_seen_ab = None
        self.iat_ab = DenStream1D(0.5) 
        #self.iat_ab = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 
        self.iat_flow_ab = IncMeanSTD(COUNT_EACH_NORM) 

        self.last_seen_ba = None
        self.iat_ba = DenStream1D(0.5)
        #self.iat_ba = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 
        self.iat_flow_ba = IncMeanSTD(COUNT_EACH_NORM) 

        self.bytes_ab = DenStream1D(1)
        #self.bytes_ab = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 
        self.bytes_flow_ab = IncMeanSTD(COUNT_EACH_NORM) 

        self.bytes_ba = DenStream1D(1) 
        #self.bytes_ba = ExpMeanSTD(COUNT_EACH_NORM, 0.02) 
        self.bytes_flow_ba = IncMeanSTD(COUNT_EACH_NORM) 


    def clearFlow(self):
        self.iat_flow_ab = IncMeanSTD(COUNT_EACH_NORM) 
        self.iat_flow_ba = IncMeanSTD(COUNT_EACH_NORM) 
        self.bytes_flow_ab = IncMeanSTD(COUNT_EACH_NORM) 
        self.bytes_flow_ba = IncMeanSTD(COUNT_EACH_NORM) 


    def update(self, packet):
        if packet.sender == packet.conn[0]:
            if self.last_seen_ab != None:
                iat = packet.ts - self.last_seen_ab
                rst, ano_score, p_c_list, p_r_list = self.iat_ab.merge(iat, packet.ts)
                #rst, ano_score, p_c_list, p_r_list = self.iat_ab.update(iat)
                self.iat_flow_ab.update(iat)
                #print("iat_ab: " + str(iat))
                #print(self.iat_ab)
                if not rst:
                    desp = "PACKET_IAT"
                    confi = sigmoid(self.total_ab/COUNT_EACH_NORM) * ano_score
                    generate_anomaly(packet.ts,
                                     desp,
                                     confi,
                                     self.index,
                                     self.anomaly_queue,
                                     packet,
                                     iat,
                                     p_c_list,
                                     p_r_list)
            self.last_seen_ab = packet.ts

            packet_len = packet.packet_len 
            rst, ano_score, p_c_list, p_r_list = self.bytes_ab.merge(packet_len, packet.ts)
            #rst, ano_score, p_c_list, p_r_list = self.bytes_ab.update(packet_len)
            self.bytes_flow_ab.update(packet_len)
            #print("bytes_ab: " + str(packet_len))
            #print(self.bytes_ab)
            if not rst:
                desp = "PACKET_BYTES"
                confi = sigmoid(self.total_ab/COUNT_EACH_NORM) * ano_score 
                generate_anomaly(packet.ts,
                                 desp,
                                 confi,
                                 self.index,
                                 self.anomaly_queue,
                                 packet,
                                 packet_len,
                                 p_c_list,
                                 p_r_list)
            self.total_ab += 1
        else:
            if self.last_seen_ba != None:
                iat = packet.ts - self.last_seen_ba
                rst, ano_score, p_c_list, p_r_list = self.iat_ba.merge(iat, packet.ts)
                #rst, ano_score, p_c_list, p_r_list = self.iat_ba.update(iat)
                self.iat_flow_ba.update(iat)
                #print("iat_ba: " + str(iat))
                #print(self.iat_ba)
                if not rst:
                    desp = "PACKET_IAT"
                    confi = sigmoid(self.total_ba/COUNT_EACH_NORM) * ano_score
                    generate_anomaly(packet.ts,
                                     desp,
                                     confi,
                                     self.index,
                                     self.anomaly_queue,
                                     packet,
                                     iat,
                                     p_c_list,
                                     p_r_list)
            self.last_seen_ba = packet.ts

            packet_len = packet.packet_len 
            rst, ano_score, p_c_list, p_r_list = self.bytes_ba.merge(packet_len, packet.ts)
            #rst, ano_score, p_c_list, p_r_list = self.bytes_ba.update(packet_len)
            self.bytes_flow_ba.update(packet_len)
            #print("bytes_ba: " + str(packet_len))
            #print(self.bytes_ba)
            if not rst:
                desp = "PACKET_BYTES"
                confi = sigmoid(self.total_ba/COUNT_EACH_NORM) * ano_score 
                generate_anomaly(packet.ts,
                                 desp,
                                 confi,
                                 self.index,
                                 self.anomaly_queue,
                                 packet,
                                 packet_len,
                                 p_c_list,
                                 p_r_list)
            self.total_ba += 1
 

class PacketAnalyzer():
    def __init__(self, anomaly_queue, flow_queue):
        self.orig_dict = dict()
        self.total = 0
        self.anomaly_queue = anomaly_queue
        self.flow_queue = flow_queue
        self.last_aggregate = -1


    def analyze(self, packet):
        if self.last_aggregate == -1:
            self.last_aggregate = packet.ts

        while packet.ts > self.last_aggregate + PERIOD:
            self.aggregate()
            self.last_aggregate += PERIOD 

        orig = packet.conn[0]
        resp = packet.conn[2]
        protocol = packet.protocol_type
        service_list = packet.service
        index = orig + ";" + resp + ";" + protocol + ";" + str(service_list)
        
        if orig not in self.orig_dict:
            confi = sigmoid(self.total/COUNT_NORM)
            generate_anomaly(packet.ts,
                             "NEW_ORIG",
                             confi,
                             index,
                             self.anomaly_queue,
                             packet)
            self.orig_dict[orig] = OrigStats()
        self.total += 1

        orig_stats = self.orig_dict[orig]
        if resp not in orig_stats.resp_dict:
            confi = sigmoid(orig_stats.total/COUNT_NORM)
            generate_anomaly(packet.ts,
                             "NEW_RESP",
                             confi,
                             index,
                             self.anomaly_queue,
                             packet)
            orig_stats.resp_dict[resp] = RespStats()
        orig_stats.total += 1

        resp_stats = orig_stats.resp_dict[resp]
        if protocol not in resp_stats.protocol_dict:
            confi = sigmoid(resp_stats.total/COUNT_NORM)
            generate_anomaly(packet.ts,
                             "NEW_PROTOCOL",
                             confi,
                             index,
                             self.anomaly_queue,
                             packet)
            resp_stats.protocol_dict[protocol] = ProtocolStats()
        resp_stats.total += 1

        protocol_stats = resp_stats.protocol_dict[protocol]
        for service in service_list:
            if service not in protocol_stats.service_dict:
                confi = sigmoid(protocol_stats.total/COUNT_NORM)
                generate_anomaly(packet.ts,
                                 "NEW_SERVICE",
                                 confi,
                                 index,
                                 self.anomaly_queue,
                                 packet)
                protocol_stats.service_dict[service] = ServiceStats(index, self.anomaly_queue)
            service_stats = protocol_stats.service_dict[service]
            service_stats.update(packet)
        protocol_stats.total += 1


    def aggregate(self):
        for orig in self.orig_dict:
            orig_stats = self.orig_dict[orig]
            for resp in orig_stats.resp_dict:
                resp_stats = orig_stats.resp_dict[resp]
                for protocol in resp_stats.protocol_dict:
                    protocol_stats = resp_stats.protocol_dict[protocol] 
                    for service in protocol_stats.service_dict:
                        service_stats = protocol_stats.service_dict[service]
                        generate_flow(self.last_aggregate,
                                      self.last_aggregate+PERIOD,
                                      orig,
                                      resp,
                                      protocol,
                                      service,
                                      service_stats,
                                      self.flow_queue)
                        service_stats.clearFlow()
