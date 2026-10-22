import json
import os
import random
import threading
import tkinter as tk
from typing import Optional

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# =====================================================================
# STRICT 4-COLOR PALETTE
# =====================================================================
DEEP_NAVY = "#010736"   # Main window background & button press state
DARK_BLUE = "#0D1C42"   # Card containers, panels & scoreboxes
ROYAL_BLUE = "#22396F"  # Interactive buttons, borders & highlights
CREAM_GOLD = "#FCF1D0"  # Typography, icons & active accents

MOVES = ("ROCK", "PAPER", "SCISSORS")
ICONS = {"ROCK": "✊", "PAPER": "✋", "SCISSORS": "✌️", "IDLE": "❔"}
WIN_MAP = {"ROCK": "SCISSORS", "PAPER": "ROCK", "SCISSORS": "PAPER"}


class GeminiRPSOpponent:
    """Manages multi-turn state with Gemini 3.8 Flash via the Interactions API."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if (HAS_GENAI and self.api_key) else None
        self.previous_interaction_id: Optional[str] = None
        self.online = self.client is not None

    def play_turn(self, player_last_move: str, round_num: int, score_summary: str) -> dict:
        """
        Calls client.interactions.create with gemini-3.8-flash and preserves state
        across turns using previous_interaction_id.
        """
        if not self.online:
            return self._local_fallback(player_last_move)

        prompt = (
            f"Round {round_num} of Rock Paper Scissors. Current score: {score_summary}.\n"
            "Predict the human's next move based on previous rounds and pick your move to beat them. "
            f"For context, the human just locked in their move for this round (do not cheat, analyze patterns, "
            f"then respond to their reveal of '{player_last_move}').\n"
            "Return ONLY valid JSON with two keys:\n"
            '  "ai_move": strictly "ROCK", "PAPER", or "SCISSORS"\n'
            '  "banter": a witty, competitive 1-sentence remark (under 16 words) reacting to the round.'
        )

        try:
            kwargs = {
                "model": "gemini-3.8-flash",
                "input": prompt,
            }
            if self.previous_interaction_id:
                kwargs["previous_interaction_id"] = self.previous_interaction_id

            interaction = self.client.interactions.create(**kwargs)
            self.previous_interaction_id = interaction.id

            raw = interaction.output_text.strip()
            if "```" in raw:
                raw = raw.split("```")[1].replace("json", "", 1).strip()

            data = json.loads(raw)
            ai_move = str(data.get("ai_move", "")).upper()
            if ai_move not in MOVES:
                ai_move = random.choice(MOVES)
            banter = str(data.get("banter", "Calculated move. Let's see how you adapt."))
            return {"ai_move": ai_move, "banter": banter}
        except Exception:
            return self._local_fallback(player_last_move)

    @staticmethod
    def _local_fallback(player_move: str) -> dict:
        ai_move = random.choice(MOVES)
        quips = {
            "WIN": "Read your pattern like open-source code.",
            "LOSE": "Lucky RNG on your end. Run it back!",
            "DRAW": "Great minds collide. Go again!",
        }
        if ai_move == player_move:
            outcome = "DRAW"
        elif WIN_MAP[ai_move] == player_move:
            outcome = "WIN"
        else:
            outcome = "LOSE"
        return {"ai_move": ai_move, "banter": quips[outcome]}


class RockPaperScissorsApp(tk.Tk):
    """Single-file GUI strictly enforcing the 4-color hex palette."""

    def __init__(self) -> None:
        super().__init__()
        self.title("ROCK // PAPER // SCISSORS — GEMINI 3.8 FLASH")
        self.geometry("680x640")
        self.minsize(620, 600)
        self.configure(bg=DEEP_NAVY)

        # Game state
        self.opponent = GeminiRPSOpponent()
        self.player_score = 0
        self.ai_score = 0
        self.draws = 0
        self.round_num = 1
        self.locked = False

        self._build_ui()

    def _build_ui(self) -> None:
        # Outer wrapper
        main = tk.Frame(self, bg=DEEP_NAVY, padx=24, pady=20)
        main.pack(fill="both", expand=True)

        # 1. Header Banner
        header = tk.Frame(
            main,
            bg=DARK_BLUE,
            highlightbackground=ROYAL_BLUE,
            highlightthickness=2,
            padx=18,
            pady=12,
        )
        header.pack(fill="x", pady=(0, 16))

        title_lbl = tk.Label(
            header,
            text="ROCK  •  PAPER  •  SCISSORS",
            font=("Helvetica", 18, "bold"),
            bg=DARK_BLUE,
            fg=CREAM_GOLD,
        )
        title_lbl.pack()

        mode_str = (
            "ENGINE: GEMINI 3.8 FLASH (INTERACTIONS API)"
            if self.opponent.online
            else "ENGINE: LOCAL TACTICAL FALLBACK (SET GEMINI_API_KEY FOR LIVE AI)"
        )
        self.sub_lbl = tk.Label(
            header,
            text=mode_str,
            font=("Courier", 9, "bold"),
            bg=DARK_BLUE,
            fg=CREAM_GOLD,
        )
        self.sub_lbl.pack(pady=(4, 0))

        # 2. Scoreboard Row
        score_frame = tk.Frame(main, bg=DEEP_NAVY)
        score_frame.pack(fill="x", pady=(0, 16))
        score_frame.columnconfigure((0, 1, 2), weight=1, uniform="score")

        self.p_score_lbl = self._create_score_card(score_frame, 0, "PLAYER", "0")
        self.d_score_lbl = self._create_score_card(score_frame, 1, "DRAWS", "0")
        self.a_score_lbl = self._create_score_card(score_frame, 2, "GEMINI", "0")

        # 3. Battle Arena
        arena = tk.Frame(
            main,
            bg=DARK_BLUE,
            highlightbackground=ROYAL_BLUE,
            highlightthickness=2,
            padx=20,
            pady=22,
        )
        arena.pack(fill="both", expand=True, pady=(0, 16))
        arena.columnconfigure((0, 2), weight=1, uniform="fighter")
        arena.columnconfigure(1, weight=0)

        # Player Pod
        p_pod = tk.Frame(arena, bg=DARK_BLUE)
        p_pod.grid(row=0, column=0, sticky="nsew")
        tk.Label(
            p_pod, text="YOU", font=("Helvetica", 11, "bold"), bg=DARK_BLUE, fg=CREAM_GOLD
        ).pack()
        self.p_icon = tk.Label(
            p_pod, text=ICONS["IDLE"], font=("Helvetica", 52), bg=DARK_BLUE, fg=CREAM_GOLD
        )
        self.p_icon.pack(pady=8)
        self.p_move_lbl = tk.Label(
            p_pod, text="WAITING", font=("Courier", 12, "bold"), bg=DARK_BLUE, fg=CREAM_GOLD
        )
        self.p_move_lbl.pack()

        # Center VS Badge
        vs_pod = tk.Frame(arena, bg=DARK_BLUE, padx=16)
        vs_pod.grid(row=0, column=1)
        self.round_badge = tk.Label(
            vs_pod,
            text="ROUND 1",
            font=("Courier", 11, "bold"),
            bg=ROYAL_BLUE,
            fg=CREAM_GOLD,
            padx=10,
            pady=4,
        )
        self.round_badge.pack(pady=(0, 10))
        tk.Label(
            vs_pod, text="VS", font=("Helvetica", 22, "bold"), bg=DARK_BLUE, fg=CREAM_GOLD
        ).pack()

        # AI Pod
        a_pod = tk.Frame(arena, bg=DARK_BLUE)
        a_pod.grid(row=0, column=2, sticky="nsew")
        tk.Label(
            a_pod, text="GEMINI", font=("Helvetica", 11, "bold"), bg=DARK_BLUE, fg=CREAM_GOLD
        ).pack()
        self.a_icon = tk.Label(
            a_pod, text=ICONS["IDLE"], font=("Helvetica", 52), bg=DARK_BLUE, fg=CREAM_GOLD
        )
        self.a_icon.pack(pady=8)
        self.a_move_lbl = tk.Label(
            a_pod, text="WAITING", font=("Courier", 12, "bold"), bg=DARK_BLUE, fg=CREAM_GOLD
        )
        self.a_move_lbl.pack()

        # Outcome & Banter Box inside Arena
        status_box = tk.Frame(
            arena,
            bg=DEEP_NAVY,
            highlightbackground=ROYAL_BLUE,
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        status_box.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(18, 0))

        self.result_lbl = tk.Label(
            status_box,
            text="CHOOSE YOUR WEAPON BELOW",
            font=("Helvetica", 13, "bold"),
            bg=DEEP_NAVY,
            fg=CREAM_GOLD,
        )
        self.result_lbl.pack()

        self.banter_lbl = tk.Label(
            status_box,
            text='"Make your first move. I am tracking your patterns."',
            font=("Courier", 10),
            bg=DEEP_NAVY,
            fg=CREAM_GOLD,
            wraplength=540,
            justify="center",
        )
        self.banter_lbl.pack(pady=(4, 0))

        # 4. Action Buttons (Rock / Paper / Scissors)
        controls = tk.Frame(main, bg=DEEP_NAVY)
        controls.pack(fill="x", pady=(0, 12))
        controls.columnconfigure((0, 1, 2), weight=1, uniform="btn")

        self.move_buttons: list[tk.Button] = []
        for idx, move in enumerate(MOVES):
            btn = tk.Button(
                controls,
                text=f"{ICONS[move]}  {move}",
                font=("Helvetica", 13, "bold"),
                bg=ROYAL_BLUE,
                fg=CREAM_GOLD,
                activebackground=DARK_BLUE,
                activeforeground=CREAM_GOLD,
                relief="flat",
                bd=0,
                highlightbackground=CREAM_GOLD,
                highlightthickness=1,
                padx=12,
                pady=14,
                cursor="hand2",
                command=lambda m=move: self._handle_move(m),
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=6)
            self._bind_hover(btn, ROYAL_BLUE, DARK_BLUE)
            self.move_buttons.append(btn)

        # 5. Footer Reset Bar
        footer = tk.Frame(main, bg=DEEP_NAVY)
        footer.pack(fill="x")

        reset_btn = tk.Button(
            footer,
            text="RESET MATCH & CLEAR INTERACTION MEMORY",
            font=("Courier", 10, "bold"),
            bg=DARK_BLUE,
            fg=CREAM_GOLD,
            activebackground=ROYAL_BLUE,
            activeforeground=CREAM_GOLD,
            relief="flat",
            bd=0,
            highlightbackground=ROYAL_BLUE,
            highlightthickness=1,
            pady=8,
            cursor="hand2",
            command=self._reset_match,
        )
        reset_btn.pack(fill="x", padx=6)
        self._bind_hover(reset_btn, DARK_BLUE, ROYAL_BLUE)

    def _create_score_card(self, parent: tk.Frame, col: int, label: str, initial: str) -> tk.Label:
        card = tk.Frame(
            parent,
            bg=DARK_BLUE,
            highlightbackground=ROYAL_BLUE,
            highlightthickness=2,
            pady=8,
        )
        card.grid(row=0, column=col, sticky="ew", padx=6)

        tk.Label(
            card, text=label, font=("Courier", 10, "bold"), bg=DARK_BLUE, fg=CREAM_GOLD
        ).pack()
        val_lbl = tk.Label(
            card, text=initial, font=("Helvetica", 22, "bold"), bg=DARK_BLUE, fg=CREAM_GOLD
        )
        val_lbl.pack()
        return val_lbl

    @staticmethod
    def _bind_hover(widget: tk.Button, default_bg: str, hover_bg: str) -> None:
        widget.bind("<Enter>", lambda _: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda _: widget.config(bg=default_bg))

    def _handle_move(self, player_move: str) -> None:
        if self.locked:
            return
        self.locked = True

        # Update UI for pending turn
        self.p_icon.config(text=ICONS[player_move])
        self.p_move_lbl.config(text=player_move)
        self.a_icon.config(text=ICONS["IDLE"])
        self.a_move_lbl.config(text="THINKING...")
        self.result_lbl.config(text="ANALYZING MOVE...")

        score_summary = f"Player {self.player_score} - Gemini {self.ai_score} (Draws: {self.draws})"
        threading.Thread(
            target=self._run_ai_turn,
            args=(player_move, self.round_num, score_summary),
            daemon=True,
        ).start()

    def _run_ai_turn(self, player_move: str, round_num: int, score_summary: str) -> None:
        res = self.opponent.play_turn(player_move, round_num, score_summary)
        self.after(0, lambda: self._resolve_round(player_move, res["ai_move"], res["banter"]))

    def _resolve_round(self, player_move: str, ai_move: str, banter: str) -> None:
        self.a_icon.config(text=ICONS[ai_move])
        self.a_move_lbl.config(text=ai_move)

        if player_move == ai_move:
            self.draws += 1
            outcome_text = f"ROUND {self.round_num}: DRAW — BOTH PICKED {player_move}"
        elif WIN_MAP[player_move] == ai_move:
            self.player_score += 1
            outcome_text = f"ROUND {self.round_num}: YOU WIN — {player_move} BEATS {ai_move}!"
        else:
            self.ai_score += 1
            outcome_text = f"ROUND {self.round_num}: GEMINI WINS — {ai_move} BEATS {player_move}!"

        self.p_score_lbl.config(text=str(self.player_score))
        self.d_score_lbl.config(text=str(self.draws))
        self.a_score_lbl.config(text=str(self.ai_score))

        self.result_lbl.config(text=outcome_text)
        self.banter_lbl.config(text=f'"{banter}"')

        self.round_num += 1
        self.round_badge.config(text=f"ROUND {self.round_num}")
        self.locked = False

    def _reset_match(self) -> None:
        if self.locked:
            return
        self.player_score = 0
        self.ai_score = 0
        self.draws = 0
        self.round_num = 1
        self.opponent.previous_interaction_id = None

        self.p_score_lbl.config(text="0")
        self.d_score_lbl.config(text="0")
        self.a_score_lbl.config(text="0")
        self.round_badge.config(text="ROUND 1")
        self.p_icon.config(text=ICONS["IDLE"])
        self.a_icon.config(text=ICONS["IDLE"])
        self.p_move_lbl.config(text="WAITING")
        self.a_move_lbl.config(text="WAITING")
        self.result_lbl.config(text="MATCH RESET — CHOOSE YOUR WEAPON")
        self.banter_lbl.config(text='"Memory wiped. Fresh session initialized."')


if __name__ == "__main__":
    app = RockPaperScissorsApp()
    app.mainloop()