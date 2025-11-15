# 🐍 Advanced Snake Game (Python + Pygame)

A modern, customizable **N × N Snake Game** built using **Python** and **Pygame**, featuring a clean UI, wrap-around movement, animations, score tracking, and a modular structure perfect for teamwork.

---

## 🚀 Features

### 🎮 Gameplay
- **Dynamic N × N Grid** (select grid size at start or via CLI)
- **Wrap-Around Walls** — snake appears on the opposite side instead of dying
- **Food-based Growth & Speed Increase**
- **Accurate Self-Collision Detection**
- **Smooth movement + responsive controls**

### 🖥 UI & Graphics
- Clean modern UI with gradient background
- Animated **Start Screen** with grid selector
- **HUD** showing Score, Highscore & Controls
- **Pause** screen (P), **Restart** (R)
- Toggle **Grid Lines** (G)

### 🧩 Team-Friendly Code
Modular structure allows multiple developers to work independently on:
- UI & Graphics
- Game Logic
- Controls & Input Systems
- Persistence (highscores/config)
- Animations, Sounds, Themes

### 💾 Persistence
- Highscore stored in `highscore.txt` automatically

---

## 📷 Screenshots
_Add gameplay screenshots here._

---

## 🛠️ Installation

### 1. Install Python
Ensure Python 3.9+ is installed:
```bash
python --version


pip install pygame


python snake_game.py


🎮 Controls
Key	Action
↑ ↓ ← →	Move snake
SPACE	Start game
ENTER	Start from start-screen
P	Pause / Resume
R	Restart
G	Toggle grid lines
Up/Down (Start screen)	Increase/Decrease grid size
