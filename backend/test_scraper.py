from scraper import JarirScraper, AmazonScraper, ExtraScraper, CarrefourScraper

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

print("\nFinished scraping Extra..")
print("Start scraping Carrefour..")

# Initialize the Carrefour scraper
carrefour_scraper = CarrefourScraper("Carrefour")

# Start scraping Carrefour
print(f"Searching for: {search_term} on Carrefour")
carrefour_products = list(carrefour_scraper.scrape_products(search_term, max_pages=3))

# Print the results from Carrefour
for index, product in enumerate(carrefour_products, start=1):
    print(f"\nCarrefour Product {index}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']} SAR")
    print(f"Info: {product['info']}")
    print(f"Rating: {product['rating']}")
    print(f"Link: {product['link']}")
    print(f"Image URL: {product['image_url']}")

# Quit the Carrefour scraper
carrefour_scraper.quit_driver()