import pygame

# 定义常量
PLANT_COLOR = (0, 128, 0)
TILE_SIZE = 32

class Block:
    def __init__(self, position, state=0):
        """
        Initialize a Block instance
        :param position: The position of the land block, format: (x, y)
        :param state: The state of the land block, default is 0
        """
        self.position = position
        self.state = state

    def change_state(self, new_state):
        """
        Change the state of the land block
        :param new_state: The new state value
        """
        self.state = new_state

    def draw(self, screen):
        """
        Draw the land block on the screen
        :param screen: The game screen object
        """
        x, y = self.position
        LAND_COLOR = (139, 69, 19)
        CULTIVATED_COLOR = (160, 82, 45)
        # Bug 修复：这里应该绘制土地块大小的矩形，而不是整个屏幕大小
        if self.state == 0:
            pygame.draw.rect(screen, LAND_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)
        elif self.state == 1:
            pygame.draw.rect(screen, CULTIVATED_COLOR, (x, y, TILE_SIZE, TILE_SIZE))


class Soil(Block):
    def __init__(self, position, state=0, plant=0):
        """
        Initialize a Soil instance
        :param position: The position of the land, format: (x, y)
        :param state: The state of the land, 0 for uncultivated, 1 for cultivated, default is 0
        :param plant: The planted crop, 0 for no plant
        """
        super().__init__(position, state)
        self.plant = plant
        self.growth_stage = 0  # Plant growth stage

    def plant_crop(self, new_plant):
        """
        Plant a crop on the land
        :param new_plant: The crop to be planted
        """
        if self.state == 1 and self.plant == 0:
            self.plant = new_plant
            self.growth_stage = 0

    def grow(self):
        """
        The plant grows
        """
        if self.plant != 0:
            self.growth_stage += 1
            if self.growth_stage >= 5:  # Assume the plant matures after 5 growth stages
                self.growth_stage = 5

    def harvest(self):
        """
        Harvest the crop on the land
        :return: The harvested crop, 0 if no crop
        """
        if self.plant != 0 and self.growth_stage == 5:
            harvested_plant = self.plant
            self.plant = 0
            self.growth_stage = 0
            return harvested_plant
        return 0

    def draw(self, screen):
        super().draw(screen)
        if self.plant != 0:
            x, y = self.position
            # 计算植物的大小，根据生长阶段动态变化
            plant_size = TILE_SIZE * (self.growth_stage / 5)
            # 绘制植物矩形，使其居中显示在土地块上
            pygame.draw.rect(screen, PLANT_COLOR, (x + (TILE_SIZE - plant_size) // 2,
                                                   y + (TILE_SIZE - plant_size) // 2,
                                                   plant_size, plant_size))
