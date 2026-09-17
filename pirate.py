import pygame
import random
import time
import os
from restuarant import Restaurant
import math
from enemy import Node, calculatePath, moveAlongPath

class Pirate:
    def __init__(self, position, payment):
        self.position = [position[0]//20 * 20, position[1]//20 * 20]
        self.active = False  # Becomes active when the boat reaches the entrance dock
        self.speed = 1
        self.baseSpeed = 1
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.inCooldown = False
        self.objectStopTime = None
        self.objectCooldownEnd = None
        self.nearObject = False
        self.payment = payment
        self.sleep = 100
        self.hunger = 100
        self.satisfaction = 50
        self.satisfactionTimeDecrease = time.time()
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "images", "pirate.png")
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(center=self.position)
        self.state = "exploring"
        self.atItem = False
        self.found = False
        self.maxHealth = 100
        self.health = 100
        self.enemy = None
        self.damage = 40
        self.attackCooldown = 3
        self.lastAttackTime = 0
        self.showHealthBar = False
        self.healthBarStartTime = 0  
        self.beingAttacked = False

    def updateSpeed(self):
        self.speed = self.baseSpeed

    def moveTowards(self, targetPosition, landPositions, treePositions, gridSize=20):
        if self.enemy:
            self.targetPos = (self.enemy.rect.x//gridSize * gridSize, self.enemy.rect.y//gridSize * gridSize)  #If moving towards an enemy
        else:
            self.targetPos = (targetPosition[0]//gridSize * gridSize, targetPosition[1]//gridSize * gridSize)  # If moving towards a building
        currentTime = time.time()


        if not hasattr(self, 'path') or not self.path or \
        self.targetPos != getattr(self, 'lastTarget', None):
            if currentTime - getattr(self, 'lastTime', 0) > 5:
                self.lastTime = currentTime             
                startPos = (self.rect.x//gridSize * gridSize, self.rect.y//gridSize * gridSize)
                try:
                    self.path = calculatePath(startPos, self.targetPos, landPositions, treePositions, gridSize) 
                except (ValueError, IndexError) as e:
                    print(f"Path calculation error: {e}")
                    self.path = []
                except Exception as e:
                    print(f"Unexpected error in path calculation: {e}")
                    self.path = []
                self.lastTarget = self.targetPos
        
        if self.path:
            currentWaypoint = self.path[0]
            if (abs(self.position[0] - currentWaypoint[0]) < 4 and 
                abs(self.position[1] - currentWaypoint[1]) < 4):
                self.path.pop(0)
            
            moveAlongPath(self, self.path, gridSize)
            self.position = [self.rect.centerx, self.rect.centery]

    def updatePirateStats(self):
        if time.time() - self.satisfactionTimeDecrease >= 1:
            self.hunger = max(0, self.hunger - (4))
            self.sleep = max(0, self.sleep - (1))
            self.satisfactionTimeDecrease = time.time()

    def checkCooldown(self):
        if self.objectCooldownEnd and time.time() > self.objectCooldownEnd:
            self.inCooldown = False

    def pay(self, objectType, object):
        self.inCooldown = True
        self.objectCooldownEnd = time.time() + 10  # 10-second cooldown
        self.nearObject = False
        self.objectStopTime = None
        self.payment = 0
        if objectType == "Tent":
            if not hasattr(self, 'sleepIncrementStartTime'):
                self.sleepIncrementStartTime = time.time()  # Set the start time only once
                self.sleepIncrementCompleted = False  # Initial state for sleep increment

            currentTime = time.time()  # Get the current time

            # Check if 5 seconds have passed
            if currentTime - self.sleepIncrementStartTime >= (5):
                
                self.sleep = 100  # Set sleep to 100 after 5 seconds
                self.sleepIncrementCompleted = True  # Mark the increment as complete
                self.payment = object.payment  # Payment after the wait
                del self.sleepIncrementStartTime  # Remove the start time once it's paid

                if hasattr(self, 'visitedTent'):
                        del self.visitedTent  # Reset the flag when moving away
                        object.removeVisitor(self)  # Remove the visitor from the restaurant

        elif objectType == "Restaurant":
            if object.food >= 2:
                if not hasattr(self, 'hungerIncrementStartTime'):
                    self.hungerIncrementStartTime = time.time()  # Set the start time only once
                    self.payment = 0  # Initialize payment

                currentTime = time.time()  # Get the current time

                # Check if 3 seconds have passed
                if currentTime - self.hungerIncrementStartTime >= (3):
                    self.hunger = 100  # Set hunger to 100 after 3 seconds
                    self.payment = object.payment  # Payment after the wait
                    object.food -= 2  # Deduct food from the restaurant
                    del self.hungerIncrementStartTime  # Remove the start time once it's paid

                    if hasattr(self, 'visitedRestaurant'):
                       
                        del self.visitedRestaurant  # Reset the flag when moving away
                        object.removeVisitor(self)  # Remove the visitor from the restaurant
            else:
                self.payment = 0  # Not enough food
        return self.payment

    def move(self, landPositions, treePositions, gridSize=20):
        # Calculate the potential new position
        newPosition = [self.position[0] + self.direction[0] * self.speed, 
                    self.position[1] + self.direction[1] * self.speed]
        gridPosition = (newPosition[0] // gridSize * gridSize, newPosition[1] // gridSize * gridSize)
    
        # Ensure the new position is within landPositions
        if tuple(gridPosition) in landPositions and tuple(gridPosition) not in treePositions:
            self.position = newPosition
            self.rect.centerx, self.rect.centery = self.position
        # Randomly change direction occasionally
        if random.random() < 0.02:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def findClosestObject(self, item, placedItems):
        closestDistance = float('inf')
        closestPosition = None
        itemObject = None
        
        # Iterate through all placed items to find the nearest restaurant or tent
        for placedItem in placedItems:
            # Check if the placed item matches the given string 
            if placedItem["item"].__class__.__name__.lower() == item:
                itemPosition = placedItem["pos"]
                
                # Calculate the distance between the pirate and the item
                distance = math.sqrt((self.position[0] - itemPosition[0])**2 + (self.position[1] - itemPosition[1])**2)
                
                if self not in placedItem["item"].visitors:
                    # Update the closest item if this one is closer
                    if distance < closestDistance and placedItem["item"].isAvailable():
                        closestDistance = distance
                        closestPosition = itemPosition
                        itemObject = placedItem["item"]
                    elif not placedItem["item"].isAvailable():
                        print("No available items", placedItem["item"].currentVisitors, placedItem["item"].isAvailable())
                else:
                    closestPosition = placedItem["pos"]
                    itemObject = placedItem["item"]
        
        return closestPosition, itemObject

    def updateStates(self):
        if self.hunger <= 40:
            self.state = "hungry"
        elif self.sleep <= 20:
            self.state = "tired"
        else:
            self.state = "exploring"

    def isAtObject(self, itemPos):
        self.position = [self.rect.x, self.rect.y]
        # Calculate the distance between the pirate and the item
        distance = math.sqrt((self.position[0] - itemPos[0])**2 + (self.position[1] - itemPos[1])**2)
        # Check if the pirate is within a certain distance of the item
        if distance <= 30:
            return True
        else:
            return False
        
    def incrementCompleted(self, item, itemObject):
        if item == "tent":
            if self.sleep == 100:
                return True
            else:
                return False
        elif item == "Restaurant":
            if self.hunger == 100:
                return True
            else:
                return False
    
    def update(self, placedItems, landPositions, treePositions):
        self.payment = 0
        self.updateStates()
        if self.state == "exploring":
            self.atItem = False
            self.move(landPositions, treePositions)
        elif self.state == "hungry":
            restaurantPosition, itemObject = self.findClosestObject("restaurant", placedItems)
            if itemObject is None:
                self.state = "exploring"
                self.atItem = False
            else:
                if self.isAtObject(restaurantPosition):
                    self.atItem = True
                    if not hasattr(self, 'visitedRestaurant'):  # Ensure 'addVisitor' is only called once
                        itemObject.addVisitor(self)
                        self.visitedRestaurant = True  # Set a flag to avoid multiple calls
                    self.payment = self.pay("Restaurant", itemObject)
                if self.payment>0:
                    self.lastTarget = None
                    del self.path
                else:
                    self.moveTowards(restaurantPosition, landPositions, treePositions)

        elif self.state == "tired":
            tentPosition, itemObject = self.findClosestObject("tent", placedItems)
            if itemObject is None:
                self.state = "exploring"
                self.atItem = False
            else:
                if self.isAtObject(tentPosition):
                    self.atItem = True
                    if not hasattr(self, 'visitedTent'):  
                        itemObject.addVisitor(self)
                        self.visitedTent = True  # Set a flag to avoid multiple calls
                if self.isAtObject(tentPosition):
                    self.payment = self.pay("Tent", itemObject)
                else:
                    self.moveTowards(tentPosition, landPositions, treePositions)
                if self.payment>0:
                    self.lastTarget = None
                    del self.path

        if not self.atItem:
            self.updatePirateStats()
        
        return self.payment
    
    def drawSatisfactionBar(self, screen, cameraX, cameraY, zoomLevel):
        
        barX = (self.position[0] * zoomLevel) + cameraX - (25 * zoomLevel)
        barY = (self.position[1] * zoomLevel) + cameraY - (40 * zoomLevel)

        
        barWidth = int(25 * zoomLevel)
        barHeight = int(4 * zoomLevel)
        spacing = int(2 * zoomLevel)  # Space between bars, also scaled

        # Calculate filled width for hunger and sleep bars 
        hungerFillWidth = int((self.hunger / 100) * barWidth)
        sleepFillWidth = int((self.sleep / 100) * barWidth)

        # Draw hunger bar
        pygame.draw.rect(screen, (100, 100, 100), (barX, barY, barWidth, barHeight))
        pygame.draw.rect(screen, (255, 0, 0), (barX, barY, hungerFillWidth, barHeight))

        # Draw sleep bar
        pygame.draw.rect(screen, (100, 100, 100), (barX, barY + barHeight + spacing, barWidth, barHeight))
        pygame.draw.rect(screen, (0, 0, 255), (barX, barY + barHeight + spacing, sleepFillWidth, barHeight))

        # Adjust font size based on zoom level
        fontSize = int(10 * zoomLevel)  # Scale font size
        font = pygame.font.Font(None, fontSize)

        # Render labels with adjusted size
        hungerLabel = font.render("Food", True, (255, 255, 255))  # White text
        sleepLabel = font.render("Sleep", True, (255, 255, 255))  # White text
        healthLabel = font.render("Health", True, (255, 255, 255))  # White text

        # Adjust label positions
        screen.blit(hungerLabel, (barX - hungerLabel.get_width() - int(5 * zoomLevel), barY))
        screen.blit(sleepLabel, (barX - sleepLabel.get_width() - int(5 * zoomLevel), barY + barHeight + spacing))
    
    def drawHealthBar(self, screen, cameraX, cameraY):
         # Calculate health bar width
        barWidth = self.rect.width
        barHeight = 5
        healthRatio = self.health / self.maxHealth
        healthBarWidth = int(barWidth * healthRatio)

        # Define health bar positions
        barX = self.rect.x + cameraX
        barY = self.rect.y - barHeight - 2 + cameraY # Position it above the building

        # Draw background bar (red)
        pygame.draw.rect(screen, (255, 0, 0), (barX, barY, barWidth, barHeight))

        # Draw health bar (green)
        pygame.draw.rect(screen, (0, 255, 0), (barX, barY, healthBarWidth, barHeight))

        # Hide health bar after 2 seconds
        currentTime = time.time()
        if currentTime - self.healthBarStartTime > 2:
            self.showHealthBar = False

    def draw(self, screen, cameraX, cameraY, zoomLevel):
        if self.active:
            screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        # Draw the health bar if it should be displayed
            if self.showHealthBar:
                self.drawHealthBar(screen, cameraX, cameraY)

            # Adjust the satisfaction bar position 
            self.drawSatisfactionBar(screen, cameraX, cameraY, zoomLevel)

    def findEnemies(self, enemyPirates):
        if not self.enemy:
            for pirate in enemyPirates:
                distance = math.sqrt((self.position[0] - pirate.rect.centerx)**2 + (self.position[1] - pirate.rect.centery)**2)
                if distance < 50000:
                    self.enemy = pirate
                    break
        else:
            distance = math.sqrt((self.position[0] - self.enemy.rect.centerx)**2 + (self.position[1] - self.enemy.rect.centery)**2)
            if distance > 500:
                self.enemy = None
    
    def attack(self):
        currentTime = time.time()
        if self.enemy:
            if currentTime - self.lastAttackTime > self.attackCooldown:
                self.lastAttackTime = currentTime
                if self.enemy.health > 0:
                    self.enemy.showHealthBar = True
                    self.enemy.healthBarStartTime = time.time()
                    self.enemy.health -= self.damage
                else:
                    self.enemy = None


