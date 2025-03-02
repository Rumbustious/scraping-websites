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
                EC.presence_of_element_located((By.CLASS_NAME, "product-listing"))
            )
            print(f"Scraping results from {self.store_name} for: {search_value}")

            unique_products = set()

            def extract_products():
                """Extract product details using BeautifulSoup."""
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                product_elements = soup.select("div.product-listing div.product-tile__item--spacer div.product-tile div.product-tile__item")

                if not product_elements:
                    print("No product tiles found. The page structure might have changed.")

                for product in product_elements:
                    try:
                        # Extract title and link
                        title_elem = product.select_one("div.product-tile__col div.product-title p.product-title__title")
                        link_elem = product.find("a", class_="product-tile__link")
                        
                        # Extract rating stars
                        rating = product.find("div", class_="rating-star")
                        rating = rating.get_text(strip=True) if rating else "N/A"

                        # Extract price
                        price_elem = product.select_one("div.product-tile__price-container div.product-tile__price div.price-box__row div.price span.price_alignment span:nth-child(2)")
                        raw_price = price_elem.get_text(strip=True) if price_elem else "N/A"
                        price = self.normalize_price(raw_price)

                        # Extract info
                        info_elem = product.select("div.product-tile__col div.product-title p.product-title__info span.product-title__info--box")
                        info = " | ".join([elem.get_text(strip=True) for elem in info_elem]) if info_elem else "No additional info available"

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
                                "rating": rating,
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

class AmazonScraper(StoreScraper):
    def scrape_products(self, search_value, max_pages=5):
        """Scrape products from Amazon for a given search value."""
        encoded_search_value = urllib.parse.quote(search_value)
        base_url = f"https://www.amazon.sa/s?k={encoded_search_value}&language=en_AE"

        try:
            for page in range(1, max_pages + 1):
                url = f"{base_url}&page={page}"
                print(f"Loading page {page} for Amazon - URL: {url}")
                self.driver.get(url)

                # Wait for the product list to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
                )
                print(f"Scraping results from {self.store_name} - Page {page} for: {search_value}")

                unique_products = set()

                def extract_products():
                    """Extract product details using BeautifulSoup."""
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")
                    
                    # Adjusted selector for product elements
                    product_elements = soup.select("div.s-result-item[data-component-type='s-search-result']")
                    
                    for product in product_elements:
                        try:
                            # Locate the product title anchor
                            title_anchor = product.select_one("a.a-link-normal.s-line-clamp-4.s-link-style.a-text-normal")
                            if not title_anchor:
                                continue  # Skip if no title anchor found
                            
                            # Look for the nested <h2> within the anchor
                            title_h2 = title_anchor.select_one("h2.a-size-base-plus.a-spacing-none.a-color-base.a-text-normal")
                            if title_h2:
                                title = title_h2.get_text(strip=True)
                            else:
                                title = title_anchor.get_text(strip=True)
                            
                            # Product link
                            link = f"https://www.amazon.sa{title_anchor['href']}"
                            
                            
                            # Product price
                            price_elem = product.select_one("span.a-price span.a-offscreen")
                            price = self.normalize_price(price_elem.get_text(strip=True)) if price_elem else "N/A"
                            
                            # Product image
                            image_elem = product.select_one("img.s-image")
                            image_url = image_elem["src"] if image_elem else ""
                            
                            # Product rating
                            rating_elem = product.select_one("span.a-icon-alt")
                            rating = rating_elem.get_text(strip=True).split()[0] if rating_elem else "N/A"

                            # Deduplicate products
                            product_key = (title, link)
                            if product_key not in unique_products:
                                unique_products.add(product_key)
                                yield {
                                    "store": self.store_name,
                                    "title": title,
                                    "link": link,
                                    "price": price,
                                    "info": "N/A",
                                    "image_url": image_url,
                                    "rating": rating,
                                }
                        except Exception as e:
                            print(f"Error extracting product details: {e}. Skipping product...")



                yield from extract_products()

                # Check for 'Next' button to paginate
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
                    if not next_button.is_enabled():
                        print("No more pages to load.")
                        break
                except NoSuchElementException:
                    print("No 'Next' button found. Stopping pagination.")
                    break

        except (TimeoutException, WebDriverException) as e:
            print(f"Error during scraping: {e}")

    def scrape_arabic(self, url):
        self.driver.get(url)
        try:
            title_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span#productTitle"))
            )
            title = title_element.text.strip()
            return {"store": self.store_name, "title_arabic": title}
        except Exception as e:
            print(f"[Amazon] Error fetching Arabic title: {e}")
            return None
    
    def scrape_availability(self, product_link):
        """
        Check availability and price of a product on Amazon based on its link.
        1) If #add-to-cart-button is present => consider available
        2) Otherwise parse #availability or #availabilityInsideBuyBox_feature_div for text.
        3) Extract price from multiple possible selectors (apexPriceToPay, a-price-whole + a-price-fraction, etc.)
        """
        try:
            self.driver.get(product_link)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # ----------- AVAILABILITY DETECTION -----------
            availability = False

            # 1) If #add-to-cart-button is present => consider it available
            add_to_cart_button = soup.select_one("#add-to-cart-button")
            if add_to_cart_button:
                availability = True

            # 2) If not found, parse text in #availability and #availabilityInsideBuyBox_feature_div
            #    Check for phrases like "In Stock", "Only X left", "Currently unavailable", etc.
            availability_container = soup.select_one("#availability") or soup.select_one("#availabilityInsideBuyBox_feature_div")
            if availability_container:
                availability_text = availability_container.get_text(strip=True).lower()
                
                # If we find "in stock" or "only x left" => available
                if ("in stock" in availability_text) or ("only" in availability_text and "left" in availability_text):
                    availability = True
                
                # If we see "currently unavailable", "out of stock", "temporarily out of stock" => not available
                if ("unavailable" in availability_text) or ("out of stock" in availability_text):
                    availability = False

            # ----------- PRICE DETECTION -----------
            # If not available => skip price
            price = "N/A"
            if availability:
                # Attempt each known pattern:
                # 1) apexPriceToPay
                apex_elem = soup.select_one("span.a-price.a-text-price.a-size-medium.apexPriceToPay span.a-offscreen")
                if apex_elem and apex_elem.text.strip():
                    raw_price = apex_elem.get_text(strip=True)
                    price = self._extract_and_normalize_price(raw_price)

                if price == "N/A":
                    # 2) a-price-whole + a-price-fraction
                    whole_elem = soup.select_one("span.a-price-whole")
                    fraction_elem = soup.select_one("span.a-price-fraction")
                    if whole_elem and fraction_elem:
                        combined_price = whole_elem.get_text(strip=True).replace(",", "")
                        frac = fraction_elem.get_text(strip=True)
                        # remove any trailing '.' in the whole_elem text
                        if combined_price.endswith("."):
                            combined_price = combined_price[:-1]
                        raw_price = f"{combined_price}.{frac}"
                        price = self._extract_and_normalize_price(raw_price)

                if price == "N/A":
                    # 3) fallback: .aok-offscreen or #price_inside_buybox
                    fallback_elem = soup.select_one("div.a-section.aok-relative span.aok-offscreen")
                    if not fallback_elem:
                        fallback_elem = soup.select_one("#price_inside_buybox")
                    if fallback_elem and fallback_elem.text.strip():
                        raw_price = fallback_elem.get_text(strip=True)
                        price = self._extract_and_normalize_price(raw_price)

            return {"availability": availability, "price": price}

        except Exception as e:
            print(f"[Amazon] Error checking availability and price for {product_link}: {e}")
            return {"availability": False, "price": "N/A"}

    def _extract_and_normalize_price(self, raw_price):
        # Helper to remove currency text (SAR, ر.س, etc.) and parse float
        try:
            raw_price = raw_price.replace("SAR", "").replace("ر.س", "")
            # remove any extra characters
            raw_price = re.sub(r"[^\d.]", "", raw_price)
            normalized_price = float(raw_price)
            return f"{normalized_price:.2f}"
        except Exception:
            return "N/A"
            
        
class ExtraScraper(StoreScraper):
    def scrape_products(self, search_value, max_pages=5):
        """Scrape products from Extra for a given search value."""
        encoded_search_value = urllib.parse.quote(search_value)
        base_url = f"https://www.extra.com/en-sa/search/?q={encoded_search_value}%3Arelevance%3Atype%3APRODUCT&text={encoded_search_value}"

        try:
            for page in range(1, max_pages + 1):
                url = f"{base_url}&pg={page}&pageSize=24&sort=relevance"
                print(f"Loading page {page} for Extra - URL: {url}")
                self.driver.get(url)

                # Wait for the product list to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "section.product-list.product-list-section.svelte-97c3bg"))
                )
                print(f"Scraping results from {self.store_name} - Page {page} for: {search_value}")

                unique_products = set()

                def extract_products():
                    """Extract product details using BeautifulSoup."""
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")
                    
                    # Adjusted selector for product elements
                    product_elements = soup.select("section.main-section.svelte-1kvantt")
                    
                    for product in product_elements:
                        try:
                            # Locate the product link
                            link_elem = product.select_one("a.position-relative.product-tile-content-wrapper.svelte-1kvantt")
                            link = f"https://www.extra.com{link_elem['href']}" if link_elem else "N/A"
                            
                            # Locate the product image
                            image_elem = product.select_one("div.left-container.svelte-1kvantt section img.img-hover.svelte-1kx3rgh")
                            image_url = image_elem["src"] if image_elem else ""
                            
                            # Locate the product name
                            name_elem = product.select_one("div.right-container.svelte-1kvantt div.product-details.svelte-1kvantt section.product-name.svelte-1kvantt div.tile-name-container.svelte-tiqn05 div.product-name.svelte-tiqn05 span.product-name-data")
                            name = name_elem.get_text(strip=True) if name_elem else "N/A"
                            
                            # Locate the product rating
                            rating_elem = product.select_one("section.product-rating-review.svelte-1kvantt div.rating.svelte-vmxu3a")
                            rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
                            
                            # Locate the product prices
                            standard_price_elem = product.select_one("section.product-price-new-container.test.jood-NOPRIME.user-NOPRIME.variant-plp-list.svelte-8gstqg section.middle.svelte-8gstqg section.price.svelte-8gstqg span.price strong")
                            standard_price = standard_price_elem.get_text(strip=True) if standard_price_elem else "N/A"
                            
                            
                            # Locate the product info
                            info_elems = product.select("section.product-stats-container.svelte-1kvantt ul.product-stats.svelte-hoio38 li.svelte-hoio38")
                            info = " | ".join([elem.get_text(strip=True) for elem in info_elems]) if info_elems else "N/A"
                            
                            # Deduplicate products
                            product_key = (link, image_url, name)
                            if product_key not in unique_products:
                                unique_products.add(product_key)
                                yield {
                                    "store": self.store_name,
                                    "link": link,
                                    "image_url": image_url,
                                    "title": name,
                                    "price": standard_price,
                                    "info": info,
                                    "rating": rating,
                                }
                        except Exception as e:
                            print(f"Error extracting product details: {e}. Skipping product...")

                yield from extract_products()

                # Check for 'Next' button to paginate
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "a.pagination-next")
                    if not next_button.is_enabled():
                        print("No more pages to load.")
                        break
                except NoSuchElementException:
                    print("No 'Next' button found. Stopping pagination.")
                    break

        except (TimeoutException, WebDriverException) as e:
            print(f"Error during scraping: {e}")

    def scrape_availability(self, product_link):
        """
        Check availability and price of a product on Extra based on its link.
        """
        try:
            self.driver.get(product_link)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # ----------- AVAILABILITY DETECTION -----------
            availability = False

            # Check for availability text
            availability_container = soup.select_one("div.availability")
            if availability_container:
                availability_text = availability_container.get_text(strip=True).lower()
                
                # If we find "in stock" or "only x left" => available
                if ("in stock" in availability_text) or ("only" in availability_text and "left" in availability_text):
                    availability = True
                
                # If we see "currently unavailable", "out of stock", "temporarily out of stock" => not available
                if ("unavailable" in availability_text) or ("out of stock" in availability_text):
                    availability = False

            # ----------- PRICE DETECTION -----------
            # If not available => skip price
            price = "N/A"
            if availability:
                # Attempt each known pattern:
                price_elem = soup.select_one("span.price")
                if price_elem and price_elem.text.strip():
                    raw_price = price_elem.get_text(strip=True).replace("SAR", "").strip()
                    price = self._extract_and_normalize_price(raw_price)

            return {"availability": availability, "price": price}

        except Exception as e:
            print(f"[Extra] Error checking availability and price for {product_link}: {e}")
            return {"availability": False, "price": "N/A"}

    def _extract_and_normalize_price(self, raw_price):
        # Helper to remove currency text (SAR, ر.س, etc.) and parse float
        try:
            raw_price = raw_price.replace("SAR", "").replace("ر.س", "")
            # remove any extra characters
            raw_price = re.sub(r"[^\d.]", "", raw_price)
            normalized_price = float(raw_price)
            return f"{normalized_price:.2f}"
        except Exception:
            return "N/A"
        

class CarrefourScraper(StoreScraper):
    def scrape_products(self, search_value, max_pages=5):
        """Scrape products from Carrefour for a given search value."""
        encoded_search_value = urllib.parse.quote(search_value)
        base_url = f"https://www.carrefourksa.com/mafsau/en/v4/search?keyword={encoded_search_value}"

        try:
            for page in range(1, max_pages + 1):
                url = f"{base_url}&page={page}"
                print(f"Loading page {page} for Carrefour - URL: {url}")
                self.driver.get(url)

                # Wait for the product list to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-lzsise"))
                )
                print(f"Scraping results from {self.store_name} - Page {page} for: {search_value}")

                unique_products = set()

                def extract_products():
                    """Extract product details using BeautifulSoup."""
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")
                    
                    # Adjusted selector for product elements
                    product_rows = soup.select("div.css-lzsise div.css-5kig18")
                    
                    for row in product_rows:
                        product_elements = row.select("div.css-l3rx45 div.css-fv9do8 div.css-b9nx4o div > ul > div.css-yqd9tx")
                        
                        for product in product_elements:
                            try:
                                # Locate the product name
                                name_elem = product.select_one("div.css-11qbfb a[data-testid='product_name']")
                                name = name_elem.get_text(strip=True) if name_elem else "N/A"
                                
                                # Locate the product price
                                price_elem = product.select_one("div[data-testid='product-card-discount-price'] div.css-14zpref")
                                if not price_elem:
                                    price_elem = product.select_one("div[data-testid='product-card-original-price'] div.css-14zpref")
                                price = price_elem.get_text(strip=True) if price_elem else "N/A"
                                
                                # Locate the product link
                                link_elem = product.select_one("div.css-11qbfb a[data-testid='product_name']")
                                link = f"https://www.carrefourksa.com{link_elem['href']}" if link_elem else "N/A"
                                
                                # Locate the product image
                                image_elem = product.select_one("div[data-testid='product_card_image_container'] img[data-testid='product_image_main']")
                                image_url = image_elem["src"] if image_elem else "N/A"
                                
                                # Deduplicate products
                                product_key = (name, price, link)
                                if product_key not in unique_products:
                                    unique_products.add(product_key)
                                    yield {
                                        "store": self.store_name,
                                        "title": name,
                                        "link": link,
                                        "price": price,
                                        "info": "N/A",
                                        "image_url": image_url,
                                        "rating": "N/A",
                                    }
                            except Exception as e:
                                print(f"Error extracting product details: {e}. Skipping product...")

                yield from extract_products()

                # Check for 'Next' button to paginate
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "a.pagination-next")
                    if not next_button.is_enabled():
                        print("No more pages to load.")
                        break
                except NoSuchElementException:
                    print("No 'Next' button found. Stopping pagination.")
                    break

        except (TimeoutException, WebDriverException) as e:
            print(f"Error during scraping: {e}")

    def scrape_availability(self, product_link):
        """
        Check availability and price of a product on Carrefour based on its link.
        """
        try:
            self.driver.get(product_link)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # ----------- AVAILABILITY DETECTION -----------
            availability = False

            # Check for availability text
            availability_container = soup.select_one("div.availability")
            if availability_container:
                availability_text = availability_container.get_text(strip=True).lower()
                
                # If we find "in stock" or "only x left" => available
                if ("in stock" in availability_text) or ("only" in availability_text and "left" in availability_text):
                    availability = True
                
                # If we see "currently unavailable", "out of stock", "temporarily out of stock" => not available
                if ("unavailable" in availability_text) or ("out of stock" in availability_text):
                    availability = False

            # ----------- PRICE DETECTION -----------
            # If not available => skip price
            price = "N/A"
            if availability:
                # Attempt each known pattern:
                price_elem = soup.select_one("span.price")
                if price_elem and price_elem.text.strip():
                    raw_price = price_elem.get_text(strip=True).replace("SAR", "").strip()
                    price = self._extract_and_normalize_price(raw_price)

            return {"availability": availability, "price": price}

        except Exception as e:
            print(f"[Carrefour] Error checking availability and price for {product_link}: {e}")
            return {"availability": False, "price": "N/A"}

    def _extract_and_normalize_price(self, raw_price):
        # Helper to remove currency text (SAR, ر.س, etc.) and parse float
        try:
            raw_price = raw_price.replace("SAR", "").replace("ر.س", "")
            # remove any extra characters
            raw_price = re.sub(r"[^\d.]", "", raw_price)
            normalized_price = float(raw_price)
            return f"{normalized_price:.2f}"
        except Exception:
            return "N/A"