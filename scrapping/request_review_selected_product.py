import json
import pandas as pd
import random
import time
import os
import requests

base_url = "https://soco-api.sociolla.com/reviews"
# Declare the product ID here
product_id = 19048
limit = 10
skip = 0
keepLoop = True
df_reviews = pd.DataFrame()

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
    
    jsondata = json.loads(response.text)
    
    for i in range(limit):
        try:
            def get_nested_value(review, keys, default=None):
                """
                Retrieve a nested value from the review JSON based on a list of keys.
                """
                value = review
                for key in keys:
                    if value and key in value:
                        value = value[key]
                    else:
                        return default
                return value
            
            # Extract the variables using the formatting function
            review = jsondata['data'][i]
            
            user_name = get_nested_value(review, ["user", "user_name"])
            is_expert_reviewer = get_nested_value(review, ["user", "is_expert_reviewer"])
            user_level = get_nested_value(review, ["user", "user_level"])
            age_range = get_nested_value(review, ["user", "age_range"])
            skin_types = get_nested_value(review, ["user", "skin_types"])
            skin_type_names = [skin['name'] for skin in skin_types] if skin_types else None
            skin_types_str = ';'.join(skin_type_names) if skin_type_names else None
            
            # Review details
            is_repurchase = review.get("is_repurchase")
            is_recommended = review.get("is_recommended")
            star_effectiveness = review.get("star_effectiveness")
            star_packaging = review.get("star_packaging")
            star_texture = review.get("star_texture")
            star_value_for_money = review.get("star_value_for_money")
            source = review.get("source")
            created_at = review.get("created_at")
            total_likes = review.get("total_likes", 0)
            is_verified_purchase = review.get("is_verified_purchase")
            details = review.get("details")
            duration_of_used = review.get("duration_of_used")
            
            # Product information
            product_id = get_nested_value(review, ["product", "id"])
            product_name = get_nested_value(review, ["product", "name"])
            product_size = get_nested_value(review, ["product", "combination", "attribute", "size", "name"])

            # Populate rev_row with the variables
            rev_row = pd.Series({
                'user_name': user_name,
                'is_expert_reviewer': is_expert_reviewer,
                'user_level': user_level,
                'skin_types': skin_types_str,
                'age_range': age_range,
                'is_repurchase': is_repurchase,
                'is_recommended': is_recommended,
                'star_effectiveness': star_effectiveness,
                'star_packaging': star_packaging,
                'star_texture': star_texture,
                'star_value_for_money': star_value_for_money,
                'source': source,
                'created_at': created_at,
                'total_likes': total_likes,
                'is_verified_purchase': is_verified_purchase,
                'details': details,
                'duration_of_used': duration_of_used,
                'product_id': product_id,
                'product_name': product_name,
                'product_size': product_size
            })
    
            # Assuming i and skip are defined
            row_df_rev = pd.DataFrame([rev_row], index=[i + skip])
    
            # Concatenate rev_row to df_reviews
            df_reviews = pd.concat([df_reviews, row_df_rev])

        except IndexError:
            file_name = f"review_{product_id}.csv"
            df_reviews.to_csv(file_name, index=False)
            keepLoop = False
            break
            
    rand_numb = abs(random.gauss(3, 1))
    time.sleep(rand_numb)
    print("\t action delayed for ", rand_numb, "second")
    print("\t scraped [", len(df_reviews), "] review(s)")
    print("")
    skip += limit
