from room import *


class Player:
    def __init__(self, name, health, attack, defense):
        self.name = name
        self.health = health
        self.attack = attack  # changed for when player is holding a sword?
        self.inventory = []  # can have different items

    # Mostly all placeholders
    def move(self, direction):
        x, y = self.position
        if direction == "up":
            self.position = (x, y - 1)
        elif direction == "down":
            self.position = (x, y + 1)
        elif direction == "left":
            self.position = (x - 1, y)
        elif direction == "right":
            self.position = (x + 1, y)

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def attack_enemy(self, enemy):
        damage = self.attack
        enemy.take_damage(damage)

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def use_item(self, item):
        if item in self.inventory:
            # placeholder
            self.inventory.remove(item)

    def pick_up_item(self, room, item):
        picked_item = room.player_pick_up_item(item)
        self.add_to_inventory(picked_item)

    def kill_monster(self, room, monster):
        room.player_kill_monster(monster)

    def trigger_trap(self, room, trap):
        room.player_trigger_trap(trap)
        self.apply_trap_effect(trap)

    def apply_trap_effect(self, trap):
        if trap == "Spiked Pit":
            self.take_damage(20)
            print(f"{self.name} fell into a {trap} and took 20 damage!")
        # add more trap effects
