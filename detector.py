"""Sliding-window rules over synthetic events. No network access."""
from collections import defaultdict, deque
from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    timestamp: float
    source: str
    port: int
    protocol: str = 'TCP'
    status: str = 'OK'

class Detector:
    def __init__(self):
        self.events = defaultdict(deque)
        self.last_alert = {}
        self.blocked = set()

    def inspect(self, packet):
        history = self.events[packet.source]
        history.append(packet)
        while history and packet.timestamp - history[0].timestamp > 10:
            history.popleft()
        # Expire inactive sources so memory does not grow indefinitely.
        for source in list(self.events):
            if self.events[source] and packet.timestamp - self.events[source][-1].timestamp > 10:
                del self.events[source]
        rules = []
        failures = sum(p.status == 'AUTH FAIL' for p in history)
        ports = len({p.port for p in history})
        if failures >= 5:
            rules.append(('BRUTE FORCE', f'{failures} failed logins / 10s'))
        if ports >= 8:
            rules.append(('PORT SCAN', f'{ports} distinct ports / 10s'))
        alerts = []
        for kind, reason in rules:
            key = (packet.source, kind)
            if packet.timestamp - self.last_alert.get(key, -100) >= 10:
                self.last_alert[key] = packet.timestamp
                self.blocked.add(packet.source)
                alerts.append((kind, packet.source, reason))
        return alerts
