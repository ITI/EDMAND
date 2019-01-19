from packet import Packet 
import datetime

def parse_conn(conn, packet):
    # Connection tuple 
    conn_tuple = conn[0]
    orig_h = str(conn_tuple[0])
    orig_p = str(conn_tuple[1])
    resp_h = str(conn_tuple[2])
    resp_p = str(conn_tuple[3])
    packet.conn = (orig_h, orig_p, resp_h, resp_p)
    #print(packet.conn)

    # Service
    packet.service = list(map(str, conn[5]))
    #print(packet.service)

    # conn_id
    conn_id = str(conn[7]) 
    #print(conn_id)


def parse_hdr(hdr, packet):
    # IPv4
    if hdr[0] is not None:
        #print("ip4")
        packet.packet_len = hdr[0][2].value
        packet.sender = str(hdr[0][6])
        packet.receiver = str(hdr[0][7])
        #print("packet_len: {}, src: {}, dst: {}".format(packet.packet_len, packet.sender, packet.receiver))

    # IPv6
    elif hdr[1] is not None: 
        #print("ip6")
        packet.packet_len = hdr[0][2].value
        packet.sender = str(hdr[0][5])
        packet.receiver = str(hdr[0][6])
        #print("packet_len: {}, src: {}, dst: {}".format(packet.packet_len, packet.sender, packet.receiver))

    # TCP
    if hdr[2] is not None:
        packet.protocol_type = "TCP"
        #print(packet.protocol_type)
        packet.tcp_flag = hdr[2][6].value
        #print("tcp_flag: {}".format(packet.tcp_flag))

    # UDP
    elif hdr[3] is not None:
        packet.protocol_type = "UDP"
        #print(packet.protocol_type)

    # ICMP
    elif hdr[4] is not None:
        packet.protocol_type = "ICMP"
        #print(packet.protocol_type)
 

def parse_packet(args):
    packet_info = args[0]
    packet = Packet()

    # Timestamp
    packet.ts = (packet_info[0] - datetime.datetime(1970, 1, 1)).total_seconds()
    #print(packet.ts)

    # Connection
    parse_conn(packet_info[1], packet)

    # Packet header
    parse_hdr(packet_info[2], packet)

    #print(packet)
    return packet
