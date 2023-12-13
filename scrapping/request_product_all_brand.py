# Import used packages
import json
import os
import pandas as pd
import random
import time
import requests
from datetime import date

# Import brands id
brands = pd.read_csv('/Users/hafizzzh/Documents/My Portofolio/scrapping-sociolla/result/all_brand_sociolla.csv')

# define funtion to scrap product for one brand
def scrape_brand_data(brand_slug, limit=50):
    base_url = "https://catalog-api2.sociolla.com/search"
    skip = 0
    data_list = []

    filter_params = {
        "brand.slug": brand_slug
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    while True:
        query_params = {
            "filter": json.dumps(filter_params),
            "limit": limit,
            "skip": skip
        }
        print
        response = requests.get(base_url, 
                                params=query_params, 
                                headers=headers)
            
        data = json.loads(response.text)
        products = data['data']
        
        # Function to get nested values
        def get_nested_value(dictionary, keys):
            for key in keys:
                dictionary = dictionary.get(key, {})
            return dictionary
        
        # Function to get price by combinations
        def get_price_by_combinations(product):
            combinations = product.get("combinations", [])
            price_by_combinations = {
                get_combination_name(entry.get("attributes", {})): entry.get("price")
                for entry in combinations
                if entry.get("status_item") == "active"
            }
            return "; ".join([f'"{key}": {value}' for key, value in price_by_combinations.items()])

        def get_combination_name(attributes):
            # Find the first key inside "attributes" that contains "name"
            name_key = next((key for key, value in attributes.items() if "name" in value), None)
            return attributes.get(name_key, {}).get("name") if name_key else None

        # Function to get categories as a semicolon-separated string
        def get_categories(product):
            categories = product.get("categories", [])
            category_names = [category.get("name") for category in categories]
            return "; ".join(category_names)

        # Loop through each product and populate the DataFrame
        if len(products)!=0:
            for product in products:
                data = {
                    "brand_name": brand_slug,
                    "product_name": product.get("name"),
                    "product_id": product.get("id"),
                    "beauty_point_earned": product.get("beauty_point_earned"),
                    "price_range": product.get("price_range"),
                    "price_by_combinations": get_price_by_combinations(product),
                    "url": product.get("url_sociolla"),
                    "active_date": product.get("active_for_sociolla_at"),
                    "default_category": get_nested_value(product, ["default_category", "name"]),
                    "categories": get_categories(product),
                    "rating_types_str": ";".join(get_nested_value(product, ["default_category", "rating_types"])),
                    "average_rating": get_nested_value(product, ["review_stats", "average_rating"]),
                    "total_reviews": get_nested_value(product, ["review_stats", "total_reviews"]),
                    "average_rating_by_types": "; ".join([f'"{key}": {value}' for key, value in get_nested_value(product, ["review_stats", "average_rating_by_types"]).items()]),
                    "total_recommended_count": get_nested_value(product, ["review_stats", "total_recommended_count"]),
                    "total_repurchase_maybe_count": get_nested_value(product, ["review_stats", "total_repurchase_maybe_count"]),
                    "total_repurchase_no_count": get_nested_value(product, ["review_stats", "total_repurchase_no_count"]),
                    "total_repurchase_yes_count": get_nested_value(product, ["review_stats", "total_repurchase_yes_count"]),
                    "total_in_wishlist": product.get("total_wishlist")
                }
                data_list.append(data)
        else:
            print(f"Scraped {len(data_list)} products for brand {brand_slug}")
            break

        rand_numb = abs(random.gauss(3, 1))
        time.sleep(rand_numb)
        skip += limit

    return pd.DataFrame(data_list)

# Specify the result folder name
today = date.today()
result_folder_name = f"result_{today}"

# Create the result folder path
result_folder = os.path.join("..", "result", result_folder_name)

# Ensure that the result folder exists, if not, create it
os.makedirs(result_folder, exist_ok=True)

# Ensure that the result folder exists, if not, create it
if not os.path.exists(result_folder):
    os.makedirs(result_folder)

# Create an empty dataframe to store all products
meta_products = pd.DataFrame()

# Loop through all brands to scrap products
for brand_slug in brands['Slug']:
    print(f"Fetching products for brand: {brand_slug}")
    brand_products = scrape_brand_data(brand_slug)
    meta_products = pd.concat([meta_products, brand_products])
    
    # Save the current product data
    result_file_path = os.path.join(result_folder, f"products_{brand_slug}.csv")
    brand_products.to_csv(result_file_path, index=False)
    print("")

# Save the aggregated dataframe to CSV
result_file_path = os.path.join(result_folder, f"products_all_brands.csv")
meta_products.to_csv(result_file_path, index=False)

print(f"\nAll products saved to: {result_file_path}")