# Pirate Tycoon

A desktop island management game built with Python and Pygame. Build a pirate settlement, manage gold and wood, keep your population fed, and defend against enemy raids. The goal is to reach **1,000,000 gold**, with completion times intended to appear on a local leaderboard.

## Features

- Procedural terrain generated with Perlin noise and rendered with a tile sheet.
- Docks, tents, farms, cookhouses, restaurants, paths, watchtowers, and woodchopper huts.
- Boats and arriving pirates, building upgrades, and resource collection.
- Farmers who transport crops and food along paths.
- Enemy pirates and captains, defensive towers, and lightning disasters.
- An in-game calendar and monthly income, expense, and profit statistics.
- Local account registration and login using SQLite and bcrypt password hashes.

## Requirements

- Python 3 with `pip` and `venv`.
- A desktop environment capable of opening a Pygame window.
- Python packages: `pygame`, `perlin-noise`, `numpy`, and `bcrypt`.

The repository does not currently pin dependency versions or specify a tested Python version.

## Setup

From the project directory, create a virtual environment:

```sh
python3 -m venv .venv
```

Activate it on macOS or Linux:

```sh
source .venv/bin/activate
```

Or on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```sh
python -m pip install pygame perlin-noise numpy bcrypt
```

Launch the main game from the project directory:

```sh
python main.py
```

Keep the terminal open: registration and login collect your username and password through terminal prompts.

## Controls

| Input | Action |
| --- | --- |
| `R` on the login screen | Register an account using the terminal prompts. |
| `L` on the login screen | Log in using the terminal prompts. |
| Arrow keys | Move the camera. |
| Click a bottom-menu item, then the map | Select and place a building, path, worker, or land tile, subject to placement and resource requirements. |
| Click a placed building | Open its upgrade controls where supported. |
| Click the stats button | Toggle the financial statistics display. |
| Click the pickaxe button, then a placed item | Toggle demolition mode and remove an item. |
| Close the window | Exit the game. |

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Main game loop, menus, economy, account handling, and completion screen. |
| `world.py`, `tiles.py`, `worldDrawer.py` | Terrain generation, tile definitions, and rendering. |
| `buildings.py` | Shared building behavior and upgrade controls. |
| `dock.py`, `boat.py`, `pirate.py` | Docks, boats, and pirate behavior. |
| `farm.py`, `farmer.py`, `cookhouse.py`, `restuarant.py` | Farming and food production. The restaurant module is spelled `restuarant.py` in the source. |
| `tent.py`, `path.py`, `watchTower.py` | Housing, paths and land, and defensive towers. |
| `enemy.py`, `enemyShips.py` | Enemy behavior and a separate enemy ship implementation. |
| `woodChopperHut.pt` | Python source for woodchoppers and their huts, currently saved with the wrong extension. |
| `main2.py`, `backup.py` | Alternative and backup game scripts. |
| `test.py` | A terrain demonstration that references an older world API. |
| `*.png`, `*.jpg` | Included image assets; additional referenced images are missing. |
