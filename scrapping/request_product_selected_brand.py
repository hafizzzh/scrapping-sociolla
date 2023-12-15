import json
import pandas as pd
import random
import time
import requests
import os
from datetime import date

base_url = "https://catalog-api2.sociolla.com/search"
# Declare the brand slug here
brand_slug = "558_cosrx"
limit = 50
skip = 0
keepLoop = True
data_list = []

filter_params = {
    "brand.slug": brand_slug
}

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

while keepLoop:
    query_params = {
            "filter": json.dumps(filter_params),
            "limit": limit,
            "skip": skip
        }
    
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

        # Create file name
        file_name = f"products_{brand_slug}.csv"
        
        # Save the aggregated dataframe to CSV
        result_file_path = os.path.join(result_folder, file_name)
        df_products = pd.DataFrame(data_list)
        df_products.to_csv(result_file_path, index=False)
        
        # Stop the loop
        keepLoop = False
        print("selesai")
        break

    rand_numb = abs(random.gauss(3, 1))
    time.sleep(rand_numb)
    print("\t action delayed for ", rand_numb, "second")
    print("\t scraped [", len(data_list), "] product(s)")
    print("")
    skip += limit