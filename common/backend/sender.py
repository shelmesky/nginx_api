import socket
import struct
import sys
 
import settings
 
multicast_addr = settings.multicast_addr
port = settings.multicast_port
 
def sender(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    
    sock.sendto(message, (multicast_addr, port))
    sock.close()
    return True


if __name__ == '__main__':
    if sys.argv[1]:
        sender(sys.argv[1])