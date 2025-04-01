import readline
import sys
import socket
import cmd
import shlex
import threading
import cowsay

FIELD_SIZE = 10

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
                params['hello'] = args[i+1]
                i += 2
            elif args[i] == 'hp' and i + 1 < len(args):
                params['hp'] = int(args[i+1])
                i += 2
            elif args[i] == 'coords' and i + 2 < len(args):
                params['x'] = int(args[i+1])
                params['y'] = int(args[i+2])
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

    def do_quit(self, arg):
        self.sock.sendall(b"quit\n")
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        return
        
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8000))
    
    client = MUDClient(sock, sys.argv[1])
    handler = threading.Thread(target=message_handler, args=(client, sock))
    handler.start()
    
    try:
        client.cmdloop()
    finally:
        handler.join()
        sock.close()

if __name__ == "__main__":
    main()
