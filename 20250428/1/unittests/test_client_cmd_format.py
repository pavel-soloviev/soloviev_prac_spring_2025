from mood.client.__main__ import MUDClient
import io
import os
import sys
import unittest
from mood import client
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestClient(unittest.TestCase):

    def setUp(self):
        self.sockfd = MagicMock()
        self.sockfd.sendall = lambda s: setattr(self.sockfd, "data", s)
        self.sockfd.recv = lambda size: self.sockfd.data[:size]

    def test_00_format(self):
        with patch("sys.stdin", io.StringIO("down\n")) as stdin:
            MUDClient(self.sockfd, stdin).cmdloop()
            self.assertEqual(self.sockfd.data.decode().rstrip(), "move down")

    def test_01_format(self):
        with patch("sys.stdin", io.StringIO("right\n")) as stdin:
            MUDClient(self.sockfd, stdin).cmdloop()
            self.assertEqual(self.sockfd.data.decode().rstrip(), "move right")

    def test_02_format(self):
        with patch(
            "sys.stdin", io.StringIO(
                "addmon dragon coords 1 1 hp 33 hello RRR\n")
        ) as stdin:
            MUDClient(self.sockfd, stdin).cmdloop()
            self.assertEqual(
                self.sockfd.data.decode().rstrip(), "addmon dragon RRR 33 1 1"
            )

    def test_03_format(self):
        with patch("sys.stdin", io.StringIO("attack dragon with axe\n")) as stdin:
            MUDClient(self.sockfd, stdin).cmdloop()
            self.assertEqual(self.sockfd.data.decode().rstrip(),
                             "attack dragon axe")

    def test_04_format(self):
        with patch("sys.stdin", io.StringIO("attack Trump\n")) as stdin:
            MUDClient(self.sockfd, stdin).cmdloop()
            self.sockfd.return_value.sendall.assert_not_called()
