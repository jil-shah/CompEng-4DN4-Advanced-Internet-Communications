import socket
import argparse
import os 
import threading

class Client:
    def __init__ (self,server_ip, server_port):
        self.server_ip = server_ip
        self.sever_port = server_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # unique id for client
        self.identifier = uuid.uuid4().hex
        # chat id
        self.chatid = None
        # thread init 
        self.thread = None

    def msg_send(self, msg):
        msg = f"{self.identifier}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.sendto(msg.encode('utf-8'), (self.multicast_group, self.multicast_port))
    
    def connect(self):
        self.sock.connect((self.server_ip, self.sever_port))
        print("Connection Successful.")
    
    def send_command(self, command):
        self.sock.send(command.encode('utf-8'))
        resp = self.sock.recv(1024)
        print(resp.decode('utf-8'))
        return resp
    
    def msg_listener(self, multicast_group, multicast_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sock.bind(multicast_port)
        mreq = struct.pack("4sl", socket.inet_aton(mcast_group), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        last_msg = None
        while True:
            data, _ = sock.recvfrom(1024)
            new_msg = data.decode('utf-8')
            sender_id, s_msg = message.split(':', 1)
            if (sender_id != self.chatid and last_msg != new_msg):
                print(msg)
            if (sender_id != self.chatid and s_msg == " has left the chat"):
                break
        last_msg = new_msg
    
    def start_chat(self, multicast_group, port):
        server_addr = ('', port)
        self.thread = threading.Thread(target=self.msg_listener, args=(multicast_group,server_addr))
        self.thread.start()
        while True:
            msg = input()
            if(msg.lower == "exit"):
                exit_msg = f"{self.chat_id} has left the chat"
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
                sock.sendto(exit_msg.encode('utf-8'), (multicast_group, port))
                break
            if(self.chatid):
                msg = f"{self.chatid}: {msg}"
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            self.sendto(msg.encode('utf-8'), (multicast_group, port))
        
        self.thread.join()
    
    def run(self):
        self.chatid = input("Enter your name: ").strip()

        while True:
            cmd = input(self.prompt)
            if (cmd == "connect"):
                self.connect()
            elif (cmd == "bye"):
                self.sock.close()
                if (self.thread):
                    self.thread.join()
                sys.exit()
            elif(cmd.startswith("name ")):
                self.chatid = cmd.split(' ', 1)[1]
                print("chat name is: {cmd.split(' ', 1)[1]}")
            elif(cmd.startswith("chat ")):           
                chatid = cmd.split()[1]
                response = self.send_command(f"getdir")
                chat_dir = json.loads(response.decode('utf-8'))
                if chatid in chat_dir[chatid]:
                    chatroom = chat_dir[chatid]
                    self.start_chat(chatid['address'], chatroom['port'])
                else:
                    print(f"chat room '{chatid}' does not exist")
            else:
                self.send_command(cmd)

class Server:



if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)
    
    args = parser.parse_args()
    roles[args.role]()
