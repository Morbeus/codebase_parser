from models.user import User  # This creates a circular import
from utils.helpers import calculate_product

class Product:
    def __init__(self, name: str):
        self.name = name
        self.price = 0
        self.owner = None
    
    def set_price(self, price: float):
        """Set the product price."""
        self.price = price
    
    def set_owner(self, user: User):
        """Set the product owner."""
        self.owner = user
        # This creates a circular reference
        user.products.append(self)
    
    def calculate_discount(self, percentage: float) -> float:
        """Calculate discounted price."""
        return calculate_product(self.price, (100 - percentage) / 100) 