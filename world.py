from perlin_noise import PerlinNoise
from tiles import *

class TerrainGenerator:
    def __init__(self, sizeX, sizeY, randomSeed):
        self.createTerrainNoise(sizeX, sizeY, randomSeed)

        # Find noise boundaries for normalization
        flattenedValues = [element for row in self.noiseMap for element in row]
        self.lowestValue = min(flattenedValues)
        self.highestValue = max(flattenedValues)

    def createTerrainNoise(self, sizeX, sizeY, randomSeed):
        self.noiseMap = []

        # Create multiple noise layers with different frequencies
        baseNoise = PerlinNoise(octaves=3, seed=randomSeed)
        detailNoise1 = PerlinNoise(octaves=6, seed=randomSeed)
        detailNoise2 = PerlinNoise(octaves=12, seed=randomSeed)
        detailNoise3 = PerlinNoise(octaves=24, seed=randomSeed)

        gridWidth, gridHeight = sizeX + 1, sizeY + 1
        for yCoord in range(gridHeight):
            currentRow = []
            for xCoord in range(gridWidth):
                # Combine multiple noise layers with diminishing influence
                noiseValue = baseNoise([xCoord/gridWidth, yCoord/gridHeight])
                noiseValue += 0.5 * detailNoise1([xCoord/gridWidth, yCoord/gridHeight])
                noiseValue += 0.25 * detailNoise2([xCoord/gridWidth, yCoord/gridHeight])
                noiseValue += 0.125 * detailNoise3([xCoord/gridWidth, yCoord/gridHeight])
                currentRow.append(noiseValue)
            self.noiseMap.append(currentRow)

    def getNoiseMap(self):
        return self.noiseMap

    def getTiledMap(self, weights):
        weightSum = sum(weights)
        valueRange = self.highestValue - self.lowestValue

        # Determine height thresholds for each terrain type based on weights
        terrainThresholds = []
        currentThreshold = self.lowestValue
        for terrainType in ALLTERRAINTYPES:
            nextThreshold = valueRange * (weights[terrainType] / weightSum) + currentThreshold
            terrainThresholds.append(nextThreshold)
            currentThreshold = nextThreshold
        terrainThresholds[SNOW] = self.highestValue

        # Convert noise values to terrain types
        terrainGrid = []
        for noiseRow in self.noiseMap:
            terrainRow = []
            for noiseValue in noiseRow:
                for terrainType in ALLTERRAINTYPES:
                    if noiseValue <= terrainThresholds[terrainType]:
                        terrainRow.append(terrainType)
                        break
            terrainGrid.append(terrainRow)
        return terrainGrid