import bisect
import hashlib
import numpy as np
import matplotlib.pyplot as plt

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
        angles = np.linspace(0, 2 * np.pi, len(self.ring), endpoint=False)
        points = np.column_stack((np.cos(angles), np.sin(angles)))

        fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
        ax.plot(points[:, 0], points[:, 1], marker='o', linestyle='-', color='b')

        for i, (_, server) in enumerate(self.ring):
            angle = 2 * np.pi * i / len(self.ring)
            ax.text(np.cos(angle), np.sin(angle), f"{server.name}\n({server.port})", ha='center', va='center', fontweight='bold')

        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()