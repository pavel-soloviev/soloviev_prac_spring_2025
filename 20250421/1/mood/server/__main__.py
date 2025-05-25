"""Server part of MOOD game."""
import asyncio
import shlex
import cowsay
from ..common import FIELD_SIZE, jgsbat
import random
import gettext
import os


locales_path = os.path.join(os.path.dirname(__file__), '..', 'locales')
translation = gettext.translation("MUD", localedir=locales_path, fallback=True)
_, ngettext = translation.gettext, translation.ngettext


class Weapon:
    """Available weapons for players."""
    weapon_dict = {'sword': 10, 'spear': 15, 'axe': 20}

    def __init__(self, name):
        self.name = name
        self.damage = self.weapon_dict[self.name]


class Player:
    """Player description."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.weapon = Weapon('sword')

    def position(self):
        return self.x, self.y

    def move(self, direction):
        if direction == 'up':
            self.y = (self.y - 1) % FIELD_SIZE
        elif direction == 'down':
            self.y = (self.y + 1) % FIELD_SIZE
        elif direction == 'left':
            self.x = (self.x - 1) % FIELD_SIZE
        elif direction == 'right':
            self.x = (self.x + 1) % FIELD_SIZE
        return self.x, self.y

    def attack_power(self):
        return self.weapon.damage


class Monster:
    """
    Monsters description
    """

    def __init__(self, name, x, y, hp, hello):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.hello = hello

    def exists(self):
        return True


class GameWorld:
    """the main functionality of our game"""
    field = [[None for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)]
    players = {}
    move_monsters = True

    def add_player(self, name):
        if name not in self.players:
            self.players[name] = Player()
            return _("Welcome {name}!").format(name=name)
        return _("Player {name} already exists").format(name=name)

    def encounter(self, x, y):
        monster = self.field[x][y]
        if monster:
            if monster.name == "jgsbat":
                return cowsay.cowsay(monster.hello, cowfile=jgsbat)
            return cowsay.cowsay(monster.hello, cow=monster.name)

    def move_player(self, name, direction):
        x, y = self.players[name].move(direction)
        result = _("Moved to ({x}, {y})").format(x=x, y=y)
        if self.field[x][y] is not None:
            result += "\n" + self.encounter(x, y)
        return result

    def add_monster(self, args):
        name, hello, hp, x, y = args
        x, y, hp = int(x), int(y), int(hp)
        replaced = self.field[x][y] is not None
        self.field[x][y] = Monster(name, x, y, hp, hello)
        message = _("Added monster {name} at ({x},{y}) saying {hello}").format(
            name=name, x=x, y=y, hello=hello)
        if replaced:
            message += _("\nReplaced old monster")
        return message

    def attack_monster(self, player_name, args):
        x, y = self.players[player_name].position()
        monster_name, weapon_name = args

        if monster_name == '.':
            if self.field[x][y] is None:
                return _("No monster here")
            monster_name = self.field[x][y].name
        elif self.field[x][y] is None or monster_name != self.field[x][y].name:
            return _("No {monster_name} here").format(monster_name=monster_name)

        weapon = Weapon(weapon_name)
        damage = min(weapon.damage, self.field[x][y].hp)
        result = _("Attacked {monster_name}").format(monster_name=monster_name) + " " + \
            ngettext(", damage {damage} hp", ", damage {damage} hps", damage).format(
                damage=damage)
        self.field[x][y].hp -= damage

        if self.field[x][y].hp <= 0:
            result += _("\n{monster_name} died").format(monster_name=monster_name)
            self.field[x][y] = None
        else:
            result += _("\n{monster_name} has").format(monster_name=monster_name) + " " + ngettext(
                "{hp_left} hp left", "{hp_left} hps left", self.field[x][y].hp).format(hp_left=self.field[x][y].hp)

        return result

    async def wanderer_movement(self):
        """Move random monster each 30 seconds"""
        while True:
            await asyncio.sleep(30)
            if not self.move_monsters:
                continue

            monsters = []
            for x in range(FIELD_SIZE):
                for y in range(FIELD_SIZE):
                    if self.field[x][y] is not None:
                        monsters.append((x, y, self.field[x][y]))

            if not monsters:
                continue

            moved = False
            attempts = 0
            max_attempts = len(monsters)

            while not moved and attempts < max_attempts:
                attempts += 1
                x, y, monster = random.choice(monsters)
                directions = ['up', 'down', 'left', 'right']
                random.shuffle(directions)

                for direction in directions:
                    new_x, new_y = x, y
                    if direction == 'up':
                        new_y = (y - 1) % FIELD_SIZE
                    elif direction == 'down':
                        new_y = (y + 1) % FIELD_SIZE
                    elif direction == 'left':
                        new_x = (x - 1) % FIELD_SIZE
                    elif direction == 'right':
                        new_x = (x + 1) % FIELD_SIZE

                    if self.field[new_x][new_y] is None:
                        self.field[x][y] = None
                        self.field[new_x][new_y] = monster
                        monster.x, monster.y = new_x, new_y
                        monster_name = monster.name

                        message = _("{monster_name} moved one cell {direction}").format(
                            monster_name=monster_name, direction=direction)
                        for queue in clients.values():
                            await queue.put(message)

                        for player_name, player in self.players.items():
                            if (player.x, player.y) == (new_x, new_y):
                                encounter_msg = self.encounter(new_x, new_y)
                                if encounter_msg:
                                    await clients[player_name].put(encounter_msg)

                        moved = True
                        break
                else:
                    monsters.remove((x, y, self.field[x][y]))

            if not moved and attempts >= max_attempts:
                pass


clients = {}
clients_locales = {}


def set_locale(locale_name):
    locales_path = os.path.join(os.path.dirname(__file__), '..', 'locales')

    try:
        translation = gettext.translation(
            "MUD",
            localedir=locales_path,
            languages=[locale_name],
            fallback=True
        )
        translation.install()
        global _
        global ngettext
        _ = translation.gettext
        ngettext = translation.ngettext
        print(f"Successfully loaded locale: {locale_name}")
    except Exception as e:
        print(f"Locale error: {e}")
        translation = gettext.NullTranslations()
        translation.install()
        _ = translation.gettext
        ngettext = translation.ngettext


async def game_loop(reader, writer, game):
    """Gameloop for our async game"""
    username = None
    locale = 'en_US'

    async def receive_messages():
        while True:
            message = await clients[username].get()
            set_locale(clients_locales.get(username, 'en_US'))
            localized_message = _(message)
            writer.write(f"{localized_message}\n".encode())
            await writer.drain()

    try:
        while not reader.at_eof():
            data = await reader.readline()
            if not data:
                break

            command = shlex.split(data.decode().strip())
            if not command:
                continue

            if command[0] == "register" and len(command) > 1:
                username = command[1]
                set_locale(locale)
                response = game.add_player(username)
                writer.write(f"{response}\n".encode())
                if response.startswith("Welcome"):
                    clients[username] = asyncio.Queue()
                    clients_locales[username] = locale
                    writer.write("<<< Welcome to Python-MUD >>>\n".encode())
                    asyncio.create_task(receive_messages())
                    for user, queue in clients.items():
                        if user != username:
                            set_locale(clients_locales.get(user, 'en_US'))
                            await queue.put(_("{username} joined the game").format(username=username))
                else:
                    break

            elif username in game.players:
                if command[0] == "move" and len(command) > 1:
                    set_locale(clients_locales.get(username, 'en_US'))
                    response = game.move_player(username, command[1])
                    writer.write(f"{response}\n".encode())

                elif command[0] == "addmon" and len(command) > 4:
                    set_locale(clients_locales.get(username, 'en_US'))
                    response = game.add_monster(command[1:])
                    writer.write(f"{response}\n".encode())
                    for user, queue in clients.items():
                        if user != username:
                            set_locale(clients_locales.get(user, 'en_US'))
                            await queue.put(_("{username}: {response}").format(username=username, response=response))

                elif command[0] == "attack" and len(command) > 1:
                    set_locale(clients_locales.get(username, 'en_US'))
                    response = game.attack_monster(username, command[1:])
                    writer.write(f"{response}\n".encode())
                    for user, queue in clients.items():
                        if user != username:
                            set_locale(clients_locales.get(user, 'en_US'))
                            await queue.put(_("{username}: {response}").format(username=username, response=response))

                elif command[0] == "sayall" and len(command) > 1:
                    message = " ".join(command[1:])
                    for user, queue in clients.items():
                        if user != username:
                            set_locale(clients_locales.get(user, 'en_US'))
                            await queue.put(_("{username}: {message}").format(username=username, message=message))
                    set_locale(clients_locales.get(username, 'en_US'))
                    writer.write("Message broadcasted.\n".encode())

                elif command[0] == "movemonsters" and len(command) == 2:
                    if command[1] in ("on", "off"):
                        game.move_monsters = (command[1] == "on")
                        set_locale(clients_locales.get(username, 'en_US'))
                        status = "on" if game.move_monsters else "off"
                        writer.write(_("Moving monsters: {status}\n").format(
                            status=status).encode())
                    else:
                        set_locale(clients_locales.get(username, 'en_US'))
                        writer.write(
                            _("Usage: movemonsters on/off\n").encode())

                elif command[0] == "locale" and len(command) == 2:
                    locale = command[1]
                    clients_locales[username] = locale
                    set_locale(locale)
                    writer.write(_("Set up locale: {locale}").format(
                        locale=locale).encode())

                elif command[0] == "quit":
                    set_locale(clients_locales.get(username, 'en_US'))
                    writer.write(_("Goodbye!\n").encode())
                    break

            await writer.drain()

    finally:
        if username in clients:
            del clients[username]
            del clients_locales[username]
            for queue in clients.values():
                set_locale(clients_locales.get(username, 'en_US'))
                await queue.put(_("{username} left the game").format(username=username))
        writer.close()
        await writer.wait_closed()


async def main():
    """Run server"""
    game_world = GameWorld()
    server = await asyncio.start_server(lambda r, w: game_loop(r, w, game_world), '0.0.0.0', 8000)

    asyncio.create_task(game_world.wanderer_movement())
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
