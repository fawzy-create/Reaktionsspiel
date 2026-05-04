import importlib
import tkinter as tk
from tkinter import messagebox

from data import add_score, load_scores


APP_TITLE = "Reaktionsspiel"
WINDOW_SIZE = "600x400"

DEFAULT_SETTINGS = {
    "player_name": "Spieler",
    "menu_bg_color": "#222831",
    "menu_title_color": "#ffffff",
    "menu_player_color": "#dddddd",
    "menu_description_color": "#b8c1cc",
    "button_bg_color": "#f0f0f0",
    "button_text_color": "#000000",
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
    "menu_title_text": "Reaktionsspiel",
    "player_label_text": "Spieler: {player}",
    "color_game_button_text": "Farb-Reaktion",
    "color_game_description": "Warte auf Blau und klicke so schnell wie moeglich.",
    "target_game_button_text": "Ziel-Reaktion",
    "target_game_description": "Warte auf das Ziel und triff es schnell.",
    "highscore_button_text": "Highscores anzeigen",
    "server_button_text": "Server testen",
    "no_highscores_text": "Noch keine Highscores vorhanden.",
    "highscore_heading_text": "Highscores:",
    "color_start_text": "Klicke, um zu starten",
    "color_wait_text": "Warte...",
    "color_wait_subtext": "Nicht klicken - warte auf Blau!",
    "color_go_text": "JETZT! Klicke!",
    "color_early_text": "Zu frueh!",
    "color_early_subtext": "Klicke zum Neustart",
    "color_result_subtext": "Klicke zum Wiederholen",
    "color_restart_text": "Klicke, um erneut zu starten",
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
}

GAMES = [
    {
        "name": "Farb-Reaktion",
        "module": "game_color",
        "button_text_key": "color_game_button_text",
        "description_key": "color_game_description",
    },
    {
        "name": "Ziel-Reaktion",
        "module": "game_target",
        "button_text_key": "target_game_button_text",
        "description_key": "target_game_description",
    },
]


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.settings = DEFAULT_SETTINGS.copy()

        self.container = tk.Frame(root, bg=self.settings["menu_bg_color"])
        self.container.pack(fill="both", expand=True)

        self.show_menu()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_container()
        self.container.configure(bg=self.settings["menu_bg_color"])

        tk.Button(
            self.container,
            text="⚙",
            font=("Helvetica", 16),
            width=2,
            bg=self.settings["button_bg_color"],
            fg=self.settings["button_text_color"],
            command=self.open_settings,
        ).place(relx=1, x=-14, y=12, anchor="ne")

        tk.Label(
            self.container,
            text=self.settings["menu_title_text"],
            font=("Helvetica", 30, "bold"),
            bg=self.settings["menu_bg_color"],
            fg=self.settings["menu_title_color"],
        ).pack(pady=(42, 8))

        tk.Label(
            self.container,
            text=self.format_player_label(),
            font=("Helvetica", 12),
            bg=self.settings["menu_bg_color"],
            fg=self.settings["menu_player_color"],
        ).pack(pady=(0, 18))

        for game in GAMES:
            tk.Button(
                self.container,
                text=self.settings[game["button_text_key"]],
                font=("Helvetica", 16, "bold"),
                width=24,
                bg=self.settings["button_bg_color"],
                fg=self.settings["button_text_color"],
                command=lambda selected=game: self.start_game(selected),
            ).pack(pady=6)

            tk.Label(
                self.container,
                text=self.settings[game["description_key"]],
                font=("Helvetica", 10),
                bg=self.settings["menu_bg_color"],
                fg=self.settings["menu_description_color"],
            ).pack(pady=(0, 8))

        tk.Button(
            self.container,
            text=self.settings["highscore_button_text"],
            font=("Helvetica", 12),
            width=24,
            bg=self.settings["button_bg_color"],
            fg=self.settings["button_text_color"],
            command=self.show_highscores,
        ).pack(pady=(18, 6))

        tk.Button(
            self.container,
            text=self.settings["server_button_text"],
            font=("Helvetica", 12),
            width=24,
            bg=self.settings["button_bg_color"],
            fg=self.settings["button_text_color"],
            command=self.check_server,
        ).pack(pady=6)

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("520x640")
        settings_window.resizable(False, False)

        canvas = tk.Canvas(settings_window, highlightthickness=0)
        scrollbar = tk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas)
        form.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        entries = {}
        fields = [
            ("player_name", "Spielername"),
            ("menu_bg_color", "Menuefarbe"),
            ("menu_title_color", "Titel-Textfarbe"),
            ("menu_player_color", "Spieler-Textfarbe"),
            ("menu_description_color", "Beschreibung-Textfarbe"),
            ("button_bg_color", "Button-Farbe"),
            ("button_text_color", "Button-Textfarbe"),
            ("waiting_color", "Startfarbe"),
            ("ready_color", "Wartefarbe"),
            ("go_color", "Klickfarbe"),
            ("result_color", "Ergebnisfarbe"),
            ("early_color", "Fehlstartfarbe"),
            ("main_text_color", "Haupttext-Farbe"),
            ("sub_text_color", "Untertext-Farbe"),
            ("highscore_text_color", "Highscore-Textfarbe"),
            ("target_fill_color", "Ziel-Fuellfarbe"),
            ("target_outline_color", "Ziel-Randfarbe"),
            ("menu_title_text", "Menue-Titel"),
            ("player_label_text", "Spieler-Text"),
            ("color_game_button_text", "Button Farbspiel"),
            ("color_game_description", "Beschreibung Farbspiel"),
            ("target_game_button_text", "Button Zielspiel"),
            ("target_game_description", "Beschreibung Zielspiel"),
            ("highscore_button_text", "Highscore-Button"),
            ("server_button_text", "Server-Button"),
            ("no_highscores_text", "Keine-Highscores-Text"),
            ("highscore_heading_text", "Highscore-Ueberschrift"),
            ("color_start_text", "Farbspiel Starttext"),
            ("color_wait_text", "Farbspiel Wartetext"),
            ("color_wait_subtext", "Farbspiel Warte-Untertext"),
            ("color_go_text", "Farbspiel Klicktext"),
            ("color_early_text", "Farbspiel Fehlstarttext"),
            ("color_early_subtext", "Farbspiel Fehlstart-Untertext"),
            ("color_result_subtext", "Farbspiel Ergebnis-Untertext"),
            ("color_restart_text", "Farbspiel Neustarttext"),
            ("target_start_text", "Zielspiel Starttext"),
            ("target_wait_text", "Zielspiel Wartetext"),
            ("target_wait_subtext", "Zielspiel Warte-Untertext"),
            ("target_go_text", "Zielspiel Zieltext"),
            ("target_miss_text", "Zielspiel Daneben-Text"),
            ("target_miss_subtext", "Zielspiel Daneben-Untertext"),
            ("target_early_text", "Zielspiel Fehlstarttext"),
            ("target_early_subtext", "Zielspiel Fehlstart-Untertext"),
            ("target_result_subtext", "Zielspiel Ergebnis-Untertext"),
            ("target_restart_text", "Zielspiel Neustarttext"),
        ]

        for row, (key, label) in enumerate(fields):
            tk.Label(form, text=label, anchor="w").grid(
                row=row, column=0, padx=14, pady=8, sticky="w"
            )
            entry = tk.Entry(form, width=34)
            entry.insert(0, self.settings[key])
            entry.grid(row=row, column=1, padx=14, pady=8)
            entries[key] = entry

        def save_settings():
            new_settings = {
                key: entry.get().strip()
                for key, entry in entries.items()
            }
            new_settings["player_name"] = new_settings["player_name"] or "Spieler"

            for key in new_settings:
                if key.endswith("_color"):
                    try:
                        settings_window.winfo_rgb(new_settings[key])
                    except tk.TclError:
                        messagebox.showerror(
                            "Ungueltige Farbe",
                            f"{new_settings[key]} ist keine gueltige Farbe.",
                        )
                        return

            self.settings.update(new_settings)
            settings_window.destroy()
            self.show_menu()

        tk.Button(
            form,
            text="Speichern",
            font=("Helvetica", 12, "bold"),
            width=18,
            command=save_settings,
        ).grid(row=len(fields), column=0, columnspan=2, pady=18)

    def start_game(self, game):
        try:
            module = importlib.import_module(game["module"])
        except ImportError as error:
            messagebox.showerror(
                "Modul fehlt",
                f"Das Modul {game['module']}.py konnte nicht geladen werden.\n\n{error}",
            )
            return

        game_window = tk.Toplevel(self.root)
        game_window.title(game["name"])
        game_window.geometry(WINDOW_SIZE)
        game_window.resizable(False, False)

        state = {
            "root": game_window,
            "game": game["name"],
            "player_name": self.settings["player_name"],
            "colors": self.settings.copy(),
            "submit_score": self.submit_score,
            "get_highscores": self.get_highscores,
        }

        if hasattr(module, "run"):
            module.run(state)
        elif hasattr(module, "ReactionGame"):
            module.ReactionGame(game_window, state)
        else:
            game_window.destroy()
            messagebox.showerror(
                "Falsches Modul",
                f"{game['module']}.py braucht eine run(state)-Funktion "
                "oder eine ReactionGame-Klasse.",
            )

    def submit_score(self, game, player_name, time_ms):
        add_score(player_name, game, time_ms)

    def get_highscores(self, game=None):
        return load_scores(game)

    def show_highscores(self):
        all_scores = self.get_highscores()
        if not all_scores:
            messagebox.showinfo("Highscores", "Noch keine Highscores vorhanden.")
            return

        sections = []
        for game in GAMES:
            scores = self.get_highscores(game["name"])
            lines = [self.settings[game["button_text_key"]]]

            if scores:
                for position, score in enumerate(scores[:5], start=1):
                    lines.append(
                        f"{position}. {score['player']} / {score['time']:.1f} ms"
                    )
            else:
                lines.append(self.settings["no_highscores_text"])

            sections.append("\n".join(lines))

        messagebox.showinfo("Highscores", "\n\n".join(sections))

    def format_player_label(self):
        try:
            return self.settings["player_label_text"].format(
                player=self.settings["player_name"]
            )
        except (KeyError, ValueError):
            return f"Spieler: {self.settings['player_name']}"

    def check_server(self):
        messagebox.showinfo(
            "Server",
            "Server-Anbindung ist vorbereitet. client.py kann hier spaeter eingebaut werden.",
        )


def main():
    root = tk.Tk()
    MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
