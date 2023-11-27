import bisect
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import uuid

class ConsistentHashRing:
    def __init__(self, servers, virtual_nodes=1):
        self.servers = servers
        self.virtual_nodes = virtual_nodes
        self.ring = self._build_ring()

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
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def get_node(self, key):
        if not self.ring:
            return None

        hashed_key = self._hash_key(key)
        index = bisect.bisect(self.ring, (hashed_key,)) % len(self.ring)
        return self.ring[index][1]

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
        for i in range(iterations):
            shopping_list_id = str(uuid.uuid4())
            server = self.get_node(shopping_list_id)
            print(f"Shopping List {shopping_list_id} assigned to Server {server.name}")