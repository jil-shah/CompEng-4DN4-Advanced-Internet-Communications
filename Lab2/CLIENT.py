import argparse
import pandas as pd
import getpass
import socket 
import hashlib

# class CLIENT:

#     ## INITIALIZE THE IP ADDRESS AND PORT NUMBER
#     def __init__ (self):
#         IP = '12.0.0.1'
#         PORT = 30001
#         self.client(IP,PORT)

#     ## get the student id and password 
#     def get_StudentInfo(self, student_id, student_password):
#         file = pd.read_csv('D:\Year5\SharedVM\4DN4-LAB2\course_grades.csv')
#         #read each line 
#         studentInfo = file[file['ID Number'] == student_id]
#         if not studentInfo.empty:
#             if(studentInfo.iloc[0]['Password'] )
#             return studentInfo
        

#     ## prompt the user 
#     # get student id, or the command
#     def client()
    
# if __name__ == "__main__":
#     roles = {'client': CLIENT}
#     parser = argparse.ArgumentParser()

#     parser.add_argument('-r', '--role',
#                         choices=roles, 
#                         help='server or client role',
#                         required=True, type=str)

#     args = parser.parse_args()
#     roles[args.role]()

# def getStudentInfo():
#     cmds = ["GMA", "GL1A", "GL2A", "GL3A","GL4A"]

#     while(True):
#         student_id = input("Enter Student ID: ")
#         password = getpass.getpass(prompt="Password: ")

#         studentInfo = file[file['ID Number'] == student_id]

#         if(not studentInfo.empty):
#             if(studentInfo.iloc[0]['Password'] == password):
#                 print("Access Granted")
#                 command = ""
#                 while(command not in cmds):
#                     command = input("Input Command (GMA, GL1A, GL2A, GL3A, and GL4A): ")

#                     if(command not in cmds):
#                         print("Invalid Command... input one of the following: GMA, GL1A, GL2A, GL3A, and GL4A")

#                 return student_id, command
#         else:
#             print("Access Denied - Incorrect Credientials")
#             continue



def getHashCredentials(student_id, student_password):
    hashoutput = hashlib.sha256()
    hashoutput.update(student_id.encode('utf-8'))
    hashoutput.update(student_password.encode('utf-8'))
    return hashoutput.digest()

def client(SERVERIP, SERVERPORT):
    cmds = ["GMA", "GL1A", "GL2A", "GL3A","GL4A"]
    studentID = input("Enter Student ID: ")
    password = getpass.getpass(prompt="Password: ")
    command = ""
    while(command not in cmds):
        command = input("Input Command (GMA, GL1A, GL2A, GL3A, and GL4A): ")
        if(command not in cmds):
            print("Invalid Command... input one of the following: GMA, GL1A, GL2A, GL3A, and GL4A")

    #create a TCP Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # client_socket.connect((SERVERIP, SERVERPORT))
        print(f"{getHashCredentials(studentID,password),command}".encode())
        # client_socket.sendall(f"{getHashCredentials(studentID,password),command}")
        # encrypted_response = client_socket.recv(1024)
        print(f"Server Response: {response.decode('utf-8')}")
        return (f"{getHashCredentials(studentID,password),command}".encode())
           

# GMA, GL1A, GL2A, GL3A, and GL4A

def load_data(CLIENTINPUT):
    file = pd.read_csv('D:\Year5\SharedVM\4DN4-LAB2\course_grades.csv')
    #read each line
    student_id = authenticate_client(CLIENTINPUT) 
    # studentInfo = file[file['ID Number'] == student_id]
    return studentId


def authenticate_client(CLIENTINPUT):
    file = pd.read_csv('D:\Year5\SharedVM\4DN4-LAB2\course_grades.csv')
    for index,row in file.iterrows():
        if(row['ID Number'] == 'Averages'):
            continue
        
        temphash = hashlib.sha256()
        temphash.update(row['ID Number'].encode('utf-8'))
        temphash.update(row['Password'].encode('utf-8'))
        temphash.digest()

        if(CLIENTINPUT == temphash):
            print("Access Granted - Student ID: "+row["ID Number"])
            return row["ID Number"]
    return False

def process_commands(data, studentId, command):
    ## (GMA, GL1A, GL2A, GL3A, and GL4A)
    if (command == "GMA"):
        response = ("Midterm Average: " + str(data["Midterm"].mean()))
    elif (command == "GL1"):
        response = ("Lab 1 Average: " + str(data["Lab 1"].mean()))
    elif (command == "GL2"):
        response = ("Lab 2 Average: " + str(data["Lab 2"].mean()))
    elif (command == "GL3"):
        response = ("Lab 3 Average: " + str(data["Lab 3"].mean()))
    elif (command == "GL4"):
        response = ("Lab 4 Average: " + str(data["Lab 4"].mean()))
    elif (command == "GG"):
        studentInfo = data[data['ID Number'] == studentID]
        grades = studentInfo[['Midterm','Lab 1', 'Lab 2', 'Lab 3', 'Lab 4']].to_dict()
        response = "Your Grades: \n"
        for x in grades:
            response += x + " - "
            for y in grades[x]:
                response += str((grades[x][y])) + "%\n"
    else:
        response = "INVALID COMMAND"

# file = pd.read_csv("D:\Year5\SharedVM\4DN4-LAB2\course_grades.csv")

# process_commands(file, "101","GMA")
clientInput = client(0, 0)
authenticate_client(clientInput)
