import socket
import sys
import platform
from threading import Thread

PORT = 4242
message_dict = {}

def get_my_ip():
    """Return the ipaddress of the local host

    On Debian-based systems we may get a rather strange address: 127.0.1.1
    See: https://www.debian.org/doc/manuals/debian-reference/ch05.en.html#_the_hostname_resolution

    """
    return socket.gethostbyname(socket.gethostname())


def threaded_client(connection, address):
    connection.send(str.encode("Please send username"))
    data = connection.recv(2048)
    username = data.decode()
    if username in message_dict.keys:
        connection.send(str.encode(f"ERROR: The username '{username}' is already used"))
    else:
        message_dict[username] = []  # initialize empty list for user
        message = data.decode()
        print(f"{username} at {address[0]}:{address[1]}")

    # Send registration confirmation
    connection.send(str.encode(f"Registered as {username}"))

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
            print(message_dict)
            print(username)
            print(message_dict)

        elif message == '2':  # client requests incoming messages
            incoming_messages = message_dict[username]
            connection.send(str.encode(str(len(incoming_messages))))  # send number of messages

            for msg in incoming_messages:
                connection.send(str.encode(msg))
            message_dict[username] = []  # clear the list of incoming messages

        #elif message == '3':



        elif "stop" in message.lower():
            break
        else:  # assume it's a regular message
            reply = f"Echo to {username}: {message}"
            connection.send(str.encode(reply))
            # add message to recipient's message list
            if message.startswith("@"):  # direct message
                recipient = message.split()[0][1:]
                if recipient in message_dict:
                    message_dict[recipient].append(f"{username}: {message}")
            else:  # broadcast message
                for recipient in message_dict:
                    if recipient != username:
                        message_dict[recipient].append(f"{username}: {message}")

    print(f"Closing connection to {address[0]}:{address[1]}")
    del message_dict[username]
    connection.close()


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
                msg = f"New connection: {addr[0]}:{addr[1]}"
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
