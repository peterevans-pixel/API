from database import get_client

if __name__ == "__main__":
    response = get_client().table("products").select("product_id", count="exact").limit(1).execute()
    print(f"Connection successful. Products in database: {response.count}")
    print("Zero is expected before importing the CSV files.")
