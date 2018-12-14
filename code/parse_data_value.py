from pybroker import *
from data_value import DataValue 

def parse_conn(conn_rec, data_value):
    fields = conn_rec.fields()

    # Connection tuple
    assert(fields[0].valid())
    d = fields[0].get()
    assert(d.which() == data.tag_record)
    conn_tuple_rec = d.as_record()
    tuple_fields = conn_tuple_rec.fields()
    resp_h = str(tuple_fields[2].get().as_address())
    data_value.holder_ip = resp_h 
    #print(data_value.holder_ip)


def parse_data_value(data_info):
    assert(data_info.which() == data.tag_record)
    data_rec = data_info.as_record()
    fields = data_rec.fields()

    data_value = DataValue()

    # Timestamp
    assert(fields[0].valid())
    ts = fields[0].get()
    assert(ts.which() == data.tag_time)
    data_value.ts = ts.as_time().value
    #print(data_value.ts)

    # Connection
    assert(fields[1].valid())
    conn = fields[1].get()
    assert(conn.which() == data.tag_record)
    conn_rec = conn.as_record()
    parse_conn(conn_rec, data_value)

    # Control Protocol 
    assert(fields[2].valid())
    protocol = fields[2].get()
    assert(protocol.which() == data.tag_string)
    data_value.protocol = protocol.as_string()
   
    # uid 
    assert(fields[3].valid())
    uid = fields[3].get()
    assert(uid.which() == data.tag_string)
    data_value.uid = uid.as_string()

    # Data type 
    assert(fields[4].valid())
    data_type = fields[4].get()
    assert(data_type.which() == data.tag_string)
    data_value.data_type = data_type.as_string()

    # Target index 
    assert(fields[5].valid())
    index = fields[5].get()
    assert(index.which() == data.tag_count)
    data_value.index = index.as_count()

    # Data value 
    assert(fields[6].valid())
    value = fields[6].get()
    assert(value.which() == data.tag_real)
    data_value.value = value.as_real()

    # Is event 
    assert(fields[7].valid())
    is_event = fields[7].get()
    assert(is_event.which() == data.tag_boolean)
    data_value.is_event = is_event.as_bool()
 
    #print(data_value)
    #print
    return data_value 
