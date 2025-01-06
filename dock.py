import time
import pygame
from buildings import Building
class Dock(Building):
    def __init__(self, size, position, orientation):
        super().__init__(position)
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
        self.upgradeCost = 30
        self.boatAdded = False

    def setGoldRate(self):
        if self.size == 'small':
            return 100
        elif self.size == 'medium':
            return 200
        elif self.size == 'large':
            return 300

    def setReturnFrequency(self):
        if self.size == "small":
            return 5
        elif self.size == "medium":
            return 3
        elif self.size == "large":
            return 2

    def isTimeForReturn(self):
        currentTime = time.time()
        if currentTime - self.lastGenerated >= self.returnFrequency:
            self.lastGenerated = currentTime
            return True
        return False

    def drawUpgrade(self, screen, cameraX, cameraY, zoomLevel):
        if self.visibleUpgradeBox:
            boxWidth = int(20 * zoomLevel)
            boxHeight = int(20 * zoomLevel)
            adjustedX = self.rect.centerx * zoomLevel - boxWidth // 2
            adjustedY = self.rect.top * zoomLevel - boxHeight - 10 * zoomLevel  

            pygame.draw.rect(screen, (200, 200, 200), 
                            (adjustedX + cameraX, adjustedY + cameraY, boxWidth, boxHeight))

            fontSize = int(8 * zoomLevel)
            font = pygame.font.SysFont(None, fontSize)

            text = font.render(f"Upgrade {self.upgradeCost}$", True, (0, 0, 0))
            textRect = text.get_rect(center=(adjustedX + boxWidth / 2 + cameraX, 
                                            adjustedY + boxHeight / 2 + cameraY))
            screen.blit(text, textRect)


    def toggleUpgrade(self, mousePos):
        # If dock is clicked, show the upgrade box
        if self.rect.collidepoint(mousePos):
            self.visibleUpgradeBox = not self.visibleUpgradeBox

    def upgradeBoxClicked(self,mousePos, gold):
        if self.visibleUpgradeBox:
            upgradeBoxRect = pygame.Rect(self.rect.x - 25 , self.rect.y - 30, 200, 25)

            if upgradeBoxRect.collidepoint(mousePos) and gold >= self.upgradeCost:
                self.goldRate += 50
                if self.returnFrequency > 1:
                    self.returnFrequency -= 1
                gold -= self.upgradeCost
                self.upgradeCost += 100
        return gold
