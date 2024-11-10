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
NoOfItems = 0

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

            # Check if the mouse is clicked on a menu item
            for item in menuItems:
                if item["rect"].collidepoint(mouseX, mouseY):
                    selectedItem = item["item"]
                    isDock = item["dock"]
                    break

            if selectedItem and mouseY < 500:
                if gold >= menuPrices[selectedItem]:
                    NoOfItems += 1
                    if isDock:
                        if -100 < adjustedMouseX < 100 and 0 <= adjustedMouseY <= islandHeight:
                            dock = Dock(selectedItem, [adjustedMouseX - dockWidth / 2, adjustedMouseY - dockHeight / 2])
                            placedItems.append(
                                {"item": dock, "pos": (adjustedMouseX - dockWidth/2, adjustedMouseY), "orientation": "left"})
                            gold -= menuPrices[selectedItem]
                            selectedItem = None
                        elif islandWidth - (dockWidth - 1) < adjustedMouseX < islandWidth + (dockWidth - 1) and 0 < adjustedMouseY < islandHeight:
                            dock = Dock(selectedItem, [adjustedMouseX, adjustedMouseY])
                            placedItems.append(
                                {"item": dock, "pos": (adjustedMouseX - dockWidth / 2, adjustedMouseY - dockHeight / 2), "orientation": "right"})
                            gold -= menuPrices[selectedItem]
                            selectedItem = None
                        elif -99 < adjustedMouseY < 99 and 0 <= adjustedMouseX <= islandWidth:
                            dock = Dock(selectedItem, [adjustedMouseX, adjustedMouseY])
                            placedItems.append({"item": dock, "pos": (adjustedMouseX - dockWidth / 2, adjustedMouseY - dockHeight / 2),"orientation": "top"})
                            gold -= menuPrices[selectedItem]
                            selectedItem = None
                        elif islandHeight - 99 < adjustedMouseY < islandHeight + 99 and 100 < mouseX < islandWidth - 100:
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
                            placedItems.append({"item": SelectedItem, "pos": (adjustedMouseX - dockWidth // 2, adjustedMouseY - dockHeight // 2), "orientation": "normal"})
                            selectedItem = None

            for docks in placedItems:
                if isinstance(docks["item"], Dock):
                    dock = docks["item"]
                    if dock.rect.collidepoint(adjustedMouseX, adjustedMouseY):
                        dock.toggleUpgrade((adjustedMouseX, adjustedMouseY))

                    gold = dock.upgradeBoxClicked((adjustedMouseX, adjustedMouseY), gold)

    # Camera movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        cameraX += speed
    if keys[pygame.K_RIGHT]:
        cameraX -= speed
    if keys[pygame.K_UP]:
        cameraY += speed
    if keys[pygame.K_DOWN]:
        cameraY -= speed

    # Draw ocean and island
    Screen.fill(Blue)
    Screen.blit(island, (cameraX, cameraY))

    # Draw the entrance dock at the top
    pygame.draw.rect(Screen, Brown, pygame.Rect(entranceDock[0] + cameraX, entranceDock[1] + cameraY, dockWidth, dockHeight))
    entranceLabel = dockFont.render("Entrance", True, White)
    labelRect = entranceLabel.get_rect(center=(entranceDock[0] + cameraX + dockWidth // 2, entranceDock[1] + cameraY + dockHeight // 2))
    Screen.blit(entranceLabel, labelRect)

    # If 4 items placed, new boat spawns in
    if NoOfItems > 3:
        newBoat = Boat([800, -1100])
        newPirate = Pirate([800,20], 0)
        boatAndPirate.append((newBoat, newPirate))
        NoOfItems = 0


    # Move the boat towards the entrance dock
    for boat, pirate in boatAndPirate:
        boat.moveTowards((800, 20))
        if boat.active:
            boat.draw(Screen, cameraX, cameraY)

        # Check if the boat reaches the entrance dock, activate the pirate
        if not boat.active and not pirate.active:
            pirate.active = True
            pirate.position = list(boat.position)  #
            population += 1

        if boat.active:
            boatRect = (boat.position[0] + cameraX, boat.position[1] + cameraY, 30, 10)
            pygame.draw.rect(Screen, Red, boatRect)

        # Find the closest object
        closestObject = None
        objectType = ""
        minDistance = 200
        payment = 0
        increaseSatisfaction = 0

        for item in placedItems:
            if not isinstance(item["item"], Dock):
                objectType = item["item"].label
                itemX, itemY = item["pos"]
                distance = ((pirate.position[0] - itemX) ** 2 + (pirate.position[1] - itemY) ** 2) ** 0.5

                # Check if the tent is within the 200-pixel range
                if distance < minDistance:
                    minDistance = distance
                    closestObject = (itemX, itemY)
                    if objectType == "Tent":
                        payment = 400

                    elif objectType == "Restaurant":
                        payment = 800


        if closestObject and not pirate.goldGenerated:
            pirate.nearObject = True
            pirate.moveTowards(closestObject)
        else:
            pirate.nearObject = False

        payment = pirate.update(objectType)
        gold += payment
        pirate.draw(Screen, cameraX, cameraY)


    # Draw items on the island
    for item in placedItems:
        dock = item["item"] if isinstance(item["item"], Dock) else None
        x, y = item["pos"]
        orientation = item["orientation"]

        if dock:
            dock.rect.topleft = (x, y)

            rotatedImage = dock.image

            # Adjust orientation if needed
            if orientation == "right" or orientation == "left":
                rotatedImage = pygame.transform.rotate(dock.image, 0)  # No rotation needed here
            else:
                rotatedImage = pygame.transform.rotate(dock.image, 90) # Rotate image

            # Update the rect for the rotated image
            rotatedRect = rotatedImage.get_rect(topleft=(x + cameraX, y + cameraY))

            Screen.blit(rotatedImage, rotatedRect)

            # Display dock size on the placed docks
            dockLabel = dockFont.render(dock.size.capitalize(), True, White)
            labelRect = dockLabel.get_rect(center=(x + cameraX + dock.rect.width // 2, y + cameraY + dock.rect.height // 2))
            Screen.blit(dockLabel, labelRect)

            # Generate gold form the docks
            if dock.isTimeForReturn():
                gold += dock.goldRate

        else:
            object = item["item"]
            x, y = item["pos"]
            objectRect = object.image.get_rect(topleft=(x + cameraX, y + cameraY))
            Screen.blit(object.image, objectRect)

    for docks in placedItems:
        if isinstance(docks["item"], Dock):
            dock = docks["item"]
            dock.drawUpgrade(Screen, cameraX, cameraY)


    # Draw menu items
    pygame.draw.rect(Screen, (200, 200, 200), (0, screenHeight - menuHeight, screenWidth, menuHeight))
    for item in menuItems:
        pygame.draw.rect(Screen, Brown, item["rect"])
        menuLabel = dockFont.render(item["item"].capitalize(), True, White)
        menuLabelRect = menuLabel.get_rect(center=(item["rect"].centerx, item["rect"].top - 10))
        Screen.blit(menuLabel, menuLabelRect)
        priceLabel = dockFont.render(f"${menuPrices[item['item']]}", True, White)
        priceLabelRect = priceLabel.get_rect(center=(item["rect"].centerx, item["rect"].top + 10))
        Screen.blit(priceLabel, priceLabelRect)

    # Display gold
    goldText = font.render(f"Gold: {gold}", True, White)
    Screen.blit(goldText, (10, 10))

    # Display population count
    populationText = populationFont.render(f"Population: {population}", True, White)
    Screen.blit(populationText, (10, 50))  # Adjust y-position as needed


    pygame.display.flip()
    timer.tick(fps)


pygame.quit()
