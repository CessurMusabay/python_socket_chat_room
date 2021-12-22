import socket
import threading
from colorama import init
from colorama import Fore

init()


class Flag:
    writeable = False
    stop = False


HOST = socket.gethostbyname(socket.gethostname())
PORT = 5033

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, PORT))
except:
    print(Fore.RED + 'Connection Failed')


def listen():
    while not Flag.stop:
        try:
            msg = server.recv(2048)
            Flag.writeable = False
            msg_str = msg.decode('utf-8')
            print(Fore.BLUE + msg_str)
            Flag.writeable = True
            if msg_str == '<exit>':
                Flag.stop = True
        except:
            Flag.stop = True


t = threading.Thread(target=listen)
t.start()

while not Flag.stop:
    if Flag.writeable:
        try:
            my_msg = input(Fore.WHITE + '')
            server.sendall(my_msg.encode('utf-8'))
        except:
            Flag.stop = True

t.join()
server.close()
print(Fore.BLUE + 'You exited chat room')
