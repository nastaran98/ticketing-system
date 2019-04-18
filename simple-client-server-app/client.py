import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address=('localhost', 10100)

sock.connect(address)
msg=input("client : ")
while msg != 'exit':
     sock.sendall(msg.encode('utf-8'))
     data=sock.recv(2048)
     print("received : %s" % data.decode('utf-8'))
     msg=input('client : ')

sock.close()



