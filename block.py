import pygame

# 定义常量
PLANT_COLOR = (0, 128, 0)
TILE_SIZE = 32

# 初始化字体
pygame.font.init()
FONT = pygame.font.Font(None, 24)  # 可以根据需要调整字体大小
SMALL_FONT = pygame.font.Font(None, 18)

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
        self.is_watered = False  # 是否已浇水
        self.water_time = 0  # 浇水时间

    def water(self, current_time):
        """浇水"""
        if self.state == 1 and not self.is_watered:
            self.is_watered = True
            self.water_time = current_time
            return True
        return False

    def grow(self, current_time):
        """植物生长"""
        if self.plant is not None and self.state == 1:
            # 计算生长时间，浇水后生长速度加快
            growth_time = self.plant.growth_time
            if self.is_watered:
                growth_time = int(growth_time / self.plant.water_boost)
            
            if current_time - self.last_growth_time >= growth_time:
                self.growth_stage += 1
                self.last_growth_time = current_time  # 更新最后生长时间
                # 每次生长后，浇水效果消失
                self.is_watered = False
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
            self.last_growth_time = current_time

    def harvest(self):
        """
        收获土地上的作物
        :return: 收获的作物，如果没有则返回 None
        """
        if self.plant is not None and self.growth_stage == self.plant.max_stages:
            plant = self.plant
            self.plant = None
            self.growth_stage = 0
            self.is_watered = False
            print(f"Harvesting plant at {self.position}")
            return plant
        return None

    def draw(self, screen):
        super().draw(screen)
        x, y = self.position
        
        # 如果已浇水，显示水滴效果
        if self.is_watered and self.state == 1:
            # 绘制淡蓝色覆盖层表示浇水
            water_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            water_surface.fill((100, 149, 237, 80))  # 半透明蓝色
            screen.blit(water_surface, (x, y))
        
        if self.plant is not None:
            # 使用植物自己的颜色
            plant_color = getattr(self.plant, 'color', PLANT_COLOR)
            # 计算植物的大小，根据生长阶段动态变化
            plant_size = max(4, int(TILE_SIZE * (self.growth_stage / self.plant.max_stages)))
            # 绘制植物矩形，使其居中显示在土地块上
            pygame.draw.rect(screen, plant_color, (x + (TILE_SIZE - plant_size) // 2,
                                                   y + (TILE_SIZE - plant_size) // 2,
                                                   plant_size, plant_size))
            # 绘制生长阶段数字标注
            text = FONT.render(str(self.growth_stage), True, (255, 255, 255))  # 白色文字
            text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
            screen.blit(text, text_rect)
            
            # 如果成熟，显示感叹号
            if self.growth_stage == self.plant.max_stages:
                ready_text = SMALL_FONT.render("!", True, (255, 255, 0))
                screen.blit(ready_text, (x + TILE_SIZE - 10, y + 2))
    
    
    def cultivate(self):
        """开垦土地"""
        if self.state == 0:
            self.state = 1
            print(f"Land at {self.position} cultivated")