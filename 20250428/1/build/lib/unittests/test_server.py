from mood.server.__main__ import run_server_finnaly
import os
import socket
import sys
import time
import multiprocessing
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

HOST = "0.0.0.0"
PORT = 8000


class TestMUDServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = multiprocessing.Process(
            target=run_server_finnaly, args=(HOST, PORT))
        cls.proc.start()
        time.sleep(1)
        cls.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.client.connect((HOST, PORT))
        cls.client.sendall(b'register Testuser\n')
        time.sleep(0.2)
        cls.client.recv(4096)
        cls.client.sendall(b"movemonsters off\n")
        time.sleep(0.2)
        cls.client.recv(4096)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.proc.terminate()
        cls.proc.join()
        cls.proc.join(timeout=1)
        if cls.proc.is_alive():
            cls.proc.kill()

    def send_and_receive(self, message):
        """Утилита для отправки команды и получения ответа"""
        self.client.sendall((message + "\n").encode())
        time.sleep(0.2)
        response = self.client.recv(4096).decode()
        return response.strip()

    def test_1(self):
        response = self.send_and_receive(
            'addmon dragon RRR 33 1 0')
        self.assertTrue(response)
        res = response.split("\n")
        self.assertEqual(
            "Added monster dragon at (1,0) saying RRR", res[0])

        response = self.send_and_receive('move right')
        self.assertTrue(response)
        res = response.split("\n", 1)
        self.assertEqual("Moved to (1, 0)", res[0])
        self.assertIn("RRR", res[1])

        response = self.send_and_receive('attack dragon axe')
        self.assertIn(
            "Attacked dragon , damage 20 hps\ndragon has 13 hps left", response)


if __name__ == '__main__':
    unittest.main()
