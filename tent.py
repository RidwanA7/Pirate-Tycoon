import pygame
from buildings import Building
import os

class Tent(Building):
    def __init__(self, position, price):
        super().__init__(position, price)
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "images", "tent.jpg")
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=position)
        self.label = "Tent"
        self.visibleUpgradeBox = True
        self.sleepPoints = 0
        self.upgradeCost = 100000
        self.payment = 400
        self.level = 1

    def applyUpgrade(self):
        if self.level == 2:
            self.payment = 5000
            self.capacity =2
            self.upgradeCost = 600000
        elif self.level == 3:
            self.payment = 10000
            self.capacity = 3
            self.upgradeCost *= 2
        else:
            self.payment *= 2
            self.capacity += 1
            self.upgradeCost *= 2

