from backend.scraper import JarirScraper, AmazonScraper

# Initialize the scraper
scraper = JarirScraper("Jarir")

# Choose a search term (Example: "laptop")
search_term = "iphone 16"

# Start scraping
print(f"Searching for: {search_term}")
products = list(scraper.scrape_products(search_term, max_scrolls=3))

# Print the results
for index, product in enumerate(products, start=1):
    print(f"\nProduct {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Info: {product['info']}")
    print(f"Rating: {product['rating']}")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")


print("\nFinished scraping jarir..")
print("Start scrapping amazon..")

scraper = AmazonScraper("Amazon")
# Start scraping
print(f"Searching for: {search_term}")
products = list(scraper.scrape_products(search_term, max_pages=3))

# Print the results
for index, product in enumerate(products, start=1):
    print(f"\nProduct {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Info: {product['info']}")
    print(f"Rating: {product['rating']}")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")

# Quit the browser session
scraper.quit_driver()
