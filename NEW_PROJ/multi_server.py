import concurrent.futures
from server import Server
from ring import ConsistentHashRing

class MultiServer:
    NUM_SERVERS = 5
    NUM_VIRTUAL_NODES = 3

    servers = [Server(name=f"server_{i}", port=6000 + i) for i in range(NUM_SERVERS)]
    ring = ConsistentHashRing(servers, NUM_VIRTUAL_NODES, plot=False, test=True, hashing_option=2)

    @staticmethod
    def run_server(server):
        server.run()

    @staticmethod
    def start_servers():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(MultiServer.run_server, MultiServer.servers)

    @staticmethod
    def assign_shopping_list(shopping_list_id):
        target_server = MultiServer.ring.get_node(shopping_list_id)
        print(f"Shopping List {shopping_list_id} assigned to Server {target_server.name}")

if __name__ == '__main__':
    # Start servers
    MultiServer.start_servers()

    print("All servers terminated.")
