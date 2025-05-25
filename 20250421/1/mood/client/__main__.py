"""Client part of MOOD game."""
import readline
import sys
import socket
import cmd
import shlex
import threading
import cowsay
from ..common import FIELD_SIZE
import time
import argparse
import gettext
import os

localedir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'locales'))

gettext.bindtextdomain('MUD', localedir)
gettext.textdomain('MUD')


def message_handler(cmd_interface, sock):
    while True:
        data = sock.recv(8192)
        if not data:
            break
        message = data.decode().rstrip()
        print(f'\n{message}')
        current_input = f'{cmd_interface.prompt}{readline.get_line_buffer()}'
        print(current_input, end='', flush=True)


def parse_attack(args):
    if not args or args[0] == 'with':
        monster = '.'
        remaining = args
    else:
        monster = args[0]
        if monster not in cowsay.list_cows() and monster != 'jgsbat':
            return "Unknown monster"
        remaining = args[1:]

    if not remaining:
        return f"attack {monster} sword"
    if len(remaining) >= 2 and remaining[0] == 'with':
        weapon = remaining[1]
        if weapon in ['sword', 'spear', 'axe']:
            return f"attack {monster} {weapon}"
    return "Unknown weapon"


def parse_addmon(args):
    try:
        params = {
            'name': args[0],
            'hello': 'Hello',
            'hp': 100,
            'x': 0,
            'y': 0
        }

        i = 1
        while i < len(args):
            if args[i] == 'hello' and i + 1 < len(args):
                params['hello'] = args[i + 1]
                i += 2
            elif args[i] == 'hp' and i + 1 < len(args):
                params['hp'] = int(args[i + 1])
                i += 2
            elif args[i] == 'coords' and i + 2 < len(args):
                params['x'] = int(args[i + 1])
                params['y'] = int(args[i + 2])
                i += 3
            else:
                i += 1

        if not (0 <= params['x'] < FIELD_SIZE and 0 <= params['y'] < FIELD_SIZE):
            return "Invalid coordinates"
        if params['name'] not in cowsay.list_cows() and params['name'] != 'jgsbat':
            return "Unknown monster"

        return f"addmon {params['name']} {params['hello']} {params['hp']} {params['x']} {params['y']}"
    except:
        return "Invalid arguments"


def parse_sayall(args):
    if len(args) != 1:
        return "Invalid arguments"
    message = args[0]
    return f"sayall {message}"


class MUDClient(cmd.Cmd):
    prompt = "MUD> "

    def __init__(self, sock, username):
        super().__init__()
        self.sock = sock
        self.sock.sendall(f"register {username}\n".encode())

    def do_movemonsters(self, arg):
        args = shlex.split(arg)
        if len(args) == 1 and args[0] in ("on", "off"):
            self.sock.sendall(f"movemonsters {args[0]}\n".encode())
        else:
            print("Usage: movemonsters on/off")

    def do_up(self, arg):
        self.sock.sendall(b"move up\n")

    def do_down(self, arg):
        self.sock.sendall(b"move down\n")

    def do_left(self, arg):
        self.sock.sendall(b"move left\n")

    def do_right(self, arg):
        self.sock.sendall(b"move right\n")

    def do_addmon(self, arg):
        result = parse_addmon(shlex.split(arg))
        if result.startswith('addmon'):
            self.sock.sendall(f"{result}\n".encode())
        else:
            print(result)

    def do_attack(self, arg):
        result = parse_attack(shlex.split(arg))
        if result.startswith('attack'):
            self.sock.sendall(f"{result}\n".encode())
        else:
            print(result)

    def complete_attack(self, text, line, begidx, endidx):
        monsters = cowsay.list_cows() + ['jgsbat']
        weapons = ['sword', 'spear', 'axe']
        parts = line[:begidx].split()

        if len(parts) == 1:
            return [m for m in monsters if m.startswith(text)]
        if len(parts) >= 2 and parts[-1] == 'with':
            return [w for w in weapons if w.startswith(text)]
        return []

    def do_sayall(self, arg):
        result = parse_sayall(shlex.split(arg))
        if result.startswith('sayall'):
            self.sock.sendall(f"{result}\n".encode())
        else:
            print(result)

    def do_locale(self, arg):
        args = shlex.split(arg)
        if len(args) != 1:
            print("Usage: locale <locale_name>")
            return

        locale_name = args[0]
        try:
            translation = gettext.translation(
                "MUD",
                localedir=localedir,
                languages=[locale_name]
            )
            translation.install()
            print(f"Locale changed to: {locale_name}")

            self.sock.sendall(f"locale {locale_name}\n".encode())
        except Exception as e:
            print(f"Failed to set locale: {e}")

    def do_quit(self, arg):
        self.sock.sendall(b"quit\n")
        return True


class FileMUDClient(MUDClient):
    def __init__(self, sock, username, file):
        cmd.Cmd.__init__(self, stdin=file, stdout=sys.stdout)
        self.sock = sock
        self.prompt = ''
        self.use_rawinput = False
        self.sock.sendall(f"register {username}\n".encode())

    def onecmd(self, line):
        time.sleep(1)  # Задержка между командами
        return super().onecmd(line)

    def do_EOF(self, arg):
        return True


def run_from_file(username, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8000))

    with open(filename) as f:
        client = FileMUDClient(sock, username, f)
        handler = threading.Thread(target=message_handler, args=(client, sock))
        handler.daemon = True
        handler.start()
        try:
            client.cmdloop()
        finally:
            sock.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("--file", help="File with commands")
    args = parser.parse_args()

    if args.file:
        run_from_file(args.username, args.file)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8000))

        client = MUDClient(sock, args.username)
        handler = threading.Thread(target=message_handler, args=(client, sock))
        handler.start()

        try:
            client.cmdloop()
        finally:
            handler.join()
            sock.close()


if __name__ == "__main__":
    main()
