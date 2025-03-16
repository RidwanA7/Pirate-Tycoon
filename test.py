from world import World
from worldDrawer import *
from tiles import *
import random
from perlin_noise import PerlinNoise

cameraX, cameraY = 0, 0
screen = pygame.display.set_mode((800, 600))

    
def cameraMovement(keys, cameraX, cameraY, speed):
    if keys[pygame.K_LEFT]:
        cameraX += speed
    if keys[pygame.K_RIGHT]:
        cameraX -= speed
    if keys[pygame.K_UP]:
        cameraY += speed
    if keys[pygame.K_DOWN]:
        cameraY -= speed
    return cameraX, cameraY

def test_generate_world(weights,random_seed):
    world_drawer = WorldDrawer()
    world = World(WORLD_X, WORLD_Y, random_seed)
    tile_map = world.get_tiled_map(weights)
    #world_drawer.draw(tile_map, cameraX, cameraY, wait_for_key = True)
    return world_drawer, tile_map, world
#weights = [50, 50, 150, 50, 300, 0, 0]#
weights = [20, 40, 70, 100, 250, 0, 0]
randomSeed = random.randint(0, 100)


world_drawer, tile_map, wolrd = test_generate_world(weights, randomSeed)
water = world_drawer.tilesheet.subsurface((208, 176, TILESIZE, TILESIZE))

background = pygame.Surface(screen.get_size())
# Tile the water texture across the background surface
for y in range(0, WINDOW_HEIGHT, TILESIZE):
    for x in range(0, WINDOW_WIDTH, TILESIZE):
        background.blit(water, (x, y))

clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    cameraX, cameraY = cameraMovement(keys, cameraX, cameraY, speed=5)

    # Draw background water first (pre-rendered for efficiency)
    world_drawer.display_surface.blit(background, (0, 0))

    # Draw dynamically generated terrain
    world_drawer.draw(tile_map, cameraX, cameraY, wait_for_key=False)

    pygame.display.flip()
    clock.tick(30)