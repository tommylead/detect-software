#!/usr/bin/env python3
"""
Whisk Session Takeover Tool

A Python automation tool that performs browser automation for the Whisk platform
using Chrome DevTools Protocol. This tool connects to an existing Chrome session
where the user is already logged into Whisk.

Prerequisites:
1. Chrome browser running with remote debugging enabled
2. User logged into Google account
3. User logged into Whisk platform

Usage:
    python whisk_session_takeover.py --prompts prompts.txt
    python whisk_session_takeover.py --prompts prompts.txt --delay 30 --debug

Author: AI Assistant
Date: 2025-07-02
"""

import asyncio
import json
import logging
import argparse
import time
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import websockets
import requests
from dataclasses import dataclass
from react_input_handler import ReactInputHandler


@dataclass
class WhiskConfig:
    """Configuration for Whisk automation"""
    chrome_debug_port: int = 9222
    generation_delay: int = 20
    retry_attempts: int = 3
    retry_delay: int = 5
    prompts_file: str = "prompts.txt"
    log_level: str = "INFO"
    whisk_url_pattern: str = "whisk"
    debug_mode: bool = False


class ChromeDevToolsClient:
    """Chrome DevTools Protocol client for browser automation"""
    
    def __init__(self, debug_port: int = 9222):
        self.debug_port = debug_port
        self.websocket = None
        self.message_id = 0
        self.logger = logging.getLogger(__name__)
        
    async def connect(self) -> bool:
        """Connect to Chrome DevTools Protocol"""
        try:
            self.logger.info(f"Attempting to connect to Chrome DevTools on port {self.debug_port}")

            # Get list of tabs
            try:
                response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=5)
                response.raise_for_status()
                tabs = response.json()
                self.logger.info(f"Found {len(tabs)} tabs in Chrome")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to connect to Chrome DevTools: {e}")
                self.logger.error("Make sure Chrome is running with --remote-debugging-port=9222")
                return False

            # Find Whisk tab
            whisk_tab = None
            for tab in tabs:
                if 'whisk' in tab.get('url', '').lower() or 'whisk' in tab.get('title', '').lower():
                    whisk_tab = tab
                    break

            # If no Whisk tab found, try to create one or use any available tab
            if not whisk_tab:
                self.logger.info("No Whisk tab found. Looking for available tab to navigate to Whisk...")

                # Try to find any active tab
                active_tab = None
                for tab in tabs:
                    if tab.get('type') == 'page' and 'webSocketDebuggerUrl' in tab:
                        active_tab = tab
                        break

                if not active_tab:
                    # Create new tab
                    self.logger.info("Creating new tab for Whisk...")
                    new_tab_response = requests.get(f"http://localhost:{self.debug_port}/json/new?https://whisk.com")
                    if new_tab_response.status_code == 200:
                        new_tab_data = new_tab_response.json()
                        whisk_tab = new_tab_data
                        self.logger.info("Created new Whisk tab")
                    else:
                        self.logger.error("Failed to create new tab")
                        return False
                else:
                    whisk_tab = active_tab
                    self.logger.info(f"Using existing tab: {active_tab.get('title', 'Unknown')}")

            # Connect to the tab
            websocket_url = whisk_tab['webSocketDebuggerUrl']
            self.logger.info(f"Connecting to WebSocket: {websocket_url}")

            try:
                self.websocket = await websockets.connect(websocket_url)
                self.logger.info(f"Successfully connected to tab: {whisk_tab.get('title', 'Unknown')}")
            except Exception as ws_error:
                self.logger.error(f"WebSocket connection failed: {ws_error}")
                return False

            # If not on Whisk, navigate to Whisk
            current_url = whisk_tab.get('url', '')
            if 'whisk' not in current_url.lower():
                self.logger.info("Navigating to Whisk.com...")
                await self.navigate_to_url("https://whisk.com")
                await asyncio.sleep(3)  # Wait for page to load
            
            # Enable runtime and DOM domains
            await self._send_command("Runtime.enable")
            await self._send_command("DOM.enable")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Chrome: {e}")
            return False

    async def navigate_to_url(self, url: str) -> bool:
        """Navigate to a specific URL"""
        try:
            await self._send_command("Page.navigate", {"url": url})
            self.logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False

    async def _send_command(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send command to Chrome DevTools"""
        self.message_id += 1
        message = {
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        
        await self.websocket.send(json.dumps(message))
        
        # Wait for response
        while True:
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("id") == self.message_id:
                if "error" in data:
                    raise Exception(f"Chrome DevTools error: {data['error']}")
                return data.get("result", {})
    
    async def execute_javascript(self, script: str) -> Any:
        """Execute JavaScript in the browser"""
        result = await self._send_command("Runtime.evaluate", {
            "expression": script,
            "returnByValue": True
        })
        
        if result.get("exceptionDetails"):
            raise Exception(f"JavaScript error: {result['exceptionDetails']}")
        
        return result.get("result", {}).get("value")
    
    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element to be present"""
        script = f"""
        (() => {{
            const element = document.querySelector('{selector}');
            return element !== null;
        }})()
        """

        return await self.execute_javascript(script)
    


    async def click_element(self, selector: str) -> bool:
        """Click an element"""
        script = f"""
        (() => {{
            const element = document.querySelector('{selector}');
            if (!element) return false;

            // Check if button is enabled
            if (element.disabled) return false;

            element.click();
            return true;
        }})()
        """

        return await self.execute_javascript(script)
    
    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()


class WhiskAutomator:
    """Main automation class for Whisk platform"""
    
    def __init__(self, config: WhiskConfig):
        self.config = config
        self.chrome_client = ChromeDevToolsClient(config.chrome_debug_port)
        self.logger = logging.getLogger(__name__)
        self.react_handler = None  # Will be initialized after chrome_client connects

        # Common selectors for Whisk interface (updated from b2 for better reliability)
        self.selectors = {
            'prompt_input': 'textarea[placeholder*="Describe your idea"], textarea.sc-19fd03b4-7.jjuyuu, textarea[placeholder*="Describe"], textarea[placeholder*="idea"], textarea',
            'generate_button': 'button[aria-label="Submit prompt"], button[type="submit"], button.sc-bece3008-0.iCCEfi, button[aria-label*="Submit"], button:has(i.google-symbols)',
            'loading_indicator': '.loading, .spinner, [data-loading="true"], .generating, [aria-busy="true"]'
        }
    
    async def initialize(self) -> bool:
        """Initialize the automation tool"""
        self.logger.info("Initializing Whisk automation tool...")

        if not await self.chrome_client.connect():
            return False

        # Initialize React handler after chrome client is connected
        self.react_handler = ReactInputHandler(self.chrome_client, self.logger)

        # Wait for page to be ready
        await asyncio.sleep(2)

        self.logger.info("Whisk automation tool initialized successfully")

        # Inspect page to find correct selectors
        await self.inspect_page_elements()

        return True

    async def inspect_page_elements(self):
        """Inspect page to find correct selectors for Whisk elements"""
        try:
            self.logger.info("🔍 Inspecting page elements...")

            # Find all textareas
            textarea_script = """
            (() => {
                const textareas = Array.from(document.querySelectorAll('textarea'));
                return textareas.map(ta => ({
                    placeholder: ta.placeholder,
                    id: ta.id,
                    className: ta.className,
                    name: ta.name,
                    ariaLabel: ta.getAttribute('aria-label'),
                    dataTestId: ta.getAttribute('data-testid'),
                    visible: ta.offsetParent !== null
                }));
            })()
            """

            textareas = await self.chrome_client.execute_javascript(textarea_script)
            if textareas:
                self.logger.info(f"Found {len(textareas)} textarea(s):")
                for i, ta in enumerate(textareas):
                    if ta.get('visible'):
                        self.logger.info(f"  Textarea {i+1}: placeholder='{ta.get('placeholder', '')}', class='{ta.get('className', '')}', id='{ta.get('id', '')}'")

            # Find all buttons
            button_script = """
            (() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.map(btn => ({
                    textContent: btn.textContent.trim(),
                    ariaLabel: btn.getAttribute('aria-label'),
                    type: btn.type,
                    className: btn.className,
                    id: btn.id,
                    dataTestId: btn.getAttribute('data-testid'),
                    disabled: btn.disabled,
                    visible: btn.offsetParent !== null,
                    hasIcon: btn.querySelector('i, svg') !== null
                }));
            })()
            """

            buttons = await self.chrome_client.execute_javascript(button_script)
            if buttons:
                visible_buttons = [btn for btn in buttons if btn.get('visible')]
                self.logger.info(f"Found {len(visible_buttons)} visible button(s):")
                for i, btn in enumerate(visible_buttons[:10]):  # Show first 10 buttons
                    text = btn.get('textContent', '')[:30]
                    aria = btn.get('ariaLabel', '')
                    disabled = btn.get('disabled', False)
                    has_icon = btn.get('hasIcon', False)
                    self.logger.info(f"  Button {i+1}: text='{text}', aria='{aria}', disabled={disabled}, hasIcon={has_icon}")

        except Exception as e:
            self.logger.warning(f"Failed to inspect page elements: {e}")
    
    def load_prompts(self) -> List[str]:
        """Load prompts from file"""
        prompts_path = Path(self.config.prompts_file)
        
        if not prompts_path.exists():
            self.logger.error(f"Prompts file not found: {prompts_path}")
            return []
        
        try:
            with open(prompts_path, 'r', encoding='utf-8') as f:
                prompts = [line.strip() for line in f if line.strip()]
            
            self.logger.info(f"Loaded {len(prompts)} prompts from {prompts_path}")
            return prompts
            
        except Exception as e:
            self.logger.error(f"Failed to load prompts: {e}")
            return []
    
    async def process_prompt(self, prompt: str, prompt_index: int) -> bool:
        """Process a single prompt with improved reliability from b2"""
        self.logger.info(f"Processing prompt {prompt_index + 1}: {prompt[:50]}...")

        for attempt in range(self.config.retry_attempts):
            try:
                # Check current page state
                self.logger.info(f"Attempt {attempt + 1}/{self.config.retry_attempts}")

                # Wait for prompt input field with improved selector priority
                textarea_found = False
                working_textarea_selector = None
                for selector in self.selectors['prompt_input'].split(', '):
                    selector = selector.strip()
                    if await self.chrome_client.wait_for_element(selector):
                        self.logger.info(f"✅ Found textarea with selector: {selector}")
                        textarea_found = True
                        working_textarea_selector = selector
                        break

                if not textarea_found:
                    self.logger.warning(f"❌ Prompt input field not found with any selector (attempt {attempt + 1})")
                    # Re-inspect page to find new selectors
                    await self.inspect_page_elements()
                    await asyncio.sleep(self.config.retry_delay)
                    continue

                # Fill the prompt using React-aware handler with improved timing
                self.logger.info(f"Filling prompt with React handler: {prompt[:30]}...")
                if not await self.react_handler.fill_react_textarea(working_textarea_selector, prompt):
                    self.logger.warning(f"Failed to fill prompt with React handler (attempt {attempt + 1})")
                    await asyncio.sleep(self.config.retry_delay)
                    continue

                # Wait a bit for React state to update
                await asyncio.sleep(1)

                # Find submit button with improved selector priority
                button_found = False
                working_button_selector = None
                for selector in self.selectors['generate_button'].split(', '):
                    selector = selector.strip()
                    if await self.chrome_client.wait_for_element(selector):
                        self.logger.info(f"✅ Found button with selector: {selector}")
                        button_found = True
                        working_button_selector = selector
                        break

                if not button_found:
                    self.logger.warning(f"❌ Generate button not found with any selector (attempt {attempt + 1})")
                    await self.inspect_page_elements()
                    await asyncio.sleep(self.config.retry_delay)
                    continue

                # Wait for React to update state and enable button with improved timeout
                self.logger.info("Waiting for submit button to be enabled...")
                button_enabled = await self.react_handler.wait_for_button_enabled_advanced(working_button_selector, timeout=20)

                if button_enabled:
                    # Button is enabled, try normal click first
                    self.logger.info("Button enabled, attempting normal click...")
                    if await self.chrome_client.click_element(working_button_selector):
                        self.logger.info("✅ Normal click successful")
                    else:
                        self.logger.warning("Normal click failed, trying force methods...")
                        if not await self.react_handler.force_enable_and_click(working_button_selector):
                            self.logger.warning(f"All click methods failed (attempt {attempt + 1})")
                            await asyncio.sleep(self.config.retry_delay)
                            continue
                else:
                    # Button not enabled naturally, try force methods
                    self.logger.warning(f"Generate button not enabled naturally, trying force methods (attempt {attempt + 1})")
                    if not await self.react_handler.force_enable_and_click(working_button_selector):
                        self.logger.warning(f"All click methods failed (attempt {attempt + 1})")
                        await asyncio.sleep(self.config.retry_delay)
                        continue

                # Wait for generation to complete with improved feedback
                self.logger.info(f"Waiting {self.config.generation_delay} seconds for generation...")
                await asyncio.sleep(self.config.generation_delay)

                self.logger.info(f"✅ Successfully processed prompt {prompt_index + 1}")
                return True

            except Exception as e:
                self.logger.error(f"Error processing prompt (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.config.retry_delay)

        self.logger.error(f"❌ Failed to process prompt after {self.config.retry_attempts} attempts")
        return False
    
    async def run(self) -> bool:
        """Run the automation process"""
        try:
            if not await self.initialize():
                return False
            
            prompts = self.load_prompts()
            if not prompts:
                return False
            
            self.logger.info(f"Starting automation for {len(prompts)} prompts...")
            
            successful_prompts = 0
            for i, prompt in enumerate(prompts):
                if await self.process_prompt(prompt, i):
                    successful_prompts += 1
                else:
                    self.logger.warning(f"Skipping failed prompt {i + 1}")
                
                # Small delay between prompts
                if i < len(prompts) - 1:
                    await asyncio.sleep(2)
            
            success_rate = (successful_prompts / len(prompts)) * 100
            self.logger.info(f"Automation completed. Success rate: {success_rate:.1f}% ({successful_prompts}/{len(prompts)})")
            
            return success_rate >= 50  # Consider successful if at least 50% of prompts processed
            
        except KeyboardInterrupt:
            self.logger.info("Automation interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"Automation failed: {e}")
            return False
        finally:
            await self.chrome_client.close()


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('whisk_automation.log', encoding='utf-8')
        ]
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Whisk Session Takeover Automation Tool")
    parser.add_argument("--prompts", default="prompts.txt", help="Path to prompts file")
    parser.add_argument("--delay", type=int, default=20, help="Generation delay in seconds")
    parser.add_argument("--port", type=int, default=9222, help="Chrome debug port")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--retries", type=int, default=3, help="Number of retry attempts")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)
    
    # Create configuration
    config = WhiskConfig(
        chrome_debug_port=args.port,
        generation_delay=args.delay,
        retry_attempts=args.retries,
        prompts_file=args.prompts,
        log_level=log_level
    )
    
    # Run automation
    automator = WhiskAutomator(config)
    
    try:
        success = asyncio.run(automator.run())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
