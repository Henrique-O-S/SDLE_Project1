import concurrent.futures
import zmq
from server import Server
from ring import ConsistentHashRing
import uuid

def run_server(server):
    server.run()

if __name__ == '__main__':    
    NUM_SERVERS = 5  # Change this to the desired number of servers
    NUM_VIRTUAL_NODES = 3  # Change this to the desired number of virtual nodes per server

    servers = [Server(name=f"server_{i}", port=6000 + i) for i in range(NUM_SERVERS)]

    ring = ConsistentHashRing(servers, NUM_VIRTUAL_NODES, plot=False, test=True, hashing_option=2) #if plot then need to close it to continue running

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_server, servers)

    print("All servers terminated.")
