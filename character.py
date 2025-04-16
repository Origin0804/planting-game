class Character:
    def __init__(self, name, x, y):
        """
        Initialize a Character instance
        :param name: The name of the character
        :param x: The initial x-coordinate of the character
        :param y: The initial y-coordinate of the character
        """
        self.name = name
        self.x = x
        self.y = y
        self.inventory = []  # Item list

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
