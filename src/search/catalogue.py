import pandas as pd
import os
import random

def load_catalogue(max_products: int = 2000) -> list:
    csv_path = "data/fashion-dataset/styles.csv"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df = df.dropna(subset=['productDisplayName', 'baseColour', 'articleType'])

    categories = df['articleType'].unique()
    per_category = 25

    sampled = []
    for category in categories:
        category_df = df[df['articleType'] == category]
        sample_size = min(per_category, len(category_df))
        sampled.append(category_df.sample(n=sample_size, random_state=42))

    df = pd.concat(sampled)

    products = []
    for _, row in df.iterrows():
        product = {
            "id": str(row['id']),
            "name": row['productDisplayName'],
            "category": row['articleType'].lower(),
            "colour": row['baseColour'].lower(),
            "style": row['usage'].lower() if pd.notna(row['usage']) else "casual",
            "material": "unknown",
            "gender": row['gender'].lower(),
            "price": _estimate_price(row['articleType'], row['masterCategory'], str(row['id'])),
            "season": row['season'] if pd.notna(row['season']) else "All Season",
            "image_url": f"https://storage.googleapis.com/shopping-agent-images/products/{row['id']}.jpg"
        }
        products.append(product)

    print(f"Loaded {len(products)} products from Fashion Dataset")
    return products

def _estimate_price(article_type: str, master_category: str, product_id: str) -> int:
    random.seed(int(product_id) if product_id.isdigit() else hash(product_id))

    price_ranges = {
        "Watches": (2999, 15999), "Handbags": (1999, 8999),
        "Formal Shoes": (2999, 8999), "Casual Shoes": (1499, 5999),
        "Sports Shoes": (1999, 6999), "Heels": (1499, 4999),
        "Flats": (999, 3499), "Sandals": (799, 2999),
        "Shirts": (799, 2999), "Jeans": (1299, 4499),
        "Tops": (699, 2499), "Dresses": (1499, 5999),
        "Kurtas": (899, 3499), "Jackets": (1999, 6999),
        "Sweaters": (999, 3999), "Sweatshirts": (799, 2999),
        "Shorts": (599, 1999), "Trousers": (999, 3999),
        "Sunglasses": (799, 3999), "Belts": (499, 1999),
        "Wallets": (599, 2499), "Caps": (399, 1299),
        "Socks": (199, 599), "Perfumes": (1499, 5999),
        "Jewellery": (499, 3999),
    }

    for key, (low, high) in price_ranges.items():
        if key.lower() in article_type.lower():
            return random.randint(low, high)

    if master_category == "Footwear":
        return random.randint(1499, 5999)
    elif master_category == "Accessories":
        return random.randint(499, 3999)
    elif master_category == "Apparel":
        return random.randint(699, 3999)

    return random.randint(699, 2999)

def _get_fallback_catalogue() -> list:
    """Small hardcoded catalogue used when CSV not available on Cloud Run."""
    return [
        {"id": "1", "name": "Nike Air Max 270", "category": "shoes", "colour": "white", "style": "sporty", "material": "mesh", "gender": "unisex", "price": 8999, "season": "Summer", "image_url": "https://picsum.photos/seed/1/300/400"},
        {"id": "2", "name": "Adidas Stan Smith", "category": "shoes", "colour": "white", "style": "casual", "material": "leather", "gender": "unisex", "price": 6999, "season": "All Season", "image_url": "https://picsum.photos/seed/2/300/400"},
        {"id": "3", "name": "Levi's Men Slim Fit Jeans", "category": "jeans", "colour": "blue", "style": "casual", "material": "denim", "gender": "men", "price": 2499, "season": "All Season", "image_url": "https://picsum.photos/seed/3/300/400"},
        {"id": "4", "name": "Arrow Formal Black Shoes", "category": "formal shoes", "colour": "black", "style": "formal", "material": "leather", "gender": "men", "price": 5999, "season": "All Season", "image_url": "https://picsum.photos/seed/4/300/400"},
        {"id": "5", "name": "Titan Women Silver Watch", "category": "watches", "colour": "silver", "style": "casual", "material": "metal", "gender": "women", "price": 4999, "season": "All Season", "image_url": "https://picsum.photos/seed/5/300/400"},
        {"id": "6", "name": "Puma Running Shoes Black", "category": "sports shoes", "colour": "black", "style": "sporty", "material": "mesh", "gender": "unisex", "price": 4499, "season": "All Season", "image_url": "https://picsum.photos/seed/6/300/400"},
        {"id": "7", "name": "H&M Women Floral Dress", "category": "dresses", "colour": "multicolor", "style": "casual", "material": "cotton", "gender": "women", "price": 1999, "season": "Summer", "image_url": "https://picsum.photos/seed/7/300/400"},
        {"id": "8", "name": "Louis Philippe Formal Shirt", "category": "shirts", "colour": "white", "style": "formal", "material": "cotton", "gender": "men", "price": 1799, "season": "All Season", "image_url": "https://picsum.photos/seed/8/300/400"},
        {"id": "9", "name": "Fastrack Unisex Sunglasses", "category": "sunglasses", "colour": "black", "style": "casual", "material": "plastic", "gender": "unisex", "price": 1299, "season": "Summer", "image_url": "https://picsum.photos/seed/9/300/400"},
        {"id": "10", "name": "Wildcraft Backpack Blue", "category": "bags", "colour": "blue", "style": "sporty", "material": "nylon", "gender": "unisex", "price": 2299, "season": "All Season", "image_url": "https://picsum.photos/seed/10/300/400"},
        {"id": "11", "name": "Mango Women Blazer", "category": "jackets", "colour": "black", "style": "formal", "material": "polyester", "gender": "women", "price": 3999, "season": "Winter", "image_url": "https://picsum.photos/seed/11/300/400"},
        {"id": "12", "name": "Woodland Men Casual Shoes", "category": "casual shoes", "colour": "brown", "style": "casual", "material": "leather", "gender": "men", "price": 3499, "season": "All Season", "image_url": "https://picsum.photos/seed/12/300/400"},
        {"id": "13", "name": "Nike Dri-FIT Sports Tshirt", "category": "tshirts", "colour": "blue", "style": "sporty", "material": "polyester", "gender": "men", "price": 1499, "season": "Summer", "image_url": "https://picsum.photos/seed/13/300/400"},
        {"id": "14", "name": "Zara Women Handbag", "category": "handbags", "colour": "beige", "style": "casual", "material": "leather", "gender": "women", "price": 4499, "season": "All Season", "image_url": "https://picsum.photos/seed/14/300/400"},
        {"id": "15", "name": "Reebok Classic Sneakers", "category": "shoes", "colour": "white", "style": "casual", "material": "leather", "gender": "unisex", "price": 5499, "season": "All Season", "image_url": "https://picsum.photos/seed/15/300/400"},
        {"id": "16", "name": "Raymond Men Formal Trousers", "category": "trousers", "colour": "grey", "style": "formal", "material": "wool", "gender": "men", "price": 2799, "season": "All Season", "image_url": "https://picsum.photos/seed/16/300/400"},
        {"id": "17", "name": "Casio Digital Sports Watch", "category": "watches", "colour": "black", "style": "sporty", "material": "plastic", "gender": "unisex", "price": 2999, "season": "All Season", "image_url": "https://picsum.photos/seed/17/300/400"},
        {"id": "18", "name": "W Women Kurta", "category": "kurtas", "colour": "red", "style": "ethnic", "material": "cotton", "gender": "women", "price": 1599, "season": "All Season", "image_url": "https://picsum.photos/seed/18/300/400"},
        {"id": "19", "name": "Skybags Travel Backpack", "category": "bags", "colour": "black", "style": "casual", "material": "polyester", "gender": "unisex", "price": 1799, "season": "All Season", "image_url": "https://picsum.photos/seed/19/300/400"},
        {"id": "20", "name": "Van Heusen Men Polo Tshirt", "category": "tshirts", "colour": "navy blue", "style": "casual", "material": "cotton", "gender": "men", "price": 1299, "season": "All Season", "image_url": "https://picsum.photos/seed/20/300/400"},
    ]

def get_catalogue() -> list:
    """
    Loads catalogue from CSV if available (local).
    Falls back to hardcoded catalogue if CSV not found (Cloud Run).
    """
    csv_path = "data/fashion-dataset/styles.csv"
    if os.path.exists(csv_path):
        return load_catalogue()
    else:
        print("CSV not found — using fallback catalogue for Cloud Run")
        return _get_fallback_catalogue()

CATALOGUE = get_catalogue()