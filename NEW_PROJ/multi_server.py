import concurrent.futures
import zmq
from server import Server
from ring import ConsistentHashRing
import uuid

def run_server(server):
    server.run()

if __name__ == '__main__':    
    num_servers = 3  # Change this to the desired number of servers
    num_virtual_nodes = 6  # Change this to the desired number of virtual nodes per server

    servers = [Server(name=f"server_{i}", port=6000 + i) for i in range(num_servers)]

    ring = ConsistentHashRing(servers, num_virtual_nodes, plot=True, test=True) #if plot then need to close it to continue running

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_server, servers)

    print("All servers terminated.")
