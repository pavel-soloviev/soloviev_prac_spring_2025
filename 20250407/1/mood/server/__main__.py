"""Server part of MOOD game."""
import asyncio
import shlex
import cowsay
from ..common import FIELD_SIZE, jgsbat
import random


class Weapon:
    weapon_dict = {'sword': 10, 'spear': 15, 'axe': 20}

    def __init__(self, name):
        self.name = name
        self.damage = self.weapon_dict[self.name]


class Player:
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
    def __init__(self, name, x, y, hp, hello):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.hello = hello

    def exists(self):
        return True


class GameWorld:
    field = [[None for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)]
    players = {}

    def add_player(self, name):
        if name not in self.players:
            self.players[name] = Player()
            return f"Welcome {name}!"
        return f"Player {name} already exists"

    def encounter(self, x, y):
        monster = self.field[x][y]
        if monster:
            if monster.name == "jgsbat":
                return cowsay.cowsay(monster.hello, cowfile=jgsbat)
            return cowsay.cowsay(monster.hello, cow=monster.name)

    def move_player(self, name, direction):
        x, y = self.players[name].move(direction)
        result = f"Moved to ({x}, {y})"
        if self.field[x][y] is not None:
            result += "\n" + self.encounter(x, y)
        return result

    def add_monster(self, args):
        name, hello, hp, x, y = args
        x, y, hp = int(x), int(y), int(hp)
        replaced = self.field[x][y] is not None
        self.field[x][y] = Monster(name, x, y, hp, hello)
        message = f"Added monster {name} at ({x},{y}) saying {hello}"
        if replaced:
            message += "\nReplaced old monster"
        return message

    def attack_monster(self, player_name, args):
        x, y = self.players[player_name].position()
        monster_name, weapon_name = args

        if monster_name == '.':
            if self.field[x][y] is None:
                return "No monster here"
            monster_name = self.field[x][y].name
        elif self.field[x][y] is None or monster_name != self.field[x][y].name:
            return f"No {monster_name} here"

        weapon = Weapon(weapon_name)
        damage = min(weapon.damage, self.field[x][y].hp)
        result = f"Attacked {monster_name}, damage {damage} hp"
        self.field[x][y].hp -= damage

        if self.field[x][y].hp <= 0:
            result += f"\n{monster_name} died"
            self.field[x][y] = None
        else:
            result += f"\n{monster_name} has {self.field[x][y].hp} hp left"

        return result
    
    async def wanderer_movement(self):
        while True:
            await asyncio.sleep(30)
            
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
                        
                        message = f"{monster.name} moved one cell {direction}"
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


async def game_loop(reader, writer):
    game = GameWorld()
    username = None

    async def receive_messages():
        while True:
            message = await clients[username].get()
            writer.write(f"{message}\n".encode())
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
                response = game.add_player(username)
                writer.write(f"{response}\n".encode())
                if response.startswith("Welcome"):
                    clients[username] = asyncio.Queue()
                    writer.write("<<< Welcome to Python-MUD >>>\n".encode())
                    asyncio.create_task(receive_messages())
                    for user, queue in clients.items():
                        if user != username:
                            await queue.put(f"{username} joined the game")
                else:
                    break

            elif username in game.players:
                if command[0] == "move" and len(command) > 1:
                    response = game.move_player(username, command[1])
                    writer.write(f"{response}\n".encode())

                elif command[0] == "addmon" and len(command) > 4:
                    response = game.add_monster(command[1:])
                    writer.write(f"{response}\n".encode())
                    for user, queue in clients.items():
                        if user != username:
                            await queue.put(f"{username}: {response}")

                elif command[0] == "attack" and len(command) > 1:
                    response = game.attack_monster(username, command[1:])
                    writer.write(f"{response}\n".encode())
                    for user, queue in clients.items():
                        if user != username:
                            await queue.put(f"{username}: {response}")

                elif command[0] == "sayall" and len(command) > 1:
                    message = " ".join(command[1:])
                    for user, queue in clients.items():
                        if user != username:
                            await queue.put(f"{username}: {message}")
                    writer.write("Message broadcasted.\n".encode())

                elif command[0] == "quit":
                    writer.write("Goodbye!\n".encode())
                    break

            await writer.drain()

    finally:
        if username in clients:
            del clients[username]
            for queue in clients.values():
                await queue.put(f"{username} left the game")
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(game_loop, '0.0.0.0', 8000)
    game_world = GameWorld()
    
    asyncio.create_task(game_world.wanderer_movement())
    async with server:
        await server.serve_forever()

asyncio.run(main())
