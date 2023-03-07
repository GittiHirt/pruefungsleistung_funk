import socket
import sys

client_socket = socket.socket()
LOCALHOST = '192.168.178.104'
PORT = 4242

#Test
try:
    host = sys.argv[1]  # server IP given on command line
except IndexError:
    host = LOCALHOST
    print(f"No server given on command line. Trying {host}")
try:
    print(f"Waiting for connection to {host}")
    client_socket.connect((host, PORT))
except socket.error as e:
    print(str(e))
    if host == LOCALHOST:
        print("Running locally on Debian based system? "
              "Then you may try 127.0.1.1 for connecting to server")
    sys.exit(1)

# Ask for connection
response = client_socket.recv(2048)
print(f"{response.decode()}")

# Send username
response = client_socket.recv(2048)
print(f"{response.decode()}")
username = input("Username: ")
client_socket.send(str.encode(username))

# Wait for registration confirmation
response = client_socket.recv(2048)
print(f"{response.decode()}")

# Do the talk
while True:
    print("====== Minimal Chat System ======")
    print("1: Send message")
    print("2: Check incoming messages")
    print("3: List online clients")
    print("4: Quit")
    msg = input("Your Selection: ")

    if not msg:  # empty message not permitted in TCP
        continue
    client_socket.send(str.encode(msg))
    if "stop" in msg.lower():  # protocol: "stop" to close connection.
        break

    elif msg == "1":
        recipient = input("Send message to: ")
        message = input("Your message: ")
        client_socket.send(str.encode(f"{recipient} {message}"))

    elif msg == "2":
        print("Checking incoming Messages...")
        client_socket.send(str.encode(msg))
        num_messages = client_socket.recv(2048).decode()
        print(f"You have {num_messages} new message(s).")
        for i in range(int(num_messages)):
            incoming_msg = client_socket.recv(2048).decode()
            print(f"{incoming_msg} \n")

    #elif msg == "3":


    #elif msg == "4":
        print("Old messages:")

    else:
        print("Listening ...")
        # Echo from Server
        response = client_socket.recv(2048)
        return_msg = response.decode()
        print(return_msg)

print("Closing connection")
client_socket.close()
