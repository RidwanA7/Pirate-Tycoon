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

```sh`
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

**Before launching:** the current checkout needs the module and asset fixes described below. Installing the dependencies alone is insufficient to run it.

After addressing those issues, launch the main game from the project directory:

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

## Known issues and local data

- **Module filename:** `main.py` imports `woodChopperHut`, but its source is named `woodChopperHut.pt`. Rename it to `woodChopperHut.py` so Python can import it.
- **Image paths:** image loading uses absolute Windows paths under `C:\Users\Study\...`, including `TILESHEETPATH` in `tiles.py`. Update these references to point to assets on your machine, preferably using paths relative to the project.
- **Missing images:** referenced assets absent from this checkout include `tree.png`, `captain.png`, `watchTower.png`, `woodChopper.png`, `woodChopperHut.png`, `1675450476_luffy-sprite.png`, and the boat sprite `d68usui-ef6c334e-11b7-4f75-88b9-ecd34c5d4bf0.png`. Supply these images or update the source to use suitable replacements.
- **Filename casing:** Git tracks both `Dock.py`/`dock.py` and `Pirate.py`/`pirate.py`. These names can conflict on filesystems that ignore case; the main script uses the lowercase imports.
- **Leaderboard initialization:** `main.py` opens `leaderboard.db` but does not create the `leaderboard` table before querying it. Initialize a table with `username` and `completion_time` columns before using the completion screen.
- **Local storage:** accounts are stored in `users.db`, and completion times use `leaderboard.db`, both relative to the working directory. The main script does not implement saving or restoring an island between sessions.
- **Tests:** there is no configured automated test suite. `test.py` references outdated names such as `World`, while `world.py` defines `TerrainGenerator`; it needs updating before use.
