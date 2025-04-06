import socket
import argparse
import sys
import threading
import json
import struct


#Setting up global variables
ALL_IP = "0.0.0.0"
PORT = 60000
ENCODING = "utf-8"
RECV_SIZE = 1024
INTERFACE_IP = "172.17.100.208" 


class Server: 
    BACKLOG = 10 

    def __init__(self):
        self.chatrooms = {}
        self.create_listen_socket()
        self.process_clients()
    
    def create_listen_socket(self):
        try: 
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((ALL_IP, PORT))
            self.socket.listen(Server.BACKLOG)
            print("Chat Room Directory Server listening on port "+str(PORT)+"...")
        except Exception as msg:
            print("Socket creation failed:"+msg)
            sys.exit(1)
        
    def process_clients(self):
        try:
            while(True):
                client_socket, address = self.socket.accept()
                print("Connection received from "+address)
                client_thread = threading.Thread(target=self.handle_client,args=(client_socket,address),daemon=True)
                client_thread.start()
        except KeyboardInterrupt:
            print("Shutting down server.")
            self.socket.close()

    def handle_client(self,sock, address):
        name = "Anonymous"
        while True:
            data = sock.recv(RECV_SIZE)
            if (not data):
                break

            command_line = data.decode(ENCODING).strip()
            print(f"[{address}] Received: {command_line}")
            args = command_line.split()

            cmd = args[0]

            if(cmd == "getdir"):
                sock.sendall(json.dumps(self.chatrooms).encode(ENCODING))

            elif(cmd == "makeroom" and len(args) == 4):
                room, ip, port = args[1], args[2], int(args[3])
                if(room in self.chatrooms or (ip, port) in self.chatrooms.values()):
                    sock.sendall("Room exists or IP/port already used".encode(ENCODING))
                else:
                    self.chatrooms[room] = (ip, port)
                    sock.sendall("Room "+room+" created".encode(ENCODING))

            elif(cmd == "deleteroom" and len(args) == 2):
                room = args[1]
                if(room in self.chatrooms):
                    del self.chatrooms[room]
                    sock.sendall("Room "+room+" deleted.".encode(ENCODING))
                else:
                    sock.sendall("Room not found.".encode(ENCODING))

            elif(cmd == "name" and len(args) == 2):
                name = args[1]
                sock.sendall("Username set to "+name+"".encode(ENCODING))

            elif(cmd == "chat" and len(args) == 2):
                room_name = args[1]
                if room_name not in self.chatrooms:
                    sock.sendall("Room not found.".encode(ENCODING))
                    continue

                multicast_ip, multicast_port = self.chatrooms[room_name]
                self.create_send_socket()

                # Start chat message forwarder
                while(True):
                    chat_data = sock.recv(RECV_SIZE)
                    if(not chat_data):
                        break
                    chat_message = chat_data.decode(ENCODING)
                    full_message = f"{name}: {chat_message}"
                    print(f"[{room_name}] {full_message}")
                    self.socketUDP.sendto(full_message.encode(ENCODING), (multicast_ip, multicast_port))

            elif (cmd == "bye"):
                if(not name):
                    name = "Anonymous"
                print(f"["+name+" @ "+address[0]+":"+address[1]+"] Connection has been closed")
                sock.sendall("Goodbye!".encode(ENCODING))
                break

            else:
                sock.sendall("Invalid command.".encode(ENCODING))

    def create_send_socket(self):
        try:
            self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socketUDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
            self.socketUDP.setblocking(False)
        except Exception as msg:
            print("UDP socket setup failed:"+ str(msg))
            sys.exit(1)

class Client: 
    def __init__(self):
        self.chat_name = "Anonymous"
        self.directory = {}
        self.get_socket()
        self.client_main_menu()
    
    def get_socket(self):
        try:
            # Recreate the socket in case it's closed
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ALL_IP, PORT))
            print(f"Connected to server on port "+str(PORT))
        except Exception as msg:
            print("Connection failed: "+str(msg))

    def connect_to_server(self):
        try:
            # Recreate the socket in case it's closed
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ALL_IP, PORT))
            print(f"Connected to server on port {PORT}")
        except Exception as msg:
            print("Connection failed:", msg)


    def client_main_menu(self):
            while(True):
                cmd = input("Would you like to... \n1) connect\n2) exit").strip().split()
                if(cmd[0] == "connect"):
                    self.connect_to_server()
                    self.crds_menu()
                elif (cmd[0] == "exit"):
                    print("Exiting.")
                    break

    def crds_menu(self):
        while True:
            try:
                cmd = input("Input Chat Command (enter any arguments required): \n1) name\n2) getdir\n3) makeroom\n4) deleteroom\n5) chat \n6) bye").strip().split()
              
                command = cmd[0]

                if(command == "name" and len(cmd) == 2):
                    self.chat_name = cmd[1]
                    self.socket.sendall(f"name {self.chat_name}".encode(ENCODING))
                    response = self.socket.recv(RECV_SIZE).decode(ENCODING)
                    print(response)

                elif(command == "getdir"):
                    self.socket.sendall("getdir".encode(ENCODING))
                    response = self.socket.recv(RECV_SIZE).decode(ENCODING)
                    self.directory = json.loads(response)
                    print("Directory:", self.directory)

                elif (command == "makeroom" and len(cmd) == 4):
                    self.socket.sendall(" ".join(cmd).encode(ENCODING))
                    print(self.socket.recv(RECV_SIZE).decode(ENCODING))

                elif (command == "deleteroom" and len(cmd) == 2):
                    self.socket.sendall(" ".join(cmd).encode(ENCODING))
                    print(self.socket.recv(RECV_SIZE).decode(ENCODING))

                elif (command == "bye"):
                    self.socket.sendall("bye".encode(ENCODING))
                    self.socket.close()
                    break

                elif (command == "chat" and len(cmd) == 2):
                    # Origonally, even if a chat existed, you could not enter it without running getdir, but technically it does exist so when chat
                    # is prompted, it should join without having to run getdir
                
                    self.socket.sendall("getdir".encode(ENCODING))
                    response = self.socket.recv(RECV_SIZE).decode(ENCODING)
                    try:
                        self.directory = json.loads(response)
                    except json.JSONDecodeError:
                        print("Could not fetch directory. Invalid response from server.")
                        continue
                    self.enter_chatroom(cmd[1])

                else:
                    print("Invalid command.")

            except (KeyboardInterrupt, EOFError):
                print("\nDisconnected from CRDS.")
                self.socket.close()
                break
                
    def enter_chatroom(self, room_name):
        if(room_name not in self.directory):
            print("Room not found. Try 'getdir' first.")
            return

        multicast_ip, multicast_port = self.directory[room_name]
        print("Entering room "+room_name+" — press Ctrl C to exit")

        # Multicast receive socket
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        recv_sock.bind(('', multicast_port))

        group = socket.inet_aton(multicast_ip)
        iface = socket.inet_aton(INTERFACE_IP)
        mreq = group + iface
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Multicast send socket
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        # Start receiver thread
        def receive_loop():
            while True:
                try:
                    data, _ = recv_sock.recvfrom(RECV_SIZE)
                    print(data.decode(ENCODING))
                except Exception:
                    break

        recv_thread = threading.Thread(target=receive_loop, daemon=True)
        recv_thread.start()

        # Notify join
        join_msg = f"{self.chat_name} has joined the chat."
        send_sock.sendto(join_msg.encode(ENCODING), (multicast_ip, multicast_port))

        # Chat loop
        print("Type '/exit' to leave the chat room.")
        while True:
            try:
                msg = input()
                if msg.strip().lower() == "/exit":
                    break
                full_msg = f"{self.chat_name}: {msg}"
                send_sock.sendto(full_msg.encode(ENCODING), (multicast_ip, multicast_port))
            except (KeyboardInterrupt, EOFError):
                print("\nUse /exit instead of Ctrl+C to safely exit.")

        # Notify leave
        leave_msg = f"{self.chat_name} has left the chat."
        send_sock.sendto(leave_msg.encode(ENCODING), (multicast_ip, multicast_port))

        # Drop multicast membership
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        recv_sock.close()
        send_sock.close()
        print("Left the chat room.")

    
#running the client and server through args
if __name__ == '__main__':
    roles = {'client': Client, 'server': Server}
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--role', choices=roles, help='server or client role', required=True)
    args = parser.parse_args()
    roles[args.role]()
  
