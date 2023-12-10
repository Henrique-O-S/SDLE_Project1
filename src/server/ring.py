import bisect
import hashlib
import random
import uuid


class ConsistentHashRing:
    def __init__(self, servers, virtual_nodes=1, hashing_option=1, replication_factor=2):
        self.servers = servers
        self.virtual_nodes = virtual_nodes
        self.hashing_option = hashing_option
        self.replication_factor = replication_factor
        if self.replication_factor > len(servers) - 1:
            print("Replication factor cannot be greater than the number of servers. Setting replication factor to", len(
                servers) - 1)
            self.replication_factor = len(servers) - 1
        self.ring = self._build_ring()

    def _build_ring(self):
        ring = []
        for server in self.servers:
            for i in range(self.virtual_nodes):
                salt = str(random.getrandbits(8))  # Random 128-bit salt
                virtual_node = f"{server.name}_virtual_{i}_{salt}"
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
        backup = []

        for index in range(index+1, len(self.ring) * 3):
            index = index % len(self.ring)
            node = self.ring[index]
            if node[1].address not in found_addresses:
                found_addresses.append(node[1].address)
                backup.append(node[1])
            if len(backup) == self.replication_factor:
                break

        return {'primary': primary_server, 'backup': backup}


    def add_node(self, server):
        for i in range(self.virtual_nodes):
            virtual_node = f"{server.name}-virtual-{i}"
            key = self._hash_key(virtual_node)
            bisect.insort(self.ring, (key, server))