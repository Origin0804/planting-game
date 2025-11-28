class Character:
    def __init__(self, name, x, y, gold=100):
        """
        Initialize a Character instance
        :param name: The name of the character
        :param x: The initial x-coordinate of the character
        :param y: The initial y-coordinate of the character
        :param gold: Initial gold amount
        """
        self.name = name
        self.x = x
        self.y = y
        self.inventory = []  # Item list
        self.gold = gold  # 金币系统
        self.direction = "down"  # 角色朝向: up, down, left, right
        self.selected_seed_index = 0  # 当前选择的种子索引

    def add_item(self, item):
        """
        Add an item to the character's inventory with stacking support
        :param item: The item instance to be added
        """
        # 如果物品可堆叠，查找现有堆叠
        if hasattr(item, 'stackable') and item.stackable:
            for inv_item in self.inventory:
                if inv_item['item'].id == item.id:
                    inv_item['count'] += 1
                    return
            # 没有找到现有堆叠，创建新的
            self.inventory.append({'item': item, 'count': 1})
        else:
            # 不可堆叠的物品（如工具）
            self.inventory.append({'item': item, 'count': 1})

    def remove_item(self, item_id, count=1):
        """
        Remove an item with the specified ID from the character's inventory
        :param item_id: The ID of the item to be removed
        :param count: Number of items to remove
        :return: The removed item if successful, None otherwise
        """
        for inv_item in self.inventory:
            if inv_item['item'].id == item_id:
                if inv_item['count'] >= count:
                    inv_item['count'] -= count
                    if inv_item['count'] <= 0:
                        self.inventory.remove(inv_item)
                    return inv_item['item']
        return None

    def get_inventory(self):
        """
        Get the character's inventory
        :return: The character's inventory list
        """
        return self.inventory
    
    def has_item(self, item_id):
        """
        Check if player has item
        :param item_id: The ID of the item to check
        :return: True if has item, False otherwise
        """
        for inv_item in self.inventory:
            if inv_item['item'].id == item_id and inv_item['count'] > 0:
                return True
        return False
    
    def get_item_count(self, item_id):
        """
        Get the count of an item in inventory
        :param item_id: The ID of the item to check
        :return: Count of the item
        """
        for inv_item in self.inventory:
            if inv_item['item'].id == item_id:
                return inv_item['count']
        return 0
    
    def add_gold(self, amount):
        """Add gold to player"""
        self.gold += amount
    
    def spend_gold(self, amount):
        """Spend gold, returns True if successful"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def get_seeds(self):
        """Get all seeds in inventory"""
        from item import ItemType
        seeds = []
        for inv_item in self.inventory:
            if inv_item['item'].type == ItemType.SEED and inv_item['count'] > 0:
                seeds.append(inv_item)
        return seeds
    
    def get_selected_seed(self):
        """Get currently selected seed"""
        seeds = self.get_seeds()
        if seeds and 0 <= self.selected_seed_index < len(seeds):
            return seeds[self.selected_seed_index]['item']
        return None
    
    def cycle_seed(self):
        """Cycle through available seeds"""
        seeds = self.get_seeds()
        if seeds:
            self.selected_seed_index = (self.selected_seed_index + 1) % len(seeds)
            return self.get_selected_seed()
        return None
