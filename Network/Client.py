import subprocess
import platform
import socket

def get_hostname(local=False):
    cmd = 'ipconfig' if platform.system() == 'Windows' else 'ifconfig'
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].decode()
    if local:
        req = "169.254"
    else:
        req = "192.168"
    start = res.index(req)
    end = start + res[start:].index(' ')
    ip_address = res[start:end].strip()
    return ip_address

class Client:
    def __init__(self, name='', local=False):
        self.client_data = {"name":name,
                            "ip_addr":get_hostname(local),
                            "host":'',
                            "port":8080,
                            "conn":socket.socket()}

    def connect(self, host, port=8080):
        self.client_data["host"] = host
        self.client_data["port"] = port
        self.client_data["conn"].connect((host, port))

    def send_msg(self, text=''):
        self.client_data["conn"].send(str(text).encode('UTF-8'))
        print("Message sent")

    def recv_msg(self, size=1024):
        return self.client_data["conn"].recv(size).decode()
            
    def send_file(self, file_path, byte_size=2048):
        file_ext = file_path.split('.')[-1]
        with open(file_path, 'rb+') as file_object:
            file_data = file_object.read()
        file_size = len(file_data)
        self.client_data["conn"].send("EXT:{}".format(file_ext).encode('UTF-8'))
        self.client_data["conn"].recv(1)
        self.client_data["conn"].send("SZ:{}".format(file_size).encode('UTF-8'))
        self.client_data["conn"].recv(1)
        for i in range(0, file_size, byte_size):
            self.client_data["conn"].send(file_data[i:i+byte_size])
            self.client_data["conn"].recv(1).decode()
        self.client_data["conn"].send(file_data[i+byte_size:])
        self.client_data["conn"].recv(1).decode()
        print("File sent")

    def recv_file(self, file_path, byte_size=2048):
        file_ext = self.client_data["conn"].recv(5).decode().split(':')[-1]
        self.client_data["conn"].send(b'1')
        file_size = int(self.client_data["conn"].recv(512).decode().split(':')[-1])
        self.client_data["conn"].send(b'1')
        file_data = b''
        for i in range(0, file_size, byte_size):
            file_data += self.client_data["conn"].recv(byte_size)
            self.client_data["conn"].send(b'1')
        file_data += self.client_data["conn"].recv(file_size%byte_size)
        self.client_data["conn"].send(b'1')
        with open(file_path+'.'+file_ext, 'wb+') as file_object:
            file_object.write(file_data)
        print("File recieved")
