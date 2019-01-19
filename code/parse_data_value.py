from data_value import DataValue 
import datetime

def parse_data_value(args):
    data_info = args[0]
    data_value = DataValue()

    # Timestamp
    data_value.ts = (data_info[0] - datetime.datetime(1970, 1, 1)).total_seconds()
    #print(data_value.ts)

    # Connection
    data_value.holder_ip = str(data_info[1][0][2])

    # Control Protocol 
    data_value.protocol = str(data_info[2])
   
    # uid 
    data_value.uid = str(data_info[3])

    # Data type 
    data_value.data_type = str(data_info[4])

    # Target index 
    data_value.index = data_info[5].value

    # Data value 
    data_value.value = data_info[6]

    # Is event 
    data_value.is_event = data_info[7]
 
    #print(data_value)
    return data_value 
