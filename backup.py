import pygame
from dock import Dock
from boat import Boat
from pirate import Pirate
from tent import Tent
from restuarant import Restaurant
from farm import Farm, FarmGroup
from cookhouse import Cookhouse
from map import TileKind, Map
from farmer import Farmer
from pygameFunctions import setAutoUpdate, updateDisplay
import time
from path import Path
from datetime import datetime, timedelta

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
islandWidth = 1600
islandHeight = 1200
island = pygame.Surface((islandWidth, islandHeight))
island.fill((0, 100, 0))
cameraX, cameraY = 0, 0
speed = 5

#speed settings
slow = 5
medium = 3
fast = 1

dayLength = slow
speedMultipliers = { slow: 1.0, medium: 2.0, fast: 4.0 } 
speedMultiplier = speedMultipliers[dayLength]
speedLabels = { slow: "Slow", medium: "Medium", fast: "Fast" }
# Speed settings positions
speedButtons = {
    "Slow": pygame.Rect(700, 10, 80, 30),
    "Medium": pygame.Rect(700, 50, 80, 30),
    "Fast": pygame.Rect(700, 90, 80, 30),
}

#date/time
currentDate = datetime(1500, 1, 1)
dayStartTime = time.time()

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Pirate Tycoon")

#colours
Blue = (0, 0, 255)
Green = (34, 139, 34)
White = (255, 255, 255)
Brown = (139, 69, 19)
Red = (255, 0, 0)

#Game Variables
gold = 100000
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
pirate = Pirate([800,20], 0) # Create a pirate at entrance
boatAndPirate = [(boat, pirate)]

#fonts
font = pygame.font.SysFont(None, 36)
dockFont = pygame.font.SysFont(None, 20)
populationFont = pygame.font.SysFont(None, 36)

#create menu
menuHeight = 100
menuPrices = {"small": 100, "medium": 500, "large": 700, "tent": 200, "restaurant": 500, "farm": 50, 'cookhouse': 100, 'path': 10,
              "farmer": 100}
menuItems = [
    {"item": 'small', "rect": pygame.Rect(10, screenHeight - menuHeight + 10, 40, 40), "dock": True},
    {"item": 'medium',"rect": pygame.Rect(70, screenHeight - menuHeight + 10, 40, 40), "dock": True},
    {"item": 'large', "rect": pygame.Rect(140, screenHeight - menuHeight + 10, 40, 40), "dock": True},
    {"item": 'tent',"rect": pygame.Rect(210, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'restaurant', "rect": pygame.Rect(280, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'farm', "rect": pygame.Rect(350, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'cookhouse', "rect": pygame.Rect(420, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'path', "rect": pygame.Rect(490, screenHeight - menuHeight + 10, 40, 40), "dock": False },
    {"item": 'farmer', "rect": pygame.Rect(560, screenHeight - menuHeight + 10, 40, 40), "dock": False }  
]



def handleMenuClicks(mouseX, mouseY, adjustedMouseX, adjustedMouseY, gold, noOfItems, selectedItem, menuItems, isDock, islandWidth, islandHeight, gridSize, dockBoats):
    # Check if the mouse is clicked on a menu item
    for label, rect in speedButtons.items():
        if rect.collidepoint(mouseX, mouseY):
            return gold, placedItems, selectedItem, isDock, noOfItems  # Skip item placement if inside speed button
        
    for item in menuItems:
        if item["rect"].collidepoint(mouseX, mouseY):
            selectedItem = item["item"]
            isDock = item["dock"]
            break
    if selectedItem and mouseY < 500:
        gridPosition = (adjustedMouseX // gridSize * gridSize, adjustedMouseY // gridSize * gridSize)

        if any(item["pos"] == gridPosition and item["item"] != "farmer" and selectedItem != "farmer" for item in placedItems):
            floatingTexts.append({
            "text": "Position occupied!",
            "x": adjustedMouseX,
            "y": adjustedMouseY,
            "expiration": time.time() + 1
            })
            return gold, placedItems, selectedItem, isDock, noOfItems
        
        if selectedItem == 'farmer':  # Farmer-specific placement logic
            if gridPosition not in pathGrid or not pathGrid.get(gridPosition, False):
                floatingTexts.append({
                    "text": "Farmers must be placed on paths!",
                    "x": adjustedMouseX,
                    "y": adjustedMouseY,
                    "expiration": time.time() + 1
                })
                return gold, placedItems, selectedItem, isDock, noOfItems

        if gold >= menuPrices[selectedItem]:
            noOfItems += 1
            currentTime = time.time()
            if isDock:
                if 0 <= adjustedMouseX < 20 and 0 <= adjustedMouseY <= islandHeight:
                    dock = Dock(selectedItem, [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "left")
                    dockBoats.append( (Boat( [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "left" ), dock))
                    placedItems.append(
                        {"item": dock, "pos": (adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize), "orientation": "left"})
                    floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                    gold -= menuPrices[selectedItem]
                    
                elif islandWidth - (20) < adjustedMouseX < islandWidth and 0 < adjustedMouseY < islandHeight:
                    dock = Dock(selectedItem, [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "right")
                    dockBoats.append( (Boat( [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "right" ), dock))
                    placedItems.append(
                        {"item": dock, "pos": (adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize),
                         "orientation": "right"})
                    floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                    gold -= menuPrices[selectedItem]
                    
                elif 0 < adjustedMouseY < 20 and 0 <= adjustedMouseX <= islandWidth:
                    dock = Dock(selectedItem, [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "top")
                    dockBoats.append(( Boat( [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "top" ), dock))
                    placedItems.append(
                        {"item": dock, "pos": (adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize),
                         "orientation": "top"})
                    floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                    gold -= menuPrices[selectedItem]
                    
                elif islandHeight - 20 < adjustedMouseY < islandHeight and 100 < mouseX < islandWidth - 100:
                    dock = Dock(selectedItem, [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "bottom")
                    dockBoats.append( (Boat( [adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize], "bottom" ), dock))
                    placedItems.append({"item": dock, "pos": (adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize), "orientation": "bottom"})
                    floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                    gold -= menuPrices[selectedItem]
                    
            else:
                if 0 <= adjustedMouseX <= islandWidth and 0 <= adjustedMouseY <= islandHeight:
                    gold -= menuPrices[selectedItem]
                    if selectedItem == 'tent':
                        SelectedItem = Tent([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize])
                    if selectedItem == 'restaurant':
                        SelectedItem = Restaurant([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize])
                    if selectedItem == 'farm':
                        SelectedItem = Farm([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize])
                        groupFarms(SelectedItem, farmGroups)
                    if selectedItem == 'cookhouse':
                        SelectedItem = Cookhouse([adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize])
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
                        print(SelectedItem.role)
                    placedItems.append(
                        {"item": SelectedItem, "pos": (adjustedMouseX//gridSize * gridSize, adjustedMouseY//gridSize * gridSize), "orientation": "normal"})
                    floatingTexts.append({"text": f"-{menuPrices[selectedItem]}$", "x": adjustedMouseX, "y": adjustedMouseY, "expiration": currentTime + 1})
                    
    return gold, placedItems, selectedItem, isDock, noOfItems

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
    for pirate,boat in boatAndPirate:
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

        if dock:
            drawDock(cameraX, cameraY, dock, orientation, scaledX, scaledY, zoomLevel, item)
        else:
            if isinstance(item["item"], Farmer):
                pass
            else:
                object = item["item"]

                scaledObject = pygame.transform.scale(object.image,
                                                    (int(object.image.get_width() * zoomLevel),
                                                    int(object.image.get_height() * zoomLevel)))

                objectRect = scaledObject.get_rect(topleft=(scaledX + cameraX, scaledY + cameraY))
                screen.blit(scaledObject, objectRect)

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

def drawBoats(screen, cameraX, cameraY):
    for boat, dock in dockBoats:
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
            boat.speed = (distance / (dock.returnFrequency*100))   # speed to complete the round trip in the returnFrequency time 
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

def drawStats(gold, population, White):
    # Display gold
    goldText = font.render(f"Gold: {gold}", True, White)
    screen.blit(goldText, (10, 10))

    # Display population count
    populationText = populationFont.render(f"Population: {population}", True, White)
    screen.blit(populationText, (10, 50))  # Adjust y-position as needed

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


def spawnBoat(noOfItems, boatAndPirate, population, cameraX, cameraY):
    if noOfItems > 4:
        newBoat = Boat([800, -1100], "none")
        newPirate = Pirate([800, 20], 0)
        boatAndPirate.append((newBoat, newPirate))
        noOfItems = 0

    # Move the boat towards the entrance dock
    for boat, pirate in boatAndPirate:
        boat.moveTowards((800, 20))
        if boat.active:
            boat.draw(screen, cameraX, cameraY)

        # Check if the boat reaches the entrance dock, activate the pirate
        if not boat.active and not pirate.active:
            pirate.active = True
            pirate.position = list(boat.position)
            population += 1

        if boat.active:
            boatRect = (boat.position[0] + cameraX, boat.position[1] + cameraY, 30, 10)
            pygame.draw.rect(screen, Red, boatRect)

    return noOfItems, boatAndPirate, population

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

def piratePayment(pirate, gold, objectType, object, speedMultiplier):
    currentTime = time.time()
    payment = pirate.update(objectType, object, speedMultiplier)
    if payment > 0:
        gold += payment
        floatingTexts.append({"text": f"+ {payment}$", "x": object.position[0], "y": object.position[1], "expiration": currentTime + 1})
    return gold, boatAndPirate


def updatePirates(boatAndPirate, placedItems, gold, speedMutiplier):
    for boat, pirate in boatAndPirate:
        closestObjectLocation, objectType, boatAndPirate, object = findClosestObject(placedItems, pirate)

        if closestObjectLocation and not pirate.inCooldown:
            pirate.nearObject = True
            pirate.moveTowards(closestObjectLocation)
        else:
            pirate.nearObject = False
        gold, boatAndPirate = piratePayment(pirate, gold, objectType, object, speedMultiplier)
        pirate.draw(screen, cameraX, cameraY, zoomLevel)
    return gold, boatAndPirate

def toggleUpgradeBox(placedItems, adjustedMouseX, adjustedMouseY, gold, zoomLevel, cameraX, cameraY):
    for items in placedItems:
        if isinstance(items["item"], Dock):
            dock = items["item"]
            if dock.rect.collidepoint(adjustedMouseX, adjustedMouseY):
                dock.toggleUpgrade((adjustedMouseX, adjustedMouseY))
            gold = dock.upgradeBoxClicked((adjustedMouseX, adjustedMouseY), gold)
        elif isinstance(items["item"], Tent):
            tent = items["item"]
            if tent.rect.collidepoint(adjustedMouseX, adjustedMouseY):
                tent.toggleUpgrade([adjustedMouseX, adjustedMouseY])
            gold = tent.upgradeBoxClicked((adjustedMouseX, adjustedMouseY), gold)
    return gold

def drawUpgradeBox(placedItems, cameraX, cameraY, zoomLevel):
    for items in placedItems:
        if isinstance(items["item"], Dock):
            dock = items["item"]
            dock.drawUpgrade(screen, cameraX, cameraY, zoomLevel)
        elif isinstance(items["item"], Tent):
            tent = items["item"]
            tent.drawUpgrade(screen, cameraX, cameraY, zoomLevel)

def drawBattleButton(screen):
    buttonRect = pygame.Rect(700, 10, 90, 40)  # Adjust position and size
    font = pygame.font.Font(None, 36)

    # Draw the button
    pygame.draw.rect(screen, (200, 0, 0), buttonRect)
    text = font.render("Battle!", True, (255, 255, 255))
    screen.blit(text, (buttonRect.x + 10, buttonRect.y + 5))

    return buttonRect

def battleButtonClicked(battleButton, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mousePos = pygame.mouse.get_pos()
        if battleButton.collidepoint(mousePos):
            return True
    return False

def battleScrren(screen):
    screen.fill((0, 0, 255))

def spawnPlayerShip(screen):
    ship = Boat((400,100), "none")
    ship.drawBattleShip(screen)
    return ship

def movePlayerShip(ship, screen):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ship.move(-ship.speed, 0)
        ship.orientation = "movingLeft"
    elif keys[pygame.K_RIGHT]:
        ship.move(ship.speed, 0)
        ship.orientation = "movingRight"
    elif keys[pygame.K_UP]:
        ship.move(0, -ship.speed)
        ship.orientation = "movingUp"
    elif keys[pygame.K_DOWN]:
        ship.move(0, ship.speed)
        ship.orientation = "movingDown"
    ship.drawBattleShip(screen)

def playerShoots():
    pass

def handleZoom(event, zoomLevel):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:  # Scroll up
            zoomLevel = min(maxZoom, zoomLevel + zoomStep)
        elif event.button == 5:  # Scroll down
            zoomLevel = max(minZoom, zoomLevel - zoomStep)
    return zoomLevel

def adjustMouseCoordinates(mouseX, mouseY, cameraX, cameraY, zoomLevel):
    # Adjust mouse coordinates for zoom level
    adjustedMouseX = (mouseX - cameraX) / zoomLevel
    adjustedMouseY = (mouseY - cameraY) / zoomLevel
    return adjustedMouseX, adjustedMouseY

def drawMouse(screen, gridSize, cameraX, cameraY):
    mouseX, mouseY = pygame.mouse.get_pos()
    adjustedMouseX = mouseX - cameraX
    adjustedMouseY = mouseY - cameraY
    posX = adjustedMouseX//gridSize * gridSize 
    posY = adjustedMouseY//gridSize * gridSize 
    screenX = posX + cameraX
    screenY = posY + cameraY
    rect = pygame.Rect(screenX, screenY, gridSize, gridSize)
    pygame.draw.rect(screen, (0, 0, 0), rect, width=2) 

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
                                minDistance = distance

                    if closestFarm and not farmer.isAtFarm(closestFarm):
                        farmer.moveTowards(closestFarm, pathGrid)
                    elif closestFarm:
                        # Get crops from the farm group
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
                            if distance < minDistance and farmer.hasAPath(cookhouse, pathGrid):
                                closestCookhouse = cookhouse
                                minDistance = distance
                    if closestCookhouse and not farmer.isAtCookhouse(closestCookhouse):
                    
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
 
               
run = True
while run:
    #Handle inputs
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

            gold, placedItems, selectedItem, isDock, noOfItems = handleMenuClicks(mouseX, mouseY, adjustedMouseX,
                                        adjustedMouseY, gold, noOfItems, selectedItem, menuItems, isDock, islandWidth, islandHeight, gridSize, dockBoats)

            gold = toggleUpgradeBox(placedItems, adjustedMouseX, adjustedMouseY, gold, zoomLevel, cameraX, cameraY)    
    keys = pygame.key.get_pressed()
    cameraX, cameraY = cameraMovement(keys, cameraX, cameraY, speed)

    screen.fill(Blue)
    drawIsland(cameraX, cameraY, dockWidth, dockHeight, White)  
    noOfItems, boatAndPirate, population = spawnBoat(noOfItems, boatAndPirate, population, cameraX, cameraY) #moves boat towards entrance
    drawPlacedItems(placedItems, cameraX, cameraY, zoomLevel)
    showFloatingTexts(screen, floatingTexts, cameraX, cameraY, font)
    increaseCropCount(speedMultiplier)
    updateFoodCount()
    moveFarmer(placedItems, pathGrid, screen, cameraX, cameraY)
    gold = generateGoldAtDock(placedItems, gold, cameraX, cameraY, floatingTexts, screen, speedMultiplier)
    boatsAtDock(dockBoats, timer)
    drawBoats(screen, cameraX, cameraY)
    gold, boatAndPirate = updatePirates(boatAndPirate, placedItems, gold, speedMultiplier) #updates pirates movements and payments when interacting with palcedItems
    drawUpgradeBox(placedItems, cameraX, cameraY, zoomLevel) #when upgrade box is clicked shows it above item 
    drawMenuItems(menuItems)
    updateDate()
    displayDate(screen, font)
    displayTimeSpeedSettings()
    updateSpeeds(boatAndPirate, placedItems, speedMultiplier)
    drawStats(gold, population, White)
    drawMouse(screen, gridSize, cameraX, cameraY)
    pygame.display.update()
    timer.tick(fps)
    

pygame.quit()
