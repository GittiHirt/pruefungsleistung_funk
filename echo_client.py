import time
from idlelib.rpc import response_queue
from pickle import TRUE
import socket
import sys
import queue
import threading

client_socket = socket.socket()
LOCALHOST = str(socket.gethostbyname(socket.gethostname()))
PORT = 4242

try:
    while True:
        request = input(f"Wollen Sie ein IP-Adresse für die Serververbindung eingeben? Ja/Nein \nEingabe:").lower()
        if request == "ja":
            LOCALHOST = input("Eingabe Server-IP:")
            host = sys.argv[1]

        elif request == "nein":
            host = sys.argv[1]  # server IP given on command line
        else:
            print("Bitte geben Sie nur 'Ja' oder 'Nein' ein.")
except IndexError:
    host = LOCALHOST
    #print(f"No server given on command line. Trying {host}")
try:
    print(f"Warte auf Verbindung mit dem Host: {host}")
    client_socket.connect((host, PORT))
except socket.error as e:
    print(str(e))
    if host == LOCALHOST:
        print("Läuft der Server lokal auf einem Debian-System "
              "Dann versuchen Sie die IP-Adresse 127.0.1.1 für die Verbindung zum Server")
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
        username = input("Benutzername: ")
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
        print("====== Minimalistisches Chat-System ======")
        print("1: Nachricht senden")
        print("2: Nachrichten abrufen")
        print("3: Liste der Online-Benutzer")
        print("4: Beenden")
        msg = input("Ihre Auswahl: ")

        if not msg:  # empty message not permitted in TCP
            continue
        client_socket.send(str.encode(msg))
        if "stop" in msg.lower():  # protocol: "stop" to close connection.
            break

        elif msg == "1":
            recipient = input("Nachricht an den Benutzer: ")
            message = input("Dein Nachricht: ")
            if len(message) > 126:
                print("Ihre Nachricht darf nicht länger als 126 Zeichen sein!")
                continue
            client_socket.send(str.encode(f"{recipient} {message}"))

        elif msg == "2":
            print("Empfange Nachrichten...")
            print("Nachrichten an Sie:")
            #client_socket.send(str.encode(msg))
            unique_messages = set()
            incomming_messages = response_queue.get()
            if incomming_messages != ['']:
                for message in incomming_messages.split("~"):
                    print(str(message))
            else:
                print("Es sind keine Nachrichten für Sie verfügbar.")
                continue


        elif msg == "3":
            print("Empfange Liste der Online-Benutzer...")
            print("Online-Benutzer:")
            client_socket.send(str.encode(msg))
            unique_messages = set()
            messages = response_queue.get()
            response_queue.get()
            for clients in messages.split("~"):
                print(clients)

        elif msg == "4":
            print("Empfange verbleibende Nachrichten...")
            unique_messages = set()
            incomming_messages = response_queue.get()
            if incomming_messages != ['']:
                for message in incomming_messages.split("~"):
                    print(str(message))
            else:
                print("Es sind keine Nachrichten für Sie verfügbar.")
                continue
            print("Beende Verbindung zum Server...")
            print("Auf Wiedersehen!")
            time.sleep(4.0)
            client_socket.send(str.encode(msg))
            receiving = False
            receive_thread.join()
            client_socket.close()
            break

        else:
            print("Falsche Eingabe")


    print("Verbindung beendet!")

except KeyboardInterrupt as ki:
    print("\nAnhalten des Servers durch Benutzereingabe!")

