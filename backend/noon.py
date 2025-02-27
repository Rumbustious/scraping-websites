class NoonScraper(StoreScraper):
    def scrape_products(self, search_value, max_pages=5):
        """Scrape products from Noon for a given search value."""
        encoded_search_value = urllib.parse.quote(search_value)
        base_url = f"https://www.noon.com/saudi-en/search/?q={encoded_search_value}"

        try:
            for page in range(1, max_pages + 1):
                url = f"{base_url}&page={page}"
                print(f"Loading page {page} for Noon - URL: {url}")
                self.driver.get(url)

                # Wait for the product list to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-57fe1f38-0.eSrvHE"))
                )
                print(f"Scraping results from {self.store_name} - Page {page} for: {search_value}")

                unique_products = set()

                def extract_products():
                    """Extract product details using BeautifulSoup."""
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")
                    
                    # Adjusted selector for product elements
                    product_elements = soup.select("div.sc-57fe1f38-0.eSrvHE")
                    
                    for product in product_elements:
                        try:
                            # Locate the product title anchor
                            title_anchor = product.select_one("a[id^='productBox']")
                            if not title_anchor:
                                continue  # Skip if no title anchor found
                            
                            # Product title
                            title = title_anchor.get("title", "").strip()
                            
                            # Product link
                            link = f"https://www.noon.com{title_anchor['href']}"
                            
                            # Product price
                            price_elem = product.select_one("strong.amount.currencyImageAmount")
                            price = price_elem.get_text(strip=True) if price_elem else "N/A"
                            
                            # Product image
                            image_elem = product.select_one("img.sc-d13a0e88-1.cindWc")
                            image_url = image_elem["src"] if image_elem else ""
                            
                            # Product rating
                            rating_elem = product.select_one("div.sc-9cb63f72-2.dGLdNc")
                            rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"

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
            print(f"[Noon] Error fetching Arabic title: {e}")
            return None
    
    def scrape_availability(self, product_link):
        """
        Check availability and price of a product on Noon based on its link.
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
            print(f"[Noon] Error checking availability and price for {product_link}: {e}")
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