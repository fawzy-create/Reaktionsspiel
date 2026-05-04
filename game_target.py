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
    "target_fill_color": "#f9d423",
    "target_outline_color": "#ffffff",
    "target_start_text": "Klicke, um zu starten",
    "target_wait_text": "Warte auf das Ziel...",
    "target_wait_subtext": "Nicht vorher klicken",
    "target_go_text": "Jetzt Ziel treffen!",
    "target_miss_text": "Daneben!",
    "target_miss_subtext": "Triff den Kreis",
    "target_early_text": "Zu frueh!",
    "target_early_subtext": "Klicke zum Neustart",
    "target_result_subtext": "Klicke zum Wiederholen",
    "target_restart_text": "Klicke, um erneut zu starten",
    "no_highscores_text": "Keine Highscores",
    "highscore_heading_text": "Highscores:",
}


def run(state):
    TargetGame(state["root"], state)


class TargetGame:
    def __init__(self, root, state=None):
        self.root = root
        self.app_state = state or {}
        self.game_name = self.app_state.get("game", "Ziel-Reaktion")
        self.player_name = self.app_state.get("player_name", "Spieler")
        self.colors = DEFAULT_COLORS.copy()
        self.colors.update(self.app_state.get("colors", {}))
        self.submit_score = self.app_state.get("submit_score", self.local_submit_score)
        self.get_highscores = self.app_state.get("get_highscores", load_scores)

        self.state = "waiting"
        self.after_id = None
        self.start_time = None
        self.target_id = None

        self.canvas = tk.Canvas(root, width=600, height=400, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.label = self.canvas.create_text(
            300,
            110,
            text=self.colors["target_start_text"],
            font=("Helvetica", 26, "bold"),
            fill=self.colors["main_text_color"],
        )
        self.sublabel = self.canvas.create_text(
            300,
            150,
            text="",
            font=("Helvetica", 15),
            fill=self.colors["sub_text_color"],
        )
        self.highscore_text = self.canvas.create_text(
            300,
            330,
            text=self.format_highscores(),
            font=("Helvetica", 13),
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
            self.start_waiting_phase()
        elif self.state == "red":
            self.handle_early_click()
        elif self.state == "target":
            clicked = self.canvas.find_withtag("current")
            if clicked and clicked[0] == self.target_id:
                reaction_time = (time.perf_counter() - self.start_time) * 1000
                self.show_result(reaction_time)
            else:
                self.set_text(
                    self.colors["target_miss_text"],
                    self.colors["target_miss_subtext"],
                )
        elif self.state == "result":
            self.reset()

    def start_waiting_phase(self):
        self.state = "red"
        self.clear_target()
        self.set_color(self.colors["ready_color"])
        self.set_text(
            self.colors["target_wait_text"],
            self.colors["target_wait_subtext"],
        )
        delay = random.randint(1200, 4200)
        self.after_id = self.root.after(delay, self.show_target)

    def handle_early_click(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.state = "waiting"
        self.set_color(self.colors["early_color"])
        self.set_text(
            self.colors["target_early_text"],
            self.colors["target_early_subtext"],
        )

    def show_target(self):
        self.after_id = None
        self.state = "target"
        self.set_color(self.colors["go_color"])
        self.set_text(self.colors["target_go_text"], "")

        radius = 28
        x = random.randint(80, 520)
        y = random.randint(190, 270)
        self.target_id = self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=self.colors["target_fill_color"],
            outline=self.colors["target_outline_color"],
            width=3,
        )
        self.start_time = time.perf_counter()

    def show_result(self, ms):
        self.state = "result"
        self.clear_target()
        self.set_color(self.colors["result_color"])
        self.submit_score(self.game_name, self.player_name, ms)
        self.set_text(f"{ms:.1f} ms", self.colors["target_result_subtext"])
        self.update_highscores()

    def clear_target(self):
        if self.target_id:
            self.canvas.delete(self.target_id)
            self.target_id = None

    def reset(self):
        self.state = "waiting"
        self.clear_target()
        self.set_color(self.colors["waiting_color"])
        self.set_text(self.colors["target_restart_text"])


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ziel-Reaktion")
    root.geometry("600x400")
    root.resizable(False, False)
    TargetGame(root)
    root.mainloop()
