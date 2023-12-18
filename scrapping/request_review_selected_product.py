from datetime import date
import json
import pandas as pd
import random
import time
import os
import requests

base_url = "https://soco-api.sociolla.com/reviews"
# Declare the product ID here
product_id = 19796
limit = 10
skip = 0
keepLoop = True
data_list = []

filter_params = {
    "is_published": True,
    "elastic_search": True,
    "product_id": product_id
}

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

while keepLoop:
    query_params = {
        "filter": json.dumps(filter_params),
        "skip": skip,
        "sort": "-created_at",
        "limit": limit 
    }
    
    response = requests.get(base_url, 
                            params=query_params, 
                            headers=headers)
    
    data = json.loads(response.text)
    reviews = data['data']
    
    # Function to get nested values
    def get_nested_value(dictionary, keys, default=None):
        for key in keys:
            try:
                dictionary = dictionary[key]
            except KeyError:
                return default
        return dictionary
    
    if len(reviews)!=0:
        for review in reviews:
            skin_types = get_nested_value(review, ["user", "skin_types"])
            skin_type_names = [skin['name'] for skin in skin_types] if skin_types else None
            
            hair_types = get_nested_value(review, ["user", "hair_types"])
            hair_type_names = [hair['name'] for hair in hair_types] if hair_types else None
            
            star_keys = [key for key in review if key.startswith("star_")]
            star_values = [f"{key}: {review[key]}" for key in star_keys]
            #ratings = '; '.join([f'"{key}": {value}' for item in data for key, value in item.items() if key.startswith("star_") and "details" < key < "tags"])

            data = {
                # User Information 
                "user_name": get_nested_value(review, ["user", "user_name"]),
                "is_expert_reviewer": get_nested_value(review, ["user", "is_expert_reviewer"]),
                "user_level": get_nested_value(review, ["user", "user_level"]),
                "age_range": get_nested_value(review, ["user", "age_range"]),
                "skin_types": ';'.join(skin_type_names) if skin_type_names else None,
                "hair_types": ';'.join(hair_type_names) if hair_type_names else None,
                
                # Review Details
                "is_repurchase": review.get("is_repurchase"),
                "is_recommended": review.get("is_recommended"),
                "source": review.get("source"),
                "created_at": review.get("created_at"),
                "total_likes": review.get("total_likes", 0),
                "is_verified_purchase": review.get("is_verified_purchase"),
                "details": review.get("details"),
                "duration_of_used": review.get("duration_of_used"),
                "ratings": "; ".join(star_values) if star_values else None,
                
                # Product Information
                "product_id": get_nested_value(review, ["product", "id"]),
                "product_name": get_nested_value(review, ["product", "name"]),
                "product_size": get_nested_value(review, ["product", "combination", "attribute", "size", "name"])                
            }
            data_list.append(data)
    else:
        today = date.today()
        result_folder_name = f"result_{today}"

        # Create the result folder path
        result_folder = os.path.join("..", "result", result_folder_name)

        # Create the folder if it doesn't already exist
        os.makedirs(result_folder, exist_ok=True)

        # Create file name
        file_name = f"review_{product_id}.csv"

        # Create the result file path
        result_file_path = os.path.join(result_folder, file_name)

        # Save the DataFrame to the file
        df_review = pd.DataFrame(data_list)
        df_review.to_csv(result_file_path, index=False)

        # Stop the loop
        keepLoop = False
        print("selesai")
        break
            
    rand_numb = abs(random.gauss(3, 1))
    time.sleep(rand_numb)
    print("\t action delayed for ", rand_numb, "second")
    print("\t scraped [", len(data_list), "] review(s)")
    print("")
    skip += limit
