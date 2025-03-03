from scraper import JarirScraper

# Choose a search term (Example: "laptop")
search_term = "iphone 16"

# Initialize the Jarir scraper
jarir_scraper = JarirScraper("Jarir")

# Start scraping Jarir
print(f"Searching for: {search_term} on Jarir")
jarir_products = list(jarir_scraper.scrape_products(search_term, max_scrolls=3))

# Print the results from Jarir
for index, product in enumerate(jarir_products, start=1):
    print(f"\nJarir Product {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Info: {product['info']}")
    print(f"Rating: {product['rating']}")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")

# Quit the Jarir scraper
jarir_scraper.quit_driver()

print("\nFinished scraping Jarir.")