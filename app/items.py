class Item:
    def __init__(self, name, sprite_idx):
        self.name = name
        self.sprite_idx = sprite_idx

class HealingPotion(Item):
    def __init__(self):
        super().__init__(name="Health Potion", sprite_idx=10)

    def use(self, user):
        user.health = min(user.health + 20, user.max_health)
        print(f"{user} used a health potion.")
class KeyItem(Item):
    def __init__(self):
        super().__init__(name="Key", sprite_idx=7)
    def use(self, user):
        pass