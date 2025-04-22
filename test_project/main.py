from utils.helpers import calculate_sum
from models.user import User
from config.settings import API_KEY
import importlib

# Dynamic import
module_name = "models.product"
dynamic_module = __import__(module_name)

def main():
    result = calculate_sum(5, 3)
    user = User("John Doe")
    print(f"Sum: {result}")
    print(f"User: {user.name}")
    print(f"API Key: {API_KEY}")
    
    # Dynamic import usage
    Product = getattr(dynamic_module, "Product")
    product = Product("Test Product")
    print(f"Product: {product.name}")

if __name__ == "__main__":
    main() 