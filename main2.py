import pygame
import random
from dock import Dock
from boat import Boat
from pirate import Pirate
from tent import Tent
from restuarant import Restaurant
from farm import Farm, FarmGroup
from cookhouse import Cookhouse
from map import TileKind, Map
from farmer import Farmer
import time
from path import Path, Land
from datetime import datetime, timedelta
import math
from enemy import Enemy, EnemyCaptain
from watchTower import WatchTower
from perlin_noise import PerlinNoise
import numpy as np
from woodChopperHut import WoodChopperHut, WoodChopper
import json
import os
import sqlite3
from tiles import *
from world import *
from worldDrawer import *


def clearLeaderBoard():
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM leaderboard;")  # Delete all rows
    conn.commit()
    conn.close()
    
    print("Leaderboard data cleared!")

#clearLeaderBoard()

#Game Settings
pygame.init()


screenWidth = 800
screenHeight = 600
fps = 100
timer = pygame.time.Clock()
zoomLevel = 1.0
minZoom = 0.01
maxZoom = 2.0
zoomStep = 0.1
gridSize = 20

islandWidth = 600   #1600
islandHeight = 600  #1200
noiseScale = 100
seed = random.randint(0, 1000)
# Initialise Perlin noise generator
noise1 = PerlinNoise(octaves=4, seed=seed)
noise2 = PerlinNoise(octaves=8, seed=seed + 1)
islandSurface = pygame.Surface((islandWidth, islandHeight))

#island.fill((0, 100, 0))
cameraX, cameraY = 0, 0
speed = 5
battleMode = False
bullets_group = pygame.sprite.Group()  # Group to manage bullets
playerBullets = pygame.sprite.Group()
enemyBullets = pygame.sprite.Group()
activeDisaster = None

#speed settings
slow = 60
medium = 45
fast = 30

#stats button
buttonRect = pygame.Rect(200, 10, 60, 40)  # Button position and size (x, y, width, height)
showStatsMenu = False  # Track if the stats menu should be displayed

dayLength = slow
speedMultipliers = { slow: 1.0, medium: 1.5, fast: 2.0} 
speedMultiplier = speedMultipliers[dayLength]
speedLabels = { slow: "Slow", medium: "Medium", fast: "Fast" }
# Speed settings positions
speedButtons = {
    "Slow": pygame.Rect(700, 10, 80, 30),
    "Medium": pygame.Rect(700, 50, 80, 30),
    "Fast": pygame.Rect(700, 90, 80, 30),
}

lastAttackCheck = time.time()

#monthly stats
profitLog = {}
currentMonthIncome = 0
currentMonthExpenses = 0
currentMonthProfit = 0

#date/time
currentDate = datetime(1500, 1, 2)
dayStartTime = time.time()

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Pirate Tycoon")

#colours
Blue = (0, 0, 255)
Green = (34, 139, 34)
White = (255, 255, 255)
Brown = (139, 69, 19)
Red = (255, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)
grey = (128, 128, 128)

#Game Variables
gold = 999999
wood = 0

population = 0
noOfItems = 0
placedItems = []
floatingTexts = []
dockBoats = []
farmGroups = []
pathGrid = {}
selectedItem = None
isDock = None
playerBoatSpawned = False
dockWidth, dockHeight = 100, 50
entranceDock = (islandWidth // 2 - dockWidth // 2, 0)

boat = Boat([800, -1100], "none")  # Create a boat starting from the ocean
boatAndPirate = [(boat, None)]

#enemies and enemy ships
enemyShips = pygame.sprite.Group()
enemyPirates = pygame.sprite.Group()
enemyAttack = False
enemiesArriving = True
shipAdded = False
piratesSpawned = False
piratesDefeated = True
piratesOnIsland = False

#fonts
font = pygame.font.SysFont(None, 36)
dockFont = pygame.font.SysFont(None, 20)
populationFont = pygame.font.SysFont(None, 36)

#create menu
menuHeight = 100
menuPrices = {"small": 1, "medium": 150000, "large": 500000, "tent": 300, "restaurant": 1000, "farm": 1000, 'cookhouse': 1000, 'path': 10,
              "farmer": 1000, "watchTower": 10000, "land": 100, "woodChopperHut": 1000} #costs 500
menuItems = [
    {"item": 'small', "rect": pygame.Rect(10, screenHeight - menuHeight + 10, 40, 40), "dock": True},
    {"item": 'medium',"rect": pygame.Rect(70, screenHeight - menuHeight + 10, 40, 40), "dock": True},
    {"item": 'large', "rect": pygame.Rect(130, screenHeight - menuHeight + 10, 40, 40), "dock": True},
    {"item": 'tent',"rect": pygame.Rect(190, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'restaurant', "rect": pygame.Rect(250, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'farm', "rect": pygame.Rect(310, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'cookhouse', "rect": pygame.Rect(370, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'path', "rect": pygame.Rect(430, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'farmer', "rect": pygame.Rect(490, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'watchTower', "rect": pygame.Rect(550, screenHeight - menuHeight + 10, 40, 40), "dock": False },  
    {"item": 'land', "rect": pygame.Rect(610, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'woodChopperHut', "rect": pygame.Rect(670, screenHeight - menuHeight + 10, 40, 40), "dock": False },
]

def generateTrees(landPositions, numTrees):
    treePositions = set()
    while len(treePositions) < numTrees:
        treePos = random.choice(landPositions)  # Pick a random land tile
        treePositions.add(treePos)
    return list(treePositions)  # Convert to list before returning

ISLAND_SIZE = 300  # Base square size
EDGE_VARIATION = 20  # How much edges can extend/shrink
GREEN = (0, 100, 0)
SAND = (194, 178, 128)  # Sand
islandArea = 5000


def generateWorld(weights, randomSeed = random.randint(1, 100)):
    worldDrawer = WorldDrawer()
    world = World(WORLD_X, WORLD_Y, randomSeed)
    tile_map = world.get_tiled_map(weights)
    return worldDrawer, tile_map, world

weights = [20, 40, 70, 100, 250, 0, 0]
world_drawer, tile_map, wolrd = generateWorld(weights)
water = world_drawer.tilesheet.subsurface((208, 176, TILESIZE, TILESIZE))
background = pygame.Surface(screen.get_size())
# Tile the water texture across the background surface
for y in range(0, WINDOW_HEIGHT, TILESIZE):
    for x in range(0, WINDOW_WIDTH, TILESIZE):
        background.blit(water, (x, y))
landPositions = world_drawer.draw_tiles(tile_map, cameraX, cameraY)
print(landPositions)
print(len(landPositions))
for x in range(len(landPositions)):
    landPositions[x] = (landPositions[x][0]//20 * 20, landPositions[x][1]//20 * 20)
lastGoldReductionTime = time.time()
#print(landPositions)

numTrees = 15
treePositions = generateTrees(landPositions, numTrees)
print("trees")

def updateExpenses(amount):
    global currentMonthExpenses
    currentMonthExpenses += amount

def updateIncome(amount):
    global currentMonthIncome
    currentMonthIncome += amount

def updateDateAndProfit():
    global currentDate, currentMonthIncome, currentMonthExpenses, currentMonthProfit, profitLog
    currentMonthProfit = currentMonthIncome - currentMonthExpenses

    # Create the key for the current month
    currentMonthKey = f"{currentDate.year}-{currentDate.month:02d}"

    # Initialize the month's profit list if not already present
    if currentMonthKey not in profitLog:
        profitLog[currentMonthKey] = {
            "income": 0,  # Start with 0 income for the current month
            "expenses": 0,  # Start with 0 expenses for the current month
            "profit": [],
        }

    # Add today's profit to the daily profit list
    if currentDate.day - 1 < len(profitLog[currentMonthKey]["profit"]):
        # If the day already exists in the list, update it
        profitLog[currentMonthKey]["profit"][currentDate.day - 1] = currentMonthProfit
    else:
        # Append today's profit if it's a new entry
        profitLog[currentMonthKey]["profit"].append(currentMonthProfit)

    # Update income and expenses for the current day
    profitLog[currentMonthKey]["income"] = currentMonthIncome
    profitLog[currentMonthKey]["expenses"] = currentMonthExpenses

    # Check if it's the start of a new month
    if currentDate.day == 1:  # Assuming the start of a new month
        # Determine the previous month and year
        previousMonth = currentDate.month - 1
        year = currentDate.year
        if previousMonth == 0:  # If current month is January, go to December of the previous year
            previousMonth = 12
            year -= 1

        # Generate the key for the previous month
        previousMonthKey = f"{year}-{previousMonth:02d}"

        # Ensure data exists for the previous month in the log
        if previousMonthKey in profitLog:
            # Calculate total profit for the previous month
            profitLog[previousMonthKey]["income"] = profitLog[previousMonthKey]["income"]
            profitLog[previousMonthKey]["expenses"] = profitLog[previousMonthKey]["expenses"]
            profitLog[previousMonthKey]["profit"] = profitLog[previousMonthKey]["profit"]

        else:
            # Handle case where previous month's data is missing
            profitLog[previousMonthKey] = {
                "income": 0,
                "expenses": 0,
                "profit": []
            }

        # Reset data for the new month
        currentMonthIncome = 0
        currentMonthExpenses = 0
        currentMonthProfit = 0

def isBlockedByDock(gridPosition, placedItems, landPositions, gridSize=20):
    for dock in placedItems:
        if isinstance(dock["item"], Dock):
            dockX, dockY = int(dock["pos"][0]), int(dock["pos"][1])
            landX, landY = int(gridPosition[0]), int(gridPosition[1])   

            # Check if on the same vertical axis (x-axis)
            if dockX == landX:
                # Ensure there's land in between
                if any((dockX, y) in landPositions for y in range(min(dockY, landY) + gridSize, max(dockY, landY), gridSize)):
                    continue  # Land in between, allow placement
                return True  # No land in between, block placement

            # Check if on the same horizontal axis (y-axis)
            if dockY == landY:
                # Ensure there's land in between
                if any((x, dockY) in landPositions for x in range(min(dockX, landX) + gridSize, max(dockX, landX), gridSize)):
                    continue  # Land in between, allow placement
                return True  # No land in between, block placement

    return False  # Placement allowed

def canPlaceDock(gridPosition, landPositions, orientation, gridSize=20, maxDistance=100):
    """ 
    Checks if a dock can be placed by ensuring there is no land in front along its path.
    
    Args:
        gridPosition (tuple): The (x, y) position where the dock is being placed.
        landPositions (set): A set of land positions.
        orientation (str): The dock's orientation ('left', 'right', 'top', 'bottom').
        gridSize (int): Grid size for alignment (default 20).
        maxDistance (int): The maximum distance to check for land in front (default 100).

    Returns:
        bool: True if the dock can be placed, False if land is blocking.
    """
    x, y = gridPosition

    # Determine direction based on orientation
    direction = {
        "left": (-gridSize, 0),
        "right": (gridSize, 0),
        "top": (0, -gridSize),
        "bottom": (0, gridSize),
    }[orientation]

    # Check all tiles in front of the dock up to maxDistance
    for i in range(gridSize, maxDistance + gridSize, gridSize):
        check_x = x + direction[0] * (i // gridSize)
        check_y = y + direction[1] * (i // gridSize)

        if (check_x, check_y) in landPositions:  # If land is found anywhere in front
            return False  

    return True  # Dock placement is valid if no land is in front
            

def handleMenuClicks(mouseX, mouseY, adjustedMouseX, adjustedMouseY, gold, noOfItems, selectedItem, menuItems, isDock, islandWidth, islandHeight, gridSize, dockBoats, landPositions, wood):
    # Check if the mouse is clicked on a menu item
    for label, rect in speedButtons.items():
        if rect.collidepoint(mouseX, mouseY):
            return gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood  # Skip item placement if inside speed button
        
    for item in menuItems:
        if item["rect"].collidepoint(mouseX, mouseY):
            selectedItem = item["item"]
            isDock = item["dock"]
            break
    if selectedItem and mouseY < 500:
        gridPosition = (adjustedMouseX // gridSize * gridSize, adjustedMouseY // gridSize * gridSize)

        gridPositionCenter = (
            (adjustedMouseX // gridSize * gridSize) + gridSize // 2,
            (adjustedMouseY // gridSize * gridSize) + gridSize // 2
        )

        if any(item["pos"] == gridPosition for item in placedItems):
            if selectedItem == 'land' and any(item["orientation"] == "land" for item in placedItems if item["pos"] == gridPosition):
                # Prevent placing land on top of land
                floatingTexts.append({
                    "text": "Position occupied!",
                    "x": adjustedMouseX,
                    "y": adjustedMouseY,
                    "expiration": time.time() + 1
                })
                return gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood

            elif selectedItem != "farmer" and any(item["orientation"] != "land" for item in placedItems if item["pos"] == gridPosition):
                # Prevent placing objects on objects (except land)
                floatingTexts.append({
                    "text": "Position occupied!",
                    "x": adjustedMouseX,
                    "y": adjustedMouseY,
                    "expiration": time.time() + 1
                })
                return gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood
            
        
        if selectedItem == 'farmer':  # Farmer-specific placement logic
            if gridPositionCenter not in pathGrid or not pathGrid.get(gridPosition, False):
                floatingTexts.append({
                    "text": "Farmers must be placed on paths!",
                    "x": adjustedMouseX,
                    "y": adjustedMouseY,
                    "expiration": time.time() + 1
                })
                return gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood
        
        # Updated land placement check
        if gold >= menuPrices[selectedItem] and selectedItem == "land" and gridPosition not in landPositions:
            if not isBlockedByDock(gridPosition, placedItems, landPositions):
                currentTime = time.time()
                landPositions.append((adjustedMouseX // gridSize * gridSize, adjustedMouseY // gridSize * gridSize))
                SelectedItem = Land([adjustedMouseX // gridSize * gridSize, adjustedMouseY // gridSize * gridSize])
                gold -= menuPrices[selectedItem]
                placedItems.append(
                    {"item": SelectedItem, "pos": (adjustedMouseX // gridSize * gridSize, adjustedMouseY // gridSize * gridSize), "orientation": "land"})
                floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                return gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood
        
        if gridPosition in treePositions:
            print("cant place on trees")
            return gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood
        
        else:
            if gold >= menuPrices[selectedItem]:
                currentTime = time.time()
                if isDock:
                    if selectedItem == 'small':
                        woodCost = 0 #costs 1
                    elif selectedItem == 'medium':
                        woodCost = 2
                    elif selectedItem == 'large':
                        woodCost = 3
                    if wood >= woodCost:
                        wood -= woodCost
                        x, y = gridPosition

                        if (x - gridSize, y) not in landPositions and gridPosition in landPositions and canPlaceDock(gridPosition, landPositions, "left"):
                            dock = Dock(selectedItem, [x, y], "left", menuPrices[selectedItem])
                            dockBoats.append((Boat([x, y], "left"), dock))
                            placedItems.append({"item": dock, "pos": (x, y), "orientation": "left"})
                            floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                            gold -= menuPrices[selectedItem]
                            noOfItems += 1
                            updateExpenses(menuPrices[selectedItem])
                        
                        elif (x + gridSize, y) not in landPositions and gridPosition in landPositions and canPlaceDock(gridPosition, landPositions, "right"):
                            dock = Dock(selectedItem, [x, y], "right", menuPrices[selectedItem])
                            dockBoats.append((Boat([x, y], "right"), dock))
                            placedItems.append({"item": dock, "pos": (x, y), "orientation": "right"})
                            floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                            gold -= menuPrices[selectedItem]
                            noOfItems += 1
                            updateExpenses(menuPrices[selectedItem])

                        elif (x, y - gridSize) not in landPositions and gridPosition in landPositions and canPlaceDock(gridPosition, landPositions, "top"):
                            dock = Dock(selectedItem, [x, y], "top", menuPrices[selectedItem])
                            dockBoats.append((Boat([x, y], "top"), dock))
                            placedItems.append({"item": dock, "pos": (x, y), "orientation": "top"})
                            floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                            gold -= menuPrices[selectedItem]
                            noOfItems += 1
                            updateExpenses(menuPrices[selectedItem])

                        elif (x, y + gridSize) not in landPositions and gridPosition in landPositions and canPlaceDock(gridPosition, landPositions, "bottom"):
                            dock = Dock(selectedItem, [x, y], "bottom", menuPrices[selectedItem])
                            dockBoats.append((Boat([x, y], "bottom"), dock))
                            placedItems.append({"item": dock, "pos": (x, y), "orientation": "bottom"})
                            floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                            gold -= menuPrices[selectedItem]
                            noOfItems += 1
                            updateExpenses(menuPrices[selectedItem])
                    else:
                        print("Not enough wood")
                else:
                    if gridPosition in landPositions and selectedItem != "land":
                        gold -= menuPrices[selectedItem]
                        updateExpenses(menuPrices[selectedItem])
                        if selectedItem == 'tent':
                            SelectedItem = Tent([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], menuPrices[selectedItem])
                            noOfItems += 1
                        if selectedItem == 'restaurant':
                            SelectedItem = Restaurant([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], menuPrices[selectedItem])
                            noOfItems += 1
                        if selectedItem == 'farm':
                            SelectedItem = Farm([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], menuPrices[selectedItem])
                            groupFarms(SelectedItem, farmGroups)
                            menuPrices["farm"] += 50000
                        if selectedItem == 'cookhouse':
                            SelectedItem = Cookhouse([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], menuPrices[selectedItem])
                        if selectedItem == 'path':
                            SelectedItem = Path([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize])
                            for i in range(SelectedItem.rect.x, SelectedItem.rect.x + 21):
                                    for j in range(SelectedItem.rect.y,SelectedItem.rect.y + 21):
                                        pathGrid[(i, j)] = True
                            for i in range(SelectedItem.rect.y, SelectedItem.rect.y + 21):
                                for j in range(SelectedItem.rect.x, SelectedItem.rect.x+ 21):
                                    pathGrid[(j, i)] = True
                        if selectedItem == 'farmer':
                            gridX = adjustedMouseX // gridSize * gridSize
                            gridY = adjustedMouseY // gridSize * gridSize
                            centerX = gridX + gridSize // 2
                            centerY = gridY + gridSize // 2
                            SelectedItem = Farmer([centerX, centerY])
                            SelectedItem.assignFarmerRole(pathGrid, placedItems)
                            menuPrices["farmer"] += 50000
                        if selectedItem == 'watchTower':
                            SelectedItem = WatchTower([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], menuPrices[selectedItem])
                        if selectedItem == 'woodChopperHut':
                            SelectedItem = WoodChopperHut([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], menuPrices[selectedItem], treePositions)
                        placedItems.append(
                            {"item": SelectedItem, "pos": (adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize), "orientation": "normal"})
                        floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
    return gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood

def drawStatsButton():
    # Draw the button
    pygame.draw.rect(screen, (200, 0, 0), buttonRect)  # Red button
    font = pygame.font.Font(None, 24)
    button_text = font.render("Stats", True, (255, 255, 255))
    screen.blit(button_text, (buttonRect.x + 10, buttonRect.y + 10))

def ToggleStatsDisplay(mouseX, mouseY, showStatsMenu):
    if buttonRect.collidepoint(mouseX, mouseY):
            showStatsMenu = not showStatsMenu  # Toggle the stats menu
    return showStatsMenu

def drawStatsDisplay(showStatsMenu, profitLog, currentMonthIncome, currentMonthExpenses, currentMonthProfit, currentDate):
    if showStatsMenu:
        statsMenuRect = pygame.Rect(100, 50, 600, 400)
        pygame.draw.rect(screen, (0, 0, 0), statsMenuRect)  # Black box
        pygame.draw.rect(screen, (255, 255, 255), statsMenuRect, 2)  # White border

        # Fonts and colors
        font = pygame.font.Font(None, 36)
        white = (255, 255, 255)
        gray = (200, 200, 200)
        green = (0, 255, 0)

        # Calculate the previous month and year
        previousMonth = currentDate.month - 1
        year = currentDate.year
        if previousMonth == 0:  # If the current month is January
            previousMonth = 12
            year -= 1

        # Previous month stats
        monthKey = f"{year}-{previousMonth:02d}"
        previousStats = profitLog.get(monthKey, {"income": 0, "expenses": 0, "profit": [0] * 30})
        prevIncome = previousStats.get("income", 0)
        prevExpenses = previousStats.get("expenses", 0)
        previousProfitHistory = previousStats.get("profit", [0] * 30)
        previousProfit = previousProfitHistory[-1] if previousProfitHistory else 0

        # Current month stats
        currentMonthKey = f"{currentDate.year}-{currentDate.month:02d}"
        currentStats = profitLog.get(currentMonthKey, {"profit": [0] * 30})
        currentProfitHistory = currentStats.get("profit", [0] * 30)

        # Display headers
        headerText = font.render("Monthly Stats", True, white)
        screen.blit(headerText, (statsMenuRect.x + 200, statsMenuRect.y + 10))

        # Left side: Previous month
        prevHeaderText = font.render("Previous Month", True, white)
        screen.blit(prevHeaderText, (statsMenuRect.x + 50, statsMenuRect.y + 50))
        prevIncomeText = font.render(f"Income: {prevIncome}", True, white)
        screen.blit(prevIncomeText, (statsMenuRect.x + 50, statsMenuRect.y + 100))
        prevExpensesText = font.render(f"Expenses: {prevExpenses}", True, white)
        screen.blit(prevExpensesText, (statsMenuRect.x + 50, statsMenuRect.y + 150))
        prevProfitText = font.render(f"Profit: {previousProfit}", True, white)
        screen.blit(prevProfitText, (statsMenuRect.x + 50, statsMenuRect.y + 200))

        # Right side: Current month
        currHeaderText = font.render("Current Month", True, white)
        screen.blit(currHeaderText, (statsMenuRect.x + 350, statsMenuRect.y + 50))
        currIncomeText = font.render(f"Income: {currentMonthIncome}", True, white)
        screen.blit(currIncomeText, (statsMenuRect.x + 350, statsMenuRect.y + 100))
        currExpensesText = font.render(f"Expenses: {currentMonthExpenses}", True, white)
        screen.blit(currExpensesText, (statsMenuRect.x + 350, statsMenuRect.y + 150))
        currProfitText = font.render(f"Profit: {currentMonthProfit}", True, white)
        screen.blit(currProfitText, (statsMenuRect.x + 350, statsMenuRect.y + 200))

        # Draw graphs
        graphWidth = 250
        graphHeight = 150
        graphX = statsMenuRect.x + 50
        graphY = statsMenuRect.y + 250

        def drawGraph(profitHistory, x, y, width, height, label):
            pygame.draw.rect(screen, gray, (x, y, width, height), 2)  # Graph border
            if len(profitHistory) > 1:
                maxProfit = max(max(profitHistory), 1)  # Avoid division by zero
                minProfit = min(min(profitHistory), 0)
                profitRange = maxProfit - minProfit or 1
                points = []
                for i, profit in enumerate(profitHistory):
                    px = x + int(i / (len(profitHistory) - 1) * (width - 10)) + 5
                    py = y + height - int((profit - minProfit) / profitRange * (height - 10)) - 5
                    points.append((px, py))
                pygame.draw.lines(screen, green, False, points, 2)

            labelText = font.render(label, True, white)
            screen.blit(labelText, (x + 10, y - 30))

        drawGraph(previousProfitHistory, graphX, graphY, graphWidth, graphHeight, "Prev Month Profit")
        drawGraph(currentProfitHistory, graphX + 300, graphY, graphWidth, graphHeight, "Curr Month Profit")

def displayTimeSpeedSettings():
    for label, rect in speedButtons.items():
        # Draw button background
        pygame.draw.rect(screen, Green if speedLabels[dayLength] == label else Brown, rect)
        # Render the text
        textSurface = font.render(label, True, White)
        textRect = textSurface.get_rect(center=rect.center)
        screen.blit(textSurface, textRect)

def handleSpeedButtonClick(mouseX, mouseY):
    global dayLength
    global speedMultiplier
    global speedMultipliers
    for label, rect in speedButtons.items():
        if rect.collidepoint(mouseX, mouseY):
            # Update the timespeed based on the clicked button
            if label == "Slow":
                dayLength = slow
                speedMultiplier = speedMultipliers[dayLength]
            elif label == "Medium":
                dayLength = medium
                speedMultiplier = speedMultipliers[dayLength]
            elif label == "Fast":
                dayLength = fast
                speedMultiplier = speedMultipliers[dayLength]
            break

def updateDate():
    global currentDate, dayStartTime
    currentTime = time.time()
    elapsedTime = currentTime - dayStartTime

    if elapsedTime >= dayLength:
        currentDate += timedelta(days=1)
        dayStartTime = currentTime

def displayDate(screen, font):
    dateText = currentDate.strftime("%B %d, %Y")
    dateSurface = font.render(dateText, True, White)
    screen.blit(dateSurface, (300, 10))

def showFloatingTexts(screen, floatingTexts, cameraX, cameraY, font):
    currentTime = time.time()   
    for text in floatingTexts[:]:  # Iterate over a copy
        if text["expiration"] > currentTime:
            textSurface = font.render(text["text"], True, Red)
            screen.blit(textSurface, (text["x"] + cameraX, text["y"] + cameraY))
        else:
            floatingTexts.remove(text)  # Remove expired texts

def updateSpeeds(boatAndPirate, placedItems, speedMultiplier):
    for boat,pirate in boatAndPirate:
        if pirate is not None:
            pirate.speed =  pirate.baseSpeed * speedMultiplier 
        boat.speed = boat.baseSpeed * speedMultiplier
    for farmer in placedItems:
        if isinstance(farmer["item"], Farmer):
            farmer = farmer["item"]
            farmer.speed = farmer.baseSpeed * speedMultiplier
        
    
def cameraMovement(keys, cameraX, cameraY, speed):
    if keys[pygame.K_LEFT]:
        cameraX += speed
    if keys[pygame.K_RIGHT]:
        cameraX -= speed
    if keys[pygame.K_UP]:
        cameraY += speed
    if keys[pygame.K_DOWN]:
        cameraY -= speed
    return cameraX, cameraY

def drawPlacedItems(placedItems, cameraX, cameraY, zoomLevel):
    for item in placedItems:
        dock = item["item"] if isinstance(item["item"], Dock) else None
        x, y = item["pos"]
        orientation = item["orientation"]

        scaledX = x * zoomLevel
        scaledY = y * zoomLevel

        object = item["item"]
        if isinstance(object, Land):
            pass
        else:
            if object.health <= 0:
                placedItems.remove(item)
        object.draw(screen, cameraX, cameraY)       

def drawDock(cameraX, cameraY, dock, orientation, scaledX, scaledY, zoomLevel, item):
    object = item["item"]

    # Scale dock image based on zoom 
    scaledImage = pygame.transform.scale(object.image,
                                         (int(object.image.get_width() * zoomLevel),
                                          int(object.image.get_height() * zoomLevel)))
  
    # Adjust position of rotated image based on zoom
    rotatedRect = scaledImage.get_rect(topleft=(scaledX + cameraX, scaledY + cameraY))
    screen.blit(scaledImage, rotatedRect)

    scaledFontSize = int(20 * zoomLevel)
    dynamicFont = pygame.font.SysFont(None, scaledFontSize)

    dockLabel = dynamicFont.render(dock.size.capitalize(), True, White)
    labelRect = dockLabel.get_rect(center=rotatedRect.center)
    screen.blit(dockLabel, labelRect)

def generateGoldAtDock(placedItems, gold, cameraX, cameraY, floatingTexts, screen, speedMultiplier):
    currentTime = time.time()
    for item in placedItems:
        dock = item["item"] if isinstance(item["item"], Dock) else None
        if dock:
            if dock.isTimeForReturn(speedMultiplier):
                gold += dock.goldRate
                updateIncome(dock.goldRate)
                dockX, dockY = item["pos"]
                floatingTexts.append({
                    "text": f"+{dock.goldRate}$",
                    "x": dockX,
                    "y": dockY - 20,
                    "expiration": (currentTime + 0.5)  # 3 seconds from now
                })
        # Render floating texts
        for text in floatingTexts[:]:  # Iterate over a copy to safely modify the list
            if text["expiration"] > currentTime:
                textSurface = font.render(text["text"], True, (255, 255, 0))
                screen.blit(textSurface, (text["x"] + cameraX , text["y"] + cameraY))
            else:
                floatingTexts.remove(text)  # Remove expired messages
    return gold

def drawBoats(screen, cameraX, cameraY, placedItems):
    for boat, dock in dockBoats:
        if any(dock is item_dict["item"] for item_dict in placedItems):  # Check if dock exists in any dict inside placedItems
            boat.draw(screen, cameraX, cameraY)
    for boat in enemyShips:
        boat.draw(screen, cameraX, cameraY)

def boatsAtDock(dockBoats, clock):
    fps = clock.get_fps()

    for boat, dock in dockBoats:
        if boat.dockType == "left":
            targetPos = (dock.position[0] - 1000, dock.position[1])
            originalPos = (dock.position[0], dock.position[1])
        elif boat.dockType == "right":
            targetPos = (dock.position[0] + 1000, dock.position[1])
            originalPos = (dock.position[0], dock.position[1])
        elif boat.dockType == "bottom":
            targetPos = (dock.position[0], dock.position[1] + 1000)
            originalPos = (dock.position[0], dock.position[1])
        elif boat.dockType == "top":
            targetPos = (dock.position[0], dock.position[1] - 1000) 
            originalPos = (dock.position[0], dock.position[1])

            if not boat.speedSet:
                distance = 1000 * 2
        if not boat.speedSet:
            distance = 1000 * 2  # total round-trip distance (to and from the target)
            boat.speed = 1 
            boat.speedSet = True
        
        # Check current movement direction
        if not boat.returning:
            if not boat.isAtTarget(targetPos):
                boat.moveTowards(targetPos)
            else:
                # Switch to returning mode when target is reached
                boat.returning = True
                boat.active = True  
        # If the boat is returning to the original position
        if boat.returning:
            if not boat.isAtTarget(originalPos):
                boat.moveTowards(originalPos)
            else:
                # Reset to move towards the target position again
                boat.returning = False
                boat.active = True  # Ensure active for the next journey

def drawMenuItems(menuItems):
    pygame.draw.rect(screen, (200, 200, 200), (0, screenHeight - menuHeight, screenWidth, menuHeight))
    for item in menuItems:
        pygame.draw.rect(screen, Brown, item["rect"])
        menuLabel = dockFont.render(item["item"].capitalize(), True, White)
        menuLabelRect = menuLabel.get_rect(center=(item["rect"].centerx, item["rect"].top - 10))
        screen.blit(menuLabel, menuLabelRect)
        priceLabel = dockFont.render(f"${menuPrices[item['item']]}", True, White)
        priceLabelRect = priceLabel.get_rect(center=(item["rect"].centerx, item["rect"].top + 10))
        screen.blit(priceLabel, priceLabelRect)
        if item["dock"] == True:
            if item["item"] == "small":
                woodText = dockFont.render(f"Wood: {1}", True, White)
            elif item["item"] == "medium":
                woodText = dockFont.render(f"Wood: {2}", True, White)
            elif item["item"] == "large":
                woodText = dockFont.render(f"Wood: {3}", True, White)
            woodTextRect = woodText.get_rect(center=(item["rect"].centerx, item["rect"].top + 30))
            screen.blit(woodText, woodTextRect)

def drawStats(gold, population, White):
    # Display gold
    goldText = font.render(f"Gold: {gold}", True, White)
    screen.blit(goldText, (10, 10))

    woodText = font.render(f"Wood: {wood}", True, White)
    screen.blit(woodText, (10, 30))  # Positioned below gold

    # Display population count
    populationText = populationFont.render(f"Population: {population}", True, White)
    screen.blit(populationText, (10, 50))  # Adjust y-position as needed

    enemiesText = font.render(f"Enemies: {len(enemyPirates)}", True, White)
    screen.blit(enemiesText, (10, 90))

def drawIsland(cameraX, cameraY, dockWidth, dockHeight, White):
    # Scale island surface based on zoom level
    scaledIsland = pygame.transform.scale(island,(int(islandWidth * zoomLevel), int(islandHeight * zoomLevel)))

    # Draw ocean and island
    screen.fill(Blue)
    screen.blit(scaledIsland, (cameraX, cameraY))

    # Draw the entrance dock at the top
    entranceDockX = entranceDock[0] * zoomLevel + cameraX
    entranceDockY = entranceDock[1] * zoomLevel + cameraY
    pygame.draw.rect(screen, Brown,
                     pygame.Rect(entranceDockX, entranceDockY, dockWidth * zoomLevel, dockHeight * zoomLevel))
    entranceLabel = dockFont.render("Entrance", True, White)
    labelRect = entranceLabel.get_rect(
        center=(entranceDockX + (dockWidth * zoomLevel) / 2, entranceDockY + (dockHeight * zoomLevel) / 2))
    screen.blit(entranceLabel, labelRect)


def spawnBoat(noOfItems, boatAndPirate, population, cameraX, cameraY, enemiesArriving, enemyAttack, piratesSpawned):
    if noOfItems > 4:
        newBoat = Boat([800, -1100], "none")
        boatAndPirate.append((newBoat, None))
        noOfItems = 0

      # Move the boat towards the entrance dock
    for i, (boat, pirate) in enumerate(boatAndPirate):
        boat.updateSpeed(speedMultiplier)
        boat.moveTowards((800, 20))
        if boat.active:
            boat.draw(screen, cameraX, cameraY)

        # Spawn the pirate only when the boat is no longer active
        if not boat.active and pirate is None: 
            newPirate = Pirate((810,30), 0)
            newPirate.active = True
            newPirate.hunger = 100
            newPirate.sleep = 100
            boatAndPirate[i] = (boat, newPirate)  # Update tuple with the new pirate
            population += 1

        if boat.active:
            boatRect = (boat.position[0] + cameraX, boat.position[1] + cameraY, 30, 10)
            pygame.draw.rect(screen, Red, boatRect)

    if enemyAttack:
        for boat in enemyShips:
            boat.updateSpeed(speedMultiplier)
            boat.moveTowards((800, 760))
            if boat.active:
                boat.draw(screen, cameraX, cameraY)
                boatRect = (boat.position[0] + cameraX, boat.position[1] + cameraY, 30, 10)
                pygame.draw.rect(screen, Red, boatRect)
            else:
                enemyShips.remove(boat)
                piratesSpawned = True

    return noOfItems, boatAndPirate, population, enemiesArriving, enemyAttack, piratesSpawned

def findClosestObject(placedItems, pirate):
    closestObjectLocation = None
    objectType = ""
    minDistance = 200
    object = None
    for item in placedItems:
        if not isinstance(item["item"], Dock) and not isinstance(item["item"], Farmer) and not isinstance(item["item"], Path) and not isinstance(item["item"], Farm) and not isinstance(item["item"], Cookhouse):
            itemX, itemY = item["pos"]
            distance = ((pirate.position[0] - itemX) ** 2 + (pirate.position[1] - itemY) ** 2) ** 0.5
            # Check if the tent is within the 200-pixel range
            if distance < minDistance:
                minDistance = distance
                closestObjectLocation = (itemX, itemY)
                if item["item"].label == "Tent":
                    object = item["item"]
                    objectType = item["item"].label
                elif item["item"].label == "Restaurant":
                    object = item["item"]
                    objectType = item["item"].label
    return closestObjectLocation, objectType, boatAndPirate, object

def findNearestItem():
    pass

def piratePayment(pirate, gold,speedMultiplier, landPositions, treePositions):
    currentTime = time.time()
    payment = pirate.update(speedMultiplier, placedItems, landPositions, treePositions)
    if payment > 0:
        gold += payment
        updateIncome(payment)
        floatingTexts.append({"text": f"+ {payment}$", "x": pirate.position[0], "y": pirate.position[1], "expiration": currentTime + 1})
    return gold, boatAndPirate

def checkSatisfaction(boatAndPirate, population, gold, floatingTexts):
    for boat, pirate in boatAndPirate:
        if pirate is not None:
            if pirate.hunger <= 0 or pirate.sleep <= 0:
                boatAndPirate.remove((boat, pirate))
                population -= 1
                gold -= 100
                floatingTexts.append({"text": "-100$", "x": pirate.position[0], "y": pirate.position[1], "expiration": time.time() + 1})
                updateExpenses(100)
    return population, gold, boatAndPirate, floatingTexts

def updatePirates(boatAndPirate, placedItems, gold, speedMutiplier, population, floatingTexts, enemyAttack, piratesOnIsland, landPositions, treePositions):
    for boat,pirate in boatAndPirate:
        if pirate is not None:
            if pirate.health <= 0:
                boatAndPirate.remove((boat, pirate))
                population -= 1
                gold -= 100
                floatingTexts.append({"text": "-100$", "x": pirate.position[0], "y": pirate.position[1], "expiration": time.time() + 1})
                updateExpenses(100)

    for boat, pirate in boatAndPirate:
        if pirate is not None:
            pirate.draw(screen, cameraX, cameraY, zoomLevel)
            pirate.findEnemies(enemyPirates)
            population, gold, boatAndPirate, floatingTexts = checkSatisfaction(boatAndPirate, population, gold, floatingTexts)
            pirate.updateSpeed(speedMultiplier)
            if pirate.enemy is not None:
                if pirate.isAtObject([pirate.enemy.rect.x, pirate.enemy.rect.y]):
                    pirate.attack()
                else:
                    pirate.moveTowards([pirate.enemy.rect.x, pirate.enemy.rect.y], landPositions, treePositions)
            else:
                gold, boatAndPirate  = piratePayment(pirate, gold, speedMultiplier, landPositions, treePositions)
        
    for enemy in enemyPirates:
        if enemy.health <= 0:
            if enemy.foundTarget:
                enemy.target.beingAttacked = False
            enemyPirates.remove(enemy)
            
    for enemy in enemyPirates:
        enemy.draw(screen, cameraX, cameraY)
        if not enemy.foundTarget:
            enemy.findClosestObject(placedItems)
            if not enemy.foundTarget:
                enemy.findClosestPirate(boatAndPirate)
            enemy.moveAround(landPositions, treePositions)
        elif enemy.atTarget():
            enemy.attack()
        elif enemy.foundTarget:
            enemy.moveTowards(landPositions, treePositions)
    
    if len(enemyPirates) == 0 and piratesOnIsland:
        enemyAttack = False
        piratesOnIsland = False
            
    return gold, boatAndPirate, population, floatingTexts, enemyAttack, piratesOnIsland

def toggleUpgradeBox(placedItems, adjustedMouseX, adjustedMouseY, gold, zoomLevel, cameraX, cameraY, selectedItem):
    for items in placedItems:
        if isinstance(items["item"], Dock):
            dock = items["item"]
            if dock.rect.collidepoint(adjustedMouseX, adjustedMouseY):
                selectedItem = None
                dock.toggleUpgrade((adjustedMouseX, adjustedMouseY))
            gold = dock.upgradePressed((adjustedMouseX, adjustedMouseY), gold, cameraX, cameraY, placedItems)  
        elif not isinstance(items["item"], Farmer) and not isinstance(items["item"], Path) and not isinstance(items["item"], Land) and not isinstance(items["item"], Farm):
            item = items["item"]
            if item.rect.collidepoint(adjustedMouseX, adjustedMouseY):
                item.toggleUpgrade((adjustedMouseX, adjustedMouseY))
                selectedItem = None
            gold = item.upgradePressed((adjustedMouseX, adjustedMouseY), gold, cameraX, cameraY, placedItems)
    return gold, selectedItem

def drawUpgradeBox(placedItems, cameraX, cameraY, zoomLevel):
    for items in placedItems:
        if isinstance(items["item"], Dock):
            dock = items["item"]
            dock.drawUpgrade(screen, cameraX, cameraY, zoomLevel)
        elif not isinstance(items["item"], Farmer) and not isinstance(items["item"], Path) and not isinstance(items["item"], Land) and not isinstance(items["item"], Farm):
            item = items["item"]
            item.drawUpgrade(screen, cameraX, cameraY, zoomLevel)

def adjustMouseCoordinates(mouseX, mouseY, cameraX, cameraY, zoomLevel):
    # Adjust mouse coordinates for zoom level
    adjustedMouseX = (mouseX - cameraX) / zoomLevel
    adjustedMouseY = (mouseY - cameraY) / zoomLevel
    return adjustedMouseX, adjustedMouseY

def drawMouse(screen, gridSize, cameraX, cameraY, destroyingMode):
    mouseX, mouseY = pygame.mouse.get_pos()
    adjustedMouseX = mouseX - cameraX
    adjustedMouseY = mouseY - cameraY
    posX = adjustedMouseX//gridSize * gridSize 
    posY = adjustedMouseY//gridSize * gridSize 
    screenX = posX + cameraX
    screenY = posY + cameraY
    rect = pygame.Rect(screenX, screenY, gridSize, gridSize)
    pygame.draw.rect(screen, (0, 0, 0), rect, width=2) 

    # If destroyingMode is active, draw a cross inside the box
    if destroyingMode:
        cross_color = (255, 0, 0)  # Red cross
        pygame.draw.line(screen, cross_color, (screenX, screenY), (screenX + gridSize, screenY + gridSize), 3)  # Diagonal \
        pygame.draw.line(screen, cross_color, (screenX, screenY + gridSize), (screenX + gridSize, screenY), 3)  # Diagonal /

def increaseCropCount(speedMultiplier):
    for group in farmGroups:
        group.generateCrops(speedMultiplier)  # Generate crops for the group
        group.drawCropCount(screen, font, cameraX, cameraY)  # Display crop count

def groupFarms(farm, farmGroups):
    connectedGroups = []

    # Find all groups connected to the newly added farm
    for group in farmGroups:
        if any(areAdjacent(farm, otherFarm) for otherFarm in group.farms):
            connectedGroups.append(group)

    if connectedGroups:
        # Merge all connected groups into a single group
        primaryGroup = connectedGroups[0]
        for group in connectedGroups[1:]:
            for otherFarm in group.farms:
                primaryGroup.addFarm(otherFarm)
            farmGroups.remove(group)  # Remove merged group from the list
        primaryGroup.addFarm(farm)
    else:
        # Create a new group if no connections found
        newGroup = FarmGroup()
        newGroup.addFarm(farm)
        farmGroups.append(newGroup)
     # Debug: Print coordinates of farms in groups
    #for group in farmGroups:
     #   print("Farm Group Coordinates:", group.getCoordinates())


def mergeGroups(targetGroup, farmGroups):
    # Merge all overlapping groups into the target group
    for group in farmGroups[:]:  # Use a copy of the list to modify while iterating
        if group != targetGroup and any(
            areAdjacent(farm1, farm2) for farm1 in targetGroup.farms for farm2 in group.farms
        ):
            # Merge farms from this group into the target group
            for farm in group.farms:
                targetGroup.addFarm(farm)
            farmGroups.remove(group)  # Remove the merged group

def areAdjacent(farm1, farm2):
    # Define adjacency as within 50 pixels (or any suitable distance)
    distanceX = abs(farm1.rect.centerx - farm2.rect.centerx)
    distanceY = abs(farm1.rect.centery - farm2.rect.centery)
    return distanceX <= 20 and distanceY <= 20

def updateFoodCount():
    for item in placedItems:
        if isinstance(item["item"], Cookhouse):
            item["item"].drawFoodCount(screen, cameraX, cameraY)
        if isinstance(item["item"], Restaurant):
            item["item"].drawFoodCount(screen, cameraX, cameraY)



def moveFarmer(placedItems, pathGrid, screen, cameraX, cameraY):
    for item in placedItems:
        if isinstance(item["item"], Farmer):
            farmer = item["item"]

            if farmer.role == 'farmToCookhouse':
                # Determine the farmer's current state and set the target accordingly
                if not farmer.carryingCrops:  # Move to farm first if not carrying crops
                    closestFarm = None
                    minDistance = float('inf')
                    for farm in placedItems:
                        if isinstance(farm["item"], Farm):
                            farm = farm["item"]
                            distance = farmer.calculateDistance(farm)
                            if distance < minDistance and farmer.hasAPath(farm, pathGrid):
                                closestFarm = farm
                                minDistance = distance    #finds closest farm

                    if closestFarm and not farmer.isAtFarm(closestFarm):  #moves towards the closest farm
                        farmer.moveTowards(closestFarm, pathGrid)
                    elif closestFarm:                     # Get crops from the farm group
                        for group in farmGroups:
                            if closestFarm in group.farms:
                                farmer.getCrops(group)
                                break
                else:  # If carrying crops, move to the cookhouse
                    closestCookhouse = None
                    minDistance = float('inf')
                    for cookHouse in placedItems:
                        if isinstance(cookHouse["item"], Cookhouse):
                            cookhouse = cookHouse["item"]
                            distance = farmer.calculateDistance(cookhouse)
                            if distance < minDistance and farmer.hasAPath(cookhouse, pathGrid): #finds closest cookhouse
                                closestCookhouse = cookhouse
                                minDistance = distance
                    if closestCookhouse and not farmer.isAtCookhouse(closestCookhouse): #moves towards the closest cookhouse                   
                        farmer.moveTowards(closestCookhouse, pathGrid)               
                    elif closestCookhouse:
                        farmer.dropCrops(closestCookhouse)  # Drop off crops
                        farmer.carryingCrops = False  # Reset carrying state
            else:
                if not farmer.carryingFood:
                    closestCookhouse = None
                    minDistance = float('inf')
                    for cookHouse in placedItems:
                        if isinstance(cookHouse["item"], Cookhouse):
                            cookhouse = cookHouse["item"]
                            distance = farmer.calculateDistance(cookhouse)
                            if distance < minDistance and farmer.hasAPath(cookhouse, pathGrid):
                                closestCookhouse = cookhouse
                                minDistance = distance
                    if closestCookhouse and not farmer.isAtCookhouse(closestCookhouse):
                        farmer.moveTowards(closestCookhouse, pathGrid)
                    elif closestCookhouse:
                        farmer.getFood(closestCookhouse)
                        farmer.carryingFood = True
                else:
                    closestRestaurant = None
                    minDistance = float('inf')
                    for restaurant in placedItems:
                        if isinstance(restaurant["item"], Restaurant):
                            restaurant = restaurant["item"]
                            distance = farmer.calculateDistance(restaurant)
                            if distance < minDistance and farmer.hasAPath(restaurant, pathGrid):
                                closestRestaurant = restaurant
                                minDistance = distance

                    if closestRestaurant and not farmer.isAtPlace(closestRestaurant):
                        farmer.moveTowards(closestRestaurant, pathGrid)
                    elif closestRestaurant:
                        farmer.dropFood(closestRestaurant) 
                        farmer.carryingFood = False
           
            farmer.draw(screen, cameraX, cameraY)

def enemyArriveAtIsland(enemyShips, shipAdded, enemyAttack):
    if enemyAttack and not shipAdded:
        enemyShip = Boat((800, 1200), "none")
        enemyShips.add(enemyShip)
        shipAdded = True
    return enemyAttack, shipAdded

def enemyPiratesSpawn(enemyGroup, position, enemyAttack, piratesSpawned, piratesOnIsland, gold):
    if 0 < gold < 350000:
        noOfPirates = 5
        noOfCaptains = 1
    elif 350000 < gold < 1000000:
        noOfPirates = 8
        noOfCaptains = 2
    elif gold >= 1000000:
        noOfPirates = 15 
        noOfCaptains = 3
    if enemyAttack and piratesSpawned:
        for i in range(noOfPirates):
            enemyPirate = Enemy(position)
            enemyGroup.add(enemyPirate)
        for j in range(noOfCaptains):
            enemyCaptain = EnemyCaptain(position)
            enemyGroup.add(enemyCaptain)
        piratesSpawned = False
        piratesOnIsland = True
       # enemyAttack = False
    return enemyAttack, piratesSpawned, piratesOnIsland

def watchTowerShoot(placedItems, enemyPirates):
    for watchTower in placedItems:
        if isinstance(watchTower["item"], WatchTower):
            watchTower = watchTower["item"]              
            watchTower.findClosestEnemy(enemyPirates)
            if watchTower.enemy:
                watchTower.shoot()
                watchTower.drawCannonBalls(screen, cameraX, cameraY)

def randomPirateAttack(gold, lastAttackCheck, enemyAttack):
    currentTime = time.time()
    if currentTime - lastAttackCheck >= 240:  # Check every 60 seconds
        lastAttackCheck = time.time()  # Reset timer
        probabilityOfAttack = min(1.0, 0.5 + gold/200000)
        if random.random() < probabilityOfAttack and not enemyAttack:
            return True, lastAttackCheck
        else:
            return False, lastAttackCheck
    else:
        return False, lastAttackCheck

def triggerNaturalDisaster(landPositions, radius=200, warningTime=3):
    """Selects a random land position and starts a disaster countdown."""
    # Select a random land tile
    disasterX, disasterY = random.choice(landPositions)
    
    return {
        "x": disasterX,
        "y": disasterY,
        "radius": radius,
        "startTime": time.time(),
        "warningTime": warningTime,
        "hitsRemaining": int(3),
        "strikeTime": time.time() + 1
    }

def drawDisasterWarning(screen, cameraX, cameraY, disaster):
    """Draws a warning circle where the disaster will strike."""
    if disaster:
        elapsed = time.time() - disaster["startTime"]
        if elapsed < disaster["warningTime"]:
            # Convert to screen coordinates with camera movement
            screenX = int((disaster["x"] + cameraX))
            screenY = int((disaster["y"] + cameraY))
            adjustedRadius = int(disaster["radius"])

            # Grey transparent circle
            overlay = pygame.Surface((adjustedRadius * 2, adjustedRadius * 2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (100, 100, 100, 120), (adjustedRadius, adjustedRadius), adjustedRadius)
            screen.blit(overlay, (screenX - adjustedRadius, screenY - adjustedRadius))

def drawLightningStrike(screen, cameraX, cameraY, disaster):
    """Draws a lightning bolt at the disaster location when it strikes."""
    if disaster and "strikeTime" in disaster and time.time()  < disaster["strikeTime"]:
        screenX = int((disaster["x"] + cameraX))
        screenY = int((disaster["y"] + cameraY))

                # Lightning bolt shape (longer and more jagged)
        points = [
            (screenX, screenY - 100),  # Start higher up
            (screenX + 15, screenY - 75),
            (screenX - 10, screenY - 50),
            (screenX + 20, screenY - 25),
            (screenX - 15, screenY),
            (screenX + 25, screenY + 25),
            (screenX - 20, screenY + 50),
            (screenX + 10, screenY + 75),
            (screenX - 5, screenY + 100)  # Ends lower
        ]
        pygame.draw.polygon(screen, (255, 255, 0), points)  # Yellow lightning


def applyDisasterDamage(placedItems, boatAndPirate, disaster, damage=50):
    """Damages all items and pirates inside the disaster radius."""
    if not disaster:
        return placedItems, boatAndPirate  # No disaster active

    disasterX, disasterY, radius = disaster["x"], disaster["y"], disaster["radius"]
    
    # Damage buildings
    for item in placedItems:
        itemX, itemY = item["item"].position
        distance = math.sqrt((itemX - disasterX) ** 2 + (itemY - disasterY) ** 2)
        if distance <= radius:
            item["item"].showHealthBar = True
            item["item"].healthBarStartTime = time.time()
            item["item"].health -= damage

    # Damage pirates
    for boat, pirate in boatAndPirate:
        if pirate is not None:
            pirateX, pirateY = pirate.position
            distance = math.sqrt((pirateX - disasterX) ** 2 + (pirateY - disasterY) ** 2)
            if distance <= radius:
                pirate.showHealthBar = True
                pirate.healthBarStartTime = time.time()
                pirate.health -= damage

    return placedItems, boatAndPirate  # Return updated objects

nextStrikeTime = None
activeDisaster = None
nextDisasterTime = time.time() + random.randint(240, 360)  # Set time for first disaster

# Define button properties
pickaxeButtonRect = pygame.Rect(20, 100, 50, 50)  # x, y, width, height
destroyingMode = False  # Track if destroying mode is on

def drawPickaxeButton(screen):
    """Draws the pickaxe button on the left side of the screen."""
    pygame.draw.rect(screen, (150, 75, 0), pickaxeButtonRect)  # Brown button
    font = pygame.font.Font(None, 24)
    text = font.render("Pickaxe", True, (255, 255, 255))
    screen.blit(text, (pickaxeButtonRect.x + 10, pickaxeButtonRect.y + 10))

def handlePickaxeClicks():
    global destroyingMode
    if pickaxeButtonRect.collidepoint(event.pos):
        destroyingMode = not destroyingMode  # Toggle destroying mode

def removeFarmFromGroup(farm, farmGroups):
    for group in farmGroups:
        if farm in group.farms:
            group.removeFarm(farm)
            break  # Exit after removing the farm from the group

def drawTrees(screen, treePositions, cameraX, cameraY):
    treeColor = (139, 69, 19)  # Green color for trees
    treeImage = pygame.image.load(r"C:\Users\Study\Pirate Tycoon\images\grassv2.png")  # Load tree image
    treeImage = pygame.transform.scale(treeImage, (20, 20))  # Resize to 20x20 pixels
    for tree in treePositions:
         screen.blit(treeImage, (tree[0] + cameraX, tree[1] + cameraY))  # Draw the tree

def updateWoodChopperHuts(screen, cameraX, cameraY, placedItems):
    for woodChopperHuts in placedItems:
        if isinstance(woodChopperHuts["item"], WoodChopperHut):
            woodChopperHut = woodChopperHuts["item"]
            woodChopperHut.update()
            woodChopperHut.draw(screen, cameraX, cameraY)

def collectWood(adjustedMouseX, adjustedMouseY, placedItems, wood):
    for hut in placedItems:
        if isinstance(hut["item"], WoodChopperHut) and hut["item"].rect.collidepoint(adjustedMouseX, adjustedMouseY):
                print("Pressed")
                wood += hut["item"].woodCount
                hut["item"].woodCount = 0
    return wood

def growTrees(landPositions, treePositions, lastGrowTime):

    if time.time() - lastGrowTime > 5:  # Check every 5 seconds
        if len(treePositions) < 15:

            availablePositions = [pos for pos in landPositions if pos not in treePositions]

            if availablePositions:
                randomPos = random.choice(availablePositions)

                # Apply 10% chance of tree growth at this position
                if random.random() < 0.1:  # 10% chance of tree growth
                    treePositions.append(randomPos)
        lastGrowTime = time.time()

    return treePositions, lastGrowTime

lastGrowTime = time.time()  # Track last tree growth time

UserDataFile = "userData.json"

def loadUsers():
    if os.path.exists(UserDataFile):
        with open(UserDataFile, "r") as file:
            return json.load(file)
    return {}

def saveUsers(users):
    with open(UserDataFile, "w") as file:
        json.dump(users, file)

def registerUser(username, password):
    users = loadUsers()
    if username in users:
        return False, "User already exists!"
    users[username] = password
    saveUsers(users)
    return True, "Registration successful!"

def loginUser(username, password):
    users = loadUsers()
    if username in users and users[username] == password:
        return True, "Login successful!"
    return False, "Invalid username or password."

def loginMenu():
    while True:
        screen.fill((50, 50, 50))
        title = font.render("Press L to Login or R to Register", True, (255, 255, 255))
        screen.blit(title, (200, 250))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:  # Login
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    success, msg = loginUser(username, password)
                    print(msg)
                    if success:
                        return username
                
                elif event.key == pygame.K_r:  # Register
                    username = input("Enter new username: ")
                    password = input("Enter new password: ")
                    success, msg = registerUser(username, password)
                    print(msg)


conn = sqlite3.connect('leaderboard.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    completion_time REAL)''')

conn.commit()
conn.close()

#playerUsername = loginMenu()

def gameCompleteScreen(gold, gameComplete, startTime, playerUsername):
    if gold >= 1000000 and not gameComplete:
        gameComplete = True
        completionTime = time.time() - startTime

        # Save completion time to the database
        conn = sqlite3.connect("leaderboard.db")
        cursor = conn.cursor()

        # Check if the player already has a time recorded
        cursor.execute("SELECT completion_time FROM leaderboard WHERE username = ?", (playerUsername,))
        existing_time = cursor.fetchone()

        if existing_time:
            existing_time = existing_time[0]
            if completionTime < existing_time:  # Only update if the new time is shorter
                cursor.execute("UPDATE leaderboard SET completion_time = ? WHERE username = ?", 
                               (completionTime, playerUsername))
        else:
            cursor.execute("INSERT INTO leaderboard (username, completion_time) VALUES (?, ?)", 
                           (playerUsername, completionTime))

        conn.commit()
        conn.close()

        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 36)
        
        popup_active = True
        while popup_active:
            screen.fill((0, 0, 0))  # Background color

            # Retrieve the top 5 fastest completion times
            conn = sqlite3.connect("leaderboard.db")
            cursor = conn.cursor()
            cursor.execute("SELECT username, completion_time FROM leaderboard ORDER BY completion_time ASC LIMIT 5")
            top_times = cursor.fetchall()
            conn.close()

            leaderboard_height = 30 * len(top_times)  # Each entry takes 30px height
            popup_height = 250 + leaderboard_height  # Adjusting popup height

            popup_rect = pygame.Rect(100, 100, 570, popup_height)  # Adjust height dynamically
            pygame.draw.rect(screen, (255, 255, 255), popup_rect, border_radius=10)

            # Display message
            text = font.render("Congratulations! You have 1,000,000 coins!", True, (0, 0, 0))
            screen.blit(text, (120, 130))

            # Display completion time
            time_text = font.render(f"Time taken: {int(completionTime // 60)} min {int(completionTime % 60)} sec", True, (0, 0, 0))
            screen.blit(time_text, (120, 180))

            # Display leaderboard
            screen.blit(font.render("Leaderboard (Fastest times):", True, (0, 0, 0)), (120, 220))
            for i, (username, time_record) in enumerate(top_times):
                entry = font.render(f"{i+1}. {username}: {int(time_record // 60)} min {int(time_record % 60)} sec", True, (0, 0, 0))
                screen.blit(entry, (120, 250 + i * 30))

            # Position "Continue" button **below** leaderboard
            continue_y = 270 + leaderboard_height
            continue_button = pygame.draw.rect(screen, (0, 255, 0), (300, continue_y, 200, 50), border_radius=10)
            button_text = font.render("Continue", True, (0, 0, 0))
            screen.blit(button_text, (360, continue_y + 15))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if continue_button.collidepoint(x, y):  
                        popup_active = False  # Close the popup when clicked

    return gameComplete

temp = False

gameComplete = False
startTime = time.time()
run = True

while run:
    currentTime = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            adjustedIslandWidth = islandWidth * zoomLevel
            adjustedIslandHeight = islandHeight * zoomLevel

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                adjustedMouseX, adjustedMouseY = adjustMouseCoordinates(mouseX, mouseY, cameraX, cameraY, zoomLevel)
                print("mouse",adjustedMouseX, adjustedMouseY)
                handleSpeedButtonClick(mouseX, mouseY)
                handlePickaxeClicks()
                showStatsMenu = ToggleStatsDisplay(mouseX, mouseY, showStatsMenu)
                if not destroyingMode:
                    gold, placedItems, selectedItem, isDock, noOfItems, landPositions, wood = handleMenuClicks(mouseX, mouseY, adjustedMouseX,
                                                adjustedMouseY, gold, noOfItems, selectedItem, menuItems, isDock, islandWidth, islandHeight, gridSize, dockBoats, landPositions, wood)
                    gold, selectedItem = toggleUpgradeBox(placedItems, adjustedMouseX, adjustedMouseY, gold, zoomLevel, cameraX, cameraY, selectedItem)    
                    wood = collectWood(adjustedMouseX, adjustedMouseY, placedItems, wood)
                else:
                    for item in placedItems:
                        itemRect = item["item"].rect
                        if itemRect.collidepoint(adjustedMouseX, adjustedMouseY):  # Check if clicked
                            placedItems.remove(item)  # Remove the item if clicked
                            if isinstance(item["item"], Farm):  # Check if the item is a Farm
                                farm = item["item"]
                                # Remove the farm from its group
                                removeFarmFromGroup(farm, farmGroups)
                            if isinstance(item["item"], Path):
                                # Remove path from pathGrid by setting the relevant positions back to False
                                for i in range(item["item"].rect.x, item["item"].rect.x + 21):
                                    for j in range(item["item"].rect.y, item["item"].rect.y + 21):
                                        pathGrid[(i, j)] = False  # Mark the positions as no longer a path
                                for i in range(item["item"].rect.y, item["item"].rect.y + 21):
                                    for j in range(item["item"].rect.x, item["item"].rect.x + 21):
                                        pathGrid[(j, i)] = False  # Mark the positions as no longer a path
                                # Check and remove any farmers currently on the path
                                for farmer in placedItems[:]:
                                    if isinstance(farmer["item"], Farmer):  # Check if the item is a Farmer
                                        farmerPos = farmer["item"].position  # Get farmer position
                                        # Check if farmer's position is within the path grid positions
                                        for i in range(item["item"].rect.x, item["item"].rect.x + 21):
                                            for j in range(item["item"].rect.y, item["item"].rect.y + 21):
                                                if (i, j) == tuple(farmerPos):  # Farmer is on the path
                                                    placedItems.remove(farmer)  # Remove the farmer
                            break  # Exit after removing the item
    


    keys = pygame.key.get_pressed()
    cameraX, cameraY = cameraMovement(keys, cameraX, cameraY, speed)
 
    # Draw the island surface to the screen
    world_drawer.display_surface.blit(background, (0, 0))
   
    world_drawer.draw(tile_map, cameraX, cameraY, wait_for_key=False)
   
    drawTrees(screen, treePositions, cameraX, cameraY)  # Draw trees
    
    noOfItems, boatAndPirate, population, enemiesArriving, enemyAttack, piratesSpawned = spawnBoat(noOfItems, boatAndPirate, population, cameraX, cameraY, enemiesArriving, enemyAttack, piratesSpawned) #moves boat towards entrance
    drawPlacedItems(placedItems, cameraX, cameraY, zoomLevel)
    showFloatingTexts(screen, floatingTexts, cameraX, cameraY, font)
    increaseCropCount(speedMultiplier)
    updateFoodCount()
    moveFarmer(placedItems, pathGrid, screen, cameraX, cameraY)
    gold = generateGoldAtDock(placedItems, gold, cameraX, cameraY, floatingTexts, screen, speedMultiplier)
    boatsAtDock(dockBoats, timer)
    drawBoats(screen, cameraX, cameraY, placedItems)

    randomAttack, lastAttackCheck = randomPirateAttack(gold, lastAttackCheck, enemyAttack)
    if randomAttack: #enemy attack becomes false once they reach the island
        enemyAttack = True
        piratesSpawned = False
        shipAdded = False
        piratesDefeated = False
    if enemyAttack and piratesOnIsland:
        currentTime = time.time()
        if currentTime - lastGoldReductionTime >= 2:  # Check if 2 seconds passed
            lastGoldReductionTime = currentTime  # Reset timer
            gold -= 10
    enemyAttack, shipAdded = enemyArriveAtIsland(enemyShips, shipAdded, enemyAttack)
    enemyAttack, piratesSpawned, piratesOnIsland = enemyPiratesSpawn(enemyPirates,(810//20 * 20, 750// 20 * 20), enemyAttack, piratesSpawned, piratesOnIsland, gold)
    gold, boatAndPirate, population, floatingTexts, enemyAttack, piratesOnIsland = updatePirates(boatAndPirate, placedItems, gold, speedMultiplier, population, floatingTexts, enemyAttack, piratesOnIsland, landPositions, treePositions) #updates pirates movements and payments when interacting with palcedItems
    watchTowerShoot(placedItems, enemyPirates)

    updateWoodChopperHuts(screen, cameraX, cameraY, placedItems)

    if activeDisaster is None and currentTime >= nextDisasterTime:  # Check if it's time for a disaster
        activeDisaster = triggerNaturalDisaster(landPositions, radius=150)
        nextStrikeTime = activeDisaster["startTime"] + activeDisaster["warningTime"]  # Set first strike time

        # Schedule the next disaster (4 to 6 minutes later)
        nextDisasterTime = currentTime + random.randint(240, 360)
    
    # Draw warning circle before disaster hits
    drawDisasterWarning(screen, cameraX, cameraY, activeDisaster)
    

    # Apply damage after the warning time
    if activeDisaster and currentTime >= nextStrikeTime:
        if activeDisaster["hitsRemaining"] >= 1:

            activeDisaster["strikeTime"] = currentTime + 1

            drawLightningStrike(screen, cameraX, cameraY, activeDisaster)

            # Apply damage to items and pirates
            placedItems, boatAndPirate = applyDisasterDamage(placedItems, boatAndPirate, activeDisaster, damage=50)

            # Reduce the number of strikes left
            activeDisaster["hitsRemaining"] = activeDisaster["hitsRemaining"] - 1
            if activeDisaster["hitsRemaining"] > 0:
                activeDisaster["x"], activeDisaster["y"] = random.choice(landPositions)
                activeDisaster["startTime"] = time.time()
                # Set the time for the next strike
                nextStrikeTime = activeDisaster["startTime"] + activeDisaster["warningTime"]  # Next strike
        else:
            # Disaster is over
            activeDisaster = None  # Reset disaster
    
    treePositions, lastGrowTIme = growTrees(landPositions, treePositions, lastGrowTime)
    
    drawUpgradeBox(placedItems, cameraX, cameraY, zoomLevel) #when upgrade box is clicked shows it above item 
    drawMenuItems(menuItems)
    drawPickaxeButton(screen)
    updateDate()
    displayDate(screen, font)
    displayTimeSpeedSettings()
    updateSpeeds(boatAndPirate, placedItems, speedMultiplier)
    updateDateAndProfit()
    drawStats(gold, population, White)
    drawStatsButton()
    drawStatsDisplay(showStatsMenu, profitLog, currentMonthIncome, currentMonthExpenses, currentMonthProfit, currentDate)
    drawMouse(screen, gridSize, cameraX, cameraY, destroyingMode)
    #gameComplete = gameCompleteScreen(gold, gameComplete, startTime, playerUsername)

    pygame.display.update()
    timer.tick(fps)
    
pygame.quit()

