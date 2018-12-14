from pybroker import *
from packet import Packet

def parse_conn(conn_rec, packet):
    fields = conn_rec.fields()

    # Connection tuple (uid included)
    assert(fields[0].valid())
    d = fields[0].get()
    assert(d.which() == data.tag_record)
    conn_tuple_rec = d.as_record()
    tuple_fields = conn_tuple_rec.fields()
    orig_h = str(tuple_fields[0].get().as_address())
    orig_p = str(tuple_fields[1].get().as_port())
    resp_h = str(tuple_fields[2].get().as_address())
    resp_p = str(tuple_fields[3].get().as_port())
    conn_tuple = (orig_h, orig_p, resp_h, resp_p)
    packet.conn = conn_tuple
    #print(packet.conn)

    # Service
    assert(fields[5].valid())
    d = fields[5].get()
    assert(d.which() == data.tag_set)
    service_set = d.as_set()
    packet.service = [] 
    for j in range(service_set.size()):
        packet.service.append(service_set[j].as_string())
    #print(packet.service)

    # uid 
    d = fields[7].get()
    assert(d.which() == data.tag_string)
    uid = d.as_string()
    #print(uid)


def parse_hdr(hdr_rec, packet):
    fields = hdr_rec.fields()

    # IPv4
    if fields[0].valid():
        #print("ip4")
        d = fields[0].get()
        assert(d.which() == data.tag_record)
        ip4_hdr_rec = d.as_record()
        ip4_hdr_fields = ip4_hdr_rec.fields()
        packet.packet_len = ip4_hdr_fields[2].get().as_count()
        packet.sender = str(ip4_hdr_fields[6].get().as_address())
        packet.receiver = str(ip4_hdr_fields[7].get().as_address())
        #print("packet_len: {}, src: {}, dst: {}".format(packet.packet_len, packet.sender, packet.receiver))

    # IPv6
    elif fields[1].valid(): 
        #print("ip6")
        d = fields[1].get()
        assert(d.which() == data.tag_record)
        ip4_hdr_rec = d.as_record()
        ip4_hdr_fields = ip4_hdr_rec.fields()
        packet.packet_len = ip4_hdr_fields[2].get().as_count()
        packet.sender = str(ip4_hdr_fields[5].get().as_address())
        packet.receiver = str(ip4_hdr_fields[6].get().as_address())
        #print("packet_len: {}, src: {}, dst: {}".format(packet.packet_len, packet.sender, packet.receiver))

    # TCP
    if fields[2].valid():
        packet.protocol_type = "TCP"
        #print(packet.protocol_type)
        d = fields[2].get()
        assert(d.which() == data.tag_record)
        tcp_hdr_rec = d.as_record()
        packet.tcp_flag = tcp_hdr_rec.fields()[6].get().as_count()
        #print("tcp_flag: {}".format(packet.tcp_flag))

    # UDP
    elif fields[3].valid():
        packet.protocol_type = "UDP"
        #print(packet.protocol_type)

    # ICMP
    elif fields[4].valid():
        packet.protocol_type = "ICMP"
        #print(packet.protocol_type)
 

def parse_packet(packet_info):
    assert(packet_info.which() == data.tag_record)
    packet_rec = packet_info.as_record()
    fields = packet_rec.fields()

    # Timestamp
    assert(fields[0].valid())
    ts = fields[0].get()
    assert(ts.which() == data.tag_time)
    # Connection
    assert(fields[1].valid())
    conn = fields[1].get()
    assert(conn.which() == data.tag_record)
    conn_rec = conn.as_record()
    # Packet header
    assert(fields[2].valid())
    hdr = fields[2].get()
    assert(hdr.which() == data.tag_record)
    hdr_rec = hdr.as_record()
   
    packet = Packet()
    packet.ts = ts.as_time().value
    #print(packet.ts)

    parse_conn(conn_rec, packet)
    parse_hdr(hdr_rec, packet)
    #print(packet)
    #print
    return packet
