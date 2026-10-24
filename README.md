# Suit (Rock-Paper-Scissors) — Minimalist Strategic Game

> A tactical **Suit / Rock-Paper-Scissors** desktop application in Python with Tkinter, featuring a strict **4-color palette** and a multi-turn predictive AI opponent powered by **Gemini 3.8 Flash**.

---

## ✦ Strict 4-Color Palette

The visual design is restricted to four tones:
- **Deep Navy** (`#010736`) — Main window backdrop and active press states.
- **Dark Blue** (`#0D1C42`) — Card containers, panels, and score displays.
- **Royal Blue** (`#22396F`) — Interactive choice buttons and border outlines.
- **Cream Gold** (`#FCF1D0`) — Primary typography, battle icons, and highlight badges.

## ✌️ Features

- **Classic Game Moves:** Rock (Batu ✊), Paper (Kertas ✋), and Scissors (Gunting ✌️).
- **Gemini 3.8 Flash Multi-Turn Opponent:**
  - Maintains conversation and match history via the Google GenAI Interactions API (`client.interactions.create` with `previous_interaction_id`).
  - Analyzes player psychological patterns, frequency bias, and streaks.
  - Automatic fallback to an intelligent Markov-chain / pattern-recognition engine when offline.
- **Scoreboard & Streak Tracking:** Win, Loss, and Draw tracking with real-time streak counters.
- **Zero Heavy Dependencies:** Written entirely in pure Python standard library (Tkinter) with optional `google-genai`.

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- *(Optional)* `google-genai` for Gemini AI features

### Installation & Run

1. Clone the repository:
   ```bash
   git clone https://github.com/ZengLLQ/suit.git
   cd suit
   ```

2. *(Optional)* Configure your Gemini API key:
   ```bash
   pip install google-genai
   export GEMINI_API_KEY="your_api_key_here"  # Windows PowerShell: $env:GEMINI_API_KEY="your_key"
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
