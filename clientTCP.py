import socket
import sys
import os
import struct
import time

TCP_IP = "127.0.0.1"
TCP_PORT = 8080
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


print("\n------------------------------------")
print("Python FTP Socket Programming")
print("-------------------------------------")
print("Choose Command:")
print("connme                :(use this first to connect to current server)")
print("ls                    : List of files")
print("size <file_path>      : file sizes")
print("upload <file_path>    : Upload files")
print("download <file_path>  : Download files")
print("rm <file_path>        : Remove files")
print("byebye                : Disconnect.")
print("-------------------------------------")


def connme():
    try:
        s.connect((TCP_IP, TCP_PORT))
        print("Connected!")
    except:
        print("Connection failed! Make sure the port is correct")

def upld(file_name):
    try:
        s.send(b"upload")
    except:
        print("Couldn't make server request. Make sure server connection established")
        return
    try:
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode())
        file_size = os.path.getsize(file_name)
        s.send(struct.pack("i", file_size))
        start_time = time.time()
        print("Sending file...")
        content = open(file_name, "rb")
        l = content.read(BUFFER_SIZE)
        while l:
            s.send(l)
            l = content.read(BUFFER_SIZE)
        content.close()
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("f", time.time() - start_time))
        print("File sent successfully")
        return
    except:
        print("Error sending file")
        return

def list_files():
    try:
        s.send(b"ls")
    except:
        print("Couldn't make server request. Make sure server connection established.")
        return
    try:
        number_of_files = struct.unpack("i", s.recv(4))[0]
        for i in range(int(number_of_files)):
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size).decode()
            file_size = struct.unpack("i", s.recv(4))[0]
            print("\t{} - {}b".format(file_name, file_size))
            s.send(b"1")
        total_directory_size = struct.unpack("i", s.recv(4))[0]
        print("Total directory size: {}b".format(total_directory_size))
    except:
        print("Couldn't retrieve listing")
        return
    try:
        s.send(b"1")
        return
    except:
        print("Couldn't get final server confirmation")
        return

def dwld(file_name):
    try:
        s.send(b"download")
    except:
        print("Couldn't make server request. Make sure server connection established.")
        return
    try:
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode())
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            print("File does not exist. Make sure the name was entered correctly")
            return
    except:
        print("Error checking file")
    try:
        s.send(b"1")
        output_file = open(file_name, "wb")
        bytes_received = 0
        print("\nDownloading...")
        while bytes_received < file_size:
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_received += BUFFER_SIZE
        output_file.close()
        print("Successfully downloaded {}".format(file_name))
        s.send(b"1")
        print("\nFile size: {}b".format(file_size))
    except:
        print("Error downloading file")
        return
    return

def delf(file_name):
    try:
        s.send(b"rm")
        s.recv(BUFFER_SIZE)
    except:
        print("Couldn't connect to server. Make sure server connection established.")
        return
    try:
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode())
    except:
        print("Couldn't send file details")
        return
    try:
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            print("The file does not exist on server")
            return
    except:
        print("Couldn't determine file existence")
        return
    try:
        confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
        while confirm_delete != "Y" and confirm_delete != "N" and confirm_delete != "YES" and confirm_delete != "NO":
            print("Command not recognized, try again")
            confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
    except:
        print("Couldn't confirm deletion status")
        return
    try:
        if confirm_delete == "Y" or confirm_delete == "YES":
            s.send(b"Y")
            delete_status = struct.unpack("i", s.recv(4))[0]
            if delete_status == 1:
                print("Successfully deleted")
                return
            else:
                print("File failed to delete")
                return
        else:
            s.send(b"N")
            print("Delete canceled!")
            return
    except:
        print("Couldn't delete file")
        return

def get_file_size(file_name):
    try:
        s.send(b"size")
    except:
        print("Couldn't make server request. Make sure server connection established.")
        return
    try:
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode())
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            print("File does not exist. Make sure the name was entered correctly")
            return
    except:
        print("Error checking file")
    try:
        s.send(b"1")
        print("File size: {} MB".format(file_size / 1024 / 1024))
        return
    except:
        print("Couldn't get final server confirmation")
        return

def quit():
    s.send(b"byebye")
    s.recv(BUFFER_SIZE)
    s.close()
    print("Server connection ended")
    return

while True:
    prompt = input("\nPlease Enter Your Command! : ")
    if prompt[:6].lower() == "connme":
        connme()
    elif prompt[:6].lower() == "upload":
        upld(prompt[7:])
    elif prompt.lower() == "ls":
        list_files()
    elif prompt[:8].lower() == "download":
        dwld(prompt[9:])
    elif prompt[:2].lower() == "rm":
        delf(prompt[3:])
    elif prompt[:4].lower() == "size":
        get_file_size(prompt[5:])
    elif prompt.lower() == "byebye":
        quit()
        break
    else:
        print("Cant find the asked Command; Please check again!")

