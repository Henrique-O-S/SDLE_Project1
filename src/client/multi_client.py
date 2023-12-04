import concurrent.futures
from client.client import Client

class MultiClient:
    NUM_CLIENTS = 2

    clients = [Client(name=f"client_{i}", port=5500 + i) for i in range(NUM_CLIENTS)]

    @staticmethod
    def run_client(client):
        client.run()

    @staticmethod
    def start_clients():
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(MultiClient.run_client, MultiClient.clients)