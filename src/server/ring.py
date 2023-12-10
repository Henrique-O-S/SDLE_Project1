import bisect
import hashlib
import random
import numpy as np
import matplotlib.pyplot as plt
import uuid


class ConsistentHashRing:
    def __init__(self, servers, virtual_nodes=1, plot=False, test=False, hashing_option=2, replication_factor=2):
        self.servers = servers
        self.virtual_nodes = virtual_nodes
        self.hashing_option = hashing_option
        self.replication_factor = replication_factor
        if self.replication_factor > len(servers) - 1:
            print("Replication factor cannot be greater than the number of servers. Setting replication factor to", len(
                servers) - 1)
            self.replication_factor = len(servers) - 1
        self.ring = self._build_ring()
        if plot:
            self.plot_ring()

    def _build_ring(self):
        ring = []
        for server in self.servers:
            for i in range(self.virtual_nodes):
                salt = str(random.getrandbits(32))  # Random 128-bit salt
                virtual_node = f"{server.name}_virtual_{i}_{salt}"
                key = self._hash_key(virtual_node)
                ring.append((key, server))

        ring.sort(key=lambda x: x[0])
        return ring

    def _hash_key(self, key):
        if self.hashing_option == 0:
            return int(hashlib.md5(key.encode()).hexdigest(), 16)
        elif self.hashing_option == 1:
            return int(hashlib.sha256(key.encode()).hexdigest(), 16) % 10**32
        elif self.hashing_option == 2:
            return int(hashlib.sha512(key.encode()).hexdigest(), 16) % 10**32

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
            # print("now in ", node[1].address)
            if node[1].address not in found_addresses:
                found_addresses.append(node[1].address)
                backup.append(node[1])
                # print("added ", node[1].address)
            if len(backup) == self.replication_factor:
                break

        return {'primary': primary_server, 'backup': backup}

    def plot_ring(self):
        num_nodes = len(self.ring)
        radius = 3  # Adjust the radius as needed

        fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
        ax.set_xlim([-radius - 2, radius + 0.2])
        ax.set_ylim([-radius - 0.2, radius + 0.2])

        circle = plt.Circle((0, 0), radius, edgecolor='black', facecolor='none')
        ax.add_artist(circle)

        unique_nodes = list(server.name for server in self.servers)
        colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_nodes)))

        node_colors = {node: colors[i] for i, node in enumerate(unique_nodes)}
        legend_handles = []


        for i, (key, server) in enumerate(self.ring):
            angle = (2 * np.pi * key) / (10 ** 32)
            #print server.name, angle in degrees
            print(server.name, key, np.degrees(angle))
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            # Plot a cross (X) for each node with a unique color
            ax.scatter(x, y, marker='x', s=100, color=node_colors[server.name])

            # Add to legend only if not added before
            if server.name not in [handle.get_label() for handle in legend_handles]:
                legend_handles.append(ax.scatter([], [], marker='x', color=node_colors[server.name], label=server.name, s=100))

        # Plot shopping lists
        assigned_shopping_lists = self.add_shopping_lists(ax)
        #append to legend number of shopping lists assinged to each server
        for server, num_lists in assigned_shopping_lists.items():
            legend_handles.append(plt.Line2D([0], [0], marker='o', color='grey', label=f"{server}: {num_lists}", markersize=10, markerfacecolor='none'))

        # Create a single legend for nodes
        legend_handles.append(plt.Line2D([0], [0], marker='x', color='w', label=f"Physical Nodes: {len(self.servers)}\nVirtual Nodes: {self.virtual_nodes}", markersize=10, markerfacecolor='none'))
        ax.legend(handles=legend_handles, loc='upper left')

        ax.set_xticks([])
        ax.set_yticks([])

        plt.show()


    def add_shopping_lists(self, ax, num_lists=20):
        assigned_shopping_lists = {server.name: 0 for server in self.servers}
        shopping_lists = [str(uuid.uuid4()) for _ in range(num_lists)]

        for shopping_list_id in shopping_lists:
            nodes = self.get_nodes(shopping_list_id)
            primary_server = nodes['primary']

            # Calculate the angle for the primary server
            primary_angle = (2 * np.pi * self._hash_key(shopping_list_id)) / (10 ** 32)
            print("shopping list", self._hash_key(shopping_list_id)  , np.degrees(primary_angle))

            # Plot the shopping list for the primary server
            x_primary = 3 * np.cos(primary_angle)
            y_primary = 3 * np.sin(primary_angle)
            ax.scatter(x_primary, y_primary, marker='o', color='grey', s=30)

            assigned_shopping_lists[primary_server.name] += 1

        print("Assigned shopping lists:", assigned_shopping_lists)
        return assigned_shopping_lists





    def add_node(self, server):
        for i in range(self.virtual_nodes):
            virtual_node = f"{server.name}-virtual-{i}"
            key = self._hash_key(virtual_node)
            bisect.insort(self.ring, (key, server))