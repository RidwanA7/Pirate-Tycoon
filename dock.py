import time
import pygame
from buildings import Building
import math

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
        self.__goldRate = self.setGoldRate()
        self.__returnFrequency = self.setReturnFrequency()
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
        self.globalDemandFactor = 1.0  


    def setGoldRate(self):
        if self.size == 'small':
            return 100
        elif self.size == 'medium':
            return 10000
        elif self.size == 'large':
            return 30000

    def setReturnFrequency(self):
        if self.size == "small":
            return 1    #30 seconds
        elif self.size == "medium":
            return 60
        elif self.size == "large":
            return 90

    def isTimeForReturn(self, ):
        currentTime = time.time()
        if currentTime - self.lastGenerated >= self.__returnFrequency:
            self.lastGenerated = currentTime
            return True
        return False

    def toggleUpgrade(self, mousePos):
        if self.rect.collidepoint(mousePos):
            self.visibleUpgradeBox = not self.visibleUpgradeBox

    def applyUpgrade(self):
        if self.size == "small":
            if self.level == 2:
                self.__goldRate = 1000
                self.upgradeCost = 100000
            elif self.level == 3:
                self.__goldRate = 5000
                self.upgradeCost += 100000
            else:
                self.__goldRate += 5000
                self.upgradeCost += 5000
        elif self.size == "medium":
            if self.level == 2:
                self.__goldRate = 15000
                self.upgradeCost = 400000
            elif self.level == 3:
                self.__goldRate = 20000
                self.upgradeCost += 100000
            else:
                self.__goldRate += 25000
                self.upgradeCost += 10000
        elif self.size == "large":
            if self.level == 2:
                self.__goldRate = 35000
                self.upgradeCost = 800000
            elif self.level == 3:
                self.__goldRate = 50000
            else:
                self.__goldRate += 100000
                self.upgradeCost += 300000
    
    def updateDemandFactor(self, population, totalDocks):
        if totalDocks == 0:
            self.globalDemandFactor = 1.0
        else:
            # more pirates means more demand, more docks means more supply
            demandRatio = population / (totalDocks * 10)
            self.globalDemandFactor = min(1.0, max(0.1, demandRatio))
    
    def updateReturnFrequencyBasedOnSatisfaction(self, avgSatisfaction):
        # As satisfaction drops, boats return more frequently (try to compensate)
        if avgSatisfaction < 40:
            self.__returnFrequency = max(1, self.__returnFrequency - 5)    
        elif avgSatisfaction > 80:
            self.__returnFrequency += 5

    # Getter methods to access encapsulated attributes
    def getGoldRate(self):
         # Simulates diminishing returns with a sigmoid curve
        baseRate = self.__goldRate
        demand = self.globalDemandFactor
        logisticFactor = 1 / (1 + math.exp(-0.1 * (demand * 10 - 5)))  # Scales between 0 and 1
        return int(baseRate * logisticFactor)

    def getReturnFrequency(self):
        return self.__returnFrequency

    def setGoldRateValue(self, newRate):
        if newRate > 0:
            self.__goldRate = newRate

    def setReturnFrequencyValue(self, newFrequency):
        if newFrequency > 0:
            self.__returnFrequency = newFrequency
