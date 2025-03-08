import pandas as pd
import getpass
import socket
import argparse
import hashlib


class Server: 

    def __init__(self):
        COURSE_GRADES = "D:/Year5/SharedVM/COMPENG-4DN4-LAB2/course_grades.csv"
        SERVER_PORT = 50000
        self.start_server(COURSE_GRADES,SERVER_PORT)

    def load_data(self, URL):
        try:
            file = pd.read_csv(URL, encoding='utf-8') # error_bad_lines=False, warn_bad_lines=True, some reason, this was giving me errors
            return file
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False

    def authenticate_client(self,CLIENTINPUT, data):
        for index,row in data.iterrows():
            if(row['ID Number'] == 'Averages'):
                continue

            temphash = hashlib.sha256()
            temphash.update(str(row['ID Number']).encode('utf-8'))
            temphash.update(row['Password'].encode('utf-8'))
            # Get the digest as bytes for the current row in the table
            hashed = temphash.digest()

            # Ensure the client received hash is the same as the current row hash
            if(CLIENTINPUT == hashed):
                print("Access Granted - Student ID: "+ str(row["ID Number"]))
                return row["ID Number"]
        return -1
        
    def process_commands(self, data, studentId, command):
        print("\nRECEIVED COMMAND: "+command)
        if (command == "GMA"):
            print("> Getting Midterm Averages...\n")
            response = ("\nFetching Midterm Average: " + str(data["Midterm"].mean()) + "\n")
        elif (command == "GL1A"):
            print("> Getting Lab 1 Average...\n")
            response = ("\nFetching Lab 1 Average: " + str(data["Lab 1"].mean()) + "\n")
        elif (command == "GL2A"):
            print("> Getting Lab 2 Average...\n")
            response = ("\nFetching Lab 2 Average: " + str(data["Lab 2"].mean()) + "\n")
        elif (command == "GL3A"):
            print("> Getting Lab 3 Average...\n")
            response = ("\nFetching Lab 3 Average: " + str(data["Lab 3"].mean()) + "\n")
        elif (command == "GL4A"):
            print("> Getting Lab 4 Average...\n")
            response = ("\nFetching Lab 4 Average: " + str(data["Lab 4"].mean()) + "\n")
        elif (command == "GG"):
            print("> Getting Your Grades...\n")
            studentInfo = data[data['ID Number'] == studentId]
            grades = studentInfo[['Midterm','Lab 1', 'Lab 2', 'Lab 3', 'Lab 4']].to_dict()
            response = "\nFetching Your Grades: \n"
            for x in grades:
                response += "    > "+ x + " - "
                for y in grades[x]:
                    response += str((grades[x][y])) + "%\n"
        elif (command == "E"):
            response = "EXITING PROGRAM\n"
        else:
            response = "INVALID COMMAND\n"
        return response

    def start_server(self, COURSE_GRADES, SERVER_PORT):
        #load the data
        student_data = self.load_data(COURSE_GRADES)
        # read from socket
        print("Data read from csv successfully")
        print(student_data)
        # Create a TCP/IP socket
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # Bind the socket to a specific address and port
        server_socket.bind(('0.0.0.0', SERVER_PORT))
        server_socket.listen()
        print("SERVER LISTING ON "+ str(SERVER_PORT))

        # process 
        while True:
            # Accept an incoming connection
            client_socket, client_address = server_socket.accept()
            with client_socket:
                data_recv = client_socket.recv(1024)
                # data receive contains hashed user id and password, and the second half is the command
                cred, cmd = data_recv[:32], data_recv[32:].decode()
                
                if not data_recv:
                    break
                # authenticate client
                student_id = -1   # set default value , when ID is not required
                if cmd == "GG":
                    student_id = self.authenticate_client(cred, student_data)
                    print("RECEIVED HASH: "+str(cred))
                    if student_id == -1:
                        response = "\n> ACCESS DEINED - USER INVALID. TRY AGAIN"
                        client_socket.sendall(response.encode())
                    else:
                        print("CONNECTION SUCCESSFUL FROM IP Address/Port: "+str(client_socket.getsockname()))
                        print("\n> ACCESS GRANTED - Records Found")
                        output_data = self.process_commands(student_data, student_id,cmd)
                        client_socket.sendall(output_data.encode())
                elif cmd == "E":
                    print("CLOSE CONNECTION")
                    response = "CONNECTION CLOSED..."
                    client_socket.sendall(response.encode())
                    client_socket.close()
                    break
                else:
                    print("CONNECTION SUCCESSFUL FROM IP Address/Port: "+str(client_socket.getsockname()))
                    output_data = self.process_commands(student_data, student_id,cmd)
                    client_socket.sendall(output_data.encode())

                    
                    
class Client: 

    def __init__(self):
        SERVER_IP = '192.168.0.108'
        SERVER_PORT = 50000
        self.client(SERVER_IP,SERVER_PORT)

    def getHashCredentials(self,student_id, student_password):
        hashoutput = hashlib.sha256()
        hashoutput.update(student_id.encode('utf-8'))
        hashoutput.update(student_password.encode('utf-8'))
        return hashoutput.digest()
                
    def client(self, SERVERIP, SERVERPORT):
        cmds = ["GG","GMA", "GL1A", "GL2A", "GL3A","GL4A","E"]
        
        while True:
            command = ""
            while(command not in cmds):
                command = input("\nInput Command (GG, GMA, GL1A, GL2A, GL3A, GL4A, and E): ")
                if(command not in cmds):
                    print("\nInvalid Command... input one of the following: GG, GMA, GL1A, GL2A, GL3A, GL4A, and E")

            print("> Command Entered: "+command)
            studentID = "-1"
            password = "none"
            hash_val = b""
            if(command == "GG"):
                studentID = input("\nEnter Student ID: ")
                password = getpass.getpass(prompt="Password: ")
                print("> Entered ID Number: "+studentID+" Password: "+password)
            #create a TCP Connect to the server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((SERVERIP, SERVERPORT))
                hash_val = self.getHashCredentials(studentID,password)
                client_socket.sendall(hash_val + command.encode())
                if(command == "GG"):
                    print("\n> ID/Password Hash "+str(hash_val) + "Sent To Server")

                encrypted_response = client_socket.recv(1024)
                print(encrypted_response.decode())
                client_socket.close()
                print("CONNECTION CLOSED.")
                if(command == "E"):
                    client_socket.close()
                    break



if __name__ == "__main__":
    roles = {'client':Client, 'server':Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()
