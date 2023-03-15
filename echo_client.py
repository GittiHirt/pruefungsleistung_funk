import time
from idlelib.rpc import response_queue
from pickle import TRUE
import socket
import sys
import queue
import threading

client_socket = socket.socket()
LOCALHOST = '10.11.21.58' #10.11.21.58 #192.168.178.104
PORT = 4242

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

try:
    def received_messages():
        while receiving:
            try:
                response_queue.put(client_socket.recv(2048).decode())

            except:
                # Bei Verbindungsproblemen beenden
                client_socket.close()
                break


    # Ask for connection
    response = client_socket.recv(2048).decode()
    response_queue.put(response)
    print(f"{response}")

    # Wait for registration confirmation
    while True:
        response = client_socket.recv(2048).decode()
        print(f"{response}")
        username = input("Username: ")
        client_socket.send(str.encode(username))
        response = client_socket.recv(2048).decode()
        if response.startswith('ERROR'):
            print(f"{response}")
            continue
        else:
            print(f"{response}")
            break

    response_queue = queue.Queue()
    receiving = True
    receive_thread = threading.Thread(target=received_messages)
    receive_thread.start()

    # Do the talk
    while True:
        time.sleep(0.1)
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
            if len(message) > 126:
                print("The input of recipient exceeds the maximum length of 126!")
                continue
            client_socket.send(str.encode(f"{recipient} {message}"))

        elif msg == "2":
            print("Checking incoming Messages...")
            print("Your messages:")
            #client_socket.send(str.encode(msg))
            unique_messages = set()
            incomming_messages = response_queue.get()
            if incomming_messages != ['']:
                for message in incomming_messages.split("~"):
                    print(str(message))
            else:
                print("Test")
                continue


        elif msg == "3":
            print("Checking list of online clients...")
            print("Online Clients:")
            client_socket.send(str.encode(msg))
            unique_messages = set()
            messages = response_queue.get()
            response_queue.get()
            for clients in messages.split("~"):
                print(clients)

        elif msg == "4":
            print("Checking old Messages...")
            unique_messages = set()
            incomming_messages = response_queue.get()
            if incomming_messages != ['']:
                for message in incomming_messages.split("~"):
                    print(str(message))
            else:
                print("Test")
                continue
            print("Closing down Session actor")
            print("Goodbye")
            time.sleep(4.0)
            client_socket.send(str.encode(msg))
            receiving = False
            receive_thread.join()
            client_socket.close()
            break

        else:
            print("Listening ...")


    print("Closing connection")

except KeyboardInterrupt as ki:
    print("\nStopping server due to user request")

