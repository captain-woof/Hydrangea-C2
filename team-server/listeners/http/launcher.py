import subprocess
import os
import signal
from time import sleep
from threading import Thread
import sys

class HttpListenerLauncher:
    host: str
    port: int
    process: subprocess.Popen
    workersNum: int
    threadOutputStreamer: Thread

    def __init__(self, host="127.0.0.1", port=8000, workersNum = 1):
        self.host = host
        self.port = port
        self.process = None
        self.workersNum = workersNum

    def streamProcessOutput(self):
        while True:
            for line in self.process.stdout:
                sys.stdout.write(line.decode())
            if self.process.poll() is not None:
                break

    def start(self, streamOutput = False):
        """Starts listener Gunicorn server as a subprocess and immediately returns."""
        if self.process is None:
            try:
                # Create and start process
                self.process = subprocess.Popen(
                    ["gunicorn", "-w", f"{self.workersNum}", "-b", f"{self.host}:{self.port}", "--chdir", os.path.join(os.path.abspath(os.path.curdir), "listeners", "http"), "http_server:app"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=os.environ
                )

                # Start output streaming if necessary
                if streamOutput:
                    self.threadOutputStreamer = Thread(
                        target=self.streamProcessOutput
                    )
                    self.threadOutputStreamer.start()

                # Wait for a few seconds to see if process is running; if not, in probably means error
                sleep(2.0)
                if self.process.poll() is None:
                    print(f"HTTP listener started on 'http://{self.host}:{self.port}'")
                    return True
                else:
                    print(f"ERROR: Failed to start listener 'http://{self.host}:{self.port}'")
                    return False
            except:
                return False
        else:
            return False

    def stop(self):
        """Stops the listener Gunicorn server and immediately returns."""
        if self.process:
            try:
                os.kill(self.process.pid, signal.SIGTERM)
                self.process.wait()

                if self.threadOutputStreamer is not None:
                    self.threadOutputStreamer.join()

                print(f"HTTP listener {self.host}{self.port} stopped")
            except Exception:
                return False
        else:
            return False
