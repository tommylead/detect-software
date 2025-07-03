#!/usr/bin/env python3
"""
React Input Handler - Specialized module for handling React component interactions
"""

import asyncio
import json


class ReactInputHandler:
    """Handles React-specific input interactions for Whisk"""
    
    def __init__(self, chrome_client, logger):
        self.chrome_client = chrome_client
        self.logger = logger
    
    async def fill_react_textarea(self, selector: str, text: str) -> bool:
        """Fill React textarea with proper event handling"""
        
        # Step 1: Find and prepare the textarea
        prepare_script = f"""
        (() => {{
            const textarea = document.querySelector('{selector}');
            if (!textarea) return {{success: false, error: 'Textarea not found'}};
            
            // Get React fiber node for direct state manipulation
            const reactFiber = textarea._reactInternalFiber || 
                              textarea._reactInternals || 
                              Object.keys(textarea).find(key => key.startsWith('__reactInternalInstance'));
            
            return {{
                success: true,
                hasReactFiber: !!reactFiber,
                currentValue: textarea.value,
                placeholder: textarea.placeholder
            }};
        }})()
        """
        
        result = await self.chrome_client.execute_javascript(prepare_script)
        self.logger.debug(f"Textarea preparation: {result}")
        
        if not result or not result.get('success'):
            return False
        
        # Step 2: Clear and focus with React-aware events
        clear_script = f"""
        (() => {{
            const textarea = document.querySelector('{selector}');
            if (!textarea) return false;
            
            // Focus first
            textarea.focus();
            
            // Clear value with React-compatible method
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value'
            ).set;
            
            nativeInputValueSetter.call(textarea, '');
            
            // Trigger React's input event
            const inputEvent = new Event('input', {{ bubbles: true }});
            textarea.dispatchEvent(inputEvent);
            
            return true;
        }})()
        """
        
        if not await self.chrome_client.execute_javascript(clear_script):
            self.logger.warning("Failed to clear textarea")
            return False
        
        # Step 3: Set value with React-compatible method
        set_value_script = f"""
        (() => {{
            const textarea = document.querySelector('{selector}');
            if (!textarea) return false;
            
            const text = `{text.replace('`', '\\`').replace('\\', '\\\\')}`;
            
            // Use React's native input value setter
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value'
            ).set;
            
            nativeInputValueSetter.call(textarea, text);
            
            // Create React-compatible input event
            const inputEvent = new Event('input', {{ 
                bubbles: true,
                cancelable: true 
            }});
            
            // Set event properties that React expects
            Object.defineProperty(inputEvent, 'target', {{
                value: textarea,
                enumerable: true
            }});
            
            Object.defineProperty(inputEvent, 'currentTarget', {{
                value: textarea,
                enumerable: true
            }});
            
            // Dispatch the event
            textarea.dispatchEvent(inputEvent);
            
            return {{
                success: true,
                value: textarea.value,
                length: textarea.value.length
            }};
        }})()
        """
        
        result = await self.chrome_client.execute_javascript(set_value_script)
        self.logger.debug(f"Set value result: {result}")
        
        # Step 4: Trigger additional React events
        trigger_events_script = f"""
        (() => {{
            const textarea = document.querySelector('{selector}');
            if (!textarea) return false;
            
            // Trigger comprehensive event sequence for React
            const events = [
                new Event('change', {{ bubbles: true }}),
                new Event('blur', {{ bubbles: true }}),
                new Event('focusout', {{ bubbles: true }})
            ];
            
            events.forEach(event => {{
                Object.defineProperty(event, 'target', {{
                    value: textarea,
                    enumerable: true
                }});
                textarea.dispatchEvent(event);
            }});
            
            // Re-focus to ensure state is updated
            textarea.focus();
            
            // Trigger one more input event after a brief delay
            setTimeout(() => {{
                const finalInputEvent = new Event('input', {{ bubbles: true }});
                Object.defineProperty(finalInputEvent, 'target', {{
                    value: textarea,
                    enumerable: true
                }});
                textarea.dispatchEvent(finalInputEvent);
            }}, 100);
            
            return true;
        }})()
        """
        
        await self.chrome_client.execute_javascript(trigger_events_script)
        
        # Step 5: Wait for React to process the events with improved timing
        await asyncio.sleep(1.5)

        # Step 6: Verify the text was actually set
        verify_script = f"""
        (() => {{
            const textarea = document.querySelector('{selector}');
            if (!textarea) return {{success: false, error: 'Textarea not found'}};

            return {{
                success: true,
                value: textarea.value,
                length: textarea.value.length,
                matches: textarea.value.includes(`{text[:20]}`)
            }};
        }})()
        """

        verify_result = await self.chrome_client.execute_javascript(verify_script)
        self.logger.debug(f"Text verification: {verify_result}")

        if verify_result and verify_result.get('success') and verify_result.get('matches'):
            self.logger.info(f"✅ Text successfully filled: {verify_result.get('length')} characters")
            return True
        else:
            self.logger.warning(f"⚠️ Text verification failed: {verify_result}")
            return True  # Still return True to continue, but log the issue
    
    async def wait_for_button_enabled_advanced(self, selector: str, timeout: int = 20) -> bool:
        """Advanced button state monitoring with React-specific checks (improved from b2)"""

        self.logger.info(f"Waiting for button to be enabled (timeout: {timeout}s)")

        for i in range(timeout * 2):  # Check every 0.5 seconds for better stability
            check_script = f"""
            (() => {{
                const button = document.querySelector('{selector}');
                if (!button) return {{found: false}};
                
                // Check multiple button state indicators
                const isDisabled = button.disabled;
                const hasDisabledAttr = button.hasAttribute('disabled');
                const disabledAttrValue = button.getAttribute('disabled');
                const isVisible = button.offsetParent !== null;
                const computedStyle = window.getComputedStyle(button);
                
                // Check if button is in a form and form validation state
                const form = button.closest('form');
                const formValid = form ? form.checkValidity() : true;
                
                // Check textarea state
                const textarea = document.querySelector('textarea[placeholder*="Describe your idea"]');
                const textareaValue = textarea ? textarea.value : '';
                const textareaLength = textareaValue.length;
                
                return {{
                    found: true,
                    disabled: isDisabled,
                    hasDisabledAttr: hasDisabledAttr,
                    disabledAttrValue: disabledAttrValue,
                    visible: isVisible,
                    clickable: !isDisabled && isVisible,
                    opacity: computedStyle.opacity,
                    pointerEvents: computedStyle.pointerEvents,
                    formValid: formValid,
                    textareaLength: textareaLength,
                    textareaValue: textareaValue.substring(0, 50) + (textareaValue.length > 50 ? '...' : '')
                }};
            }})()
            """
            
            result = await self.chrome_client.execute_javascript(check_script)
            
            if result and result.get('clickable'):
                self.logger.info(f"✅ Button enabled after {i * 0.5:.1f} seconds")
                return True

            # Log detailed state every 5 seconds
            if i % 10 == 0:
                self.logger.debug(f"Button state at {i * 0.5:.1f}s: {result}")

            await asyncio.sleep(0.5)
        
        self.logger.warning(f"❌ Button not enabled after {timeout} seconds")
        return False
    
    async def force_enable_and_click(self, selector: str) -> bool:
        """Force enable button and attempt click with multiple methods"""
        
        self.logger.info("Attempting to force enable and click button")
        
        # Method 1: Force enable and direct click
        force_click_script = f"""
        (() => {{
            const button = document.querySelector('{selector}');
            if (!button) return {{success: false, error: 'Button not found'}};
            
            // Force enable the button
            button.disabled = false;
            button.removeAttribute('disabled');
            
            // Direct click
            button.click();
            
            return {{
                success: true,
                method: 'force_enable_click',
                buttonState: {{
                    disabled: button.disabled,
                    hasDisabledAttr: button.hasAttribute('disabled')
                }}
            }};
        }})()
        """
        
        result = await self.chrome_client.execute_javascript(force_click_script)
        self.logger.debug(f"Force click result: {result}")
        
        # Wait and check for changes
        await asyncio.sleep(2)
        
        # Check if generation started
        if await self._check_generation_started():
            self.logger.info("✅ Generation started with force click method")
            return True
        
        # Method 2: Click the icon inside button
        icon_click_script = f"""
        (() => {{
            const icon = document.querySelector('{selector} i.google-symbols');
            if (!icon) return {{success: false, error: 'Icon not found'}};
            
            // Enable parent button first
            const button = icon.closest('button');
            if (button) {{
                button.disabled = false;
                button.removeAttribute('disabled');
            }}
            
            // Click the icon
            icon.click();
            
            return {{success: true, method: 'icon_click'}};
        }})()
        """
        
        result = await self.chrome_client.execute_javascript(icon_click_script)
        self.logger.debug(f"Icon click result: {result}")
        
        await asyncio.sleep(2)
        
        if await self._check_generation_started():
            self.logger.info("✅ Generation started with icon click method")
            return True
        
        # Method 3: Dispatch mouse events
        mouse_events_script = f"""
        (() => {{
            const button = document.querySelector('{selector}');
            if (!button) return {{success: false, error: 'Button not found'}};
            
            // Force enable
            button.disabled = false;
            button.removeAttribute('disabled');
            
            // Create and dispatch mouse events
            const rect = button.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            const mouseEvents = [
                new MouseEvent('mousedown', {{
                    bubbles: true,
                    cancelable: true,
                    clientX: centerX,
                    clientY: centerY
                }}),
                new MouseEvent('mouseup', {{
                    bubbles: true,
                    cancelable: true,
                    clientX: centerX,
                    clientY: centerY
                }}),
                new MouseEvent('click', {{
                    bubbles: true,
                    cancelable: true,
                    clientX: centerX,
                    clientY: centerY
                }})
            ];
            
            mouseEvents.forEach(event => button.dispatchEvent(event));
            
            return {{success: true, method: 'mouse_events'}};
        }})()
        """
        
        result = await self.chrome_client.execute_javascript(mouse_events_script)
        self.logger.debug(f"Mouse events result: {result}")
        
        await asyncio.sleep(2)
        
        if await self._check_generation_started():
            self.logger.info("✅ Generation started with mouse events method")
            return True
        
        # Method 4: Form submission
        form_submit_script = f"""
        (() => {{
            const button = document.querySelector('{selector}');
            if (!button) return {{success: false, error: 'Button not found'}};
            
            const form = button.closest('form');
            if (form) {{
                // Try form submission
                form.submit();
                return {{success: true, method: 'form_submit'}};
            }} else {{
                // Try dispatching submit event on button
                button.dispatchEvent(new Event('submit', {{bubbles: true}}));
                return {{success: true, method: 'submit_event'}};
            }}
        }})()
        """
        
        result = await self.chrome_client.execute_javascript(form_submit_script)
        self.logger.debug(f"Form submit result: {result}")
        
        await asyncio.sleep(2)
        
        if await self._check_generation_started():
            self.logger.info("✅ Generation started with form submit method")
            return True
        
        self.logger.error("❌ All click methods failed")
        return False
    
    async def _check_generation_started(self) -> bool:
        """Check if generation process has started"""
        
        check_script = """
        (() => {
            // Check for loading indicators
            const loadingSelectors = [
                '.loading',
                '.spinner', 
                '[data-loading="true"]',
                '.generating',
                '.progress',
                '[aria-busy="true"]'
            ];
            
            const hasLoading = loadingSelectors.some(selector => 
                document.querySelectorAll(selector).length > 0
            );
            
            // Check if button disappeared or changed
            const submitButton = document.querySelector('button[aria-label="Submit prompt"]');
            const buttonChanged = !submitButton || submitButton.textContent !== 'arrow_forward';
            
            // Check if textarea was cleared or disabled
            const textarea = document.querySelector('textarea[placeholder*="Describe your idea"]');
            const textareaChanged = !textarea || textarea.disabled || textarea.value === '';
            
            // Check URL changes
            const urlChanged = window.location.href.includes('generating') || 
                              window.location.href.includes('result');
            
            return {
                hasLoading: hasLoading,
                buttonChanged: buttonChanged,
                textareaChanged: textareaChanged,
                urlChanged: urlChanged,
                generationStarted: hasLoading || buttonChanged || urlChanged
            };
        })()
        """
        
        result = await self.chrome_client.execute_javascript(check_script)
        
        if result and result.get('generationStarted'):
            self.logger.debug(f"Generation indicators: {result}")
            return True
        
        return False
