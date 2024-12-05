import socket

IP_SERVER = "127.0.0.1"
PORT = 5050


def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((IP_SERVER, PORT))
            while True:
                received_data = client_socket.recv(1024).decode()
                print(received_data)

                # input-ul jucatorului va avea ca prefix '> ' pentru a putea distinge mai usor
                message = input("> ").strip()

                while message == "":
                    print("[CLIENT.PY]: Input-ul nu poate fi gol!")
                    message = input("> ").strip()

                # !!! ne asiguram ca trimitem STOP catre server inainte de a deconecta clientul
                client_socket.send(message.encode())
                if message.upper() == "STOP":
                    print("[CLIENT.PY]: Disconnecting...")
                    break
        # in caz ca rulam client.py fara server.py
        except ConnectionRefusedError:
            print("Client error: Serverul nu este pornit!")
        except Exception as e:
            print(f"Client error: {e}")

print(">>>STARTING CLIENT<<<")
start_client()