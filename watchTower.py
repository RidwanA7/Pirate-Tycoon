import pygame
import time
import os
from buildings import Building

class WatchTower(Building):
    def __init__(self, position, price):
        super().__init__(position, price)
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "images", "watchTower.png")
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=position)
        self.label = "WatchTower"
        self.lastAttackTime = 0
        self.attackCooldown = 5
        self.range = 100
        self.damage = 10
        self.enemy = None
        self.cannonBalls = []
        self.upgradeCost = 300000
    
    def findClosestEnemy(self, enemyPirates):
        if not self.enemy:
            for enemy in enemyPirates:
                distanceX = self.rect.x - enemy.rect.x
                distanceY = self.rect.y - enemy.rect.y
                distance = (distanceX ** 2 + distanceY ** 2) ** 0.5
                if distance <= self.range:
                    self.enemy = enemy
                    break
        else:
            distanceX = self.rect.x - self.enemy.rect.x
            distanceY = self.rect.y - self.enemy.rect.y
            distance = (distanceX ** 2 + distanceY ** 2) ** 0.5
            if distance > self.range:
                self.enemy = None

    def shoot(self):
        distanceX = self.rect.x - self.enemy.rect.x
        distanceY = self.rect.y - self.enemy.rect.y
        distance = (distanceX ** 2 + distanceY ** 2) ** 0.5
        if distance <= self.range:
            currentTime = time.time()
            if currentTime - self.lastAttackTime > self.attackCooldown:
                self.lastAttackTime = currentTime
                self.enemy.showHealthBar = True
                self.enemy.healthBarStartTime = time.time()
                self.cannonBalls.append({'pos': pygame.math.Vector2(self.rect.center),
                        'target': pygame.math.Vector2(self.enemy.rect.center),
                        'speed': 5
                    })
                self.enemy.health -= self.damage
                if self.enemy.health <= 0:
                    self.enemy = None

    def drawCannonBalls(self, screen, cameraX, cameraY):
        for cannonball in self.cannonBalls[:]:
            direction = (cannonball['target'] - cannonball['pos']).normalize()
            cannonball['pos'] += direction * cannonball['speed']

            # Draw the cannonball
            pygame.draw.circle(screen, (0, 0, 0), (int(cannonball['pos'].x) + cameraX, int(cannonball['pos'].y) + cameraY), 5)

            # Check if the cannonball has reached the target
            if cannonball['pos'].distance_to(cannonball['target']) < cannonball['speed']:
                self.enemy.health -= self.damage
                if self.enemy.health <= 0:
                    self.enemy = None
                self.cannonBalls.remove(cannonball)

    def applyUpgrade(self):
        if self.level == 2:
            self.damage = 15
            self.attackCooldown = 4
            self.upgradeCost = 700000
        elif self.level == 3:
            self.damage = 20
            self.attackCooldown = 3
        else:
            self.range += 10
            self.damage += 5
            self.attackCooldown -= 0.1

