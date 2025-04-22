from models.product import Product  # This completes the circular import

class User:
    def __init__(self, name: str):
        self.name = name
        self.is_active = True
        self.products = []  # List of products owned by the user
    
    def deactivate(self):
        """Deactivate the user."""
        self.is_active = False
    
    def activate(self):
        """Activate the user."""
        self.is_active = True
    
    def add_product(self, product: Product):
        """Add a product to user's collection."""
        self.products.append(product)
        product.owner = self 