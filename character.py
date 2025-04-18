import pygame
from block import TILE_SIZE

SCREEN_HEIGHT = 600  # 与main.py中的HEIGHT保持一致
SKY_HEIGHT = 150     # 天空区域高度

class Character:
    def __init__(self, name, grid_x, grid_y):
        """
        Initialize a Character instance
        :param name: The name of the character
        :param grid_x: The initial grid x-coordinate of the character
        :param grid_y: The initial grid y-coordinate of the character
        """
        self.name = name
        self.grid_x = grid_x  # 网格坐标X
        self.grid_y = grid_y  # 网格坐标Y
        self.screen_x = 0      # 实际屏幕坐标（通过grid计算）
        self.screen_y = 0
        self.inventory = []  # Item list

    @property
    def depth(self):
        """用于绘制排序的深度值"""
        return self.grid_x + self.grid_y * 100

    def add_item(self, item):
        """
        Add an item to the character's inventory
        :param item: The item instance to be added
        """
        self.inventory.append(item)

    def remove_item(self, item_id):
        """
        Remove an item with the specified ID from the character's inventory
        :param item_id: The ID of the item to be removed
        :return: The removed item if successful, None otherwise
        """
        for item in self.inventory:
            if item.id == item_id:
                self.inventory.remove(item)
                return item
        return None

    def get_inventory(self):
        """
        Get the character's inventory
        :return: The character's inventory list
        """
        return self.inventory

    def draw_player(screen, grid_x, grid_y):
        # 计算玩家在扁矩形系统中的位置

        # 将贴图加载移到函数外部（只需加载一次）
        if not hasattr(Character, 'player_image'):
            Character.player_image = pygame.transform.scale(
                pygame.image.load('character_model.png').convert_alpha(), 
                (40, 60)
            )
        screen_x = grid_x
        screen_y = SKY_HEIGHT + grid_y / 2 - 60  # 站在地块上方
        screen.blit(Character.player_image, (screen_x, screen_y))
