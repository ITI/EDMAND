@load flow_level.bro
@load protocol_level.bro
@load data_level.bro

module EndPoint;

export {
    const broker_port: port = 9999/tcp &redef;
    redef exit_only_after_terminate = F;
    redef Broker::endpoint_name = "connector";
}

event bro_init() &priority=5
{
    ##suspend_processing();
    Broker::enable();
    Broker::connect("127.0.0.1", broker_port, 1sec);
    Broker::auto_event("bro/event/packet_get", FlowLevel::packet_get);
    Broker::auto_event("bro/event/protocol_get", ProtocolLevel::protocol_get);
    Broker::auto_event("bro/event/data_get", DataLevel::data_get);
    Broker::auto_event("bro/event/bro_done", bro_done);
}

event Broker::outgoing_connection_established(peer_address: string, peer_port: port, peer_name: string)
{
    print "Broker::outgoing_connection_established", peer_address, peer_port, peer_name;
    ##continue_processing();
}

event Broker::outgoing_connection_broken(peer_address: string, peer_port: port)
{
    terminate();
}

event bro_done()
{
    print "bro_done";
}
