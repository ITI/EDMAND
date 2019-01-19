@load flow_level.bro
@load protocol_level.bro
@load data_level.bro

module EndPoint;

export {
    const broker_port: port = 9999/tcp &redef;
    redef Broker::peer_counts_as_iosource=F;
    redef exit_only_after_terminate = F;
}

event bro_init() &priority=5
{
    #suspend_processing();
    Broker::peer("127.0.0.1", broker_port, 1sec);
    Broker::auto_publish("edmand/packet_get", FlowLevel::packet_get);
    Broker::auto_publish("edmand/protocol_get", ProtocolLevel::protocol_get);
    Broker::auto_publish("edmand/data_get", DataLevel::data_get);
    Broker::auto_publish("edmand/bro_done", bro_done);
}

event Broker::peer_added(endpoint: Broker::EndpointInfo, msg: string)
{
    print "peer added", endpoint;
    #continue_processing();
}

event Broker::peer_lost(endpoint: Broker::EndpointInfo, msg: string)
{
    print "peer lost", endpoint;
    terminate();
}

event bro_done()
{
    print "bro_done";
}
