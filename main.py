import pygame
from Dock import Dock
from boat import Boat
from Pirate import Pirate
from tent import Tent
from restuarant import Restaurant

pygame.init()
screenWidth = 800
screenHeight = 600
fps = 60
timer = pygame.time.Clock()

Screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Pirate Tycoon")

Blue = (0, 0, 255)
Green = (34, 139, 34)
White = (255, 255, 255)
Brown = (139, 69, 19)
Red = (255, 0, 0)

islandWidth = 1600
islandHeight = 1200
island = pygame.Surface((islandWidth, islandHeight))
island.fill(Green)

cameraX, cameraY = 0, 0
speed = 5

gold = 1000
population = 0
noOfItems = 0

font = pygame.font.SysFont(None, 36)
dockFont = pygame.font.SysFont(None, 20)
populationFont = pygame.font.SysFont(None, 36)

menuHeight = 100
menuPrices = {"small": 100, "medium": 500, "large": 700, "tent": 200, "restaurant": 500}
menuItems = [
    {"item": 'small', "rect": pygame.Rect(10, screenHeight - menuHeight + 10, 80, 80), "dock": True},
    {"item": 'medium',"rect": pygame.Rect(100, screenHeight - menuHeight + 10, 80, 80), "dock": True},
    {"item": 'large', "rect": pygame.Rect(190, screenHeight - menuHeight + 10, 80, 80), "dock": True},
    {"item": 'tent',"rect": pygame.Rect(280, screenHeight - menuHeight + 10, 80, 80), "dock": False },
    {"item": 'restaurant', "rect": pygame.Rect(370, screenHeight - menuHeight + 10, 80, 80), "dock": False }
]

placedItems = []
selectedItem = None
isDock = None

dockWidth, dockHeight = 100, 50
entranceDock = (islandWidth // 2 - dockWidth // 2, 0)


boat = Boat([800, -1100])  # Create a boat starting from the ocean
pirate = Pirate([800,20], 0) # Create a pirate at entrance
boatAndPirate = [(boat, pirate)]

def handleMenuClicks(mouseX, mouseY, adjustedMouseX, adjustedMouseY, gold, noOfItems, selectedItem, menuItems, isDock):
    # Check if the mouse is clicked on a menu item
    for item in menuItems:
        if item["rect"].collidepoint(mouseX, mouseY):
            selectedItem = item["item"]
            isDock = item["dock"]
            break
    if selectedItem and mouseY < 500:
        if gold >= menuPrices[selectedItem]:
            noOfItems += 1
            if isDock:
                if -30 < adjustedMouseX < 40 and 0 <= adjustedMouseY <= islandHeight:
                    dock = Dock(selectedItem, [adjustedMouseX - dockWidth / 2, adjustedMouseY - dockHeight / 2])
                    placedItems.append(
                        {"item": dock, "pos": (adjustedMouseX - dockWidth / 2, adjustedMouseY), "orientation": "left"})
                    gold -= menuPrices[selectedItem]
                    selectedItem = None
                elif islandWidth - (40 - 1) < adjustedMouseX < islandWidth + (
                        40 - 1) and 0 < adjustedMouseY < islandHeight:
                    dock = Dock(selectedItem, [adjustedMouseX, adjustedMouseY])
                    placedItems.append(
                        {"item": dock, "pos": (adjustedMouseX - dockWidth / 2, adjustedMouseY - dockHeight / 2),
                         "orientation": "right"})
                    gold -= menuPrices[selectedItem]
                    selectedItem = None
                elif -40 < adjustedMouseY < 10 and 0 <= adjustedMouseX <= islandWidth:
                    dock = Dock(selectedItem, [adjustedMouseX, adjustedMouseY])
                    placedItems.append(
                        {"item": dock, "pos": (adjustedMouseX - dockWidth / 2, adjustedMouseY - dockHeight / 2),
                         "orientation": "top"})
                    gold -= menuPrices[selectedItem]
                    selectedItem = None
                elif islandHeight - 40 < adjustedMouseY < islandHeight + 40 and 100 < mouseX < islandWidth - 100:
                    dock = Dock(selectedItem, [adjustedMouseX, adjustedMouseY])
                    placedItems.append({"item": dock, "pos": (adjustedMouseX, adjustedMouseY), "orientation": "bottom"})
                    gold -= menuPrices[selectedItem]
                    selectedItem = None
            else:
                if 0 <= adjustedMouseX <= islandWidth and 0 <= adjustedMouseY <= islandHeight:
                    gold -= menuPrices[selectedItem]
                    if selectedItem == 'tent':
                        SelectedItem = Tent([adjustedMouseX, adjustedMouseY])
                    if selectedItem == 'restaurant':
                        SelectedItem = Restaurant([adjustedMouseX, adjustedMouseY])
                    placedItems.append(
                        {"item": SelectedItem, "pos": (adjustedMouseX, adjustedMouseY), "orientation": "normal"})
                    selectedItem = None
    return gold, placedItems, selectedItem, isDock, noOfItems

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

def drawPlacedItems(placedItems, cameraX, cameraY):
    for item in placedItems:
        dock = item["item"] if isinstance(item["item"], Dock) else None
        x, y = item["pos"]
        orientation = item["orientation"]
        if dock:
            drawDock(cameraX, cameraY, dock, orientation, x, y)
        else:
            object = item["item"]
            x, y = item["pos"]
            objectRect = object.image.get_rect(topleft=(x + cameraX, y + cameraY))
            Screen.blit(object.image, objectRect)
def drawDock(cameraX, cameraY, dock, orientation, x, y):
    dock.rect.topleft = (x, y)
    rotatedImage = dock.image
    if orientation == "right" or orientation == "left":
        rotatedImage = pygame.transform.rotate(dock.image, 0)  # No rotation needed here
    else:
        rotatedImage = pygame.transform.rotate(dock.image, 90)  # Rotate image
    rotatedRect = rotatedImage.get_rect(topleft=(x + cameraX, y + cameraY))
    Screen.blit(rotatedImage, rotatedRect)
    dockLabel = dockFont.render(dock.size.capitalize(), True, White)
    labelRect = dockLabel.get_rect(center=(x + cameraX + dock.rect.width // 2, y + cameraY + dock.rect.height // 2))
    Screen.blit(dockLabel, labelRect)

def generateGoldAtDock(placedItems, gold):
    for item in placedItems:
        dock = item["item"] if isinstance(item["item"], Dock) else None
        if dock:
            if dock.isTimeForReturn():
                gold += dock.goldRate
    return gold

def drawMenuItems(menuItems):
    pygame.draw.rect(Screen, (200, 200, 200), (0, screenHeight - menuHeight, screenWidth, menuHeight))
    for item in menuItems:
        pygame.draw.rect(Screen, Brown, item["rect"])
        menuLabel = dockFont.render(item["item"].capitalize(), True, White)
        menuLabelRect = menuLabel.get_rect(center=(item["rect"].centerx, item["rect"].top - 10))
        Screen.blit(menuLabel, menuLabelRect)
        priceLabel = dockFont.render(f"${menuPrices[item['item']]}", True, White)
        priceLabelRect = priceLabel.get_rect(center=(item["rect"].centerx, item["rect"].top + 10))
        Screen.blit(priceLabel, priceLabelRect)

def drawStats(gold, population, White):
    # Display gold
    goldText = font.render(f"Gold: {gold}", True, White)
    Screen.blit(goldText, (10, 10))

    # Display population count
    populationText = populationFont.render(f"Population: {population}", True, White)
    Screen.blit(populationText, (10, 50))  # Adjust y-position as needed

def drawIsland(cameraX, cameraY, dockWidth, dockHeight, White):
    # Draw ocean and island
    Screen.fill(Blue)
    Screen.blit(island, (cameraX, cameraY))
    # Draw the entrance dock at the top
    pygame.draw.rect(Screen, Brown,
                     pygame.Rect(entranceDock[0] + cameraX, entranceDock[1] + cameraY, dockWidth, dockHeight))
    entranceLabel = dockFont.render("Entrance", True, White)
    labelRect = entranceLabel.get_rect(
        center=(entranceDock[0] + cameraX + dockWidth // 2, entranceDock[1] + cameraY + dockHeight // 2))
    Screen.blit(entranceLabel, labelRect)

def spawnBoat(noOfItems, boatAndPirate, population, cameraX, cameraY):
    if noOfItems > 3:
        newBoat = Boat([800, -1100])
        newPirate = Pirate([800, 20], 0)
        boatAndPirate.append((newBoat, newPirate))
        noOfItems = 0
    # Move the boat towards the entrance dock
    for boat, pirate in boatAndPirate:
        boat.moveTowards((800, 20))
        if boat.active:
            boat.draw(Screen, cameraX, cameraY)

        # Check if the boat reaches the entrance dock, activate the pirate
        if not boat.active and not pirate.active:
            pirate.active = True
            pirate.position = list(boat.position)
            population += 1

        if boat.active:
            boatRect = (boat.position[0] + cameraX, boat.position[1] + cameraY, 30, 10)
            pygame.draw.rect(Screen, Red, boatRect)

    return noOfItems, boatAndPirate, population

def findClosestObject(placedItems, pirate):
    closestObjectLocation = None
    objectType = ""
    minDistance = 200
    object = None
    for item in placedItems:
        if not isinstance(item["item"], Dock):
            objectType = item["item"].label
            itemX, itemY = item["pos"]
            distance = ((pirate.position[0] - itemX) ** 2 + (pirate.position[1] - itemY) ** 2) ** 0.5
            # Check if the tent is within the 200-pixel range
            if distance < minDistance:
                minDistance = distance
                closestObjectLocation = (itemX, itemY)
                if objectType == "Tent":
                    object = item["item"]
                elif objectType == "Restaurant":
                    object = item["item"]
    return closestObjectLocation, objectType, boatAndPirate, object

def piratePayment(pirate, gold, objectType, object):
    payment = pirate.update(objectType)
    print(payment)
    if payment > 0:
        gold += payment
        if objectType == "Tent":
            pirate.sleep += object.sleepPoints
    return gold, boatAndPirate


def updatePirates(boatAndPirate, placedItems, gold):
    for boat, pirate in boatAndPirate:
        closestObjectLocation, objectType, boatAndPirate, object = findClosestObject(placedItems, pirate)

        if closestObjectLocation and not pirate.inCooldown:
            pirate.nearObject = True
            pirate.moveTowards(closestObjectLocation)
        else:
            pirate.nearObject = False
        gold, boatAndPirate = piratePayment(pirate, gold, objectType, object)
        pirate.draw(Screen, cameraX, cameraY)
    return gold, boatAndPirate

def toggleUpgradeBox(placedItems, adjustedMouseX, adjustedMouseY, gold):
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

def drawUpgradeBox(placedItems, cameraX, cameraY):
    for items in placedItems:
        if isinstance(items["item"], Dock):
            dock = items["item"]
            dock.drawUpgrade(Screen, cameraX, cameraY)
        elif isinstance(items["item"], Tent):
            tent = items["item"]
            tent.drawUpgrade(Screen, cameraX, cameraY)

run = True
while run:
    Screen.fill(Blue)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = event.pos
            adjustedMouseX = mouseX - cameraX
            adjustedMouseY = mouseY - cameraY

            gold, placedItems, selectedItem, isDock, noOfItems = handleMenuClicks(mouseX, mouseY, adjustedMouseX, adjustedMouseY, gold, noOfItems, selectedItem, menuItems, isDock)

            gold = toggleUpgradeBox(placedItems, adjustedMouseX, adjustedMouseY, gold)

    keys = pygame.key.get_pressed()
    cameraX, cameraY = cameraMovement(keys, cameraX, cameraY, speed)

    drawIsland(cameraX, cameraY, dockWidth, dockHeight, White)

    noOfItems, boatAndPirate, population = spawnBoat(noOfItems, boatAndPirate, population, cameraX, cameraY) #moves boat towards entrance

    gold, boatAndPirate = updatePirates(boatAndPirate, placedItems, gold) #updates pirates movements and payments when interacting with palcedItems

    drawPlacedItems(placedItems, cameraX, cameraY)
    gold = generateGoldAtDock(placedItems, gold)

    drawUpgradeBox(placedItems, cameraX, cameraY) #when upgrade box is clicked shows it above item

    drawMenuItems(menuItems)
    drawStats(gold, population, White)

    pygame.display.flip()
    timer.tick(fps)

pygame.quit()
