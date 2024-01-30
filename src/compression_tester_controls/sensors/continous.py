import threading
import time

import numpy as np


class Observer:
    def __init__(self):
        self.running = False
        self.data = np.array([])
        self.lock = threading.Lock()

    def start(self):
        """Start the continuous process in a new thread."""
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        """The method that runs continuously in the background."""
        while self.running:
            new_samples = self._read()
            with self.lock:
                self.data = np.append(self.data, new_samples)

    def _read(self):
        new_samples = np.array([])
        return new_samples

    def sample_n(self, n: int):
        """Method to sample the current data."""
        with self.lock:
            idx = max(-n, -len(self.data))
            samples = self.data[idx:]
            return samples

    def sample(self):
        """Method to sample the current data."""
        with self.lock:
            sample = self.data[-1]
            return sample

    def stop_running(self):
        """Stop the continuous process."""
        self.running = False
        self.thread.join()


# Example usage
if __name__ == "__main__":
    runner = ContinuousRunner()
    runner.start()

    try:
        while True:
            print("Last Sample Data:", runner.sample())
            print("Last 100 Samples Data:", runner.sample_n(n=100))
            time.sleep(5)  # Adjust the sampling interval as needed
    except KeyboardInterrupt:
        print("Stopping...")
        runner.stop_running()
