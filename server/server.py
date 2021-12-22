import socket
import threading
from database import DatabaseHandler
from database import Message, View
from custom_exceptions import DatabaseException
from colorama import init
from colorama import Fore

# Global Parameters
CHAT_ROOM_NAME = 'Pardus Kuramayanlar'
CHAT_COMMANDS = '        [?messages] --> Show the messages you have not seen\n        [?exit] --> Exit Application\n'
clients = []
database_handler = DatabaseHandler()

# Init Colorama
init()


def remove(connection):
    ip = connection.getpeername()[0]
    try:
        connection.close()
    except:
        pass
    if connection in clients:
        clients.remove(connection)
        print(Fore.LIGHTRED_EX + "[Lost Connection] : " + ip)


def decode_command(msg):
    command = msg.strip().replace('?', '').lower()
    if command == 'exit':
        return 1
    if command == 'message':
        return 2
    return None


def execute_command(command, connection):
    if command == 1:  # Exit
        connection.send('<exit>'.encode('utf-8'))
        remove(connection)
    elif command == 2:  # Message
        messages = database_handler.get_messages(connection.getpeername()[0])
        try:
            for msg in messages:
                connection.send(msg.get_message().encode('utf-8'))
                v = View(connection.getpeername()[0], msg.get_id())
                database_handler.insert_view(v)
        except Exception as e:
            print(Fore.RED + f"[EXCEPTION 3] : {e}")
            remove(connection)


def broadcast(message, connection, message_id):
    for client in clients:
        if client != connection:
            try:
                client.send(f'{message.get_message()}'.encode('utf-8'))
                v = View(conn.getpeername()[0], message_id)
                database_handler.insert_view(v)
            except DatabaseException as e:
                print(Fore.LIGHTRED_EX + f"[DATABASE EXCEPTION] : {e}")
            except Exception as e:
                print(Fore.RED + f"[EXCEPTION 1] : {e}")
                remove(client)


def client_handler(conn, addr):
    conn.send(
        f'Welcome to the {CHAT_ROOM_NAME}\nThese are the commands that you can use:\n{CHAT_COMMANDS}'.encode('utf-8'))
    while True:
        try:
            message = conn.recv(2048)
            if message:
                msg = message.decode('utf-8')

                if msg != '<exit>':
                    if msg[0] == '?':
                        execute_command(decode_command(msg), conn)
                    else:
                        m = Message(addr[0], msg)
                        message_id = database_handler.insert_message(m)

                        broadcast(m, conn, message_id)
                else:
                    conn.send('<exit>')
            else:
                remove(conn)
                # connection may have been lost
        except DatabaseException as e:
            print(Fore.LIGHTRED_EX + f"[DATABASE EXCEPTION] : {e}")
        except Exception as e:
            remove(conn)
            break


if __name__ == '__main__':

    # Setting up server
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5033

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(Fore.BLUE + "Listening on:", (HOST, PORT))

    while True:
        conn, addr = server.accept()
        print(Fore.CYAN + f"[New Connection] : {addr[0]}")
        clients.append(conn)
        t = threading.Thread(target=client_handler, args=(conn, addr))
        t.start()
