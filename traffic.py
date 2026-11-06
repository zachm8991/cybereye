"""Generate fictional traffic; attack buttons enqueue synthetic events only."""
import random
from collections import deque
from detector import Packet

class Traffic:
    def __init__(self):
        self.queue = deque()
        self.serial = 0

    def inject(self, kind):
        self.serial += 1
        source = f'203.0.113.{1 + self.serial % 250}'
        for i in range(10):
            self.queue.append((source, 22 if kind == 'brute' else 1000+i,
                               'AUTH FAIL' if kind == 'brute' else 'CONNECT'))

    def next(self, now):
        if self.queue:
            source, port, status = self.queue.popleft()
            return Packet(now, source, port, 'TCP', status)
        return Packet(now, f'192.168.1.{random.randint(2, 30)}',
                      random.choice([53, 80, 443]), 'UDP' if random.random() < .2 else 'TCP')
