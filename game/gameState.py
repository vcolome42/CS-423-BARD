class GameState:
    def __init__(self):
        self.player = None
        self.rooms = []
        self.is_game_over = False

    # Mostly all placeholders
    def add_player(self, player):
        self.player = player

    def add_room(self, room):
        self.rooms.append(room)

    def check_game_over(self):
        if self.player.health <= 0:
            self.is_game_over = True

    def update(self):
        self.check_game_over()
