import socket
import cmd
import shlex
import cowsay

class MUD_Client(cmd.Cmd):
    intro = "Connecting to server..."
    prompt = "MUD_cmd>> "

    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(('localhost', 1337))
            welcome_msg = self.sock.recv(1024).decode()
            print(welcome_msg, end="")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            exit(1)

    def send_command(self, command):
        self.sock.send(command.encode())
        response = self.sock.recv(1024).decode()
        print(response, end="")

    def do_exit(self, arg):
        """Exit from cmd"""
        self.send_command("exit")
        self.sock.close()
        return True

    def do_EOF(self, arg):
        """Exit on EOF"""
        self.send_command("EOF")
        self.sock.close()
        return True

    def do_up(self, arg):
        """Make step up"""
        self.send_command("up")

    def do_down(self, arg):
        """Make step down"""
        self.send_command("down")

    def do_left(self, arg):
        """Make step left"""
        self.send_command("left")

    def do_right(self, arg):
        """Make step right"""
        self.send_command("right")

    def do_addmon(self, arg):
        """Adds a monster to the cell"""
        self.send_command(f"addmon {arg}")

    def do_attack(self, arg):
        """Attack a monster at your position. Syntax: attack <monster> with <weapon>"""
        self.send_command(f"attack {arg}")

    def complete_attack(self, text, line, begidx, endidx):
        args = line[:endidx].split()
        suggestions = []
        # Hardcoded monster list for autocompletion (since client doesn't know game state)
        monsters = cowsay.list_cows() + ["jgsbat"]
        weapons_names = ["sword", "spear", "axe"]

        if len(args) == 2:
            suggestions = monsters
        elif len(args) == 3:
            suggestions = ["with"]
        elif len(args) == 4:
            suggestions = weapons_names

        return [item for item in suggestions if item.startswith(text)]

if __name__ == "__main__":
    MUD_Client().cmdloop()
