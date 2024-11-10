import pygame

class Boat(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.position = start_pos
        self.image = pygame.image.load(r'C:\Users\Study\Pirate Tycoon\__pycache__\d68usui-ef6c334e-11b7-4f75-88b9-ecd34c5d4bf0.png')
        self.image = pygame.transform.scale(self.image, (50, 100))
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = 2
        self.active = True  # Track if the boat is still moving

    def moveTowards(self, target_pos):
        if self.active:
            directionX = target_pos[0] - self.rect.x
            directionY = target_pos[1] - self.rect.y
            distance = (directionX ** 2 + directionY ** 2) ** 0.5

            # Move the boat if it's not at the target position
            if distance > self.speed:
                self.rect.x += directionX / distance * self.speed
                self.rect.y += directionY / distance * self.speed
            else:
                self.active = False  # Stop moving when at the target position

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
