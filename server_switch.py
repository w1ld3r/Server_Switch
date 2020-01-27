import socket
import queue
from select import select


HOST = '127.0.0.1'
PORT = 1234
BUFFER_SIZE = 4096
TIMEOUT = 1

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server.bind((HOST, PORT))

# Listen for incoming connections
server.listen()

# Sockets from which we expect to read
inputs = [server]

# Sockets to which we expect to write
outputs = []

# Outgoing message queues (socket:Queue)
message_queues = {}

# Switch table
table = {}


while inputs:
    # Wait for at least one of the sockets to be ready for processing
    #print("Waiting for the next event")
    readable, writable, exceptional = select(inputs, outputs, inputs, TIMEOUT)

    # Handle inputs
    for s in readable:
        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print("\nNew connection from: ", client_address)
            inputs.append(connection)
            # Give the connection a queue for data we want to send
            message_queues[connection] = queue.Queue()
        # Established connection with a client that has sent data
        else:
            data = s.recv(BUFFER_SIZE)
            if data:
                # A readable client socket has data
                #print("\nReceived %s from %s" % (repr(data), s.getpeername()))

                dstMAC = data[4:10]
                srcMAC = data[10:16]

                print("\n")
                print("Source Mac: ", ":".join("%02x" % c for c in srcMAC))
                print("Destination Mac: ", ":".join("%02x" % c for c in dstMAC))
                print("\n")

                if srcMAC not in table:
                    print("Source Mac: ", ":".join("%02x" % c for c in srcMAC), " not in table")
                    table[srcMAC] = s
                if dstMAC not in table:
                    print("Destination Mac: ", ":".join("%02x" % c for c in srcMAC), " not in table")
                    for i in inputs:
                        # if not source and not serveur
                        if i is not s and i is not server:
                            message_queues[i].put(data)
                            if i not in outputs:
                                outputs.append(i)
                else:
                    print("Destination Mac: ", ":".join("%02x" % c for c in srcMAC), " in table")
                    dstSocket = table[dstMAC]
                    message_queues[dstSocket].put(data)
                    # Add output channel for response
                    if dstSocket not in outputs:
                        outputs.append(dstSocket)
            else:
                # Interpret empty result as closed connection
                print("Closing", s.getpeername(), "after reading no data")
                # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)

                # Remove message queue
                del message_queues[s]

    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:
            # No messages waiting so stop checking for writability.
            print("Output queue for", s.getpeername(), "is empty")
            outputs.remove(s)
        else:
            print("Sending %s to %s" % (next_msg, s.getpeername()))
            s.send(next_msg)

    # Handle "exceptional conditions"
    for s in exceptional:
        print("Handling exceptional condition for", s.getpeername())
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        # Remove message queue
        del message_queues[s]

