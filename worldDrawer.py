import pygame
from tiles import *


class WorldDrawer:
    def __init__(self):
        # Initialize display
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

        # Load and process tileset
        self.tilesetImage = pygame.image.load(TILESHEETPATH).convert_alpha()
        self.gridLocationsDetected = False

        # Extract all tile variants for each terrain type
        self.terrainImagesets = []
        for terrainType in ALLTERRAINTYPES:
            tileVariants = []
            for tileCoords in TERRAINTILES[terrainType]:
                tileVariants.append(self.tilesetImage.subsurface((tileCoords[0], tileCoords[1], TILESIZE, TILESIZE)))
            self.terrainImagesets.append(tileVariants)

    def draw(self, heightMap, cameraX, cameraY, waitForKey):
        self.renderTerrain(heightMap, cameraX, cameraY)
        if waitForKey:
            self.pauseForInput()

    def pauseForInput(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                break

    def renderTerrain(self, terrainTypeMap, cameraX, cameraY):
        landCoordinates = []
        for yPos, row in enumerate(terrainTypeMap):
            for xPos, value in enumerate(row):
                if xPos == WORLDX or yPos == WORLDY:
                    continue
                
                # Determine terrain types at the four corners of this tile
                cornerTerrainTypes = []
                cornerTerrainTypes.append(terrainTypeMap[yPos + 1][xPos + 1])
                cornerTerrainTypes.append(terrainTypeMap[yPos + 1][xPos])
                cornerTerrainTypes.append(terrainTypeMap[yPos][xPos + 1])
                cornerTerrainTypes.append(terrainTypeMap[yPos][xPos])

                # Find appropriate tile variant based on corner types
                for terrainType in ALLTERRAINTYPES:
                    if terrainType in cornerTerrainTypes:
                        variantIndex = self.calculateTileVariant(cornerTerrainTypes, terrainType)
                        tileImage = self.terrainImagesets[terrainType][variantIndex]
                        break

                # Apply camera offset for scrolling effect
                displayX = xPos * TILESIZE + cameraX
                displayY = yPos * TILESIZE + cameraY
                if terrainType == 4 or terrainType == 3:
                    landCoordinates.append((xPos * TILESIZE, yPos * TILESIZE))
                
                self.screen.blit(tileImage, (displayX, displayY))
        
        if not self.gridLocationsDetected:
            self.gridLocationsDetected = True
            return landCoordinates

    def calculateTileVariant(self, cornerTypes, terrainType):
        variantCode = 0
        for bitPosition, cornerType in enumerate(cornerTypes):
            if cornerType == terrainType:
                variantCode += 2 ** bitPosition
        return variantCode
