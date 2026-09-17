import pygame
import time
import random
from farmer import Farmer
from path import Path, Land
import math
import os

class Node:
    def __init__(self, pos, gCost=float('inf'), hCost=0):
        self.pos = pos
        self.gCost = gCost  # Cost from start to this node
        self.hCost = hCost  # Estimated cost from this node to end
        self.fCost = gCost + hCost  # Total cost
        self.parent = None

def calculatePath(startPos, targetPos, landPositions, treePositions, gridSize):
    def getNeighbors(pos):
        x, y = pos
        neighbors = [
            (x + gridSize, y),  # right
            (x - gridSize, y),  # left
            (x, y + gridSize),  # down
            (x, y - gridSize)   # up
        ]
        return [n for n in neighbors if n in landPositions and n not in treePositions]
    
    def heuristic(pos, target):
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])
    
    def findNearestLand(pos):
        """Find the closest land position to the given pos."""
        if pos in landPositions and pos not in treePositions:
            return pos  # Target is already valid

        # Find nearest valid land tile
        nearestLand = min((p for p in landPositions if p not in treePositions), key=lambda p: heuristic(pos, p))
        return nearestLand
    
    startGrid = (startPos[0], startPos[1])
    targetGrid = findNearestLand((targetPos[0], targetPos[1]))  # Ensure valid target
    
    startNode = Node(startGrid, gCost=0, hCost=heuristic(startGrid, targetGrid))
    
    openSet = {startGrid: startNode}
    closedSet = set()
    
    while openSet:
        currentPos = min(openSet, key=lambda pos: openSet[pos].fCost) #finds node with lowest total cost
        current = openSet.pop(currentPos) #removes that node from open set
        
        if current.pos == targetGrid:
            path = []
            while current:
                path.append(current.pos)
                current = current.parent
            return path[::-1]
        
        closedSet.add(currentPos)
        
        for neighborPos in getNeighbors(currentPos):
            if neighborPos in closedSet:
                continue
                
            gCost = current.gCost + gridSize
            
            if neighborPos not in openSet:
                neighbor = Node(neighborPos)
                openSet[neighborPos] = neighbor
            else:
                neighbor = openSet[neighborPos]
                if gCost >= neighbor.gCost:
                    continue
            
            neighbor.parent = current
            neighbor.gCost = gCost
            neighbor.hCost = heuristic(neighborPos, targetGrid)
            neighbor.fCost = neighbor.gCost + neighbor.hCost
    
    return None

def moveAlongPath(self, path, gridSize):
    if not path or len(path) < 2:
        return
    
    nextPos = path[0]
    
    dx = nextPos[0] - self.rect.x
    dy = nextPos[1] - self.rect.y
    
    if abs(dx) > self.speed:
        self.rect.x += self.speed if dx > 0 else -self.speed
    else:
        self.rect.x = nextPos[0]
        
    if abs(dy) > self.speed:
        self.rect.y += self.speed if dy > 0 else -self.speed
    else:
        self.rect.y = nextPos[1]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()  # Initialise the sprite base class
        self.speed = 1
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "images", "farmer.png")
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(center=position)
        self.attackCooldown = 3
        self.damage = 40
        self.lastAttackTime = 0
        self.foundTarget = False
        self.targetPos = None
        self.target = None
        self.changeDirectionTime = 0
        self.maxHealth = 100
        self.health = 100
        self.showHealthBar = False
        self.healthBarStartTime = 0
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def findClosestObject(self, placedItems):
        closestDistance = float('inf')
        for placedItem in placedItems:
            object = placedItem["item"]
            if not isinstance(object, Farmer) and not isinstance(object, Path) and not isinstance(object, Land):
                if not object.beingAttacked:
                    distance = ((self.rect.x - object.rect.x) ** 2 + (self.rect.y - object.rect.y) ** 2) ** 0.5
                    if distance < closestDistance:
                        closestDistance = distance
                        targetObject = object
                        self.targetPos = object.rect.x, object.rect.y
                        self.foundTarget = True

        if self.foundTarget:
            self.target = targetObject
            targetObject.beingAttacked = True

    def findClosestPirate(self, boatAndPirates):
        closestDistance = float('inf')
        for boat, pirate in boatAndPirates:
            if pirate is not None:
                distance = ((self.rect.x - pirate.rect.centerx) ** 2 + (self.rect.y - pirate.rect.centery) ** 2) ** 0.5
                if not pirate.beingAttacked:
                    if distance < closestDistance:
                        closestDistance = distance
                        targetObject = pirate
                        self.targetPos = pirate.rect.centerx, pirate.rect.centery
                        self.foundTarget = True
            if self.foundTarget:
                self.target = targetObject
                self.target.beingAttacked = True
                    
    def moveTowards(self, landPositions, treePositions, gridSize=20):
        if self.target:
            centerx, centery = self.target.rect.center
            self.targetPos = (centerx//gridSize * gridSize, centery//gridSize * gridSize)  # Update dynamically
            
            currentTime = time.time()

            if not hasattr(self, 'path') or not self.path or \
            self.targetPos != getattr(self, 'last_target', None):
                if currentTime - getattr(self, 'lastTime', 0) > 1:
                    self.lastTime = currentTime
                    startPos = (self.rect.x//gridSize * gridSize, self.rect.y//gridSize * gridSize)
                    self.path = calculatePath(startPos, self.targetPos, landPositions, treePositions, gridSize)
                    self.lastTarget = self.targetPos
                
            if self.path:
                currentWaypoint = self.path[0]
                if (abs(self.rect.x - currentWaypoint[0]) < 4 and 
                    abs(self.rect.y - currentWaypoint[1]) < 4):
                    self.path.pop(0)
                
                moveAlongPath(self, self.path, gridSize)
    
    def atTarget(self):
        targetX, targetY = self.target.rect.x, self.target.rect.y
        distance = math.sqrt((self.rect.x - targetX) ** 2 + (self.rect.y - targetY)**2)
        if distance <= 30:
            return True
        return False
    
    def attack(self):
        # Attack the target
        currentTime = time.time()
        if currentTime - self.lastAttackTime > self.attackCooldown:
            self.lastAttackTime = currentTime
            self.target.showHealthBar = True
            self.target.healthBarStartTime = time.time()
            self.target.health -= self.damage
        if self.target.health <= 0:
            self.target = None
            self.foundTarget = False

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
    
    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        # Draw the health bar if it should be displayed
        if self.showHealthBar:
            self.drawHealthBar(screen, cameraX, cameraY)

    def moveAround(self, landPositions, treePositions, gridSize=20):
       # Calculate the next position
        newPosition = [self.rect.x + self.direction[0] * self.speed, 
                        self.rect.y + self.direction[1] * self.speed]

        gridPosition = (newPosition[0] // gridSize * gridSize, newPosition[1] // gridSize * gridSize)

        # Only move if the new position is on land
        if tuple(gridPosition) in landPositions and gridPosition not in treePositions:
            self.rect.x, self.rect.y = newPosition[0], newPosition[1]
        # Randomly change direction occasionally
        if random.random() < 0.02:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]) 

class EnemyCaptain(Enemy):
    def __init__(self, position):
        super().__init__(position)
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "images", "captain.png")
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.attackCooldown = 2
        self.damage = 50
        self.maxHealth = 150
        self.health = 150
        self.speed = 1