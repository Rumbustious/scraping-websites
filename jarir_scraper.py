from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep
import urllib.parse
import re


class StoreScraper:
    def __init__(self, store_name):
        self.store_name = store_name
        self.driver = self.setup_driver()

    def setup_driver(self):
        options = EdgeOptions()

        # Headless mode for performance
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")

        # Use a custom user-agent to avoid detection
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/109.0.0.0 Safari/537.36"
        )

        # Initialize Edge WebDriver (Ensure `msedgedriver` is in PATH)
        service = EdgeService()
        driver = webdriver.Edge(service=service, options=options)
        return driver

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def clean_image_url(self, image_url):
        if image_url.startswith("//"):
            image_url = "https:" + image_url

        image_url = image_url.replace("////", "//")

        if "100_00" in image_url:
            image_url = image_url.replace("100_00", "100_01")

        if "?locale=" in image_url:
            image_url = image_url.split("?locale=")[0] + "?locale=en-GB,en-"
        elif "&amp;fmt=" in image_url:
            image_url = image_url.split("&amp;")[0]

        return image_url

    @staticmethod
    def normalize_price(price):
        if not price:
            return "N/A"
        try:
            price = price.replace("\n", "").strip()
            price = re.sub(r"[^\d.,]", "", price)
            price = price.replace(",", "")
            return f"{float(price):.2f}"
        except (ValueError, IndexError):
            return "N/A"


class JarirScraper(StoreScraper):
    def handle_popups(self):
        """Handle popups for language selection and cookie consent."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#switcher-button-en"))
            ).click()
            print("Language selected: English")
        except TimeoutException:
            print("Language popup did not appear or was already handled.")

        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
            print("Accepted cookie consent.")
        except TimeoutException:
            print("Cookie consent popup did not appear or was already handled.")

    def scrape_products(self, search_value, max_scrolls=5):
        """Scrape products from the Jarir website."""
        encoded_search_value = urllib.parse.quote(search_value)
        url = f"https://www.jarir.com/sa-en/catalogsearch/result?search={encoded_search_value}&country=sa"

        try:
            self.driver.get(url)
            self.handle_popups()

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-tile__item--spacer"))
            )
            print(f"Scraping results from {self.store_name} for: {search_value}")

            unique_products = set()

            def extract_products():
                """Extract product details using BeautifulSoup."""
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                product_elements = soup.find_all("div", class_="product-tile__item--spacer")

                if not product_elements:
                    print("No product tiles found. The page structure might have changed.")

                for product in product_elements:
                    try:
                        # Extract title and link
                        title_elem = product.find("p", class_="product-title__title")
                        link_elem = product.find("a", class_="product-tile__link")

                        # Extract price
                        price_elem = product.find("div", class_="price")
                        raw_price = price_elem.get_text(strip=True) if price_elem else "N/A"
                        price = self.normalize_price(raw_price)

                        # Extract info
                        info_elem = product.find("p", class_="product-title__info")
                        info = (
                            info_elem.get_text(" | ", strip=True)
                            if info_elem
                            else "No additional info available"
                        )

                        # Extract image
                        image_elem = product.find("img", {"loading": "eager", "class": "image--contain"})
                        image_url = self.clean_image_url(image_elem["src"]) if image_elem else ""

                        # Format the product link
                        title = title_elem.get_text(strip=True) if title_elem else "No title"
                        link = f"https://www.jarir.com{link_elem['href']}" if link_elem else "No link"

                        product_key = (title, link)
                        if product_key not in unique_products:
                            unique_products.add(product_key)
                            yield {
                                "store": self.store_name,
                                "title": title,
                                "link": link,
                                "price": price,
                                "info": info,
                                "image_url": image_url,
                            }
                    except AttributeError as e:
                        print(f"Error extracting product details: {e}. Skipping product...")

            yield from extract_products()

            # Implement scrolling for dynamic content loading
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            for _ in range(max_scrolls):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(3)
                yield from extract_products()
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("No more products to load.")
                    break
                last_height = new_height

        except (TimeoutException, WebDriverException) as e:
            print(f"Error during scraping: {e}")

    def scrape_availability(self, product_link):
        """Check product availability and price."""
        try:
            self.driver.get(product_link)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Check for availability
            notify_me_buttons = soup.select("button.button--primary.button--fluid.button--secondary")
            add_to_cart_buttons = soup.select("button.button--add-to-cart.button--primary.button--fluid")
            availability = bool(add_to_cart_buttons or not notify_me_buttons)

            # Extract the price
            price_element = soup.select_one("div.price-box__row div.price span.price__currency + span")
            price = self.normalize_price(price_element.get_text(strip=True) if price_element else "")

            return {"availability": availability, "price": price}

        except Exception as e:
            print(f"[{self.store_name}] Error checking availability and price for {product_link}: {e}")
            return {"availability": False, "price": "N/A"}
