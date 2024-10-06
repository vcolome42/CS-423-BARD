class Room:
    # Mostly all placeholders
    def __init__(self):
        self.items = []
        self.monsters = []
        self.traps = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def add_monster(self, monster):
        self.monsters.append(monster)

    def remove_monster(self, monster):
        if monster in self.monsters:
            self.monsters.remove(monster)

    def add_trap(self, trap):
        self.traps.append(trap)

    def remove_trap(self, trap):
        if trap in self.traps:
            self.traps.remove(trap)

    def player_pick_up_item(self, item):
        self.remove_item(item)
        return item

    def player_kill_monster(self, monster):
        self.remove_monster(monster)

    def player_trigger_trap(self, trap):
        self.remove_trap(trap)
