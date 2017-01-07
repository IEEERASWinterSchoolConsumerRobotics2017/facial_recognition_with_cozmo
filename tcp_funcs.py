import datetime
import socket

TCP_IP = '10.18.81.7'
TCP_PORT = 8896
BUFFER_SIZE = 1024
#Robot:              TCP 8896
#   Def: Get item user wants
#   req item des
#   rep item des item(%s)
#
#   Def: Guest Entered Room
#   set guest enter time(%s yyyy-mm-dd-hh-mm-ss)
#   rep ok
#
#   Def: Intruder
#   set guest intruder time(%s yyyy-mm-dd-hh-mm-ss)
#   rep ok

def tcp_get_items():
    
    MESSAGE = "req item des"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE.encode())
    data = s.recv(BUFFER_SIZE)
    s.close()
    
    items = data.decode().split(" ")[3:]
    if items[0] == "None":
        return None
    print("received items:"+ str(items))
    return items

def guest_entered_room():
    time_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") 
    MESSAGE = "set guest enter time "
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE.encode())
    data = s.recv(BUFFER_SIZE)
    s.close()
    
    items = data.decode().split(" ")[0]
    print("received data:"+ str(items))
    return items

def tcp_intruder_found():
    time_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") 
    MESSAGE = "set guest intruder time " + time_str
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE.encode())
    data = s.recv(BUFFER_SIZE)
    s.close()
    
    items = data.decode().split(" ")[0]
    print("received data:"+ str(items))
    return items
