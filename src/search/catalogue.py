# catalogue.py
# Loads the real Fashion Product Dataset (44,000+ products)
# from the Kaggle paramaggarwal dataset.
# Columns: id, gender, masterCategory, subCategory, 
#           articleType, baseColour, season, usage, productDisplayName

import pandas as pd
import os

def load_catalogue(max_products: int = 500) -> list:
    """
    Loads fashion products from styles.csv.
    max_products: how many to load (500 is fast, 5000 is impressive)
    Returns a list of product dictionaries matching our app's format.
    """
    csv_path = "data/fashion-dataset/styles.csv"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path, on_bad_lines='skip')

    # Drop rows with missing critical fields
    df = df.dropna(subset=['productDisplayName', 'baseColour', 'articleType'])

    # Take a sample for speed — increase later
    df = df.head(max_products)

    # Convert each row into our standard product dictionary
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
            "price": _estimate_price(row['articleType'], row['masterCategory']),
            "season": row['season'] if pd.notna(row['season']) else "All Season",
            "image_url": f"https://picsum.photos/seed/{row['id']}/300/400"
        }
        products.append(product)

    print(f"Loaded {len(products)} products from Fashion Dataset")
    return products

def _estimate_price(article_type: str, master_category: str) -> int:
    """
    Estimates price in rupees based on product category.
    Real dataset has no prices so we generate realistic ones.
    """
    price_map = {
        "Watches": 8999, "Handbags": 4999, "Shoes": 5999,
        "Casual Shoes": 3999, "Sports Shoes": 4499, "Formal Shoes": 5999,
        "Heels": 3499, "Flats": 2499, "Sandals": 1999,
        "Shirts": 1499, "Jeans": 2499, "Tops": 1299,
        "Dresses": 2999, "Kurtas": 1799, "Sarees": 3999,
        "Jackets": 3999, "Sweaters": 2499, "Sweatshirts": 1999,
        "Shorts": 1299, "Trousers": 2299, "Skirts": 1799,
        "Sunglasses": 1999, "Belts": 999, "Wallets": 1499,
        "Caps": 799, "Socks": 299, "Innerwear": 499,
        "Perfumes": 2999, "Jewellery": 1999,
    }
    # Check article type first, then fall back to category-based estimate
    for key, price in price_map.items():
        if key.lower() in article_type.lower():
            return price
    # Default by master category
    if master_category == "Footwear":
        return 3999
    elif master_category == "Accessories":
        return 1999
    elif master_category == "Apparel":
        return 1999
    return 1499

# Load catalogue once at module level
CATALOGUE = load_catalogue(max_products=500)