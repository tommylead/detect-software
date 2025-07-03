# Whisk Session Takeover Tool

A Python automation tool for the Whisk platform using Chrome DevTools Protocol. Connects to existing Chrome sessions for stable, reliable automation.

## Features

- **Session Takeover**: Uses existing Chrome session (no authentication bypass)
- **Chrome DevTools Protocol**: Stable browser automation
- **Automatic Tab Detection**: Finds and connects to Whisk tabs
- **Batch Processing**: Processes multiple prompts from files
- **React Component Support**: Handles React state updates correctly
- **Error Handling**: Comprehensive retry logic and recovery
- **Detailed Logging**: Progress tracking and debugging

## Prerequisites

- **Python 3.7+**
- **Google Chrome**
- **Whisk account** with access to generation interface

## Installation

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Start Chrome with debugging:**
   ```bash
   # Windows
   start_chrome_debug.bat

   # macOS/Linux
   ./start_chrome_debug.sh
   ```

3. **Manual setup:**
   - Log into Google account in Chrome
   - Navigate to Whisk platform
   - Ensure you can access the generation interface

## Usage

### Basic Usage
```bash
# Run with default settings
python whisk_session_takeover.py --prompts prompts.txt

# With debug logging
python whisk_session_takeover.py --prompts prompts.txt --debug

# Custom delay and retries
python whisk_session_takeover.py --prompts prompts.txt --delay 30 --retries 5
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--prompts` | `prompts.txt` | Path to prompts file |
| `--delay` | `20` | Generation delay (seconds) |
| `--debug` | `False` | Enable debug logging |
| `--retries` | `3` | Retry attempts per prompt |

## Prompts File Format

Create a text file with one prompt per line:
```
Create a modern website homepage for a tech startup
Design a mobile app interface for food delivery
Generate a logo concept for an eco-friendly brand
```

## Troubleshooting

**Common Issues:**
- **"No Whisk tab found"**: Ensure Chrome is running with debugging and Whisk tab is open
- **"Failed to connect to Chrome"**: Check Chrome is running with `--remote-debugging-port=9222`
- **Generation not completing**: Increase delay with `--delay` option or check account credits

**Debug logging:**
```bash
python whisk_session_takeover.py --prompts prompts.txt --debug
```

## Success Rate

Expected: **85-90%** under normal conditions

## License

Provided as-is for educational and automation purposes. Use responsibly in accordance with Whisk's terms of service.
