# Auto Page Scroll Bot

A Python script that automatically scrolls web pages. Can be compiled into a standalone `.exe` file.

## Features

- Automatically scrolls any webpage
- Configurable scroll speed and duration
- Two scroll modes: continuous scroll and smooth scroll
- Easy to use command-line interface
- Can be compiled to a standalone `.exe` file

## Requirements

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by Selenium 4.6+)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the script:
```bash
python auto_scroll.py
```

## Building the Executable

### Option 1: Using the batch script (Windows)
```bash
build_exe.bat
```

### Option 2: Manual build
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AutoScrollBot" auto_scroll.py
```

The executable will be created in the `dist` folder.

## Usage

1. Run the script or executable
2. Enter the URL you want to scroll (or press Enter for default)
3. Choose scroll mode:
   - **Mode 1 (Continuous)**: Continuously scrolls at a set speed
   - **Mode 2 (Smooth)**: Smoothly scrolls from top to bottom
4. Set the duration in seconds
5. For continuous mode, set the scroll speed in pixels

## Notes

- The script uses Chrome browser (make sure Chrome is installed)
- ChromeDriver is automatically downloaded by Selenium 4.6+
- You can stop scrolling early by pressing Ctrl+C
- The browser window will remain open after scrolling completes

## Troubleshooting

If you encounter issues:

1. **ChromeDriver errors**: Make sure Chrome browser is installed and up to date
2. **Import errors**: Run `pip install -r requirements.txt`
3. **Build errors**: Make sure PyInstaller is installed: `pip install pyinstaller`



