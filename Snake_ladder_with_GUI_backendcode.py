import random
import winsound

class SoundManager:
    DICE_SOUND = r"C:\Users\akash.verma\OneDrive - VCTI\Desktop\STUDY\Python-workspace\Python_session\Snakes&Ladders_project\dice.wav"
    LADDER_SOUND = r"C:\Users\akash.verma\OneDrive - VCTI\Desktop\STUDY\Python-workspace\Python_session\Snakes&Ladders_project\ladder.wav"
    SNAKE_SOUND = r"C:\Users\akash.verma\OneDrive - VCTI\Desktop\STUDY\Python-workspace\Python_session\Snakes&Ladders_project\snake.wav"

    @staticmethod
    def play(path):
        winsound.PlaySound(path, winsound.SND_ASYNC)

    @staticmethod
    def win_sound():
        winsound.Beep(1200, 400)
        winsound.Beep(1500, 400)
        winsound.Beep(1800, 600)

class Board:
    def __init__(self):
        self.ladders = {4: 25, 13: 46, 33: 49, 42: 63, 50: 69, 62: 81, 74: 92}
        self.snakes = {27: 5, 40: 3, 43: 18, 54: 31, 66: 45, 89: 53, 95: 77, 99: 41}

    def check_snake_or_ladder(self, player_id, pos):
        """Return new position after checking snake/ladder, play sound if any."""
        if pos in self.ladders:
            SoundManager.play(SoundManager.LADDER_SOUND)
            return self.ladders[pos]
        elif pos in self.snakes:
            SoundManager.play(SoundManager.SNAKE_SOUND)
            return self.snakes[pos]
        return pos

class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.position = 0
        self.is_open = False  # Player needs a 6 to start

    def move(self, steps):
        """Move player by steps (max 100)."""
        if self.position + steps <= 100:
            self.position += steps

class Game:
    """Core game logic for GUI usage only."""
    def __init__(self):
        self.players = []
        self.board = Board()

    def roll_dice(self):
        """Roll a dice and play sound."""
        SoundManager.play(SoundManager.DICE_SOUND)
        return random.randint(1, 6)


