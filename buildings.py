import pygame
import time

class Building(pygame.sprite.Sprite):
    def __init__(self, position, price):
        super().__init__()
        self.position = position
        self.level = 1
        self.image = None
        self.rect = None
        self.visibleUpgradeBox = True
        self.upgradeCost = 30
        self.capacity = 1
        self.currentVisitors = 0
        self.visitors = []
        self.beingAttacked = False
        self.maxHealth = 100
        self.health = 100
        self.showHealthBar = False
        self.healthBarStartTime = 0
        self.upgradeCost = 30
        self.price = price
    
    def applyUpgrade(self):
        pass

    def isAvailable(self):
        return len(self.visitors) < self.capacity

    def addVisitor(self, pirate):
        if len(self.visitors) < self.capacity and pirate not in self.visitors:
            self.visitors.append(pirate)
    
    def removeVisitor(self, pirate):
        if pirate in self.visitors:
            self.visitors.remove(pirate)

    def toggleUpgrade(self, mousePos):
        # If dock is clicked, show the upgrade box
        if self.rect.collidepoint(mousePos):
            self.visibleUpgradeBox = not self.visibleUpgradeBox

    def drawUpgrade(self, screen, cameraX, cameraY, zoomLevel):
        if self.visibleUpgradeBox:
            # Adjust position and dimensions for zoom
            centerx, centery = self.rect.center
            adjustedX = centerx * zoomLevel - 25 * zoomLevel
            adjustedY = centery * zoomLevel - 50 * zoomLevel  # Shift upwards for extra bar space
            boxWidth = int(80 * zoomLevel)
            boxHeight = int(20 * zoomLevel)

            # Draw Sell Box (above Repair Box)
            sellBoxY = adjustedY - 2*boxHeight  # Position above repair box
            pygame.draw.rect(screen, (150, 100, 100), (adjustedX + cameraX, sellBoxY + cameraY, boxWidth, boxHeight))

            # Draw Repair Box (above Upgrade Box)
            repairBoxY = adjustedY - boxHeight  # Position above the upgrade box
            pygame.draw.rect(screen, (180, 180, 180), (adjustedX + cameraX, repairBoxY + cameraY, boxWidth, boxHeight))

            # Draw Upgrade Box
            pygame.draw.rect(screen, (200, 200, 200), (adjustedX + cameraX, adjustedY + cameraY, boxWidth, boxHeight))

            # Adjust font size for zoom
            fontSize = int(16 * zoomLevel)
            font = pygame.font.SysFont(None, fontSize)

            # Render Sell Text
            sellText = font.render(f"Sell {self.price * 0.3}$", True, (0, 0, 0))
            screen.blit(sellText, (adjustedX + 5 * zoomLevel + cameraX, sellBoxY + 5 * zoomLevel + cameraY))

            # Render Upgrade Text
            upgradeText = font.render(f"Upgrade {self.upgradeCost}$", True, (0, 0, 0))
            screen.blit(upgradeText, (adjustedX + 5 * zoomLevel + cameraX, adjustedY + 5 * zoomLevel + cameraY))

            # Render Repair Text
            repairText = font.render("Repair 30$", True, (0, 0, 0))
            screen.blit(repairText, (adjustedX + 5 * zoomLevel + cameraX, repairBoxY + 5 * zoomLevel + cameraY))

    def upgradePressed(self, mousePos, gold, cameraX, cameraY, placedItems):
        if self.visibleUpgradeBox:
            centerx, centery = self.rect.center
            adjustedX = centerx  - 25 
            adjustedY = centery  - 50 
            boxWidth = int(80 )
            boxHeight = int(20)

            # Define boxes at the same positions where they're drawn
            repairBoxY = adjustedY - boxHeight

            # Define Sell Box Rectangle
            sellBoxY = adjustedY - 2*boxHeight
            sellBoxRect = pygame.Rect(
                adjustedX ,
                sellBoxY ,
                boxWidth,
                boxHeight
        )
            
            # Define Upgrade Box Rectangle
            upgradeBoxRect = pygame.Rect(
                adjustedX ,
                adjustedY ,
                boxWidth,
                boxHeight
            )

            # Define Repair Box Rectangle
            repairBoxRect = pygame.Rect(
                adjustedX ,
                repairBoxY ,
                boxWidth,
                boxHeight
            )

            # Check if Sell button is clicked
            if sellBoxRect.collidepoint(mousePos):
                gold += self.price * 0.3
                for item in placedItems:
                    if item["item"] == self:
                        placedItems.remove(item)


            # Check if Repair button is clicked
            if repairBoxRect.collidepoint(mousePos) and gold >= 30:
                gold -= 30
                self.health = self.maxHealth
                self.showHealthBar = True

            # Check if Upgrade button is clicked
            elif upgradeBoxRect.collidepoint(mousePos) and gold >= self.upgradeCost:
                gold -= self.upgradeCost
                self.level += 1
                self.applyUpgrade()
        
        return gold
    
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
        # Draw the building
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))

        # Draw the health bar if it should be displayed
        if self.showHealthBar:
            self.drawHealthBar(screen, cameraX, cameraY)

