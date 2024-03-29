import socket
import sys
import platform
from threading import Thread

import time
from unittest import expectedFailure

PORT = 4242
message_dict = {}


def get_my_ip():
    """Return the ipaddress of the local host

    On Debian-based systems we may get a rather strange address: 127.0.1.1
    See: https://www.debian.org/doc/manuals/debian-reference/ch05.en.html#_the_hostname_resolution

    """
    return socket.gethostbyname(socket.gethostname())


# recieve username and check it
def threaded_client(connection, address):
    try:
        while True:
            connection.send(str.encode("Bitte senden Sie Ihren Benutzername"))
            data = connection.recv(2048)
            username = data.decode()
            if username in list(message_dict.keys()):
                connection.send(str.encode(f"ERROR: Der Benutzername '{username}' ist bereits vergeben!"))
                continue
            break
        message_dict[username] = []
        message = data.decode()
        print(f"{username} at {address[0]}:{address[1]}")

        # Send registration confirmation
        connection.send(str.encode(f"Registriert als {username} erfolgreich!"))

        while True:
            print(f"Listening for {address[0]}:{address[1]} ...")
            data = connection.recv(2048)
            message = data.decode()
            if message == '1':
                # Receive recipient and message from client
                data = connection.recv(2048).decode()
                recipient, message = data.split(" ", 1)
                # Add message to recipient's message list
                if recipient in message_dict:
                    message_dict[recipient].append(f"{username}: {message}")
                    print((f"{username}: {message}"))

            elif message == '2':  # client requests incoming messages
                incoming_messages = message_dict[username]
                if incoming_messages != []:
                    connection.send(str.encode('~'.join(list(incoming_messages))))
                    print((str.encode('~'.join(list(incoming_messages)))))
                else:
                    connection.send(str.encode("Keine neuen Nachrichten"))
                message_dict[username] = []

            elif message == '3':
                if len(message_dict.keys()) == 1:
                    connection.send(str.encode(f" {username},du bist der einzige Online-Benutzer!"))
                else:
                    connection.send(str.encode('~'.join(list(message_dict.keys()))))
                    print('~'.join(list(message_dict.keys())))
                    print(str.encode('~'.join(list(message_dict.keys()))))

            elif message == '4':
                incoming_messages = message_dict[username]
                if incoming_messages != []:
                    connection.send(str.encode('~'.join(list(incoming_messages))))
                    print((str.encode('~'.join(list(incoming_messages)))))
                else:
                    connection.send(str.encode("Keine neuen Nachrichten"))
                message_dict[username] = []
                time.sleep(2.0)
                connection.close()
                print(f"Closing connection to {address[0]}:{address[1]}")
                del message_dict[username]
                break

            elif "stop" in message.lower():
                print(f"Closing connection to {address[0]}:{address[1]}")
                del message_dict[username]
                break


    except WindowsError as e:
        if e.winerror == 10054:
            try:
                del message_dict[username]
            finally:
                print(f"Closing connection to {address[0]}:{address[1]}")


if __name__ == "__main__":
    # Socket setup
    server_socket = socket.socket()
    try:
        server_socket.bind((get_my_ip(), PORT))
    except socket.error as e:
        print(e)
        server_socket.close()
        sys.exit(1)
    if platform.system() == "Windows":
        # Windows: No reaction to signals during socket.accept()
        #          => Wake up periodically from accept.
        server_socket.settimeout(1)
    # Start socket
    server_socket.listen()



    print("===== Start Chat Server =====")
    print(f"Starting Server on {get_my_ip()}:{PORT}")
    print("Server running")
    # Accept connections
    conn_cnt = 0
    try:
        while True:
            try:
                # print("Ready for a new connection ...\n")
                conn, addr = server_socket.accept()
                msg = f"Neue Verbindung: {addr[0]}:{addr[1]}"
                print(msg)
                conn.send(msg.encode())
                Thread(target=threaded_client, args=(conn, addr), daemon=True).start()
                conn_cnt += 1  # TODO: De-register connections
                print(f"{conn_cnt} connections")
            except socket.timeout:  # Windows (Python >= 3.10: TimeoutError)
                continue
    except KeyboardInterrupt:
        print("\nStopping server due to user request")
    finally:
        print("Closing server socket")
        server_socket.close()
