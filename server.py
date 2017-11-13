import sys
import socket
import select

HOST = ''
SOCKET_LIST = []
RECV_BUFFER = 4096
PORT = 9229
clients = []
dict = {}


def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)

    print "Chat server started on port " + str(PORT)

    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                alias = sockfd.recv(RECV_BUFFER)
                while alias in dict.values():
                    sockfd.send("This alias is already taken :( Please, choose another one\n")
                    answer = sockfd.recv(RECV_BUFFER)
                    a = answer.split(" ")
                    s = a[-1]
                    alias = s[:len(s) - 1]
                add_client(alias, sockfd)
                sockfd.send("You can start messaging\n")

                broadcast(server_socket, sockfd, "[%s] entered our chatting room\n" % alias)

            # a message from a client, not a new connection
            else:
                # process data recieved from client,
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        handle_data(data, server_socket, sock)
                    else:
                        # remove the socket that's broken
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)

                        # exception
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    continue

    server_socket.close()




# broadcast chat messages to all connected clients
def broadcast(server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock:
            try:
                socket.send(message)
            except:
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    del_client(socket)
                    SOCKET_LIST.remove(socket)


def handle_data(data, server_socket, sock):
    print(data)
    if "/list" in data:
        sock.send(send_list())
    elif "/quit" in data:
        b = dict.get(sock)
        broadcast(server_socket, sock, "\r" + "Client [%s] has left the chat\n" % b)
        del_client(sock)
    elif "/thumbup" in data:
        b = dict.get(sock)
        msg = send_thumbup()
        broadcast(server_socket, sock, "\r" + "%s>>>" % b + msg)
        sock.send(msg)
    elif "/giraf" in data:
        b = dict.get(sock)
        msg = send_giraf()
        broadcast(server_socket, sock, "\r" + "%s>>>" % b + msg)
        sock.send(msg)
    elif "/cat" in data:
        b = dict.get(sock)
        msg = send_cheshire()
        broadcast(server_socket, sock, "\r" + "%s>>>" % b + msg)
        sock.send(msg)
    elif "/devil" in data:
        b = dict.get(sock)
        msg = send_devil()
        broadcast(server_socket, sock, "\r" + "%s>>>" % b + msg)
        sock.send(msg)
    elif "/dsc" in data:
        sock.send ("Enter alias of client you want to disconnect (send /cancel for cancellation)\n")
        answer = sock.recv(RECV_BUFFER)
        a = answer.split(" ")
        s = a[-1]
        b = s[:len(s)-1]
        if  "/cancel" not in answer:
            alias = answer
            sock.send("Are you sure you want to delete %s from the chat? (y/n)\n" %b)
            answer = sock.recv(RECV_BUFFER)
            if "y" in answer:
                print "Disconnecting " + b + "..."
                sck = get_key(dict, b)
                del_client(sck)
                broadcast(server_socket, sock, "\r" + "Client [%s] was disconnected from the chat\n" %b)
                sock.send("Client [%s] was disconnected from the chat\n" %b)
            else:
                sock.send("Deletion cancelled\n")
        else:
            sock.send("Deletion cancelled\n")
    else:
        broadcast(server_socket, sock, "\r" + data)


def add_client(alias, sockfd):
    if alias not in dict:
        dict[sockfd] = alias
        print "List of connected users: " + str(dict.values())


def del_client(sock):
    del dict[sock]
    SOCKET_LIST.remove(sock)
    sock.close()
    print "List of connected users: " + str(dict.values())


def del_alias (alias):
    k = get_key(dict, alias)
    if k in dict.keys():
        socket = get_key(dict, alias)
        del dict[socket]
        socket.close()
        return "Client with alias %s was deleted from the chat\n" %alias
    else:
        return "No such client\n"


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


def send_list():
    msg = str(dict.values())
    return "List of online clients: " + msg + "\n"


def send_thumbup():
    msg = "             \n           /(|          \n          (  :          \n         __\  \  _____  \n       (____)  `|       \n      (____)|   |       \n       (____).__|       \n        (___)__.|_____  \n"
    return msg


def send_giraf():
    msg = ("""\

                                           ._ o o
                                           \_`-)|_
                                        ,""       /
                                     ,"  ## |   O O.
                                    ," ##   ,-\__    `.
                                  ,"       /     `--._;)
                                ,"     ## /
                              ,"   ##    /


                        \n""")
    return msg


def send_cheshire():
    msg =  ("""\

           .'\   /`.
         .'.-.`-'.-.`.
    ..._:   .-. .-.   :_...
  .'    '-.(o ) (o ).-'    `.
 :  _    _ _`~(_)~`_ _    _  :
:  /:   ' .-=_   _=-. `   ;\  :
:   :|-.._  '     `  _..-|:   :
 :   `:| |`:-:-.-:-:'| |:'   :
  `.   `.| | | | | | |.'   .'
    `.   `-:_| | |_:-'   .'
      `-._   ````    _.-'
          ``-------''


                    \n""")
    return msg

def send_devil():
    msg = (""""\

         (\-"```"-/)
           ^\   /^
        ;/ ~_\ /_~ \;
        |  / \Y/ \  |
       (,   0   0   ,)
        |   /   \   |
        | (_\._./_) |
         \  v-.-v  /
          \ `===' /
           `-----`


                        \n""")
    return msg

if __name__ == "__main__":
    sys.exit(chat_server())