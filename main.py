import pygame
import random
import json
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

def save_game(player, blocks):
    game_state = {
        "player": {
            "name": player.name,
            "grid_x": player.grid_x,
            "grid_y": player.grid_y,
            "inventory": [{"id": item.id, "type": item.type.value, "name": item.name, "description": item.description} for item in player.inventory]
        },
        "blocks": [
            {
                "grid_x": block.grid_x,
                "grid_y": block.grid_y,
                "state": block.state,
                "plant": {
                    "id": block.plant.id if block.plant else None,
                    "growth_stage": block.growth_stage,
                    "last_growth_time": block.last_growth_time
                } if block.plant else None
            } for block in blocks
        ]
    }
    with open("game_state.json", "w") as f:
        json.dump(game_state, f, indent=4)

# 加载游戏状态
def load_game():
    try:
        with open("game_state.json", "r") as f:
            game_state = json.load(f)
            # 重新创建玩家对象
            player_data = game_state["player"]
            player = Character(player_data["name"], player_data["grid_x"], player_data["grid_y"])
            for item_data in player_data["inventory"]:
                item_type = ItemType(item_data["type"])
                item = Item(item_data["id"], item_data["name"], item_type, item_data["description"])
                player.add_item(item)

            # 重新创建土地块
            blocks = []
            for block_data in game_state["blocks"]:
                soil = Soil((block_data["grid_x"], block_data["grid_y"]), block_data["state"])
                if block_data["plant"] and block_data["plant"]["id"] == wheat.id:
                    soil.plant = wheat
                    soil.growth_stage = block_data["plant"]["growth_stage"]
                    soil.last_growth_time = block_data["plant"]["last_growth_time"]
                blocks.append(soil)
            return player, blocks
    except FileNotFoundError:
        return None, None

# 创建屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Stardew Valley")

# 加载人物模型素材
player_image = pygame.image.load('character_model.png').convert_alpha()
# 调整图片大小以适应 TILE_SIZE
player_image = pygame.transform.scale(player_image, (40, 60))

# 加载云的图片
cloud_image = pygame.image.load('cloud.png').convert_alpha()
# 可以根据需要调整云的大小
cloud_image = pygame.transform.scale(cloud_image, (100, 50))

# 初始化云的位置和移动速度
cloud_x = random.randint(0, WIDTH)
cloud_y = random.randint(0, SKY_HEIGHT - cloud_image.get_height())
cloud_speed = 1


# 定义小麦种子
wheat_seed = Item(2, "Wheat Seed", ItemType.SEED, "A seed for planting wheat")
# 定义小麦产品
wheat_product = Item(5, "Wheat", ItemType.PRODUCT, "Mature wheat, can be sold or used")
# 定义小麦植物
wheat = Plant(4, "Wheat Plant", wheat_seed, 100, wheat_product, 5)

# 定义工具
hoe = Item(1, "Hoe", ItemType.TOOL, "Used to cultivate land")

# 初始化游戏状态
player, blocks = load_game()
if player is None or blocks is None:
    # 如果没有保存的游戏状态，初始化新游戏
    player = Character("Player", WIDTH // 2, HEIGHT // 2)
    # 添加物品到玩家背包
    player.add_item(hoe)
    player.add_item(wheat_seed)

    # 创建土地块列表
    GRID_COLS = WIDTH // TILE_SIZE
    GRID_ROWS = (HEIGHT - SKY_HEIGHT) // 16

    blocks = []
    for grid_y in range(GRID_ROWS):
        for grid_x in range(GRID_COLS):
            blocks.append(Soil((grid_x * TILE_SIZE, grid_y * TILE_SIZE)))

all_objects = []
for block in blocks:
    all_objects.append(('block', block))
# 游戏主循环
running = True
clock = pygame.time.Clock()
grow_timer = 0
is_inventory_open = False

# 添加背包相关新常量
ITEM_SIZE = 50                # 物品格子尺寸（宽高）
INVENTORY_PADDING = 10         # 背包内边距
INVENTORY_COLUMNS = 4          # 每行显示物品数量
ITEM_SPACING = 5               # 物品之间的间距
INVENTORY_TITLE_HEIGHT = 30    # 背包标题区域高度

while running:
    screen.fill(SKY_COLOR, (0, 0, WIDTH, SKY_HEIGHT))

    # 更新云的位置
    cloud_x += cloud_speed
    if cloud_x > WIDTH:
        cloud_x = -cloud_image.get_width()
        cloud_y = random.randint(0, SKY_HEIGHT - cloud_image.get_height())

    # 绘制云
    screen.blit(cloud_image, (cloud_x, cloud_y))

    current_time = pygame.time.get_ticks()  # 每次循环获取当前时间
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(player, blocks)
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_tile_x = round(player.grid_x / TILE_SIZE) * TILE_SIZE
                player_tile_y = round(player.grid_y / TILE_SIZE) * TILE_SIZE

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
                            seed_count = random.randint(wheat.seed_harvested_min, wheat.seed_harvested_max)
                            for _ in range(seed_count):
                                player.add_item(wheat_seed)
                            print(f"Harvested {harvested.product_item.name} and {seed_count} wheat seeds")
                        elif event.key == pygame.K_e:
                            # 检查背包是否已满
                            if len(player.inventory) < INVENTORY_SIZE:
                                # 背包未满，添加物品
                                player.add_item(harvested.product_item)
                                print(f"Added {harvested.product_item.name} to inventory")
                            else:
                                # 背包已满，提示无法添加
                                print("Inventory is full. Cannot add item.")
                        elif event.key == pygame.K_i:
                            is_inventory_open = not is_inventory_open
            elif event.key == pygame.K_s:
                save_game(player, blocks)
                print("Game saved.")
            elif event.key == pygame.K_l:
                player, blocks = load_game()
                if player and blocks:
                    all_objects = []
                    for block in blocks:
                        all_objects.append(('block', block))
                    print("Game loaded.")
                else:
                    print("No saved game found.")
            # 添加按下 Q 键保存游戏并退出的逻辑
            elif event.key == pygame.K_q:
                save_game(player, blocks)
                print("Game saved. Exiting...")
                running = False


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

    # 按顺序绘制所有对象
    for obj in all_objects:
        if obj[0] == 'block':
            obj[1].draw(screen)
        elif obj[0] == 'player':
            # 玩家绘制需要额外处理
            Character.draw_player(screen, player.grid_x, player.grid_y)

    # 在绘制高亮框的位置修改：
    player_tile_x = round(player.grid_x / TILE_SIZE) * TILE_SIZE
    player_tile_y = round(player.grid_y / TILE_SIZE) * TILE_SIZE

    rect_width = TILE_SIZE
    rect_height = TILE_SIZE // 2
    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (player_tile_x, SKY_HEIGHT + player_tile_y / 2, rect_width, rect_height), 3)

    # 显示角色坐标
    coord_text = FONT.render(f"X: {player.grid_x}, Y: {player.grid_y}", True, BLACK)
    screen.blit(coord_text, (10, 10))

    # 显示背包界面
    if is_inventory_open:
        # 动态计算背包尺寸（根据物品数量）
        item_count = len(player.inventory)
        rows = (item_count + INVENTORY_COLUMNS - 1) // INVENTORY_COLUMNS
        inventory_width = INVENTORY_PADDING*2 + INVENTORY_COLUMNS*(ITEM_SIZE + ITEM_SPACING)
        inventory_height = INVENTORY_PADDING*2 + INVENTORY_TITLE_HEIGHT + rows*(ITEM_SIZE + ITEM_SPACING)
        inventory_height = min(inventory_height, HEIGHT - 20)  # 限制最大高度
        inventory_rect = pygame.Rect(WIDTH - inventory_width - 10, 10, inventory_width, inventory_height)
        
        # 绘制背包背景
        pygame.draw.rect(screen, INVENTORY_BG_COLOR, inventory_rect)
        pygame.draw.rect(screen, BLACK, inventory_rect, 2)  # 添加边框
        
        # 绘制背包标题
        title_text = FONT.render("Inventory", True, BLACK)
        screen.blit(title_text, (inventory_rect.x + INVENTORY_PADDING, inventory_rect.y + INVENTORY_PADDING))
        
        # 绘制物品格子
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_rect = None
        hovered_item = None
        
        for index, item in enumerate(player.inventory):
            # 计算网格位置
            row = index // INVENTORY_COLUMNS
            col = index % INVENTORY_COLUMNS
            x = inventory_rect.x + INVENTORY_PADDING + col*(ITEM_SIZE + ITEM_SPACING)
            y = inventory_rect.y + INVENTORY_TITLE_HEIGHT + row*(ITEM_SIZE + ITEM_SPACING) + INVENTORY_PADDING
            
            # 绘制物品背景框
            item_rect = pygame.Rect(x, y, ITEM_SIZE, ITEM_SIZE)
            pygame.draw.rect(screen, WHITE, item_rect)  # 白色内背景
            # 根据物品类型绘制边框
            border_color = BLACK
            if item.type == ItemType.TOOL:
                border_color = (0, 0, 255)    # 蓝色-工具
            elif item.type == ItemType.SEED:
                border_color = (0, 128, 0)    # 绿色-种子
            elif item.type == ItemType.PRODUCT:
                border_color = (139, 69, 19)   # 棕色-产品
            pygame.draw.rect(screen, border_color, item_rect, 2)
            
            # 绘制物品名称（居中显示）
            item_text = FONT.render(item.name, True, BLACK)
            text_pos = (x + (ITEM_SIZE - item_text.get_width())//2, 
                        y + (ITEM_SIZE - item_text.get_height())//2)
            screen.blit(item_text, text_pos)
            
            # 悬停检测
            if item_rect.collidepoint(mouse_x, mouse_y):
                hovered_rect = item_rect
                hovered_item = item
        
        # 绘制悬停高亮和提示
        if hovered_item:
            # 高亮当前悬停的物品格子
            if hovered_rect:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, hovered_rect, 3)
            
            # 显示物品描述（跟随鼠标位置）
            desc_text = FONT.render(hovered_item.description, True, BLACK)
            # 计算提示位置（避免超出屏幕）
            tip_x = mouse_x + 10
            tip_y = mouse_y + 10
            if tip_x + desc_text.get_width() + 20 > WIDTH:
                tip_x = mouse_x - desc_text.get_width() - 20
            if tip_y + desc_text.get_height() + 10 > HEIGHT:
                tip_y = mouse_y - desc_text.get_height() - 10
            # 绘制提示背景和文字
            desc_bg_rect = desc_text.get_rect(topleft=(tip_x, tip_y)).inflate(10, 5)
            pygame.draw.rect(screen, TIP_BG_COLOR, desc_bg_rect)
            screen.blit(desc_text, (tip_x, tip_y))

    # 显示按键提示
    controls_text = FONT.render("W: Up, A: Left, S: Down, D: Right, SPACE: Interact, E: Inventory, S: Save, L: Load", True, BLACK)
    screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 30))

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 退出 Pygame
pygame.quit()
