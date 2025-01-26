import pygame
import time

class Building(pygame.sprite.Sprite):
    def __init__(self, position):
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
        # Draw the upgrade box if visible
        if self.visibleUpgradeBox:
            # Adjust position and dimensions for zoom
            adjustedX = self.rect.x * zoomLevel - 25 * zoomLevel
            adjustedY = self.rect.y * zoomLevel - 30 * zoomLevel
            boxWidth = int(40 * zoomLevel)
            boxHeight = int(10 * zoomLevel)

            # Draw the scaled upgrade box
            pygame.draw.rect(screen, (200, 200, 200), (adjustedX + cameraX, adjustedY + cameraY, boxWidth, boxHeight))

            # Adjust font size for zoom
            fontSize = int(8 * zoomLevel)
            font = pygame.font.SysFont(None, fontSize)

            # Render and position text
            text = font.render(f"Upgrade {self.upgradeCost}$", True, (0, 0, 0))
            textX = adjustedX + 5 * zoomLevel  # Adjust text padding for zoom
            textY = adjustedY + 5 * zoomLevel
            screen.blit(text, (textX + cameraX, textY + cameraY))

    def upgradeBoxClicked(self, mousePos, gold):
        if self.visibleUpgradeBox:
            upgradeBoxRect = pygame.Rect(self.rect.x - 25, self.rect.y - 30, 200, 25)
        return gold
    
    def drawHealthBar(self, screen, cameraX, cameraY):
         # Calculate health bar width
        bar_width = self.rect.width
        bar_height = 5
        health_ratio = self.health / self.maxHealth
        health_bar_width = int(bar_width * health_ratio)

        # Define health bar positions
        bar_x = self.rect.x + cameraX
        bar_y = self.rect.y - bar_height - 2 + cameraY # Position it above the building

        # Draw background bar (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Draw health bar (green)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_bar_width, bar_height))

        # Hide health bar after 2 seconds
        current_time = time.time()
        if current_time - self.healthBarStartTime > 2:
            self.showHealthBar = False

    def draw(self, screen, cameraX, cameraY):
        # Draw the building
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))

        # Draw the health bar if it should be displayed
        if self.showHealthBar:
            self.drawHealthBar(screen, cameraX, cameraY)

    

