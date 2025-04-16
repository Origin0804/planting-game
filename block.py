import pygame

# 定义常量
PLANT_COLOR = (0, 128, 0)
TILE_SIZE = 32

# 初始化字体
pygame.font.init()
FONT = pygame.font.Font(None, 24)  # 可以根据需要调整字体大小

class Block:
    def __init__(self, position, state=0):
        """
        初始化一个 Block 实例
        :param position: 土地块的位置，格式: (x, y)
        :param state: 土地块的状态，默认值为 0
        """
        self.position = position
        self.state = state

    def change_state(self, new_state):
        """
        更改土地块的状态
        :param new_state: 新的状态值
        """
        self.state = new_state

    def draw(self, screen):
        """
        在屏幕上绘制土地块
        :param screen: 游戏屏幕对象
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
    def __init__(self, position, state=0, plant=None):
        """
        初始化一个 Soil 实例
        :param position: 土地的位置，格式: (x, y)
        :param state: 土地的状态，0 表示未开垦，1 表示已开垦，默认值为 0
        :param plant: 种植的作物，None 表示没有种植
        """
        super().__init__(position, state)
        self.plant = plant
        self.growth_stage = 0
        self.last_growth_time = 0  # 添加生长时间记录属性

    def grow(self, current_time):
        """植物生长"""
        if self.plant is not None and self.state == 1:
            if current_time - self.last_growth_time >= self.plant.growth_time:
                self.growth_stage += 1
                self.last_growth_time = current_time  # 更新最后生长时间
                if self.growth_stage >= self.plant.max_stages:
                    self.growth_stage = self.plant.max_stages

    def plant_crop(self, new_plant, current_time):
        """
        在土地上种植作物
        :param new_plant: 要种植的作物
        :param current_time: 当前时间
        """
        if self.state == 1 and self.plant is None:
            self.plant = new_plant
            self.growth_stage = 0

    def harvest(self):
        """
        收获土地上的作物
        :return: 收获的作物，如果没有则返回 None
        """
        if self.plant is not None and self.growth_stage == self.plant.max_stages:
            plant = self.plant
            self.plant = None
            self.growth_stage = 0
            print(f"Harvesting plant at {self.position}")
            return plant
        return None

    def draw(self, screen):
        super().draw(screen)
        if self.plant is not None:
            x, y = self.position
            # 计算植物的大小，根据生长阶段动态变化
            plant_size = TILE_SIZE * (self.growth_stage / self.plant.max_stages)
            # 绘制植物矩形，使其居中显示在土地块上
            pygame.draw.rect(screen, PLANT_COLOR, (x + (TILE_SIZE - plant_size) // 2,
                                                   y + (TILE_SIZE - plant_size) // 2,
                                                   plant_size, plant_size))
            # 绘制生长阶段数字标注
            text = FONT.render(str(self.growth_stage), True, (255, 255, 255))  # 白色文字
            text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
            screen.blit(text, text_rect)   
    
    
    def cultivate(self):
        """开垦土地"""
        if self.state == 0:
            self.state = 1
            print(f"Land at {self.position} cultivated")