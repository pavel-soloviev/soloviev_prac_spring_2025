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
    weapons = {'sword': 10, 'spear': 15, 'axe': 20}

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
        """Attack a monster at your position. Syntax: attack <monster> with <weapon>"""
        try:
            args = shlex.split(arg)
        except ValueError as e:
            print(f"Argument parsing error: {e}")
            return

        if not args:
            print("Specify a monster name")
            return


        monster_name = args[0]
        weapon_name = "sword"  # Default weapon
        
        if len(args) > 2 and args[1] == "with":
            weapon_name = args[2]

        if weapon_name not in self.weapons:
            print("Unknown weapon")
            return

        x, y = self.player_pos
        if (x, y) not in monsters or monsters[(x, y)][0] != monster_name:
            print(f"No {monster_name} here")
            return

        damage = self.weapons[weapon_name]
        name, hello, hp = monsters[(x, y)]
        actual_damage = min(hp, damage)
        hp -= actual_damage

        print(f"Attacked {name}, damage {actual_damage} hp")
        if hp <= 0:
            print(f"{name} died")
            del monsters[(x, y)]
        else:
            print(f"{name} now has {hp} hp")
            monsters[(x, y)] = (name, hello, hp)
    
    def complete_attack(self, text, line, begidx, endidx):
        args = line[:endidx].split()
        suggestions = []
        monsters = cowsay.list_cows() + ["jgsbat"]
        weapons_names = list(self.weapons.keys())

        if len(args) == 2:
            suggestions = monsters
        elif len(args) == 3:
            suggestions = ["with"]
        elif len(args) == 4:
            suggestions = weapons_names

        return [item for item in suggestions if item.startswith(text)]


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

