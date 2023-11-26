import zmq

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

while True:
    socks = dict(poller.poll())

    if frontend_socket in socks and socks[frontend_socket] == zmq.POLLIN:
        # Message from client
        multipart_message = frontend_socket.recv_multipart()

        print("Received message from client:", multipart_message)

        if len(multipart_message) >= 2:
            client_id, message = multipart_message[1:]
            print("Message from client:", message)

            # Forward the message to the server
            backend_socket.send_multipart([b"", message])

    if backend_socket in socks and socks[backend_socket] == zmq.POLLIN:
        # Message from server
        frames = backend_socket.recv_multipart()

        # Check if there are at least two frames
        if len(frames) >= 2:
            client_identity, response = frames[0], frames[1]

            print(f"Received message from server {client_identity}: {response.decode('utf-8')}")

            # Forward the message to the client
            frontend_socket.send_multipart([client_identity, response])
