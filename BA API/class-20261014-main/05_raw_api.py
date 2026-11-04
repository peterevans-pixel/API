"""Optional: the same read without the Supabase client library."""
import requests
from config import get_settings

if __name__ == "__main__":
    url, key = get_settings()
    # A new sb_secret_ key goes in apikey; it is not a user JWT.
    response = requests.get(
        f"{url}/rest/v1/products",
        headers={"apikey": key},
        params={"select": "product_name,price", "price": "lte.25", "order": "price.asc"},
        timeout=30,
    )
    response.raise_for_status()
    print("HTTP status:", response.status_code)
    print("JSON response:", response.json())
