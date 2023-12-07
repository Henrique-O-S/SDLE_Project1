# --------------------------------------------------------------

import concurrent.futures
from broker.broker import Broker

# --------------------------------------------------------------

class MultiBroker:
    NUM_BROKERS = 3
    brokers = [Broker(name=f"broker_{i}", frontend_port=5500 + i, backend_port=8500 + i, replication_port=9500 + i) for i in range(NUM_BROKERS)]
    
# --------------------------------------------------------------

    @staticmethod
    def run_broker(broker):
        broker.run()

    @staticmethod
    def start_brokers():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(MultiBroker.run_broker, MultiBroker.brokers)

# --------------------------------------------------------------
