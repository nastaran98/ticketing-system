import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_address=('localhost', 10100)

sock.bind(server_address)
sock.listen(5)
client, address =sock.accept()

while True:
    data=client.recv(2048)
    if data:
        print("message : %s" % data)
        client.send(data)
client.close()



