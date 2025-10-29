from Snake_ladder_with_GUI_backendcode import Game, Player, SoundManager
import tkinter as tk
from tkinter import Canvas, simpledialog, messagebox
from PIL import Image, ImageTk
import random
import os

class SnakeLadderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake and Ladder GUI")
        self.root.geometry("600x680")
        self.root.state('zoomed')

        # Hide window temporarily until name inputs are done
        self.root.withdraw()

        # Player setup
        self.player_colors = ["red", "blue", "green", "yellow"]
        self.players_tokens = {}
        self.leaderboard = []
        self.game = Game()

        # Ask number of players
        num_players = simpledialog.askinteger(
            "Players", "Enter number of players (2–4):", minvalue=2, maxvalue=4, parent=self.root
        )
        if not num_players:
            messagebox.showerror("Error", "Please enter valid number of players!")
            self.root.destroy()
            return

        # Ask names for each player
        self.game.players = []
        for i in range(num_players):
            while True:
                name = simpledialog.askstring(
                    "Player Name", f"Enter name for Player {i + 1}:", parent=self.root
                )

                # If user presses Cancel or closes the window → quit the game
                if name is None:
                    self.root.destroy()
                    return

                name = name.strip()
                if name == "":
                    messagebox.showwarning("Warning", "Player name cannot be empty!", parent=self.root)
                    continue

                # Valid name entered → create player
                player = Player(i + 1)
                player.name = name
                self.game.players.append(player)
                break


        # Now show the window again after inputs
        self.root.deiconify()

        # Quit button (top right)
        quit_btn = tk.Button(root, text="❌ Quit", font=("Arial", 12, "bold"),
                             bg="red", fg="white", command=self.root.quit)
        quit_btn.place(relx=0.98, rely=0.02, anchor="ne")

        # Load the board image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        board_path =os.path.join(current_dir, "snakes&ladders_board.png")

        board_img = Image.open(board_path).resize((500, 500))
        self.board_photo = ImageTk.PhotoImage(board_img)

        # Canvas for the board
        self.canvas = Canvas(root, width=500, height=500)
        self.canvas.pack(pady=10)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.board_photo)

        self.player_colors = self.player_colors[:num_players]

        # Create tokens for players
        for i, player in enumerate(self.game.players):
            x, y = self.get_coordinates(player.position, i)
            token = self.canvas.create_oval(x, y, x + 20, y + 20,
                                            fill=self.player_colors[i],
                                            outline="white", width=2)
            self.players_tokens[player.id] = token

        # Status label
        self.status = tk.Label(root, text="", font=("Arial", 16))
        self.status.pack(pady=5)

        # Roll Dice button
        self.roll_btn = tk.Button(root, text="Roll Dice", font=("Arial", 12), command=self.roll_dice)
        self.roll_btn.pack(side="right", padx=(0, 500), pady=(0, 5))

        # Dice Canvas
        self.dice_canvas = Canvas(root, width=80, height=80, bg="white", relief="raised", bd=2)
        self.dice_canvas.pack(side="left", padx=(500, 0), pady=(0, 5))

        self.current_player_index = 0
        self.update_status_for_current_player()

    # -------------------- Dice Drawing --------------------
    def draw_dice_face(self, value):
        """Draw dice face with player-specific color."""
        self.dice_canvas.delete("all")
        cx, cy, r = 40, 40, 8
        color = self.player_colors[self.current_player_index]
        positions = {
            1: [(cx, cy)],
            2: [(20, 20), (60, 60)],
            3: [(20, 20), (cx, cy), (60, 60)],
            4: [(20, 20), (20, 60), (60, 20), (60, 60)],
            5: [(20, 20), (20, 60), (cx, cy), (60, 20), (60, 60)],
            6: [(20, 20), (20, 40), (20, 60), (60, 20), (60, 40), (60, 60)],
        }
        for (x, y) in positions[value]:
            self.dice_canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)

    def animate_dice_roll(self, final_value, callback):
        rolls = 6
        delay = 60
        def roll_frame(i):
            if i < rolls:
                val = random.randint(1, 6)
                self.draw_dice_face(val)
                self.root.after(delay, lambda: roll_frame(i + 1))
            else:
                self.draw_dice_face(final_value)
                callback()
        roll_frame(0)

    # -------------------- Game Logic --------------------
    def get_coordinates(self, position, player_index=0):
        """Get board coordinates with offset to prevent overlapping tokens."""
        if position == 0:
            base_x, base_y = 10, 460
        else:
            row = (position - 1) // 10
            col = (position - 1) % 10
            if row % 2 == 1:
                col = 9 - col
            base_x = 50 * col + 10
            base_y = 500 - 50 * (row + 1) + 10

        # Offset pattern for players
        offsets = [(-5, -5), (15, -5), (-5, 15), (15, 15)]
        dx, dy = offsets[player_index % len(offsets)]
        return base_x + dx, base_y + dy

    def update_status_for_current_player(self):
        if self.game.players:
            player = self.game.players[self.current_player_index]
            color = self.player_colors[self.current_player_index]
            self.status.config(
                text=f"{player.name}'s turn.",
                bg='goldenrod' if color == 'yellow' else color,
                fg='white'
            )

    def roll_dice(self):
        player = self.game.players[self.current_player_index]
        dice_value = self.game.roll_dice()
        self.roll_btn.config(state=tk.DISABLED)
        SoundManager.play(SoundManager.DICE_SOUND)
        self.animate_dice_roll(dice_value, lambda: self.after_dice_roll(player, dice_value))

    def after_dice_roll(self, player, dice):
        if not player.is_open:
            if dice == 6:
                player.is_open = True
                self.status.config(text=f"{player.name} opened the game! Roll again.")
                self.roll_btn.config(state=tk.NORMAL)
            else:
                self.next_turn()
            return

        player.move(dice)
        self.update_token_position(player)

        if dice == 6:
            self.status.config(text=f"{player.name} rolled a 6! Roll again.")
            self.roll_btn.config(state=tk.NORMAL)
            return

        self.root.after(400, lambda: self.handle_snake_or_ladder(player))

    def handle_snake_or_ladder(self, player):
        current_pos = player.position
        new_pos = self.game.board.check_snake_or_ladder(player.id, current_pos)
        if new_pos != current_pos:
            self.root.after(400, lambda: self.animate_snake_ladder_move(player, new_pos))
        else:
            self.check_winner_or_next_turn(player, rolled_six=False)

    def animate_snake_ladder_move(self, player, new_pos):
        player.position = new_pos
        self.update_token_position(player)
        self.check_winner_or_next_turn(player, rolled_six=False)

    def update_token_position(self, player):
        """Update token position with offset logic."""
        player_index = next(i for i, p in enumerate(self.game.players) if p.id == player.id)
        x, y = self.get_coordinates(player.position, player_index)
        self.canvas.coords(self.players_tokens[player.id], x, y, x + 20, y + 20)

    def check_winner_or_next_turn(self, player, rolled_six):
        if player.position == 100:
            self.status.config(text=f"🎉 {player.name} wins!")
            SoundManager.win_sound()
            self.leaderboard.append((player.name, self.player_colors[self.current_player_index]))
            self.roll_btn.config(state=tk.DISABLED)
            self.show_winner_options(player)
            return
        if rolled_six:
            self.status.config(text=f"{player.name} rolled 6! Roll again.")
            return
        self.next_turn()

    def next_turn(self):
        if len(self.game.players) == 1:
            last_player = self.game.players[0]
            if all(pname != last_player.name for pname, _ in self.leaderboard):
                self.leaderboard.append((last_player.name, self.player_colors[0]))
            self.show_leaderboard()
            return

        attempts = 0
        while attempts < len(self.game.players):
            self.current_player_index = (self.current_player_index + 1) % len(self.game.players)
            player = self.game.players[self.current_player_index]
            if player.position < 100:
                break
            attempts += 1

        self.update_status_for_current_player()
        self.roll_btn.config(state=tk.NORMAL)

    def show_winner_options(self, player):
        win_window = tk.Toplevel(self.root)
        win_window.title(f"{player.name} won!")
        win_window.geometry("300x180")

        tk.Label(win_window,
                 text=f"🎉 {player.name} ({self.player_colors[self.current_player_index]}) won!",
                 font=("Arial", 12)).pack(pady=10)

        tk.Button(win_window, text="Continue with remaining players",
                  command=lambda: self.continue_with_remaining(player, win_window)).pack(pady=5)

        tk.Button(win_window, text="Start a New Game",
                  command=lambda: self.start_new_game()).pack(pady=5)

        tk.Button(win_window, text="Show Leaderboard",
                  command=lambda: [win_window.destroy(), self.show_leaderboard()]).pack(pady=5)

    def continue_with_remaining(self, player, win_window):
        win_window.destroy()
        if player.id in [p.id for p in self.game.players]:
            idx = next(i for i, p in enumerate(self.game.players) if p.id == player.id)
            self.game.players.pop(idx)
            token_id = self.players_tokens.pop(player.id, None)
            if token_id:
                self.canvas.delete(token_id)
            self.player_colors.pop(idx)

        if len(self.game.players) == 1:
            last_player = self.game.players[0]
            if all(pname != last_player.name for pname, _ in self.leaderboard):
                self.leaderboard.append((last_player.name, self.player_colors[0]))
            self.show_leaderboard()
            return

        if self.current_player_index >= len(self.game.players):
            self.current_player_index = 0

        self.roll_btn.config(state=tk.NORMAL)
        self.update_status_for_current_player()

    def start_new_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root)

    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("🏆 Leaderboard")
        leaderboard_window.geometry("300x250")

        tk.Label(leaderboard_window, text="Final Leaderboard", font=("Arial", 14, "bold")).pack(pady=10)
        for i, (name, color) in enumerate(self.leaderboard, start=1):
            tk.Label(leaderboard_window, text=f"{i}. {name} ({color})", font=("Arial", 12)).pack()

        tk.Button(leaderboard_window, text="Close", command=leaderboard_window.destroy).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = SnakeLadderGUI(root)
    root.mainloop()
