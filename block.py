import pygame
import random

# 定义常量
PLANT_COLOR = (0, 128, 0)
SCREEN_HEIGHT = 600  # 与main.py中的HEIGHT保持一致
SKY_HEIGHT = 150     # 天空区域高度
TILE_SIZE = 32

# 初始化字体
pygame.font.init()
FONT = pygame.font.Font(None, 24)  # 可以根据需要调整字体大小

WHEAT_TEXTURES = [
    pygame.transform.scale(pygame.image.load(f'wheat{i}.png'), (TILE_SIZE, TILE_SIZE)) 
    for i in range(1, 6)
]
# 在文件顶部添加
SCREEN_HEIGHT = 600  # 与main.py中的HEIGHT保持一致
SKY_HEIGHT = 150     # 天空区域高度

# 一次性加载所有泥土贴图
SOIL_TEXTURES = [
    pygame.transform.scale(pygame.image.load(f'soil{i}.png'), (32, 16)) 
    for i in range(1, 5)
]

class Block:
    def __init__(self, grid_x, grid_y):
        """
        :param grid_x: 网格坐标X (从0开始的整数)
        :param grid_y: 网格坐标Y (从0开始的整数)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.state = 0  # 0 表示未开垦，1 表示已开垦
        # 转换为屏幕坐标（扁矩形：宽度32，高度16）
        self.screen_x = grid_x
        self.screen_y = SKY_HEIGHT + grid_y / 2 # 留出天空区域
        
    @property
    def depth(self):
        """用于绘制排序的深度值"""
        return self.grid_x + self.grid_y * 100

    def draw(self, screen):
        # 扁矩形绘制（宽32，高16）
        pygame.draw.rect(screen, (150, 80, 30), 
                        (self.screen_x, self.screen_y, 32, 16))

    def change_state(self, new_state):
        """
        更改土地块的状态
        :param new_state: 新的状态值
        """
        self.state = new_state



class Soil(Block):
    def __init__(self, position, state=0, plant=None):
        """
        初始化一个 Soil 实例
        :param position: 土地的位置，格式: (x, y)
        :param state: 土地的状态，0 表示未开垦，1 表示已开垦，默认值为 0
        :param plant: 种植的作物，None 表示没有种植
        :param picture_number: 贴图编号，默认为 0
        """
        super().__init__(position, state)
        self.plant = plant
        self.growth_stage = 0
        self.last_growth_time = 0  # 添加生长时间记录属性
        # 随机选择 0 到 3 之间的索引，对应 SOIL_TEXTURES 列表
        self.picture_index = random.randint(0, 3)

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
            print(f"Harvesting {plant.name} at {self.grid_x}, {self.grid_y}")
            return plant
        return None
    def draw(self, screen):
        # 从预加载的贴图列表中获取对应的泥土贴图
        soil_image = SOIL_TEXTURES[self.picture_index]
        screen.blit(soil_image, (self.screen_x, self.screen_y))

        if self.plant is not None:
            x, y = self.screen_x, self.screen_y
            # 根据生长阶段选择贴图
            stage = min(self.growth_stage, len(WHEAT_TEXTURES) - 1)
            plant_image = WHEAT_TEXTURES[stage]
            plant_y = y - plant_image.get_height() + 16
            screen.blit(plant_image, (x, plant_y))
            # 调整生长阶段数字标注的位置
            text = FONT.render(str(self.growth_stage), True, (255, 255, 255))  # 白色文字
            # 让提示框显示在植物上方
            text_rect = text.get_rect(center=(x + TILE_SIZE // 2, plant_y - 10))
            screen.blit(text, text_rect)
        elif self.state == 1:
            # 绘制未开垦的土地
            pygame.draw.rect(screen, (139, 69, 19), (self.screen_x, self.screen_y, 32, 16))

    
    
    def cultivate(self):
        """开垦土地"""
        if self.state == 0:
            self.state = 1
            print(f"Land at {self.grid_x}, {self.grid_y} cultivated")
