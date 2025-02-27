from scraper import JarirScraper, AmazonScraper, NoonScraper, ExtraScraper

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

print("\nFinished scraping Jarir..")
print("Start scraping Amazon..")

# Initialize the Amazon scraper
amazon_scraper = AmazonScraper("Amazon")

# Start scraping Amazon
print(f"Searching for: {search_term} on Amazon")
amazon_products = list(amazon_scraper.scrape_products(search_term, max_pages=1))

# Print the results from Amazon
for index, product in enumerate(amazon_products, start=1):
    print(f"\nAmazon Product {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Info: {product['info']}")
    print(f"Rating: {product['rating']}")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")

# Quit the Amazon scraper
amazon_scraper.quit_driver()

print("\nFinished scraping Amazon..")
print("Start scraping Noon..")

# Initialize the Noon scraper
noon_scraper = NoonScraper("Noon")

# Start scraping Noon
print(f"Searching for: {search_term} on Noon")
noon_products = list(noon_scraper.scrape_products(search_term, max_pages=3))

# Print the results from Noon
for index, product in enumerate(noon_products, start=1):
    print(f"\nNoon Product {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Info: {product['info']}")
    print(f"Rating: {product['rating']}")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")

# Quit the Noon scraper
noon_scraper.quit_driver()

print("\nFinished scraping Noon..")
print("Start scraping Extra..")

# Initialize the Extra scraper
extra_scraper = ExtraScraper("Extra")

# Start scraping Extra
print(f"Searching for: {search_term} on Extra")
extra_products = list(extra_scraper.scrape_products(search_term, max_pages=3))

# Print the results from Extra
for index, product in enumerate(extra_products, start=1):
    print(f"\nExtra Product {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Info: {product['info']}")
    print(f"Rating: {product['rating']}")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")

# Quit the Extra scraper
extra_scraper.quit_driver()