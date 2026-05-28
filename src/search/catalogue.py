import pandas as pd
import os
import random

def load_catalogue(max_products: int = 2000) -> list:
    csv_path = "data/fashion-dataset/styles.csv"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df = df.dropna(subset=['productDisplayName', 'baseColour', 'articleType'])

    # Stratified sampling — take equal products per category
    # This ensures diversity regardless of how CSV is sorted
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
    """
    Generates realistic varied prices using product ID as seed.
    Same product always gets same price (deterministic).
    Prices vary within a realistic range per category.
    """
    # Use product ID as random seed for consistency
    random.seed(int(product_id) if product_id.isdigit() else hash(product_id))

    price_ranges = {
        "Watches": (2999, 15999),
        "Handbags": (1999, 8999),
        "Formal Shoes": (2999, 8999),
        "Casual Shoes": (1499, 5999),
        "Sports Shoes": (1999, 6999),
        "Heels": (1499, 4999),
        "Flats": (999, 3499),
        "Sandals": (799, 2999),
        "Shirts": (799, 2999),
        "Jeans": (1299, 4499),
        "Tops": (699, 2499),
        "Dresses": (1499, 5999),
        "Kurtas": (899, 3499),
        "Jackets": (1999, 6999),
        "Sweaters": (999, 3999),
        "Sweatshirts": (799, 2999),
        "Shorts": (599, 1999),
        "Trousers": (999, 3999),
        "Sunglasses": (799, 3999),
        "Belts": (499, 1999),
        "Wallets": (599, 2499),
        "Caps": (399, 1299),
        "Socks": (199, 599),
        "Perfumes": (1499, 5999),
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

CATALOGUE = load_catalogue(max_products=2000)