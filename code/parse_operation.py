from pybroker import *
from operation import Operation 

def parse_conn(conn_rec, operation):
    fields = conn_rec.fields()

    # Connection tuple
    assert(fields[0].valid())
    d = fields[0].get()
    assert(d.which() == data.tag_record)
    conn_tuple_rec = d.as_record()
    tuple_fields = conn_tuple_rec.fields()
    orig_h = str(tuple_fields[0].get().as_address())
    resp_h = str(tuple_fields[2].get().as_address())
    operation.orig_ip = orig_h 
    operation.resp_ip = resp_h 


def parse_operation(protocol_info):
    assert(protocol_info.which() == data.tag_record)
    protocol_rec = protocol_info.as_record()
    fields = protocol_rec.fields()

    operation = Operation()

    # Timestamp
    assert(fields[0].valid())
    ts = fields[0].get()
    assert(ts.which() == data.tag_time)
    operation.ts = ts.as_time().value

    # Connection
    assert(fields[1].valid())
    conn = fields[1].get()
    assert(conn.which() == data.tag_record)
    conn_rec = conn.as_record()
    parse_conn(conn_rec, operation) 

    # Control Protocol (service) 
    assert(fields[2].valid())
    service = fields[2].get()
    assert(service.which() == data.tag_string)
    operation.service = service.as_string()
   
    # uid 
    assert(fields[3].valid())
    uid = fields[3].get()
    assert(uid.which() == data.tag_string)
    operation.uid = uid.as_string()

    # Function code 
    assert(fields[4].valid())
    fc = fields[4].get()
    assert(fc.which() == data.tag_count)
    operation.fc = fc.as_count()

    # Function name 
    assert(fields[5].valid())
    fn = fields[5].get()
    assert(fn.which() == data.tag_string)
    operation.fn = fn.as_string()

    # Is from teh originator side 
    assert(fields[6].valid())
    is_orig = fields[6].get()
    assert(is_orig.which() == data.tag_boolean)
    operation.is_orig = is_orig.as_bool()
 
    #print(operation)
    #print
    return operation
