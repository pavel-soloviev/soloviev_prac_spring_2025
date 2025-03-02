import sys
import cowsay

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


def add_monster(x, y, name, hello):
    try:
        x, y = int(x), int(y)
        if x < 0 or x > 9 or y < 0 or y > 9:
            raise ValueError
    except ValueError:
        print("Invalid arguments")
        return

    available_cows = cowsay.list_cows()
    if name not in available_cows:
        print("Cannot add unknown monster")
    else:
        replaced = (x, y) in monsters
        monsters[(x, y)] = (name, hello)
        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
        if replaced:
            print("Replaced the old monster")


def encounter(x, y):
    print(cowsay.cowsay(monsters[(x, y)][1], cow=monsters[(x, y)][0]))


def parse_commands(command):
    parts = command.strip().split()
    if not parts:
        return

    if parts[0] in ("up", "down", "left", "right"):
        move(parts[0])
    elif parts[0] == "addmon" and len(parts) == 5:
        add_monster(parts[2], parts[3], parts[1], parts[4])
    else:
        print("Invalid command")


if __name__ == "__main__":
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

