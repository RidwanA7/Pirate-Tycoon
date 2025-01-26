import pygame
import time
import random
from farmer import Farmer
from path import Path

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()  # Initialise the sprite base class
        self.speed = 5
        self.image = pygame.image.load(r'C:\Users\Study\Pirate Tycoon\images\farmer.png')
        self.image = pygame.transform.scale(self.image, (10, 10))
        self.rect = self.image.get_rect(center=position)
        self.attackCooldown = 2
        self.damage = 10
        self.lastAttackTime = 0
        self.foundTarget = False
        self.targetPos = None
        self.target = None
        self.changeDirectionTime = 0

    def findClosestObject(self, placedItems):
        closestDistance = float('inf')
        for placedItem in placedItems:
            object = placedItem["item"]
            if not isinstance(object, Farmer) and not isinstance(object, Path):
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
                    
    def moveTowards(self):
        targetX, targetY = self.targetPos
        directionX = targetX - self.rect.x
        directionY = targetY - self.rect.y
        distance = (directionX ** 2 + directionY ** 2) ** 0.5

        if distance > 4:
            self.rect.x += directionX / distance * self.speed
            self.rect.y += directionY / distance * self.speed
    
    def atTarget(self):
        targetX, targetY = self.targetPos
        if abs(self.rect.x - targetX) <= 4 and abs(self.rect.y - targetY) <= 4:
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
    
    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))

    def moveAround(self):
        currentTime = time.time()
        if currentTime - self.changeDirectionTime > random.uniform(2, 3):
            self.randomDirection = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
            self.changeDirectionTime = currentTime

        # Update position
        self.rect.x += self.randomDirection[0] * self.speed
        self.rect.y += self.randomDirection[1] * self.speed

        # Keep within bounds (e.g., the screen or a specific area)
        islandWidth, islandHeight = 1600, 1200  # Example screen size; adjust as needed
        self.rect.x = max(0, min(self.rect.x, islandWidth - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, islandHeight - self.rect.height))
