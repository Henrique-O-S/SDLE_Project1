import zmq

from multi_server import MultiServer

context = zmq.Context()
frontend_socket = context.socket(zmq.ROUTER)
backend_socket = context.socket(zmq.DEALER)
frontend_socket.bind("tcp://127.0.0.1:5559")  # Clients connect to this address
backend_socket.bind("tcp://127.0.0.1:5560")   # Servers connect to this address

poller = zmq.Poller()
poller.register(frontend_socket, zmq.POLLIN)
poller.register(backend_socket, zmq.POLLIN)

target_server_address = "tcp://127.0.0.1:6001"
backend_socket.connect(target_server_address) 

ring = MultiServer.ring


while True:
    socks = dict(poller.poll())

    if frontend_socket in socks and socks[frontend_socket] == zmq.POLLIN:
        # Message from client
        multipart_message = frontend_socket.recv_multipart()
        print("ROUTER // Raw message from client | ", multipart_message)

        #print("Received message from client:", multipart_message)

        client_id, dummy, message = multipart_message[0:]
        #print("Message from client:", message)

        # Forward the message to the server
        backend_socket.send_multipart([b"", client_id, message])

    if backend_socket in socks and socks[backend_socket] == zmq.POLLIN:
        # Message from server
        multipart_message = backend_socket.recv_multipart()
        print("DEALER // Raw message from server | ", multipart_message)

        client_identity, response = multipart_message[1], multipart_message[2]

        #print(f"Message from server {client_identity}: {response.decode('utf-8')}")

        # Forward the message to the client
        frontend_socket.send_multipart([client_identity, b"", response])
