import time
import shelve

import settings

time_format = settings.time_format
port_count_file = settings.port_count_file
port_start_count = settings.port_start_count


def timestamp_to_timestr(time_stamp):
    return time.strftime(time_format, time.localtime(time_stamp))


def get_tcp_port():
    db = shelve.open(port_count_file)
    try:
        port = db['port']
    except KeyError:
        db['port'] = settings.port_start_count
        return port_start_count
    port += 1
    db['port'] = port
    db.close()
    return port