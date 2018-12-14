#!/usr/bin/env python

import gevent
import sys
import timeit
from gevent import select
from gevent.queue import Queue, Empty
from pybroker import *
from pprint import pprint
from parse_packet import parse_packet
from parse_operation import parse_operation
from parse_data_value import parse_data_value
from packet import Packet
from flow import Flow
from operation import Operation
from data_value import DataValue 
from analyze_packet import PacketAnalyzer 
from analyze_flow import FlowAnalyzer 
from analyze_operation import OperationAnalyzer
from analyze_data import DataAnalyzer 
from manage_anomaly import AnomalyManager
            
raw_packet_queue = Queue()
raw_operation_queue = Queue()
raw_data_value_queue = Queue()
packet_queue = Queue()
operation_queue = Queue()
data_value_queue = Queue()
flow_queue = Queue()
anomaly_queue = Queue()
meta_alert_queue = Queue()
TIMEOUT = 5


def listener():
    epl = endpoint("listener")
    mql = message_queue("bro/event", epl)
    icsq = epl.incoming_connection_status()
    
    epl.listen(9999, "127.0.0.1")
    select.select([icsq.fd()],[],[])
    msgs = icsq.want_pop()
    
    for m in msgs:
        print("incoming connection", m.peer_name, m.status)
        assert(m.peer_name == "connector")
        assert(m.status == incoming_connection_status.tag_established)
    
    total_time = 0
    count = 0
    while True:
        select.select([mql.fd()], [], [])
        msgs = mql.want_pop()
        for m in msgs:
            start = timeit.default_timer()
            event_name = m[0] 
            if(event_name.as_string() == "FlowLevel::packet_get"):
                raw_packet_queue.put_nowait(m[1])
            if(event_name.as_string() == "ProtocolLevel::protocol_get"):
                raw_operation_queue.put_nowait(m[1])
            if(event_name.as_string() == "DataLevel::data_get"):
                raw_data_value_queue.put_nowait(m[1])
            if(event_name.as_string() == "bro_done"):
                #print("Listener quit!")
                if count != 0:
                    print("Listener time: " + str(total_time/count))
                return;
            #print("got message")
            total_time += timeit.default_timer() - start
            count += 1
            gevent.sleep(0)


def packet_parser(n):
    try:
        total_time = 0
        count = 0
        while True:
            #print(count)
            count += 1
            start = timeit.default_timer()
            raw_packet = raw_packet_queue.get(timeout=TIMEOUT)
            packet = parse_packet(raw_packet)
            packet_queue.put_nowait(packet)
            total_time += timeit.default_timer() - start
            gevent.sleep(0)
    except Empty:
        #print('Packet parser %s quit!' % (n))
        if count != 0:
            print("Packet parser time: " + str(total_time/count))


def operation_parser(n):
    try:
        total_time = 0
        count = 0
        while True:
            #print(count)
            count += 1
            start = timeit.default_timer()
            raw_operation = raw_operation_queue.get(timeout=TIMEOUT)
            operation = parse_operation(raw_operation)
            operation_queue.put_nowait(operation)
            total_time += timeit.default_timer() - start
            gevent.sleep(0)
    except Empty:
        #print('Operation parser %s quit!' % (n))
        if count != 0:
            print("Operation parser time: " + str(total_time/count))


def data_value_parser(n):
    try:
        total_time = 0
        count = 0
        while True:
            #print(count)
            count += 1
            start = timeit.default_timer()
            raw_data_value = raw_data_value_queue.get(timeout=TIMEOUT)
            data_value = parse_data_value(raw_data_value)
            data_value_queue.put_nowait(data_value)
            total_time += timeit.default_timer() - start
            gevent.sleep(0)
    except Empty:
        #print('Data value parser %s quit!' % (n))
        if count != 0:
            print("Content parser time: " + str(total_time/count))


def packet_analyzer(n):
    try:
        total_time = 0
        count = 0
        anl = PacketAnalyzer(anomaly_queue, flow_queue)
        while True:
            start = timeit.default_timer()
            packet = packet_queue.get(timeout=TIMEOUT)
            #print(packet)
            anl.analyze(packet)
            total_time += timeit.default_timer() - start
            count += 1
            gevent.sleep(0)
    except Empty:
        #print('Packet analyzer %s quit!' % (n))
        if count != 0:
            print("Packet analyzer time: " + str(total_time/count))

def flow_analyzer(n):
    try:
        total_time = 0
        count = 0
        anl = FlowAnalyzer(anomaly_queue)
        while True:
            start = timeit.default_timer()
            flow = flow_queue.get(timeout=TIMEOUT)
            #print(flow)
            anl.analyze(flow)
            total_time += timeit.default_timer() - start
            count += 1
            gevent.sleep(0)
    except Empty:
        #print('Flow analyzer %s quit!' % (n))
        if count != 0:
            print("Flow analyzer time: " + str(total_time/count))


def operation_analyzer(n):
    try:
        total_time = 0
        count = 0
        anl = OperationAnalyzer(anomaly_queue)
        while True:
            start = timeit.default_timer()
            operation = operation_queue.get(timeout=TIMEOUT)
            #print(operation)
            anl.analyze(operation)
            total_time += timeit.default_timer() - start
            count += 1
            gevent.sleep(0)
    except Empty:
        #print('Operation analyzer %s quit!' % (n))
        if count != 0:
            print("Operation analyzer time: " + str(total_time/count))


def data_value_analyzer(n):
    try:
        total_time = 0
        count = 0
        anl = DataAnalyzer(anomaly_queue)
        while True:
            start = timeit.default_timer()
            data_value = data_value_queue.get(timeout=TIMEOUT)
            #print(data_value)
            anl.analyze(data_value)
            total_time += timeit.default_timer() - start
            count += 1
            gevent.sleep(0)
    except Empty:
        #print('Data value analyzer %s quit!' % (n))
        if count != 0:
            print("Content analyzer time: " + str(total_time/count))


def anomaly_manager(n):
    try:
        total_time = 0
        count = 0
        mng = AnomalyManager(meta_alert_queue)
        while True:
            start = timeit.default_timer()
            anomaly = anomaly_queue.get(timeout=TIMEOUT)
            r ../trace/dnp3_test8_with_anomaly.pcap end_point.bro
            total_time += timeit.default_timer() - otart
            count += 1
            gevent.sleep(0)
    except Empty:
        mng.print_alerts()
        mng.stop()
        #print('Anomaly Manager %s quit!' % (n))
        if count != 0:
            print("Anomaly Manager time: " + str(total_time/count))


def main():
    gevent.joinall([
        gevent.spawn(listener),
        gevent.spawn(packet_parser, 1),
        gevent.spawn(operation_parser, 1),
        gevent.spawn(data_value_parser, 1),
        gevent.spawn(packet_analyzer, 1),
        gevent.spawn(flow_analyzer, 1),
        gevent.spawn(operation_analyzer, 1),
        gevent.spawn(data_value_analyzer, 1),
        gevent.spawn(anomaly_manager, 1),
    ])
 

if __name__ == '__main__': main()
