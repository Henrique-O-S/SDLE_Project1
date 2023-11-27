import concurrent.futures
import zmq
from server import Server
from ring import ConsistentHashRing

def run_server(server):
    server.run()

if __name__ == '__main__':    
    num_servers = 5  # Change this to the desired number of servers
    num_virtual_nodes = 4  # Change this to the desired number of virtual nodes per server
    servers = [Server(name=f"server_{i}", port=6000 + i) for i in range(num_servers)]
    ring = ConsistentHashRing(servers, num_virtual_nodes)
    print("Creating servers, if line bellow is not commented, need to close graph to continue execution")    
    ring.plot_ring()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_server, servers)

    print("All servers terminated.")
