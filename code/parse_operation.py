from operation import Operation 
import datetime

def parse_operation(args):
    protocol_info = args[0]
    operation = Operation()

    # Timestamp
    operation.ts = (protocol_info[0] - datetime.datetime(1970, 1, 1)).total_seconds()

    # Connection
    operation.orig_ip = str(protocol_info[1][0][0])
    operation.resp_ip = str(protocol_info[1][0][2])

    # Control Protocol (service) 
    operation.service = str(protocol_info[2])
   
    # uid 
    operation.uid = str(protocol_info[3])

    # Function code 
    operation.fc = protocol_info[4].value

    # Function name 
    operation.fn = str(protocol_info[5])

    # Is from teh originator side 
    operation.is_orig = protocol_info[6]
 
    #print(operation)
    return operation
