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
            # Get list of tabs
            response = requests.get(f"http://localhost:{self.debug_port}/json")
            tabs = response.json()
            
            # Find Whisk tab
            whisk_tab = None
            for tab in tabs:
                if 'whisk' in tab.get('url', '').lower() or 'whisk' in tab.get('title', '').lower():
                    whisk_tab = tab
                    break
            
            if not whisk_tab:
                self.logger.error("No Whisk tab found. Please ensure Whisk is open in Chrome.")
                return False
            
            # Connect to the Whisk tab
            websocket_url = whisk_tab['webSocketDebuggerUrl']
            self.websocket = await websockets.connect(websocket_url)
            self.logger.info(f"Connected to Whisk tab: {whisk_tab['title']}")
            
            # Enable runtime and DOM domains
            await self._send_command("Runtime.enable")
            await self._send_command("DOM.enable")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Chrome: {e}")
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

        # Common selectors for Whisk interface (updated based on actual HTML inspection)
        self.selectors = {
            'prompt_input': 'textarea[placeholder*="Describe your idea"], textarea.sc-19fd03b4-7.jjuyuu, textarea',
            'generate_button': 'button[aria-label="Submit prompt"], button[type="submit"], button.sc-bece3008-0.iCCEfi',
            'loading_indicator': '.loading, .spinner, [data-loading="true"], .generating'
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
        return True
    
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
        """Process a single prompt"""
        self.logger.info(f"Processing prompt {prompt_index + 1}: {prompt[:50]}...")
        
        for attempt in range(self.config.retry_attempts):
            try:
                # Wait for prompt input field
                if not await self.chrome_client.wait_for_element(self.selectors['prompt_input']):
                    self.logger.warning(f"Prompt input field not found (attempt {attempt + 1})")
                    await asyncio.sleep(self.config.retry_delay)
                    continue

                # Fill the prompt using React-aware handler
                self.logger.info(f"Filling prompt with React handler: {prompt[:30]}...")
                if not await self.react_handler.fill_react_textarea(self.selectors['prompt_input'], prompt):
                    self.logger.warning(f"Failed to fill prompt with React handler (attempt {attempt + 1})")
                    await asyncio.sleep(self.config.retry_delay)
                    continue

                # Wait for React to update state and enable button
                self.logger.info("Waiting for submit button to be enabled...")
                if not await self.react_handler.wait_for_button_enabled_advanced(self.selectors['generate_button'], timeout=15):
                    self.logger.warning(f"Generate button not enabled naturally, trying force methods (attempt {attempt + 1})")

                    # Try force enable and click
                    if not await self.react_handler.force_enable_and_click(self.selectors['generate_button']):
                        self.logger.warning(f"All click methods failed (attempt {attempt + 1})")
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                else:
                    # Button is enabled, try normal click
                    self.logger.info("Button enabled, attempting normal click...")
                    if not await self.chrome_client.click_element(self.selectors['generate_button']):
                        self.logger.warning(f"Normal click failed, trying force methods (attempt {attempt + 1})")
                        if not await self.react_handler.force_enable_and_click(self.selectors['generate_button']):
                            self.logger.warning(f"All click methods failed (attempt {attempt + 1})")
                            await asyncio.sleep(self.config.retry_delay)
                            continue
                
                # Wait for generation to complete
                self.logger.info(f"Waiting {self.config.generation_delay} seconds for generation...")
                await asyncio.sleep(self.config.generation_delay)
                
                self.logger.info(f"Successfully processed prompt {prompt_index + 1}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error processing prompt (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.config.retry_delay)
        
        self.logger.error(f"Failed to process prompt after {self.config.retry_attempts} attempts")
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
