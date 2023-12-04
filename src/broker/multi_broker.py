# --------------------------------------------------------------

import concurrent.futures
from broker.broker import Broker

# --------------------------------------------------------------

class MultiBroker:
    NUM_BROKERS = 2
    brokers = [Broker(name=f"broker_{i}", frontend_port=5500 + i, backend_port=8500 + i) for i in range(NUM_BROKERS)]
    #brokers = [Broker(name=f"broker_0", frontend_port=5500, backend_port=8500, pulse_check_interval=1), Broker(name=f"broker_1", frontend_port=5501, backend_port=8501, pulse_check_interval=20)]
# --------------------------------------------------------------

    @staticmethod
    def run_broker(broker):
        broker.run()

    @staticmethod
    def start_brokers():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(MultiBroker.run_broker, MultiBroker.brokers)

# --------------------------------------------------------------
