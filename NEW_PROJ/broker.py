import zmq
from multi_server import MultiServer

class Broker:
    def __init__(self, frontend_port=5559, backend_port=5560):
        self.context = zmq.Context()
        self.frontend_socket = self.context.socket(zmq.ROUTER)
        self.backend_socket = self.context.socket(zmq.DEALER)
        self.frontend_socket.bind(f"tcp://127.0.0.1:{frontend_port}")
        self.backend_socket.bind(f"tcp://127.0.0.1:{backend_port}")
        self.poller = zmq.Poller()
        self.poller.register(self.frontend_socket, zmq.POLLIN)
        self.poller.register(self.backend_socket, zmq.POLLIN)

    def run(self):
        while True:
            socks = dict(self.poller.poll())

            if self.frontend_socket in socks and socks[self.frontend_socket] == zmq.POLLIN:
                # Message from client
                multipart_message = self.frontend_socket.recv_multipart()
                print("ROUTER // Raw message from client | ", multipart_message)

                print(MultiServer.get_server(multipart_message[2].decode('utf-8')).address)

                self.backend_socket.connect(MultiServer.get_server(multipart_message[2].decode('utf-8')).address)

                client_id, dummy, message = multipart_message[0:]
                # Forward the message to the server
                self.backend_socket.send_multipart([b"", client_id, message])

            if self.backend_socket in socks and socks[self.backend_socket] == zmq.POLLIN:
                # Message from server
                multipart_message = self.backend_socket.recv_multipart()
                print("DEALER // Raw message from server | ", multipart_message)

                client_identity, response = multipart_message[1], multipart_message[2]

                # Forward the message to the client
                self.frontend_socket.send_multipart([client_identity, b"", response])

if __name__ == '__main__':
    broker = Broker()
    broker.run()
