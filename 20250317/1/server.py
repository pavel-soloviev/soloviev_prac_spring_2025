import socket
import cowsay
from io import StringIO

# Custom jgsbat cow
jgsbat = cowsay.read_dot_cow(StringIO("""
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\'--'//__
         (((""`  `"")))
EOC
"""))

GRID_SIZE = 10
monsters = {}
player_pos = [0, 0]
weapons = {'sword': 10, 'spear': 15, 'axe': 20}

def wrap_position(x, y):
    return x % GRID_SIZE, y % GRID_SIZE

def add_monster(name, hp, x, y, hello):
    try:
        x, y, hp = int(x), int(y), int(hp)
        if x < 0 or x > 9 or y < 0 or y > 9 or hp <= 0:
            raise ValueError
    except ValueError:
        return "Invalid arguments\n"
    
    available_cows = cowsay.list_cows()
    if name not in available_cows and name != "jgsbat":
        return "Cannot add unknown monster\n"
    else:
        replaced = (x, y) in monsters
        monsters[(x, y)] = (name, hello, hp)
        response = f"Added monster {name} to ({x}, {y}) saying {hello}\n"
        if replaced:
            response += "Replaced the old monster\n"
        return response

def encounter(x, y):
    name, hello, hp = monsters[(x, y)]
    if name == "jgsbat":
        return cowsay.cowsay(f"{hello}", cowfile=jgsbat) + "\n"
    else:
        return cowsay.cowsay(f"{hello}", cow=name) + "\n"

def handle_command(command):
    global player_pos
    parts = command.strip().split()
    if not parts:
        return "Empty command\n"

    cmd = parts[0]
    if cmd == "exit" or cmd == "EOF":
        return "Good bye!\n"
    
    elif cmd in ["up", "down", "left", "right"]:
        x, y = player_pos
        if cmd == "up":
            x, y = wrap_position(x, y - 1)
        elif cmd == "down":
            x, y = wrap_position(x, y + 1)
        elif cmd == "left":
            x, y = wrap_position(x - 1, y)
        elif cmd == "right":
            x, y = wrap_position(x + 1, y)
        
        player_pos = [x, y]
        response = f"Moved to ({x}, {y})\n"
        if (x, y) in monsters:
            response += encounter(x, y)
        return response
    
    elif cmd == "addmon":
        try:
            name = parts[1]
            params = {}
            i = 2
            while i < len(parts):
                if parts[i] == "coords" and i + 2 < len(parts):
                    params["coords"] = (parts[i + 1], parts[i + 2])
                    i += 3
                else:
                    params[parts[i]] = parts[i + 1]
                    i += 2
            return add_monster(name, params["hp"], params["coords"][0], params["coords"][1], params["hello"])
        except (IndexError, KeyError):
            return "Invalid addmon command format\n"
    
    elif cmd == "attack":
        try:
            monster_name = parts[1]
            weapon_name = "sword"  # Default weapon
            if len(parts) > 3 and parts[2] == "with":
                weapon_name = parts[3]

            if weapon_name not in weapons:
                return "Unknown weapon\n"

            x, y = player_pos
            if (x, y) not in monsters or monsters[(x, y)][0] != monster_name:
                return f"No {monster_name} here\n"

            damage = weapons[weapon_name]
            name, hello, hp = monsters[(x, y)]
            actual_damage = min(hp, damage)
            hp -= actual_damage

            response = f"Attacked {name}, damage {actual_damage} hp\n"
            if hp <= 0:
                response += f"{name} died\n"
                del monsters[(x, y)]
            else:
                response += f"{name} now has {hp} hp\n"
                monsters[(x, y)] = (name, hello, hp)
            return response
        except IndexError:
            return "Specify a monster name\n"

    return "Unknown command\n"

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 1337))
    server_socket.listen(1)
    print("Server started on port 1337...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Client connected: {addr}")

        # Send welcome message
        client_socket.send("<<< Welcome to Python-MUD 0.1 >>>\n".encode())

        while True:
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break

            response = handle_command(data)
            client_socket.send(response.encode())

            if data in ["exit", "EOF"]:
                break

        client_socket.close()
        print(f"Client disconnected: {addr}")

if __name__ == "__main__":
    start_server()
