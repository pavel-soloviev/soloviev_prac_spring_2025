import sys
import shlex
import cowsay
from io import StringIO

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


def wrap_position(x, y):
    return x % GRID_SIZE, y % GRID_SIZE


def move(direction):
    global player_pos
    x, y = player_pos

    match direction:
        case "up":
            y -= 1
        case "down":
            y += 1
        case "left":
            x -= 1
        case "right":
            x += 1
        case _:
            print("Invalid command")
            return

    x, y = wrap_position(x, y)
    player_pos = [x, y]
    print(f"Moved to ({x}, {y})")
    if (x, y) in monsters:
        encounter(x, y)


def add_monster(name, hp, x, y, hello):
    try:
        x, y, hp = int(x), int(y), int(hp)
        if x < 0 or x > 9 or y < 0 or y > 9 or hp <= 0:
            raise ValueError
    except ValueError:
        print("Invalid arguments")
        return

    available_cows = cowsay.list_cows()
    if name not in available_cows and name != "jgsbat":
        print("Cannot add unknown monster")
    else:
        replaced = (x, y) in monsters
        monsters[(x, y)] = (name, hello, hp)
        print(
            f"Added monster {name} to ({x}, {y}) saying {hello}")
        if replaced:
            print("Replaced the old monster")


def encounter(x, y):
    name, hello, hp = monsters[(x, y)]
    if name == "jgsbat":
        print(cowsay.cowsay(f"{hello}", cowfile=jgsbat))
    else:
        print(cowsay.cowsay(f"{hello}", cow=name))


def parse_commands(command):
    parts = shlex.split(command)
    if not parts:
        return

    if parts[0] in ("up", "down", "left", "right"):
        move(parts[0])
    elif parts[0] == "addmon":
        try:
            params = {}
            i = 2
            while i < len(parts):
                if parts[i] == "coords":
                    params["coords"] = (parts[i + 1], parts[i + 2])
                    i += 3
                else:
                    params[parts[i]] = parts[i + 1]
                    i += 2
            add_monster(parts[1], params["hp"], params["coords"]
                        [0], params["coords"][1], params["hello"])
        except (IndexError, KeyError, ValueError):
            print("Invalid addmon command format")
    else:
        print("Invalid command")


if __name__ == "__main__":
    print("<<< Welcome to Python-MUD 0.1 >>>")
    if sys.stdin.isatty():  # Интерактивный режим
        while True:
            try:
                command = input("Enter command: ")
                parse_commands(command)
            except EOFError:
                break
    else:  # Чтение из файла
        for line in sys.stdin:
            parse_commands(line)


