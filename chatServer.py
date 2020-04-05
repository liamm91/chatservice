import socket, time, random

'''
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(("127.0.0.1", 5008))
tcp.listen(1)
c, address = tcp.accept()
print("connection from: " + str(address))
tcp.close()
del c, address
'''

adminhash = random.randint(100000, 200000)
adminport = 0

forcehash = random.randint(0, 500000)
forcefail = 0
forcedhash = False

#udpServer
print("modes: [localhost: -l, external ip: -ip], port: -p *****, name: -n **name**")
print("-d for default chatroom: ex. -ip -p 5000 -n Chatroom")
while True:
    setup = str(input())
    setup = setup.split(" ")
    print("\n")
    #print(setup)

    if "-d" not in setup:
        if "--testing" in setup or "-t" in setup:
            #print("loading testing settings: 127.0.0.1:5000")
            host = "127.0.0.1"
            port = 5000
            break

        #ipconfig
        if "-l" in setup and "-ip" not in setup:
            print("booting localhost")
            host = "127.0.0.1"

        elif "-ip" in setup and "-l" not in setup:
            try:
                print("chose ipv4")
                ipcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ipcon.connect(("msn.com", 80))
                host = ipcon.getsockname()[0]
                ipcon.close()
                del ipcon
            except socket.error:
                print("you do not have internet access")
                input("press enter to exit...")
                exit(1)

        elif "-l" and "-ip" in setup:
            print("cannot use this computer ipv4 addr and localhost at the same time.\n\n")
            continue

        else:
            print("you need to have either -l or -ip in the startup.\n\n")
            continue

        #port
        if "-p" in setup:
            port = int(setup[int(setup.index("-p")+1)])
            if port <= 1024:
                print("port %d is for system protocols" % port)
                continue
            else:
                pass
        elif "-p" not in setup:
            print("you need to specify a port number.\n\n")
            continue

        #name
        if "-n" in setup:
            #serverName = str(setup[int(setup.index("-n")+1)])
            temp = setup[setup.index("-n")+1:]
            serverName = ""
            for string in temp:
                serverName = serverName + str(string) + " "
            serverName = str(serverName[:-1])
            #print(serverName)
            break
        else:
            serverName = str(host)
            break
    else:
        print("booting in default settings\n\n")
        try:
            ipcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ipcon.connect(("msn.com", 80))
            host = ipcon.getsockname()[0]
            ipcon.close()
            del ipcon
            port = 5000
        except socket.error:
            print("you do not have internet access")
            input()
            del setup, adminport, adminhash, forcedhash, forcefail, forcedhash
            exit(1)

print("\n\nstarting udp chat server name: %s : using ip: %s on port number: %i" % (serverName, host, port))
print("--adminhash: %d" % adminhash)
print("--forcehash: %d" % forcehash)

clients = []
blockedclients = []

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.settimeout(0.5)
s.setblocking(1)

quitting = False
print("Server started.\n\n")

#main loop
while not quitting:
    try:
        #recieving data
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        portsort = addr[1]
        print(time.ctime(time.time()) + str(addr) + ": :" + str(data))

        #admin configs
        if "--adminhash" in str(data) or "-a" in str(data) and "--force" not in str(data):
            if str(adminhash) in str(data) and adminport == 0:
                adminport = portsort
                s.sendto(bytes("--admin stop, blockip, blockport\n\n", "utf-8"), addr)
                print(str(addr) + " is now admin on this server")
                print(adminport)
            elif "1234567890" not in str(data) and adminport == 0:
                print(str(addr) + " got the adminhash wrong")
            else:
                print(str(addr) + "tried to claim admin but admin was already claimed")

        #the --force commands for the server
        elif "--adminhash" in str(data) or "-a" in str(data) and "--force" in str(data) and forcefail <= 5:
            if str(forcehash) in str(data):
                adminport = portsort
                s.sendto(bytes("--admin stop, blockip, blockport\n\n", "utf-8"), addr)
                print(str(addr) + " is now admin on this server")
                print(adminport)
            elif "showhash" in str(data) and adminport != 0 and str(adminhash) in str(data):
                s.sendto(bytes("forcehash: " + str(forcehash) + "\n\n", "utf-8"), addr)
                print("sent the force hash to", addr)
                for client in clients:
                    if client[1] == adminport:
                        findadmin = client
                try:
                    print("testing for admin")
                    s.sendto(bytes("user %s tried --adminhash --force showhash" % str(addr), "utf-8"), findadmin)
                except:
                    print("admin not responding")
                    clients = clients.remove(findadmin)
                    adminport = 0
                del findadmin, client

            else:
                print(str(addr) + " tried an --force command")
                forcefail += 1
        else:
            pass

        #admincommands
        if "--admin" in str(data) or "-a" in str(data) and portsort == adminport:
            if "stop" in str(data):
                print("stopping server")
                for client in clients:
                    s.sendto(bytes("server has been stopped, it was fun while it lasted", "utf-8"), client)
                qutting = True
                break

            if "blockip" in str(data):
                temp = str(data).strip("'")
                temp = temp.split("blockip ")[1]
                if len(temp.split(".")) == 4:
                    blockedclients.append(temp)
                    print("blocked ip: %s" % temp)
                    print("blocked clients: %s" % str(blockedclients))
                else:
                    print("tried to block ip: %s but failed" % str(temp))
                    print("blocked clients: %s " % str(blockedclients))

            if "blockport" in str(data):
                temp = str(data).strip("'")
                try:
                    temp = int(temp.split("blockport ")[1])
                    blockedclients.append(temp)
                    print("blocked port %d" % temp)
                    print("blocked clients: %s " % str(blockedclients))
                except:
                    print("tried to grab port %s from --admin blockport but failed" % str(temp))
                    print("blocked clients: %s" % str(blockedclients))

        elif ("--admin" in str(data) and portsort != adminport) and "--adminhash" not in str(data):
            print("an admin command was sent by a non-admin %s" % str(addr))
        else:
            pass

        if "--isaliveadmin" in str(data) or "-iaa" in str(data) and adminport != 0:
            print("sending query to admin")
            for client in clients:
                if client[1] == adminport:
                    findadmin = client
            try:
                s.sendto(bytes("user %s tested for alive admin" % str(addr), "utf-8"), findadmin)
                print("query completed, admin alive")
            except:
                adminhash = random.randint(100000, 200000)
                adminport = 0
                print("query failed setting adminport to 0\nsetting adminhash %d" % adminhash)
        elif "--isaliveadmin" in str(data) or "-iaa" in str(data) and adminport == 0:
            s.sendto(bytes("admin has not been claimed", "utf-8"), addr)
            continue

        #adding clients to send packets to
        if addr not in clients:
            clients.append(addr)
            s.sendto(bytes("--sendName %s" % serverName, "utf-8"), addr)
            print("sending name of server to %s" % str(addr))

        #sending messages
        if portsort not in blockedclients or addr[0] not in blockedclients:
            print(clients)
            for client in clients:
                if client[1] in blockedclients or client[0] in blockedclients:
                    print("not sending to blocked user: %s" % str(client))
                    print("blocked clients: %s" % str(blockedclients))
                    continue
                else:
                    pass

                if client[1] == portsort:
                    print("not echoing message to: " + str(client))
                else:
                    if portsort == adminport:
                        #print("admin port: ", adminport)
                        if "**admin**" not in data:
                            temp = str(data).strip("'")
                            data = str("**admin** " + str(temp))
                            del temp
                        else:
                            pass
                    if "--" in str(data) or "-a" in str(data) or "-iaa" in str(data) or "clientadd:" in str(data):
                        print("not sending special message")
                        continue
                    print('sending ' + str(data) + ' to: ' + str(client))
                    try:
                        s.sendto(bytes(data, "utf-8"), client)
                    except socket.error:
                        clients.remove(client)
        else:
            print("not sending message from blocked client to active clients")

        time.sleep(0.03)

    except Exception as e:
        print(e)
        #if "10054" in str(e):
        #    print("WinError 10054 caused by dead client: %s. Removing dead client" % str(client))
        time.sleep(0.03)
        pass
    print("\n\n")

s.close()
del s, clients, blockedclients, setup, forcehash, adminhash, forcedhash, adminport, quitting, host, port, portsort
del serverName
exit(0)
