import os
import sys

BASE_PORT = 20000
IMAGE = "cc7w/linux-training:v8"
NUM_CONTAINERS = 3

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "start":
        for i in range(NUM_CONTAINERS):
            port = BASE_PORT + i
            cmd = f"docker run -p 127.0.0.1:{port}:22 -d --name server{i} {IMAGE}"
            print(cmd)
            os.system(cmd)
    elif len(sys.argv) == 2 and sys.argv[1] == "destroy":
        for i in range(NUM_CONTAINERS):
            cmd = f"docker stop server{i} && docker rm server{i}"
            print(cmd)
            os.system(cmd)
    else:
        print("Usage: ./configure.py start|destroy")
        sys.exit(1)
