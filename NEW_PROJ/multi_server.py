import multiprocessing
import time
import subprocess
import sys

def run_server(port):
    subprocess.run([sys.executable, "server.py", str(port)])

if __name__ == '__main__':
    num_servers = 5  # Change this to the desired number of servers

    processes = []

    for i in range(num_servers):
        port = 6000 + i  # You can use different ports for each server
        process = multiprocessing.Process(target=run_server, args=(port,))
        processes.append(process)
        process.start()

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("Terminating servers...")
        for process in processes:
            process.terminate()
            process.join()

    print("All servers terminated.")
