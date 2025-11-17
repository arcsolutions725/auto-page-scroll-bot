"""
Auto Page Scroll Bot
Automatically scrolls a web page with configurable speed and duration.
"""

import time
import sys

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - tkinter may be unavailable on some systems
    tk = None
    messagebox = None

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

DEFAULT_URL = "https://www.example.com"
DEFAULT_DURATION = 30
DEFAULT_SCROLL_SPEED = 1
DEFAULT_RUN_FOREVER = False


def console_available():
    """Return True if stdin is interactive and usable."""
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except Exception:
        return False


def _show_info_dialog(title, message):
    """Display a message box if tkinter is available."""
    if tk is None or messagebox is None:
        return
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message, parent=root)
    root.destroy()


def _parse_positive_int(value, default):
    """Convert string to positive int, return default on failure."""
    try:
        parsed = int(value)
        if parsed <= 0:
            raise ValueError
        return parsed
    except (TypeError, ValueError):
        return default


def collect_console_config(defaults):
    """Prompt for configuration using the console."""
    url = input("Enter the URL to scroll (or press Enter for default): ").strip()
    if not url:
        url = defaults["url"]
        print(f"Using default URL: {url}")

    print("\nScroll modes:")
    print("1. Continuous scroll (default)")
    print("2. Smooth scroll to bottom")
    mode = input("Choose mode (1 or 2, default: 1): ").strip() or defaults["mode"]
    if mode not in ("1", "2"):
        mode = defaults["mode"]
        print("Invalid choice. Using default mode (1).")

    duration_input = input("Enter scroll duration in seconds (default: 30): ").strip()
    duration = _parse_positive_int(duration_input, defaults["duration"])

    run_forever_input = input("Run indefinitely? (y/N): ").strip().lower()
    run_forever = run_forever_input in ("y", "yes")

    scroll_speed = defaults["scroll_speed"]
    if mode == "1":
        speed_input = input("Enter scroll speed in pixels (default: 1): ").strip()
        scroll_speed = _parse_positive_int(speed_input, defaults["scroll_speed"])

    return {
        "url": url,
        "mode": mode,
        "duration": duration,
        "scroll_speed": scroll_speed,
        "run_forever": run_forever,
    }


def show_gui_config_dialog(defaults):
    """Prompt for configuration using a simple Tkinter dialog."""
    if tk is None:
        _show_info_dialog(
            "Auto Page Scroll Bot",
            "Graphical prompts are unavailable. Default settings will be used.",
        )
        return defaults.copy()

    result = {"config": None}

    root = tk.Tk()
    root.title("Auto Page Scroll Bot - Settings")
    root.resizable(True, True)
    root.minsize(420, 340)
    root.configure(padx=10, pady=10)

    url_var = tk.StringVar(value=defaults["url"])
    mode_var = tk.StringVar(value=defaults["mode"])
    duration_var = tk.StringVar(value=str(defaults["duration"]))
    scroll_var = tk.StringVar(value=str(defaults["scroll_speed"]))
    run_forever_var = tk.BooleanVar(value=defaults["run_forever"])
    status_var = tk.StringVar(value="")

    def submit():
        url_value = url_var.get().strip() or defaults["url"]
        selected_mode = mode_var.get()
        if run_forever_var.get():
            duration_value = defaults["duration"]
        else:
            duration_value = _parse_positive_int(duration_var.get(), 0)
            if duration_value <= 0:
                status_var.set("Duration must be a positive integer.")
                return

        scroll_value = defaults["scroll_speed"]
        if selected_mode == "1":
            scroll_value = _parse_positive_int(scroll_var.get(), 0)
            if scroll_value <= 0:
                status_var.set("Scroll speed must be a positive integer.")
                return

        result["config"] = {
            "url": url_value,
            "mode": selected_mode,
            "duration": duration_value,
            "scroll_speed": scroll_value,
            "run_forever": run_forever_var.get(),
        }
        root.destroy()

    def cancel():
        result["config"] = None
        root.destroy()

    def on_close():
        cancel()

    url_label = tk.Label(root, text="URL to scroll:")
    url_entry = tk.Entry(root, textvariable=url_var, width=50)

    mode_frame = tk.LabelFrame(root, text="Scroll mode")
    tk.Radiobutton(mode_frame, text="Continuous", variable=mode_var, value="1").pack(anchor="w")
    tk.Radiobutton(mode_frame, text="Smooth to bottom", variable=mode_var, value="2").pack(anchor="w")

    duration_label = tk.Label(root, text="Duration (seconds):")
    duration_entry = tk.Entry(root, textvariable=duration_var, width=10)

    scroll_label = tk.Label(root, text="Scroll speed (pixels per iteration, mode 1):")
    scroll_entry = tk.Entry(root, textvariable=scroll_var, width=10)

    def refresh_controls(*_):
        mode_state = "normal" if mode_var.get() == "1" else "disabled"
        scroll_entry.configure(state=mode_state)

        duration_state = "disabled" if run_forever_var.get() else "normal"
        duration_entry.configure(state=duration_state)

    mode_var.trace_add("write", refresh_controls)
    run_forever_var.trace_add("write", refresh_controls)
    refresh_controls()

    button_frame = tk.Frame(root)
    submit_btn = tk.Button(button_frame, text="Start", command=submit, width=12)
    cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel, width=12)

    status_label = tk.Label(root, textvariable=status_var, fg="red")

    url_label.pack(pady=(10, 0))
    url_entry.pack(pady=2)
    mode_frame.pack(fill="x", padx=10, pady=10)
    duration_label.pack()
    duration_entry.pack()
    run_forever_check = tk.Checkbutton(root, text="Loop forever", variable=run_forever_var)
    run_forever_check.pack(pady=(5, 5))
    scroll_label.pack(pady=(10, 0))
    scroll_entry.pack()
    status_label.pack()
    button_frame.pack(pady=10)
    submit_btn.pack(side="left", padx=5)
    cancel_btn.pack(side="right", padx=5)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    return result["config"]


def collect_user_config():
    """Collect configuration based on available input methods."""
    defaults = {
        "url": DEFAULT_URL,
        "mode": "1",
        "duration": DEFAULT_DURATION,
        "scroll_speed": DEFAULT_SCROLL_SPEED,
        "run_forever": DEFAULT_RUN_FOREVER,
    }

    if console_available():
        return collect_console_config(defaults)

    config = show_gui_config_dialog(defaults)
    if config is None:
        _show_info_dialog("Auto Page Scroll Bot", "Configuration cancelled. The application will close.")
    return config


def notify_completion(run_forever=False):
    """Pause for user acknowledgement depending on environment."""
    if run_forever:
        return
    if console_available():
        try:
            input("Press Enter to close the browser...")
        except RuntimeError:
            # Fall back to GUI dialog if stdin becomes unavailable mid-run.
            _show_info_dialog("Auto Page Scroll Bot", "Scrolling completed! Click OK to close the browser.")
    else:
        _show_info_dialog("Auto Page Scroll Bot", "Scrolling completed! Click OK to close the browser.")


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
    
    def scroll_page(self, scroll_speed=1, duration=None, scroll_direction='down'):
        """
        Scroll the page automatically.
        
        Args:
            scroll_speed: Pixels to scroll per iteration (default: 1)
            duration: Duration in seconds to scroll (None for infinite)
            scroll_direction: 'down' or 'up' (default: 'down')
        """
        if not self.driver:
            print("Browser not started!")
            return
        
        duration_text = f"{duration} seconds" if duration is not None else "indefinitely"
        print(f"Starting auto-scroll for {duration_text}...")
        print(f"Scroll speed: {scroll_speed} pixels per iteration")
        print(f"Direction: {scroll_direction}")
        print("Press Ctrl+C to stop early")
        
        start_time = time.time()
        end_time = None if duration is None else start_time + duration
        direction = 1 if scroll_direction == 'down' else -1
        
        try:
            while duration is None or time.time() < end_time:
                # Get current scroll position
                current_scroll = self.driver.execute_script("return window.pageYOffset;")
                
                # Scroll
                scroll_delta = scroll_speed * direction
                self.driver.execute_script(f"window.scrollBy(0, {scroll_delta});")
                
                # Check bounds and reverse direction when needed
                page_height = self.driver.execute_script("return document.body.scrollHeight;")
                window_height = self.driver.execute_script("return window.innerHeight;")
                max_scroll = max(page_height - window_height, 0)

                if direction == 1 and current_scroll >= max_scroll:
                    direction = -1
                    print("Reached bottom of page. Reversing to scroll up.")
                elif direction == -1 and current_scroll <= 0:
                    direction = 1
                    print("Reached top of page. Reversing to scroll down.")
                
                time.sleep(0.01)  # Small delay for smooth scrolling
                
        except KeyboardInterrupt:
            print("\nScrolling stopped by user.")
        except Exception as e:
            print(f"Error during scrolling: {e}")
    
    def smooth_scroll_to_bottom(self, duration=None):
        """Smoothly scroll to the bottom of the page."""
        if not self.driver:
            print("Browser not started!")
            return
        
        duration_text = f"{duration} seconds" if duration is not None else "indefinitely"
        print(f"Smooth scrolling for {duration_text}...")
        start_time = time.time()
        end_time = None if duration is None else start_time + duration
        cycle_duration = duration if duration else DEFAULT_DURATION
        
        try:
            while duration is None or time.time() < end_time:
                # Get page dimensions
                page_height = self.driver.execute_script("return document.body.scrollHeight;")
                window_height = self.driver.execute_script("return window.innerHeight;")
                current_scroll = self.driver.execute_script("return window.pageYOffset;")
                
                # Calculate scroll position based on elapsed time
                elapsed = time.time() - start_time
                progress = min(elapsed / cycle_duration, 1.0) if cycle_duration else 1.0
                target_scroll = (page_height - window_height) * progress
                
                # Smooth scroll to target
                self.driver.execute_script(f"window.scrollTo(0, {target_scroll});")
                
                # If reached bottom, scroll back to top
                if current_scroll + window_height >= page_height:
                    print("Reached bottom. Restarting from top...")
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    start_time = time.time()  # Reset timer
                    if duration:
                        end_time = start_time + duration
                
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

    config = collect_user_config()
    if not config:
        print("No configuration provided. Exiting.")
        return

    url = config["url"]
    mode = config["mode"]
    scroll_speed = config["scroll_speed"]
    run_forever = config.get("run_forever", False)
    duration = None if run_forever else config["duration"]
    
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
        
        if not run_forever:
            print("\nScrolling completed!")
            notify_completion(run_forever=False)
        
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

