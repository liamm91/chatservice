import socket, threading, time

print("-l: localhost, -ip for local external ipv4\n\n")
while True:
    serverIP = str(input("IP of the server: "))
    if serverIP == "-l":
        serverIP = "127.0.0.1"
        break
    elif serverIP == "-ip":
        try:
            ipcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ipcon.connect(("msn.com", 80))
            serverIP = ipcon.getsockname()[0]
            ipcon.close()
            del ipcon
        except socket.error as e:
            print("error: %s" % str(e))
            continue
        break
    elif len(serverIP.split(".")) == 4:
        if ":" not in serverIP:
            break
        else:
            temp = serverIP.split(":")[0]
            try:
                socket.inet_aton(temp)
                print("valid IP address")
            except socket.error:
                print("invalid ip")
                continue
            del temp
            break
    else:
        print("invalid ip")
        continue

if ":" not in serverIP:
    while True:
        try:
            serverPort = int(input("Port of the server: "))
            break
        except:
            print("invalid port\n")
            continue
else:
    serverPort = int(serverIP.split(":")[1])

tLock = threading.Lock()
shutdown = False

def recieving(sock):
    while not shutdown:
        try:
            tLock.acquire()
            while True:
                data, addr = sock.recvfrom(1024)
                data = data.decode("utf-8")
                data = str(data).strip("'")
                #print(data)
                #print("--sendName" in str(data))

                if "--t" in str(data):
                    continue

                elif "--sendName" in str(data):
                    temp = data.strip("--sendName ")
                    if temp.count(".") != 3:
                        print("You have entered chatting server: %s" % data.strip("--sendName "))
                    else:
                        print("You have entered a chat server.")
                    del temp
                    continue

                else:
                    print(str(data))
        except:
            pass

        finally:
            tLock.release()

if serverIP != "127.0.0.1":
    ipcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ipcon.connect(("msn.com", 80))
    host = ipcon.getsockname()[0]
    port = 0
    ipcon.close()
    del ipcon
else:
    host = "127.0.0.1"
    port = 0


server = (serverIP, serverPort)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

print("*: q for quit :*\n\n")

alias = str(input("Name: "))
rT = threading.Thread(target=recieving, args=("RecvThread", s))
rT.start()
s.sendto(bytes("clientadd: %s" % alias, "utf-8"), server)
time.sleep(0.5)
message = input(alias + " :>> ")
while message != 'q':
    if message != '':
        s.sendto(bytes(alias + ": " + message, "utf-8"), server)
    tLock.acquire()
    message = input(alias + " :>> ")
    tLock.release()
    time.sleep(0.2)

shutdown = True
rT.join()
s.close()
