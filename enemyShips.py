import pygame
from bullet import Bullet

class EnemyShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 30))  # Enemy ship size
        self.image.fill((255, 0, 0))  # Red colour for enemy ships
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 100

    def moveTowardsPlayer(self, playerShip):
        # Calculate direction to the player
        playerX, playerY = playerShip.rect.center
        dx = playerX - self.rect.centerx
        dy = playerY - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        if distance != 0:
            dx /= distance
            dy /= distance

        # Reduce speed for the enemy ship
        enemySpeed = 1.5  # Slower than the player's speed
        self.rect.x += dx * enemySpeed
        self.rect.y += dy * enemySpeed

    def shootPlayer(self, playerShip, bulletsGroup):
        if pygame.time.get_ticks() % 60 == 0:  # Shoot periodically
            dx = playerShip.rect.centerx - self.rect.centerx
            dy = playerShip.rect.centery - self.rect.centery
            distance = (dx**2 + dy**2)**0.5
            if distance != 0:
                dx /= distance
                dy /= distance

            # Set a bullet speed (adjust as needed)
            bulletSpeed = 5
            velocity_x = dx * bulletSpeed
            velocity_y = dy * bulletSpeed

            # Create the bullet
            bullet = Bullet(self.rect.centerx, self.rect.centery, velocity_x, velocity_y)
            bulletsGroup.add(bullet)
