import pygame

class Path(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((100, 100, 100))  # Gray color for roads
        self.rect = self.image.get_rect(topleft=position)
        self.position = position
        self.cost = 20  # Gold cost to place a road
        self.label = "Path"

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))

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
