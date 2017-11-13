import sys
import socket
import select


def chat_client():
    if (len(sys.argv) < 3):
        print 'Usage : python client.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    print "==== Welcome to amazing chat! ====\n Here are some commands you can use: \n /list - list all participants of the chat \n" \
          " /quit - leave chat \n /dsc - disconnect particular person from the chat \n \n Also you can use some ASC II Art stickers: \n /devil \n /cat \n /thumbup \n /giraf \n"

    alias = raw_input("Enter username: ")


    # connect to remote host
    try:
        s.connect((host, port))

    except:
        print 'Unable to connect'
        sys.exit()


    s.send(alias)
    sys.stdout.write('[Me]: ')
    sys.stdout.flush()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])

        for sock in ready_to_read:
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(4096)
                if not data:
                    print '\nDisconnected from chat server'
                    sys.exit()
                else:
                    # print data
                   # print(data)
                    sys.stdout.write(data)
                    sys.stdout.write('[Me]: ')
                    sys.stdout.flush()

            else:
                # user entered a message
                msg = raw_input()
                s.send(alias + ">>> " + msg + "\n")
                sys.stdout.write('[Me]:')
                sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(chat_client())