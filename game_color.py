import random
import time
import tkinter as tk

from data import add_score, load_scores


DEFAULT_COLORS = {
    "waiting_color": "#444444",
    "ready_color": "#c0392b",
    "go_color": "#1a6eb5",
    "result_color": "#1a1a2e",
    "early_color": "#8B0000",
    "main_text_color": "#ffffff",
    "sub_text_color": "#ffffff",
    "highscore_text_color": "#ffff00",
    "color_start_text": "Klicke, um zu starten",
    "color_wait_text": "Warte...",
    "color_wait_subtext": "Nicht klicken - warte auf Blau!",
    "color_go_text": "JETZT! Klicke!",
    "color_early_text": "Zu frueh!",
    "color_early_subtext": "Klicke zum Neustart",
    "color_result_subtext": "Klicke zum Wiederholen",
    "color_restart_text": "Klicke, um erneut zu starten",
    "no_highscores_text": "Keine Highscores",
    "highscore_heading_text": "Highscores:",
}


def run(state):
    ReactionGame(state["root"], state)


class ReactionGame:
    def __init__(self, root, state=None):
        self.root = root
        self.app_state = state or {}
        self.game_name = self.app_state.get("game", "Farb-Reaktion")
        self.player_name = self.app_state.get("player_name", "Spieler")
        self.colors = DEFAULT_COLORS.copy()
        self.colors.update(self.app_state.get("colors", {}))
        self.submit_score = self.app_state.get("submit_score", self.local_submit_score)
        self.get_highscores = self.app_state.get("get_highscores", load_scores)

        self.state = "waiting"
        self.start_time = None
        self.after_id = None

        self.canvas = tk.Canvas(root, width=600, height=400, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.label = self.canvas.create_text(
            300,
            150,
            text=self.colors["color_start_text"],
            font=("Helvetica", 28, "bold"),
            fill=self.colors["main_text_color"],
        )
        self.sublabel = self.canvas.create_text(
            300,
            200,
            text="",
            font=("Helvetica", 16),
            fill=self.colors["sub_text_color"],
        )
        self.highscore_text = self.canvas.create_text(
            300,
            300,
            text=self.format_highscores(),
            font=("Helvetica", 14),
            fill=self.colors["highscore_text_color"],
        )

        self.canvas.bind("<Button-1>", self.on_click)
        self.set_color(self.colors["waiting_color"])

    def local_submit_score(self, game, player_name, time_ms):
        add_score(player_name, game, time_ms)

    def set_color(self, color):
        self.canvas.configure(bg=color)
        self.root.configure(bg=color)

    def set_text(self, main, sub=""):
        self.canvas.itemconfig(self.label, text=main)
        self.canvas.itemconfig(self.sublabel, text=sub)

    def format_highscores(self):
        scores = self.get_highscores(self.game_name)
        if not scores:
            return self.colors["no_highscores_text"]

        lines = [self.colors["highscore_heading_text"]]
        for position, score in enumerate(scores[:5], start=1):
            lines.append(f"{position}. {score['player']} - {score['time']:.1f} ms")
        return "\n".join(lines)

    def update_highscores(self):
        self.canvas.itemconfig(self.highscore_text, text=self.format_highscores())

    def on_click(self, event):
        if self.state == "waiting":
            self.start_red_phase()
        elif self.state == "red":
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.state = "waiting"
            self.set_color(self.colors["early_color"])
            self.set_text(
                self.colors["color_early_text"],
                self.colors["color_early_subtext"],
            )
        elif self.state == "blue":
            reaction_time = (time.perf_counter() - self.start_time) * 1000
            self.state = "result"
            self.set_color(self.colors["result_color"])
            self.show_result(reaction_time)
        elif self.state == "result":
            self.state = "waiting"
            self.set_color(self.colors["waiting_color"])
            self.set_text(self.colors["color_restart_text"])

    def start_red_phase(self):
        self.state = "red"
        self.set_color(self.colors["ready_color"])
        self.set_text(
            self.colors["color_wait_text"],
            self.colors["color_wait_subtext"],
        )
        delay = random.randint(1500, 5000)
        self.after_id = self.root.after(delay, self.go_blue)

    def go_blue(self):
        self.after_id = None
        self.state = "blue"
        self.start_time = time.perf_counter()
        self.set_color(self.colors["go_color"])
        self.set_text(self.colors["color_go_text"])

    def show_result(self, ms):
        self.submit_score(self.game_name, self.player_name, ms)
        self.set_text(f"{ms:.1f} ms", self.colors["color_result_subtext"])
        self.update_highscores()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Farb-Reaktion")
    root.geometry("600x400")
    root.resizable(False, False)
    ReactionGame(root)
    root.mainloop()
