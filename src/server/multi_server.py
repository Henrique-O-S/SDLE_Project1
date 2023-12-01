# --------------------------------------------------------------

import concurrent.futures
from server.server import Server
from server.ring import ConsistentHashRing

# --------------------------------------------------------------

class MultiServer:
    NUM_SERVERS = 5
    NUM_VIRTUAL_NODES = 20

    servers = [Server(name=f"server_{i}", port=8000 + i) for i in range(NUM_SERVERS)]
    ring = ConsistentHashRing(servers, NUM_VIRTUAL_NODES, plot=False, test=False, hashing_option=2)

# --------------------------------------------------------------

    @staticmethod
    def run_server(server):
        server.run()

    @staticmethod
    def start_servers():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(MultiServer.run_server, MultiServer.servers)
    
    @staticmethod
    def get_server(key):
        return MultiServer.ring.get_node(key)

# --------------------------------------------------------------
