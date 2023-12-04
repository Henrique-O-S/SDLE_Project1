import bisect
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import uuid

class ConsistentHashRing:
    def __init__(self, servers, virtual_nodes=1, plot=False, test=False, hashing_option=0):
        self.servers = servers
        self.virtual_nodes = virtual_nodes
        self.hashing_option = hashing_option
        self.ring = self._build_ring()
        if plot:
            self.plot_ring()
        if test:
            self.test_ring(100)

    def _build_ring(self):
        ring = []
        for server in self.servers:
            for i in range(self.virtual_nodes):
                virtual_node = f"{server.name}-virtual-{i}"
                key = self._hash_key(virtual_node)
                ring.append((key, server))

        ring.sort(key=lambda x: x[0])
        return ring

    def _hash_key(self, key):
        if self.hashing_option == 0:
            return int(hashlib.md5(key.encode()).hexdigest(), 16)
        elif self.hashing_option == 1:
            return int(hashlib.sha256(key.encode()).hexdigest(), 16)
        elif self.hashing_option == 2:
            return int(hashlib.sha512(key.encode()).hexdigest(), 16)

    def get_nodes(self, key):
        if not self.ring:
            return None

        hashed_key = self._hash_key(key)
        index = bisect.bisect(self.ring, (hashed_key,)) % len(self.ring)

        # Retrieve the server responsible for the given key
        primary_server = self.ring[index][1]

        found_addresses = [primary_server.address]
        ret = []

        for node in self.ring[index+1:]:
            print("now in ", node[1].address)
            if node[1].address not in found_addresses:
                found_addresses.append(node[1].address)
                ret.append(node[1])
                print("added ", node[1].address)
            if len(ret) == 2:
                break


        return {'primary': primary_server, 'backup': ret}





    def plot_ring(self):
        num_nodes = len(self.ring)
        radius = 2  # Adjust the radius as needed

        fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
        ax.set_xlim([-radius, radius])
        ax.set_ylim([-radius, radius])

        circle = plt.Circle((0, 0), radius, edgecolor='b', facecolor='none')
        ax.add_artist(circle)

        for i, (_, server) in enumerate(self.ring):
            angle = 2 * np.pi * i / num_nodes
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            ax.text(x, y, f"{server.name}\n({server.port})\n({i % self.virtual_nodes})", ha='center', va='center', fontweight='bold')

        ax.set_xticks([])
        ax.set_yticks([])

        plt.show()

    def add_node(self, server):
        for i in range(self.virtual_nodes):
            virtual_node = f"{server.name}-virtual-{i}"
            key = self._hash_key(virtual_node)
            bisect.insort(self.ring, (key, server))

    def test_ring(self, iterations):
        print("Testing ring...")
        assignments_count = {server.name: 0 for server in self.servers}
        for i in range(iterations):
            i+1
            shopping_list_id = str(uuid.uuid4())
            server = self.get_node(shopping_list_id)
            assignments_count[server.name] += 1
            #print(f"Shopping List {shopping_list_id} assigned to Server {server.name}")
        print("Test complete")
        for server_name, count in assignments_count.items():
            print(f"Server {server_name} got {count} shopping lists.")