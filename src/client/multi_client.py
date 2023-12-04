import concurrent.futures
from client.client import Client
from broker.multi_broker import MultiBroker

class MultiClient:
    NUM_CLIENTS = 2
    number = MultiBroker.NUM_BROKERS
    clients = []
    for i in range(NUM_CLIENTS):
        clients.append(Client(name=f"client_{i}", broker_port=5500 + (i % number)))

    @staticmethod
    def run_client(client):
        client.run()

    @staticmethod
    def start_clients():
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(MultiClient.run_client, MultiClient.clients)