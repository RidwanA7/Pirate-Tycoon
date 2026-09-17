import pygame
import time

class Path(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((100, 100, 100))  # Gray color for roads
        self.rect = self.image.get_rect(topleft=position)
        self.position = position
        self.cost = 20  # Gold cost to place a road
        self.label = "Path"
        self.health = 50
        self.maxHealth = 50
        self.showHealthBar = False
        self.healthBarStartTime = 0

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))

        
        # Draw the health bar if it should be displayed
        if self.showHealthBar:
            self.drawHealthBar(screen, cameraX, cameraY)

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

class Land(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((34, 139, 34))  # Green color for land
        self.rect = self.image.get_rect(topleft=position)
        self.position = position
        self.cost = 10  # Gold cost to place land
        self.label = "Land"

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))