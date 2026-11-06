import unittest
from detector import Detector, Packet

class DetectorTests(unittest.TestCase):
    def test_brute_and_cooldown(self):
        d = Detector()
        results = []
        for i in range(10):
            results += d.inspect(Packet(i*.1, '203.0.113.1', 22, status='AUTH FAIL'))
        self.assertEqual([a[0] for a in results], ['BRUTE FORCE'])
        self.assertIn('203.0.113.1', d.blocked)

    def test_scan(self):
        d = Detector()
        results = []
        for i in range(10):
            results += d.inspect(Packet(i*.1, '203.0.113.2', 1000+i))
        self.assertEqual([a[0] for a in results], ['PORT SCAN'])

    def test_window_expires(self):
        d = Detector()
        for i in range(4):
            self.assertFalse(d.inspect(Packet(i, 'source', 22, status='AUTH FAIL')))
        self.assertFalse(d.inspect(Packet(20, 'source', 22, status='AUTH FAIL')))

    def test_normal(self):
        d = Detector()
        for i in range(100):
            self.assertFalse(d.inspect(Packet(i*.1, 'normal', [53, 80, 443][i%3])))

if __name__ == '__main__':
    unittest.main()
