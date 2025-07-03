#!/usr/bin/env python3
"""
Whisk Automation Tool - Licensed Professional Edition
Giao diện chính với hệ thống xác thực license
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import asyncio
import sys
import os
import subprocess
import platform
import time
from pathlib import Path

# Import license authentication
from license_auth import authenticate_license, LicenseAuth

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class WhiskGUILicensed:
    def __init__(self):
        # Xác thực license trước khi khởi tạo GUI
        if not self.check_license():
            sys.exit(0)
        
        self.root = tk.Tk()
        self.root.title("Whisk Automation Tool - Licensed Professional Edition v2.1.1")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Set custom icon (remove feather icon, use ico_chuan.ico)
        self.set_window_icon(self.root)
        
        # License info
        self.license_auth = LicenseAuth()
        
        # Variables
        self.chrome_process = None
        self.automation_running = False
        self.automation_thread = None
        
        # Setup styles
        self.setup_styles()

        # Create GUI
        self.create_gui()

        # Initialize automation
        self.init_automation()

    def set_window_icon(self, window):
        """Set custom icon for window, removing feather icon"""
        try:
            # Try multiple icon paths
            icon_paths = [
                "ico_chuan.ico",
                os.path.join(os.path.dirname(__file__), "ico_chuan.ico"),
                os.path.join("dist", "ico_chuan.ico"),
                "ico_chuan.png"  # Fallback to PNG
            ]

            icon_set = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        if icon_path.endswith('.ico'):
                            window.iconbitmap(icon_path)
                        elif icon_path.endswith('.png') and PIL_AVAILABLE:
                            # Use PNG with PIL if available
                            from PIL import Image, ImageTk
                            img = Image.open(icon_path)
                            img = img.resize((32, 32), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            window.iconphoto(True, photo)
                        icon_set = True
                        print(f"✅ Icon loaded from: {icon_path}")
                        break
                    except Exception as e:
                        print(f"⚠️ Failed to load icon from {icon_path}: {e}")
                        continue

            if not icon_set:
                # Remove default icon to avoid feather icon
                try:
                    window.iconbitmap("")
                    print("🚫 Removed default icon (no custom icon found)")
                except:
                    pass

        except Exception as e:
            print(f"❌ Icon setup error: {e}")
            try:
                window.iconbitmap("")
            except:
                pass

    def check_license(self):
        """Kiểm tra license trước khi khởi động"""
        try:
            # Xác thực license
            result = authenticate_license()
            return result

        except Exception as e:
            messagebox.showerror("License Error", f"License authentication failed: {str(e)}")
            return False
    
    def create_splash_screen(self):
        """Tạo splash screen trong khi check license"""
        try:
            splash = tk.Tk()
            splash.title("Whisk Automation Tool")
            splash.geometry("400x200")
            splash.resizable(False, False)
            
            # Center splash screen
            splash.eval('tk::PlaceWindow . center')
            
            # Content
            frame = ttk.Frame(splash, padding="30")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Logo/Title
            title_label = ttk.Label(frame, text="🎨 Whisk Automation Tool", 
                                   font=("Segoe UI", 16, "bold"), foreground="#2196F3")
            title_label.pack(pady=(0, 10))
            
            subtitle_label = ttk.Label(frame, text="Licensed Professional Edition", 
                                      font=("Segoe UI", 10), foreground="#666666")
            subtitle_label.pack(pady=(0, 20))
            
            # Loading
            loading_label = ttk.Label(frame, text="🔐 Checking license...", 
                                     font=("Segoe UI", 10))
            loading_label.pack(pady=(0, 10))
            
            progress = ttk.Progressbar(frame, mode='indeterminate')
            progress.pack(fill=tk.X, pady=(0, 20))
            progress.start()
            
            # Support
            support_label = ttk.Label(frame, text="Support: Zalo 0379822057 (Nghĩa)", 
                                     font=("Segoe UI", 8), foreground="#2196F3")
            support_label.pack()
            
            splash.update()
            return splash
            
        except:
            return None
    
    def setup_styles(self):
        """Thiết lập styles cho giao diện"""
        style = ttk.Style()
        
        # Configure modern button style
        style.configure("Modern.TButton",
                       padding=(10, 5),
                       font=("Segoe UI", 9))
        
        # Configure header style
        style.configure("Header.TLabel",
                       font=("Segoe UI", 12, "bold"),
                       foreground="#2196F3")
        
        # Configure status style
        style.configure("Status.TLabel",
                       font=("Segoe UI", 9),
                       foreground="#666666")
    
    def create_gui(self):
        """Tạo giao diện chính"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header section
        self.create_header(main_frame)
        
        # License status section
        self.create_license_status(main_frame)
        
        # Configuration section
        self.create_config_section(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
        # Content section
        self.create_content_section(main_frame)
        
        # Log section
        self.create_log_section(main_frame)
    
    def create_header(self, parent):
        """Tạo header với logo và thông tin"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Logo section - FORCE ico_chuan.png
        logo_loaded = False
        if PIL_AVAILABLE:
            try:
                # Get resource path for PyInstaller
                def get_resource_path(relative_path):
                    try:
                        # PyInstaller creates a temp folder and stores path in _MEIPASS
                        base_path = sys._MEIPASS
                        print(f"🔍 PyInstaller base path: {base_path}")
                    except Exception:
                        base_path = os.path.abspath(".")
                        print(f"🔍 Current directory: {base_path}")
                    return os.path.join(base_path, relative_path)

                # FORCE ico_chuan.png ONLY - no fallback to old logos
                logo_file = "ico_chuan.png"
                print(f"🎨 Attempting to load: {logo_file}")

                # Try multiple paths
                logo_paths = [
                    get_resource_path(logo_file),  # PyInstaller resource path
                    logo_file,                     # Current directory
                    os.path.join(".", logo_file),  # Explicit current dir
                ]

                for logo_path in logo_paths:
                    print(f"🔍 Trying path: {logo_path}")
                    try:
                        if os.path.exists(logo_path):
                            print(f"✅ File exists: {logo_path}")
                            logo_img = Image.open(logo_path)
                            logo_img = logo_img.resize((48, 48), Image.Resampling.LANCZOS)
                            self.logo_photo = ImageTk.PhotoImage(logo_img)
                            logo_label = ttk.Label(header_frame, image=self.logo_photo)
                            logo_label.grid(row=0, column=0, padx=(0, 15))
                            logo_loaded = True
                            print(f"🎉 SUCCESS: Logo loaded from {logo_path}")
                            break
                        else:
                            print(f"❌ File not found: {logo_path}")
                    except Exception as e:
                        print(f"❌ Failed to load from {logo_path}: {e}")
                        continue

                if not logo_loaded:
                    print("❌ FAILED to load ico_chuan.png from any path")

            except Exception as e:
                print(f"❌ Logo loading error: {e}")
                pass
        
        if not logo_loaded:
            logo_label = ttk.Label(header_frame, text="🎨", font=("Arial", 32))
            logo_label.grid(row=0, column=0, padx=(0, 15))
        
        # Title and info
        title_info_frame = ttk.Frame(header_frame)
        title_info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        title_info_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(title_info_frame, text="Whisk Automation Tool", 
                               style="Header.TLabel")
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Subtitle with license info
        subtitle_label = ttk.Label(title_info_frame, 
                                  text="Licensed Professional Edition v2.0", 
                                  style="Status.TLabel")
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # Support info
        support_label = ttk.Label(title_info_frame, 
                                 text="📞 Support: Zalo 0379822057 (Nghĩa)", 
                                 font=("Segoe UI", 9), foreground="#2196F3")
        support_label.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
    
    def create_license_status(self, parent):
        """Tạo section hiển thị trạng thái license"""
        license_frame = ttk.LabelFrame(parent, text="🔐 License Status", padding="10")
        license_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        license_frame.columnconfigure(1, weight=1)
        
        # Hardware ID
        ttk.Label(license_frame, text="Hardware ID:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        hwid_label = ttk.Label(license_frame, text=self.license_auth.hwid, 
                              font=("Consolas", 9), foreground="#2196F3")
        hwid_label.grid(row=0, column=1, sticky=tk.W)
        
        # License status
        ttk.Label(license_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.license_status_label = ttk.Label(license_frame, text="✅ Licensed", 
                                             foreground="green", font=("Segoe UI", 9, "bold"))
        self.license_status_label.grid(row=1, column=1, sticky=tk.W)
    
    def create_config_section(self, parent):
        """Tạo section cấu hình"""
        config_frame = ttk.LabelFrame(parent, text="⚙️ Configuration", padding="10")
        config_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Wait time configuration
        ttk.Label(config_frame, text="Wait Time (seconds):").grid(row=0, column=0, sticky=tk.W)
        
        self.delay_var = tk.StringVar(value="20")
        wait_spinbox = ttk.Spinbox(config_frame, from_=5, to=120, textvariable=self.delay_var, width=10)
        wait_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(15, 0))
        
        # Debug mode
        self.debug_var = tk.BooleanVar()
        debug_check = ttk.Checkbutton(config_frame, text="Debug Mode", variable=self.debug_var)
        debug_check.grid(row=0, column=2, sticky=tk.W, padx=(30, 0))
    
    def create_control_buttons(self, parent):
        """Tạo control buttons"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Chrome control
        self.chrome_btn = ttk.Button(control_frame, text="🚀 Start Chrome",
                                    command=self.start_chrome, style="Modern.TButton")
        self.chrome_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.chrome_status = ttk.Label(control_frame, text="❌ Not Started", foreground="red")
        self.chrome_status.pack(side=tk.LEFT, padx=(0, 20))
        
        # Automation control
        self.start_btn = ttk.Button(control_frame, text="▶️ Start Automation", 
                                   command=self.start_automation, style="Modern.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop", 
                                  command=self.stop_automation, style="Modern.TButton", 
                                  state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
    
    def create_content_section(self, parent):
        """Tạo section nhập content"""
        content_frame = ttk.LabelFrame(parent, text="📝 Content Prompts", padding="10")
        content_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # File operations
        file_frame = ttk.Frame(content_frame)
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="📁 Load File", command=self.load_prompts).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(file_frame, text="💾 Save File", command=self.save_prompts).pack(side=tk.LEFT)
        
        # Text area
        self.content_text = scrolledtext.ScrolledText(content_frame, height=8, 
                                                     font=("Consolas", 10))
        self.content_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load default prompts
        self.load_default_prompts()
    
    def create_log_section(self, parent):
        """Tạo section log"""
        log_frame = ttk.LabelFrame(parent, text="📋 Activity Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                 font=("Consolas", 9), state="disabled")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for main sections
        parent.rowconfigure(5, weight=1)
        parent.rowconfigure(6, weight=1)
    
    def init_automation(self):
        """Khởi tạo automation module"""
        try:
            self.log_message("🔐 License verified - initializing automation...")
            self.log_message(f"📱 Hardware ID: {self.license_auth.hwid}")
            self.log_message("✅ Licensed Professional Edition ready")
            
        except Exception as e:
            self.log_message(f"❌ Initialization error: {str(e)}")
    
    def find_chrome_path(self):
        """Tìm Chrome path trên Windows"""
        possible_paths = [
            # Chrome paths
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),

            # Edge paths (fallback)
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",

            # Try PATH
            "chrome.exe",
            "google-chrome",
            "msedge.exe"
        ]

        for path in possible_paths:
            try:
                if os.path.exists(path):
                    self.log_message(f"✅ Found browser: {path}")
                    return path
                elif path in ["chrome.exe", "google-chrome", "msedge.exe"]:
                    # Try to find in PATH
                    result = subprocess.run(["where", path], capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        found_path = result.stdout.strip().split('\n')[0]
                        self.log_message(f"✅ Found browser in PATH: {found_path}")
                        return found_path
            except:
                continue

        return None



    def check_port_availability(self, port=9222):
        """Check if a port is available for binding"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result != 0  # Port is available if connection failed
        except:
            return True  # Assume available if check fails

    def kill_chrome_on_port(self, port=9222):
        """Kill Chrome processes that might be using the debug port"""
        try:
            # Find processes using the port
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        for conn in proc.info['connections'] or []:
                            if conn.laddr.port == port:
                                self.log_message(f"🔄 Killing Chrome process {proc.info['pid']} using port {port}")
                                proc.kill()
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            # Fallback to taskkill if psutil not available
            try:
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"],
                             capture_output=True, timeout=5)
                return True
            except:
                pass
        return False

    def start_chrome(self):
        """Khởi động Chrome với debug mode - Fixed version with better port handling"""
        try:
            self.log_message("🚀 Starting Chrome with debug mode...")

            # Check if Chrome debug port is already accessible
            self.log_message("🔍 Checking if Chrome debug port is already available...")
            try:
                import requests
                response = requests.get("http://127.0.0.1:9222/json", timeout=3)
                if response.status_code == 200:
                    tabs = response.json()
                    self.log_message(f"✅ Chrome debug port already accessible - Found {len(tabs)} tabs")
                    self.log_message("💡 Using existing Chrome instance")

                    # Update UI
                    self.chrome_btn.config(text="🔄 Restart Chrome", state="normal")
                    self.chrome_status.config(text="✅ Running", foreground="green")

                    self.log_message("✅ Chrome is ready for automation")
                    self.log_message("📋 Vui lòng:")
                    self.log_message("   1. Đăng nhập Google trong Chrome")
                    self.log_message("   2. Truy cập: https://labs.google/fx/tools/whisk")
                    self.log_message("   3. Đảm bảo thấy giao diện tạo design")
                    return
            except:
                self.log_message("⏳ Chrome debug port not available, starting new instance...")

            # Check if port 9222 is available
            if not self.check_port_availability(9222):
                self.log_message("⚠️ Port 9222 is in use, attempting to free it...")
                if self.kill_chrome_on_port(9222):
                    time.sleep(3)  # Wait for port to be freed
                    if not self.check_port_availability(9222):
                        raise Exception("Port 9222 is still in use after cleanup attempt")
                else:
                    raise Exception("Port 9222 is in use and cannot be freed")

            # Find Chrome path
            chrome_path = self.find_chrome_path()
            if not chrome_path:
                raise Exception("Chrome/Edge browser not found. Please install Google Chrome or Microsoft Edge.")

            self.log_message(f"🔍 Using browser: {chrome_path}")

            # Kill any existing Chrome processes that might block debug port
            self.log_message("🔄 Ensuring clean Chrome startup...")
            try:
                # Only kill Chrome processes that might interfere with debug port
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"],
                             capture_output=True, timeout=5)
                time.sleep(2)  # Wait for processes to fully close
            except:
                pass  # Ignore if no Chrome processes to kill

            # Chrome command with comprehensive debug parameters
            temp_dir = os.path.join(os.environ.get('TEMP', ''), f'chrome-debug-{int(time.time())}')
            chrome_cmd = [
                chrome_path,
                "--remote-debugging-port=9222",
                "--remote-debugging-address=127.0.0.1",
                f"--user-data-dir={temp_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection"
            ]

            self.log_message("🔧 Starting Chrome with comprehensive debug parameters...")
            self.log_message(f"🗂️ Using temporary profile: {temp_dir}")
            self.log_message("🔍 Debug port: 127.0.0.1:9222")

            # Start Chrome with better error handling
            try:
                self.chrome_process = subprocess.Popen(
                    chrome_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
                )
                self.log_message(f"✅ Chrome process started (PID: {self.chrome_process.pid})")
            except Exception as start_error:
                raise Exception(f"Failed to start Chrome process: {start_error}")

            # Wait longer for Chrome to start and verify debug port
            self.log_message("⏳ Waiting for Chrome to initialize...")
            time.sleep(5)  # Longer wait time for reliable startup

            # Verify debug port is accessible with comprehensive diagnostics
            debug_accessible = False
            self.log_message("🔍 Verifying Chrome debug port accessibility...")

            for attempt in range(15):  # Try for 15 seconds
                try:
                    # Check if Chrome process is still running
                    if self.chrome_process.poll() is not None:
                        stdout, stderr = self.chrome_process.communicate()
                        error_msg = stderr.decode() if stderr else "Unknown error"
                        raise Exception(f"Chrome process died unexpectedly. Error: {error_msg}")

                    import requests
                    # Try both localhost and 127.0.0.1
                    for host in ["127.0.0.1", "localhost"]:
                        try:
                            response = requests.get(f"http://{host}:9222/json", timeout=2)
                            if response.status_code == 200:
                                tabs = response.json()
                                self.log_message(f"✅ Chrome debug port accessible on {host}:9222")
                                self.log_message(f"📊 Found {len(tabs)} tabs")
                                debug_accessible = True
                                break
                        except requests.exceptions.ConnectionError:
                            continue

                    if debug_accessible:
                        break

                except requests.exceptions.ConnectionError:
                    pass
                except Exception as e:
                    self.log_message(f"⚠️ Debug port check error (attempt {attempt + 1}/15): {str(e)}")

                if attempt < 14:
                    self.log_message(f"⏳ Waiting for debug port... (attempt {attempt + 1}/15)")
                    time.sleep(1)
                else:
                    # Final diagnostic before failing
                    self.log_message("🔍 Final diagnostic check...")

                    # Check if port is in use
                    try:
                        import socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex(('127.0.0.1', 9222))
                        sock.close()
                        if result == 0:
                            self.log_message("⚠️ Port 9222 is open but not responding to HTTP requests")
                        else:
                            self.log_message("❌ Port 9222 is not accessible")
                    except:
                        pass

                    # Check Chrome process status
                    if self.chrome_process.poll() is None:
                        self.log_message("✅ Chrome process is still running")
                    else:
                        self.log_message("❌ Chrome process has terminated")

                    raise Exception("Chrome debug port not accessible after 15 seconds. Check firewall/antivirus settings.")

            if not debug_accessible:
                raise Exception("Could not establish debug port connection after all attempts")

            # Update UI
            self.chrome_btn.config(text="🔄 Restart Chrome", state="normal")
            self.chrome_status.config(text="✅ Running", foreground="green")

            self.log_message("✅ Chrome started successfully")
            self.log_message("💡 Chrome is ready for automation")
            self.log_message("📋 Vui lòng:")
            self.log_message("   1. Đăng nhập Google trong Chrome")
            self.log_message("   2. Truy cập: https://labs.google/fx/tools/whisk")
            self.log_message("   3. Đảm bảo thấy giao diện tạo design")

        except Exception as e:
            self.log_message(f"❌ Failed to start Chrome: {str(e)}")
            # Reset UI state
            self.chrome_btn.config(text="🚀 Start Chrome", state="normal")
            self.chrome_status.config(text="❌ Not Started", foreground="red")
            messagebox.showerror("Chrome Error", f"Failed to start Chrome: {str(e)}\n\nPlease install Google Chrome or Microsoft Edge.")
    
    def start_automation(self):
        """Bắt đầu automation"""
        if self.automation_running:
            return
        
        prompts = self.get_prompts()
        if not prompts:
            messagebox.showwarning("No Content", "Please enter some prompts first")
            return
        
        self.automation_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Running...", foreground="orange")
        
        # Start automation in thread
        self.automation_thread = threading.Thread(target=self.run_automation, args=(prompts,))
        self.automation_thread.daemon = True
        self.automation_thread.start()
    
    def run_automation(self, prompts):
        """Chạy automation (placeholder)"""
        try:
            self.log_message(f"▶️ Starting automation for {len(prompts)} prompts...")
            
            # Import automation module
            from whisk_session_takeover import WhiskAutomator, WhiskConfig, setup_logging
            
            # Setup logging
            log_level = "DEBUG" if self.debug_var.get() else "INFO"
            setup_logging(log_level)
            
            # Create config
            config = WhiskConfig(
                chrome_debug_port=9222,
                generation_delay=int(self.delay_var.get()),
                retry_attempts=3,
                retry_delay=5,
                prompts_file="prompts.txt",
                log_level=log_level,
                whisk_url_pattern="whisk",
                debug_mode=self.debug_var.get()
            )
            
            # Run automation
            automator = WhiskAutomator(config)

            # Initialize automation
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Test Chrome connection first
                self.log_message("🔌 Testing Chrome DevTools connection...")
                import requests

                # Try multiple times to connect
                connection_successful = False
                for conn_attempt in range(5):
                    try:
                        response = requests.get("http://localhost:9222/json", timeout=5)
                        if response.status_code == 200:
                            tabs = response.json()
                            self.log_message(f"✅ Chrome DevTools accessible - Found {len(tabs)} tabs")
                            connection_successful = True

                            # Log available tabs
                            for i, tab in enumerate(tabs[:3]):  # Show first 3 tabs
                                title = tab.get('title', 'No title')[:50]
                                url = tab.get('url', 'No URL')[:50]
                                tab_type = tab.get('type', 'unknown')
                                self.log_message(f"   Tab {i+1} ({tab_type}): {title}")
                                self.log_message(f"      URL: {url}")

                            # Check for Whisk tabs
                            whisk_tabs = [tab for tab in tabs if 'whisk' in tab.get('url', '').lower() or 'whisk' in tab.get('title', '').lower()]
                            if whisk_tabs:
                                self.log_message(f"🎯 Found {len(whisk_tabs)} Whisk tab(s) - ready for automation")
                            else:
                                self.log_message("⚠️ No Whisk tabs found - creating new Whisk tab...")
                                if self.open_whisk_tab():
                                    self.log_message("✅ Whisk tab created successfully")
                                else:
                                    self.log_message("❌ Failed to create Whisk tab")
                                    self.log_message("💡 Please manually open whisk.com in Chrome")
                            break
                        else:
                            self.log_message(f"❌ Debug port returned status {response.status_code}")
                    except requests.exceptions.ConnectionError as conn_error:
                        if conn_attempt < 4:
                            self.log_message(f"⏳ Connection attempt {conn_attempt + 1}/5 failed, retrying...")
                            time.sleep(2)
                        else:
                            self.log_message(f"❌ Chrome DevTools not accessible after 5 attempts: {conn_error}")
                    except Exception as other_error:
                        self.log_message(f"❌ Unexpected error: {other_error}")
                        break

                if not connection_successful:
                    self.log_message("❌ Could not connect to Chrome DevTools")
                    self.log_message("💡 Make sure Chrome was started with debug mode")
                    self.log_message("💡 Try clicking 'Start Chrome' button again")
                    self.log_message("💡 Check if Chrome is running and not blocked by firewall")
                    return

                # Initialize the automator
                self.log_message("🔌 Initializing automation...")
                if not loop.run_until_complete(automator.initialize()):
                    self.log_message("❌ Failed to initialize automation")
                    self.log_message("💡 Make sure you have a tab open in Chrome")
                    self.log_message("💡 Try opening whisk.com in a new tab")
                    return

                self.log_message("✅ Automation initialized successfully")

                # Process each prompt
                successful_prompts = 0
                for i, prompt in enumerate(prompts):
                    if not self.automation_running:
                        self.log_message("⏹️ Automation stopped by user")
                        break

                    self.log_message(f"📝 Processing prompt {i+1}/{len(prompts)}: {prompt[:50]}...")

                    try:
                        success = loop.run_until_complete(automator.process_prompt(prompt, i))
                        if success:
                            successful_prompts += 1
                            self.log_message(f"✅ Completed prompt {i+1}")
                        else:
                            self.log_message(f"❌ Failed prompt {i+1}")
                    except Exception as prompt_error:
                        self.log_message(f"❌ Error processing prompt {i+1}: {str(prompt_error)}")

                    # Small delay between prompts
                    if i < len(prompts) - 1 and self.automation_running:
                        time.sleep(2)

                if self.automation_running:
                    success_rate = (successful_prompts / len(prompts)) * 100
                    self.log_message(f"🎉 Automation completed! Success rate: {success_rate:.1f}% ({successful_prompts}/{len(prompts)})")

            except Exception as automation_error:
                self.log_message(f"❌ Automation failed: {str(automation_error)}")
            finally:
                loop.close()
                
        except Exception as e:
            self.log_message(f"❌ Automation error: {str(e)}")
        finally:
            # Reset UI state
            self.root.after(0, self.reset_automation_ui)
    
    def stop_automation(self):
        """Dừng automation"""
        self.automation_running = False
        self.log_message("⏹️ Stopping automation...")
    
    def reset_automation_ui(self):
        """Reset UI sau khi automation kết thúc"""
        self.automation_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Ready", foreground="green")
    
    def get_prompts(self):
        """Lấy danh sách prompts từ text area"""
        content = self.content_text.get("1.0", tk.END).strip()
        if not content:
            return []
        
        prompts = [line.strip() for line in content.split('\n') if line.strip()]
        return prompts
    
    def load_prompts(self):
        """Load prompts từ file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Load Prompts",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.content_text.delete("1.0", tk.END)
                self.content_text.insert("1.0", content)
                
                self.log_message(f"📁 Loaded prompts from: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file: {str(e)}")
    
    def save_prompts(self):
        """Save prompts to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Prompts",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                content = self.content_text.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log_message(f"💾 Saved prompts to: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
    
    def load_default_prompts(self):
        """Load default prompts"""
        try:
            if os.path.exists("prompts.txt"):
                with open("prompts.txt", 'r', encoding='utf-8') as f:
                    content = f.read()
                self.content_text.insert("1.0", content)
                self.log_message("📁 Loaded default prompts from prompts.txt")
        except:
            # Default prompts if file doesn't exist
            default_prompts = """Create a modern logo for tech startup
Design a mobile app interface for food delivery
Create a poster for music festival"""
            self.content_text.insert("1.0", default_prompts)
    
    def log_message(self, message):
        """Thêm message vào log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
        # Update UI
        self.root.update_idletasks()
    
    def run(self):
        """Chạy ứng dụng"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            # Cleanup Chrome processes
            try:
                if self.chrome_process:
                    self.chrome_process.terminate()
                    time.sleep(1)

                # Force kill any remaining Chrome processes
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"],
                             capture_output=True, timeout=5)
            except:
                pass


def main():
    """Hàm main"""
    try:
        app = WhiskGUILicensed()
        app.run()
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()
