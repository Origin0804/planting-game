import pygame
import random
from block import Block, Soil
from item import Item, ItemType, Plant
from character import Character

# 初始化 Pygame
pygame.init()

# 定义常量
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
SKY_COLOR = (135, 206, 235)  # 天空蓝
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_HEIGHT = 150     # 天空区域高度
MOVE_SPEED = 5
FONT = pygame.font.Font(None, 24)
INVENTORY_WIDTH = 200
INVENTORY_HEIGHT = 300
INVENTORY_BG_COLOR = (220, 220, 220)
TIP_BG_COLOR = (255, 255, 200)
HIGHLIGHT_COLOR = (255, 0, 0)

# 创建屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Stardew Valley")

# 加载人物模型素材
player_image = pygame.image.load('character_model.png').convert_alpha()
# 调整图片大小以适应 TILE_SIZE
player_image = pygame.transform.scale(player_image, (40, 60))

# 后续代码保持不变

# Create a character instance
player = Character("Player", 
                  (WIDTH//2),  # 初始网格X
                  (HEIGHT//2)) # 初始网格Y
# 定义小麦种子
wheat_seed = Item(2, "Wheat Seed", "A seed for planting wheat")
# 定义小麦产品
wheat_product = Item(5, "Wheat", "Mature wheat, can be sold or used")
# 定义小麦植物
wheat = Plant(4, "Wheat Plant", wheat_seed, 100, wheat_product, 5)

# 定义工具
hoe = Item(1, "Hoe", ItemType.TOOL, "Used to cultivate land")

# 添加物品到玩家背包
player.add_item(hoe)
player.add_item(wheat_seed)

# 创建土地块列表
# 计算实际可放置地块的网格数量
GRID_COLS = WIDTH // TILE_SIZE
GRID_ROWS = (HEIGHT - SKY_HEIGHT) // 16  # 根据扁矩形高度计算

all_objects = []

blocks = []
for grid_y in range(GRID_ROWS):
    for grid_x in range(GRID_COLS):
        blocks.append(Soil(grid_x * TILE_SIZE, grid_y * TILE_SIZE))
for block in blocks:
    all_objects.append(('block', block))

# 游戏主循环
running = True
clock = pygame.time.Clock()
grow_timer = 0
is_inventory_open = False

while running:
    screen.fill(SKY_COLOR, (0, 0, WIDTH, SKY_HEIGHT))
    current_time = pygame.time.get_ticks()  # 每次循环获取当前时间
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_tile_x = round(player.grid_x/TILE_SIZE)*TILE_SIZE
                player_tile_y = round(player.grid_y/TILE_SIZE)*TILE_SIZE




                target_block = None
                # 精确查找玩家所在的土地块
                for block in blocks:
                    if block.grid_x == player_tile_x and block.grid_y == player_tile_y:
                        target_block = block
                        break
                if target_block:
                    print(f"Found target block at position: {target_block.grid_x}, {target_block.grid_y}")
                    land_state = target_block.state
                    has_hoe = any(item.id == 1 for item in player.inventory)
                    has_wheat_seed = any(item.id == 2 for item in player.inventory)

                    if land_state == 0:  # 土地未开垦
                        if has_hoe:

                            target_block.change_state(1)  # 假设 change_state 1 代表开垦
                    elif land_state == 1 and target_block.plant is None:  # 开垦未播种
                        if has_wheat_seed:
                            target_block.plant_crop(wheat, current_time)
                            # 从背包移除种子
                            for item in player.inventory[:]:
                                if item.id == 2:
                                    player.inventory.remove(item)
                                    break
                    else:
                        harvested = target_block.harvest()
                        if harvested:
                            player.add_item(harvested.product_item)
                            # 随机生成 1 - 2 个种子

                            seed_count = random.randint(1, 2)  # 假设种子收获范围 1 - 2
                            for _ in range(seed_count):


                                player.add_item(wheat_seed)
                            print(f"Harvested {harvested} and {seed_count} wheat seeds")
            elif event.key == pygame.K_e:
                is_inventory_open = not is_inventory_open


    all_objects.append(('player', player))

    # 按深度排序（从小到大，先绘制后面的物体）
    all_objects.sort(key=lambda x: x[1].depth)


    # 处理按键事件，使用 WASD 控制移动
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.grid_x > 0:
        player.grid_x -= MOVE_SPEED
    if keys[pygame.K_d] and player.grid_x < WIDTH - 1:
        player.grid_x += MOVE_SPEED
    if keys[pygame.K_w] and player.grid_y > 0:
        player.grid_y -= MOVE_SPEED
    if keys[pygame.K_s] and player.grid_y < HEIGHT - 1:
        player.grid_y += MOVE_SPEED

    # 植物生长逻辑
    for block in blocks:
        if isinstance(block, Soil):
            block.grow(current_time)  # 传入当前时间

    # 绘制背景
    screen.fill(WHITE)

    # 按顺序绘制所有对象
    for obj in all_objects:
        if obj[0] == 'block':
            obj[1].draw(screen)
        elif obj[0] == 'player':
            # 玩家绘制需要额外处理
            Character.draw_player(screen, player.grid_x, player.grid_y)


    #Character.draw_player(screen, player.grid_x, player.grid_y)
    
    # 在绘制高亮框的位置修改：
    player_tile_x = round(player.grid_x/TILE_SIZE)*TILE_SIZE
    player_tile_y = round(player.grid_y/TILE_SIZE)*TILE_SIZE 

    rect_width = TILE_SIZE
    rect_height = TILE_SIZE // 2
    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (player_tile_x, SKY_HEIGHT + player_tile_y/2, rect_width, rect_height), 3)

    # 显示角色坐标
    coord_text = FONT.render(f"X: {player.grid_x}, Y: {player.grid_y}", True, BLACK)
    screen.blit(coord_text, (10, 10))

    # 显示背包界面
    if is_inventory_open:
        pygame.draw.rect(screen, INVENTORY_BG_COLOR, (WIDTH - INVENTORY_WIDTH - 10, 10, INVENTORY_WIDTH, INVENTORY_HEIGHT))
        inventory_y = 20
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_item = None
        for item in player.inventory:
            color = BLACK
            if item.type == ItemType.TOOL:
                color = (0, 0, 255)
            elif item.type == ItemType.SEED:
                color = (0, 128, 0)
            elif item.type == ItemType.PRODUCT:
                color = (139, 69, 19)
            item_text = FONT.render(item.name, True, color)
            item_rect = item_text.get_rect(topleft=(WIDTH - INVENTORY_WIDTH, inventory_y))
            screen.blit(item_text, item_rect)
            if item_rect.collidepoint(mouse_x, mouse_y):
                hovered_item = item
            inventory_y += 30

        if hovered_item:
            desc_text = FONT.render(hovered_item.description, True, BLACK)
            desc_rect = desc_text.get_rect(topleft=(WIDTH - INVENTORY_WIDTH, inventory_y))
            pygame.draw.rect(screen, TIP_BG_COLOR, desc_rect.inflate(10, 5))
            screen.blit(desc_text, desc_rect)

    # 显示按键提示
    controls_text = FONT.render("W: Up, A: Left, S: Down, D: Right, SPACE: Interact, E: Inventory", True, BLACK)
    screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 30))

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 退出 Pygame
pygame.quit()
