import socket
import struct
import textwrap


def main():
    # raw socket is used to receive raw packets.This means packets received at the Ethernet layer will directly pass to the raw socket.
    # first argument: socket family,second arg: socket type and third one is protocol( it is ntohs(3) to make sure it is compatible with all types of computers)

    connect = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    while True:
        eth_frame, addr = connect.recvfrom(65536)   #receive ethernet packets
        src_addr, dst_addr, protocol, data = ethernetframe(eth_frame)
        print('\nethernet frame:')
        print('src:{} , dst:{} ,protocol:{} '.format(src_addr, dst_addr, protocol))
        #separeting packets according to their ptotocol
        if (protocol == 8):
            version, headerlength, TTL, protocol, src, dst, data = IP_packet(data)
            print("\n\t IP Packet :")
            print(
                "\n\t\t version:{}, headerlength:{}, TTL :{}".format(version, headerlength, TTL))
            print("\n\t\t protocol:{} , src:{} , dst:{}".format(protocol, src, dst))

        if (protocol == 1):
            thistype, code, checksum, data = ICMP(data)
            print("\n\t ICMP Packet :")
            print(
                "\n\ttype :{}, code:{}, checksum :{}".format(thistype, code, checksum))
            print('\n\t\t data:')

            print(print(show(data)))

        if (protocol == 6):
            srcport, dstport, seqnum, ack, flag1, flag2, flag3, flag4, flag5, flag6, data = TCP(data)
            print("\n\t TCP Packet :")
            print(
                "\n\tsrc_port :{}, dst_port:{}, seqnum :{},ACK:{}".format(srcport, dstport, seqnum, ack))
            print("\n\t flags:")
            print('\n\t\t URG:{},ACK:{},push:{},RST:{},SYN:{},FIN:{}'.format(flag1, flag2, flag3, flag4, flag5, flag6))
            print("\n\t data:")
            print(show(data))

        if (protocol == 17):
            srcport, dstport, length, data = UDP(data)
            print("\n\t UDP Packet :")
            print(
                "\n\tsrc_port :{}, dst_port:{}, length :{}".format(srcport, dstport, length))
            print("\n\t data:")
            print(show(data))


def ethernetframe(data):
    # rcv 6 byte , sender 6 byte , type 2 byte (H : unsigned short)
    src_addr, dst_addr, protocol = struct.unpack('! 6s 6s H', data[:14])
    return get_mac_address(src_addr), get_mac_address(dst_addr), socket.htons(protocol), data[14:] # return data[14:] means that from block 15 of data till the end


def get_mac_address(byte_to_convert):
    #convert every digits in form of hex with 2 number and then join them with : to make mac address
    sections = map('{:02x}'.format, byte_to_convert)
    return ':'.join(sections).upper()


def IP_packet(data):
    version_and_headerlength = data[0]
    version = version_and_headerlength >> 4 #shift right to separate version
    headerlength = (version_and_headerlength & 15) * 4
    TTL, protocol, src, dst = struct.unpack('! 8x B B 2x 4s 4s ', data[:20])
    return version, headerlength, TTL, protocol, getip(src), getip(dst), data[headerlength:]


def getip(address):
    return '.'.join(map(str, address))


def ICMP(data):
    thistype, code, checksum = struct.unpack('! B B H ', data[:4])
    return thistype, code, checksum, data[4:]


def TCP(data):
    srcport, dstport, seqnum, ack, box = struct.unpack('! H H L L H', data[:14])
    offset = (box >> 12) * 4
    flag1 = (box & 32) >> 5
    flag2 = (box & 16) >> 4
    flag3 = (box & 8) >> 3
    flag4 = (box & 4) >> 2
    flag5 = (box & 2) >> 1
    flag6 = (box & 1)
    return srcport, dstport, seqnum, ack, flag1, flag2, flag3, flag4, flag5, flag6, data[offset:]


def UDP(data):
    srcport, dstport, length = struct.unpack('! H H 2x H', data[:8])
    return srcport, dstport, length, data[8:]


def show(data, size=80):
    if (isinstance(data, bytes)):
        data = ''.join(r'\x{:02x}'.format(byte) for byte in data)
        if size % 2 == 0:
            size = size - 1
    return '\t\t\n\t\t'.join([line for line in textwrap.wrap(data, size)])


main()
