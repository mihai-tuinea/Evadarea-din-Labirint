import socket
import random
import math
from collections import deque

IP_SERVER = "127.0.0.1"
PORT = 5050


class Labirint:
    def __init__(self, client_socket):
        self.total_miscari = 0
        self.i_jucator = self.j_jucator = self.i_monstru = self.j_monstru = 0
        self.model_ales, self.coord_iesiri, self.visited = [], [], []
        self.rezultat_final = ""

        self.alege_model()
        self.start_joc(client_socket)

    def alege_model(self):
        """
        - alege aleatoriu un model din cele 5 fisiere
        - transforma continutul intr-o lista 2D
        - identifica iesirile si genereaza entitatile
        """
        file_name = f"labirint_{random.randint(0, 4)}.txt"
        with open(file_name, "r") as file:
            self.model_ales = [list(line.strip()) for line in file.readlines()]

        self.gaseste_iesiri()
        self.genereaza_jucator()
        self.genereaza_monstru()

        self.model_ales[self.i_jucator][self.j_jucator] = "J"
        self.model_ales[self.i_monstru][self.j_monstru] = "M"

        # pe partea serverului putem vedea labirintul complet in pozitia de start
        print("Labirintul ales:")
        for row in self.model_ales:
            print(" ".join(row))

        # in labirint este intuneric => vom folosii visited pentru
        # a retine casutele vizitate
        self.visited = [[False for _ in row] for row in self.model_ales]
        self.visited[self.i_jucator][self.j_jucator] = True

    def afisare_stare_curenta(self, client_socket, optional=""):
        stare_curenta = optional
        stare_curenta += "Starea curenta a labirintului:\n"

        # daca casuta nu a fost vizitata se va afisa un simplu ' '
        # + in afisare avem cate un spatiu suplimentar intre coloane pentru claritate
        stare_curenta += '\n'.join(
            ' '.join(' ' if not self.visited[i][j] else self.model_ales[i][j] for j in range(len(self.model_ales)))
            for i in range(len(self.model_ales)))
        client_socket.send(stare_curenta.encode())

    def validare_alegere(self, client_socket, optiuni_valide, optional=""):
        while True:
            alegere_client = client_socket.recv(1024).decode()
            if alegere_client in optiuni_valide:
                return alegere_client
            self.afisare_stare_curenta(client_socket, optional)

    def start_joc(self, client_socket):
        directii = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

        ghid = "Jocul a inceput! Alegeti una din urmatoarele comenzi:\n"
        ghid += "U - Sus (Up)\nD - Jos (Down)\nL - Stanga (Left)\nR - Dreapta (Right)\n"

        while True:
            if self.total_miscari == 0:
                self.afisare_stare_curenta(client_socket, ghid)
            else:
                self.afisare_stare_curenta(client_socket)

            alegere_client = self.validare_alegere(client_socket, directii,
                                                   "Nu exista o astfel de varianta. Verificati si introduceti din nou\n")
            self.total_miscari += 1

            offset = directii[alegere_client]
            new_i = self.i_jucator + offset[0]
            new_j = self.j_jucator + offset[1]

            while self.model_ales[new_i][new_j] == "#":
                self.visited[new_i][new_j] = True
                self.afisare_stare_curenta(client_socket, "Imposibil, ai lovit un perete. Încearcă altă directie.\n")

                alegere_client = self.validare_alegere(client_socket, directii,
                                                       "Nu exista o astfel de varianta. Verificati si introduceti din nou\n")
                # consideram a fi o "miscare" si cand jucatorul se da cu capul de pereti
                self.total_miscari += 1

                offset = directii[alegere_client]
                new_i = self.i_jucator + offset[0]
                new_j = self.j_jucator + offset[1]

            self.visited[new_i][new_j] = True
            match self.model_ales[new_i][new_j]:
                case "E":
                    self.rezultat_final += f"Ai reusit!\nAi iesit din labirint in {self.total_miscari} miscari!\n"
                    self.finalizare_joc(client_socket)
                    break
                case "M":
                    self.rezultat_final += "Ai picat prada monstrului din labirint ... ai pierdut jocul. Incerca din nou!\n"
                    self.finalizare_joc(client_socket)
                    break
                case " ":
                    self.model_ales[self.i_jucator][self.j_jucator] = " "
                    self.i_jucator = new_i
                    self.j_jucator = new_j
                    self.model_ales[self.i_jucator][self.j_jucator] = "J"

    def finalizare_joc(self, client_socket):
        self.rezultat_final += "Pentru a juca din nou introduceti 'START'. Pentru a opri jocul introduceti 'STOP'"
        client_socket.send(self.rezultat_final.encode())

    def gaseste_iesiri(self):
        """
        cauta toate iesirile si salveaza coordonatele lor
        """
        for i in range(len(self.model_ales)):
            for j in range(len(self.model_ales[i])):
                if self.model_ales[i][j] == "E":
                    self.coord_iesiri.append((i, j))

    def pathfinder(self, coord_list):
        """
        determina cel mai scurt path catre o destinatie (monstru/iesire)
        utilizand algoritmul BFS
        folosim aceasta functie pentru a verifica:
        - daca exista minim 1 path jucator->iesire pt fiecare iesire
        - daca exista un path jucator->monstru (=> monstrul nu este blocat intr-o camera fara iesiri)
        """
        rows = len(self.model_ales)
        cols = len(self.model_ales[0])
        directii = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        paths = 0

        if coord_list == [(self.i_monstru, self.j_monstru)]:
            dest_char = "M"
        else:
            dest_char = "E"

        for destinatie in coord_list:
            start = (self.i_jucator, self.j_jucator)
            # queue pt BFS
            queue = deque([start])
            coord_vizitate = set()

            while queue:
                (current_row, current_col) = queue.popleft()
                if (current_row, current_col) in coord_vizitate:
                    continue
                coord_vizitate.add((current_row, current_col))

                # daca am gasit path catre destinatie
                if (current_row, current_col) == destinatie:
                    paths += 1
                    break

                for row_offset, col_offset in directii:
                    neighbor_row = current_row + row_offset
                    neighbor_col = current_col + col_offset
                    # verifica daca pozitia candidat:
                    # - este in limitele labirintului
                    # - este spatiu liber sau destinatia
                    # - nu a mai fost vizitat deja
                    if (0 <= neighbor_row < rows and 0 <= neighbor_col < cols
                            and self.model_ales[neighbor_row][neighbor_col] in (' ', dest_char)
                            and (neighbor_row, neighbor_col) not in coord_vizitate
                    ):
                        queue.append((neighbor_row, neighbor_col))

        # verificam daca exista cel putin 1 path pentru fiecare tuple de coordonate
        if paths >= len(coord_list):
            return True
        return False

    def distanta(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def blocheaza_iesirea(self):
        """
        verifica daca pozitia curenta a monstrului blocheaza vreo iesire
        consideram ca NU blocheaza iesirea daca exista
        cel putin 2 casute intre monstru si iesire
        """
        for iesire in range(len(self.coord_iesiri)):
            i_iesire = self.coord_iesiri[iesire][0]
            j_iesire = self.coord_iesiri[iesire][1]
            if self.distanta(i_iesire, j_iesire, self.i_monstru, self.j_monstru) <= 2:
                return True
        return False

    def genereaza_monstru(self):
        """
        generam monstrul dupa regulile jocului
        - sa nu se genereze peste E / # / J
        - sa nu blocheze oricare iesire
        - sa nu fie "blocat" (este imposibil ca jucatorul sa piarda)
        - sa exista o distanta de minim 3 casute intre jucator si monstru
        """
        coord_monstru = [(self.i_monstru, self.j_monstru)]
        while (self.model_ales[self.i_monstru][self.j_monstru] in ["E", "#", "J"]
               or self.blocheaza_iesirea()
               or not self.pathfinder(coord_monstru)
               or self.distanta(self.i_jucator, self.j_jucator, self.i_monstru, self.j_monstru) <= 3
        ):
            self.i_monstru = random.randint(0, 9)
            self.j_monstru = random.randint(0, 9)
            coord_monstru = [(self.i_monstru, self.j_monstru)]

    def ok_jucator_iesire(self):
        """
        verifica daca intre jucator si iesire sunt minim 2 casute (= 3 mutari pentru a castiga)
        """
        for iesire in range(len(self.coord_iesiri)):
            i_iesire = self.coord_iesiri[iesire][0]
            j_iesire = self.coord_iesiri[iesire][1]
            if self.distanta(i_iesire, j_iesire, self.i_jucator, self.j_jucator) <= 2:
                return False
        return True

    def genereaza_jucator(self):
        """
        conditiile pentru a genera jucatorul:
        - sa nu ocupe o casuta '#' sau 'E'
        - sa existe minim 3 casute intre jucator si iesire (minimul de mutari pentru a castiga)
        - sa existe minim 3 casute intre jucator si monstru
        """
        while (self.model_ales[self.i_jucator][self.j_jucator] in ["E", "#"]
               or not self.ok_jucator_iesire()
               or not self.pathfinder(self.coord_iesiri)
        ):
            self.i_jucator = random.randint(0, 9)
            self.j_jucator = random.randint(0, 9)


def handle_client(client_socket):
    """
    Functie pentru a gestiona conexiunea cu un client
    - Primeste comenzile START sau STOP
    - Ruleaza jocul Labirint cand clientul trimite START
    """
    with client_socket:  # folosim 'with' pentru inchide automat conexiunea
        while True:
            try:
                received_data = client_socket.recv(1024).decode().strip()

                # daca clientul se deconecteaza sau trimite STOP
                if not received_data or received_data.upper() == "STOP":
                    print("Clientul s-a deconectat!")
                    print("Server shutting down...")
                    break

                elif received_data.upper() == "START":
                    joc = Labirint(client_socket)

                else:
                    client_socket.send("Input invalid! Introduceti 'START' sau 'STOP'".encode())

            # folosim acest error handling pentru cazul in care
            # clientul introduce comanda 'STOP' in timpul jocului
            except ConnectionResetError:
                print("Connection error: Clientul s-a deconectat in timpul jocului!")
                break


def start_server():
    """
    porneste serverul si asteapta conexiuni de la client
    """
    # server IPv4 TCP
    with socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM) as server_socket:  # 'with' pentru a inchide automat conexiunea
        server_socket.bind((IP_SERVER, PORT))
        server_socket.listen(1)
        print(f"Serverul TCP asculta pe adresa {IP_SERVER}:{PORT}...")

        try:
            client_socket, client_address = server_socket.accept()
            print(f"Accesat de catre {client_address}")
            welcome_message = "V-ati conectat la serverul TCP!\n"
            welcome_message += "Pentru a incepe jocul introduceti 'START'\n"
            welcome_message += "Pentru a va deconecta introduceti 'STOP'"
            client_socket.send(welcome_message.encode())

            handle_client(client_socket)

        except Exception as e:
            print(f"Server error: {e}")


print(">>>STARTING SERVER<<<")
start_server()
