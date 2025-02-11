from jarir_scraper import JarirScraper  # Import your scraper class

# Initialize the scraper
scraper = JarirScraper("Jarir")

# Choose a search term (Example: "laptop")
search_term = "laptop"

# Start scraping
print(f"Searching for: {search_term}")
products = list(scraper.scrape_products(search_term, max_scrolls=3))

# Print the results
for index, product in enumerate(products, start=1):
    print(f"\nProduct {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")

# Quit the browser session
scraper.quit_driver()
