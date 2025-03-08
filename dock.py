import time
import pygame
from buildings import Building

class Dock(Building):
    def __init__(self, size, position, orientation, price):
        super().__init__(position, price)
        self.image = pygame.image.load(r"C:\Users\Study\PycharmProjects\NEA Images\Wp3TJeiWRvK6ltBUFT4DdQ.jpg")
        self.image = pygame.transform.scale(self.image, (20, 20))
        if orientation == "right":
            self.orientation = "right"
        elif orientation == "left":
            self.orientation = "left"
        elif orientation == "top":
            self.orientation = "top"
        elif orientation == "bottom":
            self.orientation = "bottom"
        self.position = position
        self.rect = self.image.get_rect(topleft=position)
        self.size = size
        self.goldRate = self.setGoldRate()
        self.returnFrequency = self.setReturnFrequency()
        self.level = 1
        self.lastGenerated = time.time()
        self.visibleUpgradeBox = True
        if self.size == "small":
            self.upgradeCost = 50000
        elif self.size == "medium":
            self.upgradeCost = 250000
        elif self.size == "large":
            self.upgradeCost = 700000
        self.boatAdded = False

    def setGoldRate(self):
        if self.size == 'small':
            return 100
        elif self.size == 'medium':
            return 10000
        elif self.size == 'large':
            return 30000

    def setReturnFrequency(self):
        if self.size == "small":
            return 30
        elif self.size == "medium":
            return 60
        elif self.size == "large":
            return 90

    def isTimeForReturn(self, speedMultiplier):
        currentTime = time.time()
        if currentTime - self.lastGenerated >= self.returnFrequency/ speedMultiplier:
            self.lastGenerated = currentTime
            return True
        return False

    def toggleUpgrade(self, mousePos):
        # If dock is clicked, show the upgrade box
        if self.rect.collidepoint(mousePos):
            self.visibleUpgradeBox = not self.visibleUpgradeBox

    def applyUpgrade(self):
        if self.size == "small":
            if self.level == 2:
                self.goldRate = 1000
                self.upgradeCost = 100000
            elif self.level == 3:
                self.goldRate = 5000
                self.upgradeCost += 100000
            else:
                self.goldRate += 5000
                self.upgradeCost += 5000
        elif self.size == "medium":
            if self.level == 2:
                self.goldRate = 15000
                self.upgradeCost = 400000
            elif self.level == 3:
                self.goldRate =20000
                self.upgradeCost += 100000
            else:
                self.goldRate += 25000
                self.upgradeCost += 10000
        elif self.size == "large":
            if self.level == 2:
                self.goldRate = 35000
                self.upgradeCost = 800000
            elif self.level == 3:
                self.goldRate = 50000
            else:
                self.goldRate += 100000
                self.upgradeCost += 300000
