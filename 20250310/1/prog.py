import sys
import shlex
import cowsay
from io import StringIO
import cmd

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


def wrap_position(x, y):
    return x % GRID_SIZE, y % GRID_SIZE


class MUD_Comandline(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = "MUD_cmd>> "
    player_pos = [0, 0]

    def do_exit(self, arg):
        """Exit from cmd"""
        print("Good bye!")
        return True

    def do_EOF(self, arg):
        return True

    def do_up(self, arg):
        """Make step up"""
        x, y = self.player_pos
        x, y = wrap_position(x, y - 1)
        self.player_pos = [x, y]
        print(f"Moved to ({x}, {y})")
        if (x, y) in monsters:
            encounter(x, y)

    def do_down(self, arg):
        """Make step down"""
        x, y = self.player_pos
        x, y = wrap_position(x, y + 1)
        self.player_pos = [x, y]
        print(f"Moved to ({x}, {y})")
        if (x, y) in monsters:
            encounter(x, y)

    def do_left(self, arg):
        """Make step left"""
        x, y = self.player_pos
        x, y = wrap_position(x - 1, y)
        self.player_pos = [x, y]
        print(f"Moved to ({x}, {y})")
        if (x, y) in monsters:
            encounter(x, y)

    def do_right(self, arg):
        """Make step right"""
        x, y = self.player_pos
        x, y = wrap_position(x + 1, y)
        self.player_pos = [x, y]
        print(f"Moved to ({x}, {y})")
        if (x, y) in monsters:
            encounter(x, y)

    def do_addmon(self, arg):
        """Adds a monster to the cell"""
        try:
            args = shlex.split(arg)
        except ValueError as e:
            print(f"Argument parsing error: {e}")
            return
        if not args:
            return
        try:
            params = {}
            i = 1
            while i < len(args):
                if args[i] == "coords" and i + 2 < len(args):
                    params["coords"] = (args[i + 1], args[i + 2])
                    i += 3
                else:
                    params[args[i]] = args[i + 1]
                    i += 2
            add_monster(args[0], params["hp"], params["coords"]
                        [0], params["coords"][1], params["hello"])
        except (IndexError, KeyError, ValueError):
            print("Invalid addmon command format")

    def do_attack(self, arg):
        """Attack a monster by name"""
        if not arg:
            print("Usage: attack <monster_name>")
            return

        x, y = self.player_pos
        if (x, y) not in monsters:
            print(f"No {arg} here")
            return

        name, hello, hp = monsters[(x, y)]
        if name != arg:
            print(f"No {arg} here")
            return

        damage = 10
        new_hp = max(0, hp - damage)
        print(f"Attacked {name}, damage {damage} hp")

        if new_hp == 0:
            print(f"{name} died")
            del monsters[(x, y)]
        else:
            print(f"{name} now has {new_hp} hp")
            monsters[(x, y)] = (name, hello, new_hp)

    def complete_attack(self, text, line, begidx, endidx):
        """Autocomplete monster names for attack command"""
        return [name for name in cowsay.list_cows() + ["jgsbat"] if name.startswith(text)]


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


if __name__ == "__main__":
    MUD_Comandline().cmdloop()

