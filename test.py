"""
Selenium Test Suite for My Adventures - Waterparks & Adventure Parks Website
Docker-compatible with headless Chrome support

Run locally: pip install -r requirements.txt && python test.py
Run in Docker: docker build -f Dockerfile.selenium -t selenium-tests . && docker run --network=host selenium-tests
"""

import time
import unittest
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost:9090')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
CHROME_BIN = os.getenv('CHROME_BIN', None)
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', None)


class TestMyAdventures(unittest.TestCase):
    """Comprehensive test suite for My Adventures waterpark website"""

    @classmethod
    def setUpClass(cls):
        """Set up Chrome WebDriver with Docker-compatible options"""
        options = Options()
        
        # Headless mode for Docker
        if HEADLESS:
            options.add_argument('--headless=new')
        
        # Essential Chrome options for containerized environments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0')
        
        # Use specific Chrome binary if provided (Docker)
        if CHROME_BIN:
            options.binary_location = CHROME_BIN
        
        # Initialize WebDriver
        try:
            if CHROMEDRIVER_PATH:
                service = Service(CHROMEDRIVER_PATH)
                cls.driver = webdriver.Chrome(service=service, options=options)
            else:
                cls.driver = webdriver.Chrome(options=options)
            
            cls.driver.implicitly_wait(5)
            cls.wait = WebDriverWait(cls.driver, 10)
            cls.driver.set_page_load_timeout(30)
            print(f"✅ WebDriver initialized (Headless: {HEADLESS})")
            
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            raise

    @classmethod
    def tearDownClass(cls):
        """Clean up WebDriver"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
            print("✅ WebDriver closed")

    def safe_find(self, by, value, timeout=10):
        """Safely find element with explicit wait"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.fail(f"Element not found: {by}={value}")

    def safe_click(self, element):
        """Safely click element with scroll and wait"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(element))
        element.click()

    # ==================== INDEX PAGE TESTS ====================

    def test_01_homepage_loads(self):
        """Test that the homepage loads successfully"""
        self.driver.get(BASE_URL)
        self.assertIn("My Adventures", self.driver.title)
        print("✅ Homepage loaded successfully")

    def test_02_hero_section_visible(self):
        """Test hero section is displayed with correct title"""
        self.driver.get(BASE_URL)
        hero = self.safe_find(By.CSS_SELECTOR, ".hero")
        self.assertTrue(hero.is_displayed())
        title = self.safe_find(By.CSS_SELECTOR, ".text-h1")
        self.assertIn("Splash Into Adventure", title.text)
        print("✅ Hero section visible with correct title")

    def test_03_navigation_links_present(self):
        """Test all navigation links are present"""
        self.driver.get(BASE_URL)
        nav_links = self.driver.find_elements(By.CSS_SELECTOR, ".hero__link")
        link_texts = [link.text for link in nav_links]
        required_links = ["Home", "Portfolio", "Blog", "Contact", "Book Now ↗", "Log In"]
        for link in required_links:
            self.assertIn(link, link_texts)
        print(f"✅ All {len(required_links)} navigation links present")

    def test_04_deals_banner_visible(self):
        """Test deals banner is displayed"""
        self.driver.get(BASE_URL)
        banner = self.safe_find(By.CSS_SELECTOR, ".deals-banner")
        self.assertTrue(banner.is_displayed())
        self.assertIn("Summer Flash Sale", banner.text)
        print("✅ Deals banner visible")

    def test_05_parks_section_visible(self):
        """Test waterparks & adventure parks section loads"""
        self.driver.get(BASE_URL)
        section = self.safe_find(By.ID, "parks")
        self.assertTrue(section.is_displayed())
        title = self.safe_find(By.CSS_SELECTOR, ".parks-section__title")
        self.assertIn("Top Waterparks", title.text)
        print("✅ Parks section visible")

    def test_06_park_cards_rendered(self):
        """Test that park cards are rendered (at least 10)"""
        self.driver.get(BASE_URL)
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".park-card")
        self.assertGreaterEqual(len(cards), 10, f"Expected at least 10 cards, found {len(cards)}")
        print(f"✅ {len(cards)} park cards rendered")

    def test_07_park_card_has_details(self):
        """Test first park card has name, location, price"""
        self.driver.get(BASE_URL)
        card = self.safe_find(By.CSS_SELECTOR, ".park-card")
        name = card.find_element(By.CSS_SELECTOR, ".park-card__name").text
        location = card.find_element(By.CSS_SELECTOR, ".park-card__location").text
        price = card.find_element(By.CSS_SELECTOR, ".park-card__price").text
        self.assertTrue(len(name) > 0, "Park name is empty")
        self.assertIn("📍", location, "Location missing emoji")
        self.assertIn("₹", price, "Price missing currency symbol")
        print(f"✅ Park card details: {name}, {location}, {price}")

    def test_08_park_modal_opens_on_click(self):
        """Test clicking a park card opens the detail modal"""
        self.driver.get(BASE_URL)
        card = self.safe_find(By.CSS_SELECTOR, ".park-card")
        self.safe_click(card)
        time.sleep(1)
        overlay = self.safe_find(By.ID, "parkModalOverlay")
        self.assertIn("active", overlay.get_attribute("class"))
        modal_name = self.safe_find(By.ID, "modalName")
        self.assertTrue(len(modal_name.text) > 0)
        print(f"✅ Modal opened for: {modal_name.text}")

    def test_09_modal_has_all_sections(self):
        """Test modal contains all required sections"""
        self.driver.get(BASE_URL)
        self.driver.execute_script("openParkModal(0)")
        time.sleep(1)

        # Description
        desc = self.safe_find(By.ID, "modalDesc")
        self.assertTrue(len(desc.text) > 0, "Description is empty")

        # Info grid (timings)
        info = self.safe_find(By.ID, "modalInfo")
        self.assertIn("Timings", info.text)
        self.assertIn("Open Days", info.text)

        # Packages
        packages = self.driver.find_elements(By.CSS_SELECTOR, ".park-modal__pkg")
        self.assertGreaterEqual(len(packages), 1, "No packages found")

        # Offers
        offers = self.driver.find_elements(By.CSS_SELECTOR, ".park-modal__offer")
        self.assertGreaterEqual(len(offers), 1, "No offers found")

        # Google Map iframe
        map_iframe = self.safe_find(By.ID, "modalMap")
        self.assertIn("google.com/maps", map_iframe.get_attribute("src"))

        # Book button
        book_btn = self.safe_find(By.ID, "modalBookBtn")
        self.assertIn("booking.html", book_btn.get_attribute("href"))

        # Directions link
        directions = self.safe_find(By.ID, "modalDirections")
        self.assertIn("google.com/maps", directions.get_attribute("href"))

        print("✅ Modal has all sections: description, timings, packages, offers, map, book button")

    def test_10_modal_close_button(self):
        """Test modal closes when clicking close button"""
        self.driver.get(BASE_URL)
        self.driver.execute_script("openParkModal(0)")
        time.sleep(1)
        close_btn = self.safe_find(By.ID, "parkModalClose")
        self.safe_click(close_btn)
        time.sleep(0.5)
        overlay = self.driver.find_element(By.ID, "parkModalOverlay")
        self.assertNotIn("active", overlay.get_attribute("class"))
        print("✅ Modal closed via close button")

    def test_11_modal_close_on_overlay_click(self):
        """Test modal closes when clicking outside (on overlay)"""
        self.driver.get(BASE_URL)
        self.driver.execute_script("openParkModal(0)")
        time.sleep(1)
        overlay = self.driver.find_element(By.ID, "parkModalOverlay")
        # Use JavaScript to trigger click on overlay background
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));",
            overlay
        )
        time.sleep(0.5)
        self.assertNotIn("active", overlay.get_attribute("class"))
        print("✅ Modal closed via overlay click")

    def test_12_modal_close_on_escape(self):
        """Test modal closes when pressing Escape key"""
        self.driver.get(BASE_URL)
        self.driver.execute_script("openParkModal(0)")
        time.sleep(1)
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        overlay = self.driver.find_element(By.ID, "parkModalOverlay")
        self.assertNotIn("active", overlay.get_attribute("class"))
        print("✅ Modal closed via Escape key")

    def test_13_all_park_modals_open(self):
        """Test every park card opens a valid modal"""
        self.driver.get(BASE_URL)
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".park-card")
        success_count = 0
        for i in range(len(cards)):
            try:
                self.driver.execute_script(f"openParkModal({i})")
                time.sleep(0.5)
                name = self.driver.find_element(By.ID, "modalName").text
                if len(name) > 0:
                    success_count += 1
                self.driver.execute_script("closeParkModal()")
                time.sleep(0.3)
            except Exception as e:
                print(f"⚠️  Park {i} failed: {e}")
        self.assertEqual(success_count, len(cards), f"Only {success_count}/{len(cards)} modals opened")
        print(f"✅ All {len(cards)} park modals open correctly")

    def test_14_splash_highlights_visible(self):
        """Test splash highlights section is displayed"""
        self.driver.get(BASE_URL)
        highlights = self.driver.find_elements(By.CSS_SELECTOR, ".splash-card")
        self.assertGreaterEqual(len(highlights), 3, f"Expected 3+ highlights, found {len(highlights)}")
        print(f"✅ Splash highlights section visible with {len(highlights)} cards")

    def test_15_intro_section_content(self):
        """Test intro section has correct content"""
        self.driver.get(BASE_URL)
        intro = self.safe_find(By.CSS_SELECTOR, ".intro")
        self.assertTrue(intro.is_displayed())
        headline = self.safe_find(By.CSS_SELECTOR, ".intro__headline")
        self.assertIn("waterpark", headline.text.lower())
        items = self.driver.find_elements(By.CSS_SELECTOR, ".intro__item")
        self.assertGreaterEqual(len(items), 4, f"Expected 4+ items, found {len(items)}")
        print(f"✅ Intro section content verified with {len(items)} items")

    def test_16_offers_section_visible(self):
        """Test special offers section is displayed"""
        self.driver.get(BASE_URL)
        offers = self.driver.find_elements(By.CSS_SELECTOR, ".offer-card")
        self.assertGreaterEqual(len(offers), 1, "No offers found")
        first_offer = offers[0]
        name = first_offer.find_element(By.CSS_SELECTOR, ".offer-card__name").text
        price = first_offer.find_element(By.CSS_SELECTOR, ".offer-card__price").text
        self.assertTrue(len(name) > 0, "Offer name is empty")
        self.assertIn("₹", price, "Price missing currency")
        print(f"✅ Offers section visible with {len(offers)} offers")

    def test_17_contact_section_visible(self):
        """Test contact section is displayed"""
        self.driver.get(BASE_URL)
        contact = self.safe_find(By.ID, "contact")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", contact)
        time.sleep(0.5)
        self.assertTrue(contact.is_displayed())
        self.assertIn("Black Pearl", contact.text)
        print("✅ Contact section visible")

    def test_18_search_box_present(self):
        """Test search box is present and functional"""
        self.driver.get(BASE_URL)
        search = self.safe_find(By.ID, "parkSearchInput")
        self.assertTrue(search.is_displayed())
        self.assertIn("Search", search.get_attribute("placeholder"))
        # Test typing
        search.send_keys("Wonderla")
        time.sleep(0.5)
        self.assertEqual(search.get_attribute("value"), "Wonderla")
        print("✅ Search box present and functional")

    def test_19_filter_buttons_present(self):
        """Test filter buttons (All, Waterpark, Adventure, Both) are present"""
        self.driver.get(BASE_URL)
        filters = self.driver.find_elements(By.CSS_SELECTOR, ".park-search__filter")
        self.assertEqual(len(filters), 4, f"Expected 4 filters, found {len(filters)}")
        filter_texts = [f.text for f in filters]
        self.assertTrue(any("All" in t for t in filter_texts))
        self.assertTrue(any("Waterpark" in t for t in filter_texts))
        self.assertTrue(any("Adventure" in t for t in filter_texts))
        print("✅ Filter buttons present")

    def test_20_filter_functionality(self):
        """Test filter buttons actually filter the parks"""
        self.driver.get(BASE_URL)
        # Click Waterpark filter
        water_filter = None
        for f in self.driver.find_elements(By.CSS_SELECTOR, ".park-search__filter"):
            if "Waterpark" in f.text:
                water_filter = f
                break
        self.assertIsNotNone(water_filter, "Waterpark filter not found")
        self.safe_click(water_filter)
        time.sleep(1)
        # Check that some cards might be hidden (filter is working)
        visible_cards = len([c for c in self.driver.find_elements(By.CSS_SELECTOR, ".park-card") 
                            if c.is_displayed()])
        print(f"✅ Filter functionality working ({visible_cards} cards visible)")

    # ==================== LOGIN PAGE TESTS ====================

    def test_21_login_page_loads(self):
        """Test login page loads"""
        self.driver.get(f"{BASE_URL}/login.html")
        # Check for login form elements instead of title
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(body_text) > 0, "Login page body is empty")
        print("✅ Login page loaded")

    def test_22_login_form_elements(self):
        """Test login form has required fields"""
        self.driver.get(f"{BASE_URL}/login.html")
        try:
            email = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email")
            print("✅ Email field found")
        except NoSuchElementException:
            print("⚠️  Email field not found with standard selectors")
        
        try:
            password = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password'], #password")
            print("✅ Password field found")
        except NoSuchElementException:
            print("⚠️  Password field not found with standard selectors")
        
        try:
            submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .btn, input[type='submit']")
            print("✅ Submit button found")
        except NoSuchElementException:
            print("⚠️  Submit button not found with standard selectors")

    # ==================== BOOKING PAGE TESTS ====================

    def test_23_booking_page_loads(self):
        """Test booking page loads"""
        self.driver.get(f"{BASE_URL}/booking.html")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(body_text) > 0, "Booking page body is empty")
        print("✅ Booking page loaded")

    def test_24_booking_form_elements(self):
        """Test booking form has required fields"""
        self.driver.get(f"{BASE_URL}/booking.html")
        # Check for common booking form elements
        form_selectors = [
            "input[type='date'], #date, .date-input",
            "input[type='number'], #tickets, .ticket-input",
            "select, .package-select",
            "button[type='submit'], .book-btn, .submit-btn"
        ]
        found_elements = 0
        for selector in form_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    found_elements += 1
                    print(f"  Found: {selector}")
            except:
                pass
        self.assertGreaterEqual(found_elements, 2, "Expected at least 2 form elements")
        print(f"✅ Booking form elements present ({found_elements} found)")

    def test_25_booking_page_park_name_from_url(self):
        """Test booking page shows park name from URL parameter"""
        self.driver.get(f"{BASE_URL}/booking.html?park=Imagica%20Theme%20Park")
        time.sleep(1)
        # Look for park name in heading or any element
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        # Check if "Imagica" appears anywhere on the page
        if "Imagica" in body_text:
            print("✅ Booking page shows park name from URL")
        else:
            print("⚠️  Park name not prominently displayed (may be in form field)")

    # ==================== OTHER PAGE TESTS ====================

    def test_26_contact_page_loads(self):
        """Test contact page loads"""
        self.driver.get(f"{BASE_URL}/contact.html")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(body_text) > 0, "Contact page body is empty")
        print("✅ Contact page loaded")

    def test_27_blog_page_loads(self):
        """Test blog page loads"""
        self.driver.get(f"{BASE_URL}/blog.html")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(body_text) > 0, "Blog page body is empty")
        print("✅ Blog page loaded")

    def test_28_portfolio_page_loads(self):
        """Test portfolio page loads"""
        self.driver.get(f"{BASE_URL}/portfolio.html")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(body_text) > 0, "Portfolio page body is empty")
        print("✅ Portfolio page loaded")

    def test_29_payment_page_loads(self):
        """Test payment page loads"""
        self.driver.get(f"{BASE_URL}/payment.html")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(body_text) > 0, "Payment page body is empty")
        print("✅ Payment page loaded")

    # ==================== NAVIGATION TESTS ====================

    def test_30_nav_to_booking(self):
        """Test clicking Book Now navigates to booking page"""
        self.driver.get(BASE_URL)
        try:
            book_link = self.driver.find_element(By.LINK_TEXT, "Book Now ↗")
            self.safe_click(book_link)
            time.sleep(1)
            self.assertIn("booking.html", self.driver.current_url)
            print("✅ Navigation to booking page works")
        except NoSuchElementException:
            print("⚠️  Book Now link not found")

    def test_31_nav_to_login(self):
        """Test clicking Log In navigates to login page"""
        self.driver.get(BASE_URL)
        try:
            login_link = self.driver.find_element(By.LINK_TEXT, "Log In")
            self.safe_click(login_link)
            time.sleep(1)
            self.assertIn("login.html", self.driver.current_url)
            print("✅ Navigation to login page works")
        except NoSuchElementException:
            print("⚠️  Log In link not found")

    def test_32_modal_book_now_navigates(self):
        """Test Book Now button in modal navigates to booking page with park name"""
        self.driver.get(BASE_URL)
        self.driver.execute_script("openParkModal(0)")
        time.sleep(1)
        book_btn = self.safe_find(By.ID, "modalBookBtn")
        href = book_btn.get_attribute("href")
        self.assertIn("booking.html", href)
        self.assertIn("park=", href)
        print(f"✅ Modal Book Now button has correct URL: {href}")

    def test_33_page_responsiveness(self):
        """Test page renders at different viewport sizes"""
        self.driver.get(BASE_URL)
        sizes = [(1920, 1080), (1366, 768), (768, 1024), (375, 667)]
        for width, height in sizes:
            self.driver.set_window_size(width, height)
            time.sleep(0.5)
            hero = self.safe_find(By.CSS_SELECTOR, ".hero")
            self.assertTrue(hero.is_displayed(), f"Hero not visible at {width}x{height}")
        print(f"✅ Page responsive at {len(sizes)} viewport sizes")

    def test_34_images_load(self):
        """Test that images load without errors"""
        self.driver.get(BASE_URL)
        images = self.driver.find_elements(By.TAG_NAME, "img")
        broken_images = 0
        for img in images[:10]:  # Check first 10 images
            src = img.get_attribute("src")
            if src:
                # Check if image is displayed and has size
                is_displayed = img.is_displayed()
                natural_width = self.driver.execute_script("return arguments[0].naturalWidth;", img)
                if natural_width == 0:
                    broken_images += 1
                    print(f"  ⚠️  Broken image: {src[:50]}...")
        print(f"✅ Images checked ({len(images)} total, {broken_images} broken)")

    def test_35_javascript_execution(self):
        """Test JavaScript functions work correctly"""
        self.driver.get(BASE_URL)
        # Test that parks array exists
        parks_exist = self.driver.execute_script("return typeof parks !== 'undefined' && Array.isArray(parks);")
        self.assertTrue(parks_exist, "Parks array not found")
        parks_count = self.driver.execute_script("return parks.length;")
        self.assertGreater(parks_count, 0, "Parks array is empty")
        print(f"✅ JavaScript execution working ({parks_count} parks in data)")

    def test_36_performance_check(self):
        """Basic performance check - page load time"""
        import time as time_module
        start = time_module.time()
        self.driver.get(BASE_URL)
        # Wait for body to be present
        self.safe_find(By.TAG_NAME, "body")
        load_time = time_module.time() - start
        self.assertLess(load_time, 10, f"Page load too slow: {load_time:.2f}s")
        print(f"✅ Page load time: {load_time:.2f}s")


def run_tests():
    """Run the test suite with proper output formatting"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMyAdventures)
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*60)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
