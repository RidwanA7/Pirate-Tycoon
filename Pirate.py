import pygame
import random
import time

class Pirate:
    def __init__(self, position, payment):
        self.position = position
        self.active = False  # Becomes active when the boat reaches the entrance dock
        self.speed = 2
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.inCooldown = False
        self.objectStopTime = None
        self.objectCooldownEnd = None
        self.nearObject = False
        self.payment = payment
        self.sleep = 50
        self.hunger = 50
        self.satisfaction = 50
        self.satisfactionTimeDecrease = time.time()
        self.image = pygame.image.load(r'C:\Users\Study\Pirate Tycoon\__pycache__\1675450476_luffy-sprite.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=self.position)

    def moveTowards(self, targetPosition):
        if self.position[0] < targetPosition[0]:
            self.position[0] += self.speed
        elif self.position[0] > targetPosition[0]:
            self.position[0] -= self.speed
        if self.position[1] < targetPosition[1]:
            self.position[1] += self.speed
        elif self.position[1] > targetPosition[1]:
            self.position[1] -= self.speed
        # Update rect position to match the new position
        self.rect.center = self.position

    def updatePirateStats(self):
        if time.time() - self.satisfactionTimeDecrease >= 15:
            self.hunger = max(0, self.hunger - 20)
            self.sleep = max(0, self.sleep - 20)
            self.satisfactionTimeDecrease = time.time()

    def checkCooldown(self):
        if self.objectCooldownEnd and time.time() > self.objectCooldownEnd:
            self.inCooldown = False

    def pay(self, object):
        self.inCooldown = True
        self.objectCooldownEnd = time.time() + 10  # 10-second cooldown
        self.nearObject = False
        self.objectStopTime = None
        if object == "Tent":
            self.payment = 400
            self.sleep += 10
        elif object == "Restaurant":
            self.payment = 800
            self.hunger += 10
        return self.payment

    def move(self):
        # Random movement if not near the object or after cooldown
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed
        self.rect.center = self.position
        # Randomly change direction occasionally
        if random.random() < 0.02:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        # Checks screen boundary
        self.position[0] = max(0, min(self.position[0], 800))
        self.position[1] = max(0, min(self.position[1], 600))

    def update(self, object):
        self.payment = 0
        self.updatePirateStats()
        self.checkCooldown()
        if self.active:
            # Check if near an object
            if self.nearObject and not self.inCooldown:
                if self.objectStopTime is None:  # Start the 5-second wait at the object
                    self.objectStopTime = time.time()
                elif time.time() - self.objectStopTime >= 5:
                    self.payment = self.pay(object)
            self.move()
        return self.payment
    def drawSatisfactionBar(self, screen, cameraX, cameraY, zoomLevel):
        
        barX = (self.position[0] * zoomLevel) + cameraX - (25 * zoomLevel)
        barY = (self.position[1] * zoomLevel) + cameraY - (40 * zoomLevel)

        
        barWidth = int(50 * zoomLevel)
        barHeight = int(8 * zoomLevel)
        spacing = int(2 * zoomLevel)  # Space between bars, also scaled

        # Calculate filled width for hunger and sleep bars based on zoomed bar width
        hungerFillWidth = int((self.hunger / 100) * barWidth)
        sleepFillWidth = int((self.sleep / 100) * barWidth)

        # Draw hunger bar
        pygame.draw.rect(screen, (100, 100, 100), (barX, barY, barWidth, barHeight))
        pygame.draw.rect(screen, (255, 0, 0), (barX, barY, hungerFillWidth, barHeight))

        # Draw sleep bar
        pygame.draw.rect(screen, (100, 100, 100), (barX, barY + barHeight + spacing, barWidth, barHeight))
        pygame.draw.rect(screen, (0, 0, 255), (barX, barY + barHeight + spacing, sleepFillWidth, barHeight))

        # Adjust font size based on zoom level
        fontSize = int(20 * zoomLevel)  # Scale font size
        font = pygame.font.Font(None, fontSize)

        # Render labels with adjusted size
        hungerLabel = font.render("Hunger", True, (255, 255, 255))  # White text
        sleepLabel = font.render("Sleep", True, (255, 255, 255))  # White text

        # Adjust label positions based on zoom
        screen.blit(hungerLabel, (barX - hungerLabel.get_width() - int(5 * zoomLevel), barY))
        screen.blit(sleepLabel, (barX - sleepLabel.get_width() - int(5 * zoomLevel), barY + barHeight + spacing))

    def draw(self, screen, cameraX, cameraY, zoomLevel):
        if self.active:
            # Scale the image based on zoom factor
            scaledImage = pygame.transform.scale(self.image,
                                                 (int(self.image.get_width() * zoomLevel),
                                                  int(self.image.get_height() * zoomLevel)))

            # Adjust position based on zoom factor
            scaledX = (self.position[0] * zoomLevel) + cameraX - scaledImage.get_width() // 2
            scaledY = (self.position[1] * zoomLevel) + cameraY - scaledImage.get_height() // 2

            # Draw the scaled image at the adjusted position
            screen.blit(scaledImage, (scaledX, scaledY))

            # Adjust the satisfaction bar position based on zoom
            self.drawSatisfactionBar(screen, cameraX, cameraY, zoomLevel)


