"""
Auto Page Scroll Bot
Automatically scrolls a web page with configurable speed and duration.
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False


class AutoScrollBot:
    def __init__(self, headless=False):
        """Initialize the browser with Chrome options."""
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = None
    
    def start_browser(self):
        """Start the Chrome browser."""
        try:
            if USE_WEBDRIVER_MANAGER:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            else:
                self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.maximize_window()
            print("Browser started successfully!")
            return True
        except Exception as e:
            print(f"Error starting browser: {e}")
            print("Make sure Chrome browser is installed.")
            if not USE_WEBDRIVER_MANAGER:
                print("Consider installing webdriver-manager: pip install webdriver-manager")
            return False
    
    def navigate_to_url(self, url):
        """Navigate to the specified URL."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            print(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            return True
        except Exception as e:
            print(f"Error navigating to URL: {e}")
            return False
    
    def scroll_page(self, scroll_speed=1, duration=30, scroll_direction='down'):
        """
        Scroll the page automatically.
        
        Args:
            scroll_speed: Pixels to scroll per iteration (default: 1)
            duration: Duration in seconds to scroll (default: 30)
            scroll_direction: 'down' or 'up' (default: 'down')
        """
        if not self.driver:
            print("Browser not started!")
            return
        
        print(f"Starting auto-scroll for {duration} seconds...")
        print(f"Scroll speed: {scroll_speed} pixels per iteration")
        print(f"Direction: {scroll_direction}")
        print("Press Ctrl+C to stop early")
        
        start_time = time.time()
        scroll_delta = scroll_speed if scroll_direction == 'down' else -scroll_speed
        
        try:
            while time.time() - start_time < duration:
                # Get current scroll position
                current_scroll = self.driver.execute_script("return window.pageYOffset;")
                
                # Scroll
                self.driver.execute_script(f"window.scrollBy(0, {scroll_delta});")
                
                # Check if we've reached the bottom (for downward scroll) or top (for upward scroll)
                if scroll_direction == 'down':
                    page_height = self.driver.execute_script("return document.body.scrollHeight;")
                    window_height = self.driver.execute_script("return window.innerHeight;")
                    if current_scroll + window_height >= page_height:
                        print("Reached bottom of page. Scrolling back to top...")
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(1)
                else:
                    if current_scroll <= 0:
                        print("Reached top of page. Scrolling to bottom...")
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                
                time.sleep(0.01)  # Small delay for smooth scrolling
                
        except KeyboardInterrupt:
            print("\nScrolling stopped by user.")
        except Exception as e:
            print(f"Error during scrolling: {e}")
    
    def smooth_scroll_to_bottom(self, duration=30):
        """Smoothly scroll to the bottom of the page."""
        if not self.driver:
            print("Browser not started!")
            return
        
        print(f"Smooth scrolling for {duration} seconds...")
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # Get page dimensions
                page_height = self.driver.execute_script("return document.body.scrollHeight;")
                window_height = self.driver.execute_script("return window.innerHeight;")
                current_scroll = self.driver.execute_script("return window.pageYOffset;")
                
                # Calculate scroll position based on elapsed time
                elapsed = time.time() - start_time
                progress = min(elapsed / duration, 1.0)
                target_scroll = (page_height - window_height) * progress
                
                # Smooth scroll to target
                self.driver.execute_script(f"window.scrollTo(0, {target_scroll});")
                
                # If reached bottom, scroll back to top
                if current_scroll + window_height >= page_height:
                    print("Reached bottom. Restarting from top...")
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    start_time = time.time()  # Reset timer
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nScrolling stopped by user.")
        except Exception as e:
            print(f"Error during scrolling: {e}")
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            print("Browser closed.")


def main():
    """Main function to run the auto-scroll bot."""
    print("=" * 50)
    print("Auto Page Scroll Bot")
    print("=" * 50)
    
    # Get URL from user
    url = input("Enter the URL to scroll (or press Enter for default): ").strip()
    if not url:
        url = "https://www.example.com"
        print(f"Using default URL: {url}")
    
    # Get scroll mode
    print("\nScroll modes:")
    print("1. Continuous scroll (default)")
    print("2. Smooth scroll to bottom")
    mode = input("Choose mode (1 or 2, default: 1): ").strip() or "1"
    
    # Get duration
    duration_input = input("Enter scroll duration in seconds (default: 30): ").strip()
    duration = int(duration_input) if duration_input.isdigit() else 30
    
    # Get scroll speed (for continuous mode)
    scroll_speed = 1
    if mode == "1":
        speed_input = input("Enter scroll speed in pixels (default: 1): ").strip()
        scroll_speed = int(speed_input) if speed_input.isdigit() else 1
    
    # Initialize bot
    bot = AutoScrollBot(headless=False)
    
    if not bot.start_browser():
        return
    
    try:
        if not bot.navigate_to_url(url):
            return
        
        # Start scrolling based on mode
        if mode == "2":
            bot.smooth_scroll_to_bottom(duration=duration)
        else:
            bot.scroll_page(scroll_speed=scroll_speed, duration=duration)
        
        print("\nScrolling completed!")
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        bot.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
        sys.exit(0)

