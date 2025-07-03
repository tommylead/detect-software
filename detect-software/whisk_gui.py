#!/usr/bin/env python3
"""
Whisk Automation Tool - Professional GUI Interface
Giao diện đồ họa chuyên nghiệp cho tool automation Whisk
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
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class WhiskGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisk Automation Tool - Professional Edition")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Set modern style
        self.setup_style()

        # Set icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Variables
        self.is_running = False
        self.chrome_started = False

        # Setup GUI
        self.setup_gui()
        self.load_prompts()

    def setup_style(self):
        """Thiết lập style chuyên nghiệp"""
        style = ttk.Style()

        # Configure modern theme
        style.theme_use('clam')

        # Custom colors
        bg_color = "#f0f0f0"
        accent_color = "#2196F3"
        success_color = "#4CAF50"
        error_color = "#F44336"

        # Configure styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=accent_color)
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Status.TLabel', font=('Segoe UI', 10))
        style.configure('Success.TLabel', font=('Segoe UI', 10), foreground=success_color)
        style.configure('Error.TLabel', font=('Segoe UI', 10), foreground=error_color)
        style.configure('Modern.TButton', font=('Segoe UI', 10))
        style.configure('Action.TButton', font=('Segoe UI', 11, 'bold'))

        self.root.configure(bg=bg_color)
        
    def setup_gui(self):
        """Thiết lập giao diện chuyên nghiệp"""
        # Main container with modern styling
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=2)  # Prompts section gets more space
        main_frame.rowconfigure(6, weight=1)  # Log section gets some space

        # Header section with logo and title
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)

        # Logo section
        logo_loaded = False
        if PIL_AVAILABLE:
            try:
                # Try to load logo files
                logo_files = ["ico_chuan.png", "logo.png", "icon.ico"]

                for logo_file in logo_files:
                    try:
                        if os.path.exists(logo_file):
                            logo_img = Image.open(logo_file)
                            logo_img = logo_img.resize((48, 48), Image.Resampling.LANCZOS)
                            self.logo_photo = ImageTk.PhotoImage(logo_img)
                            logo_label = ttk.Label(header_frame, image=self.logo_photo)
                            logo_label.grid(row=0, column=0, padx=(0, 15))
                            logo_loaded = True
                            break
                    except:
                        continue
            except:
                pass

        if not logo_loaded:
            # Fallback to emoji if no logo available
            logo_label = ttk.Label(header_frame, text="🎨", font=("Arial", 32))
            logo_label.grid(row=0, column=0, padx=(0, 15))

        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))

        title_label = ttk.Label(title_frame, text="Whisk Automation Tool",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)

        subtitle_label = ttk.Label(title_frame, text="Professional AI Content Generation Assistant",
                                  font=("Segoe UI", 10), foreground="#666666")
        subtitle_label.grid(row=1, column=0, sticky=tk.W)

        # Contact info
        contact_frame = ttk.Frame(header_frame)
        contact_frame.grid(row=0, column=2, sticky=tk.E)

        contact_label = ttk.Label(contact_frame, text="Hỗ trợ: Zalo 0379822057 (Nghĩa)",
                                 font=("Segoe UI", 9), foreground="#2196F3")
        contact_label.grid(row=0, column=0)

        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Status section with modern cards
        status_frame = ttk.LabelFrame(main_frame, text="📊 System Status", padding="15", style='Header.TLabel')
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        status_frame.columnconfigure(1, weight=1)

        # Chrome status card
        chrome_card = ttk.Frame(status_frame, relief='solid', borderwidth=1)
        chrome_card.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        chrome_card.columnconfigure(1, weight=1)

        ttk.Label(chrome_card, text="🌐", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=10)
        chrome_info = ttk.Frame(chrome_card)
        chrome_info.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=10)

        ttk.Label(chrome_info, text="Chrome Debug", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.chrome_status = ttk.Label(chrome_info, text="❌ Chưa khởi động", style='Error.TLabel')
        self.chrome_status.grid(row=1, column=0, sticky=tk.W)

        # Whisk status card
        whisk_card = ttk.Frame(status_frame, relief='solid', borderwidth=1)
        whisk_card.grid(row=0, column=1, sticky=(tk.W, tk.E))
        whisk_card.columnconfigure(1, weight=1)

        ttk.Label(whisk_card, text="🎨", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=10)
        whisk_info = ttk.Frame(whisk_card)
        whisk_info.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=10)

        ttk.Label(whisk_info, text="Whisk Connection", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.whisk_status = ttk.Label(whisk_info, text="❌ Chưa kết nối", style='Error.TLabel')
        self.whisk_status.grid(row=1, column=0, sticky=tk.W)

        # Prompts section
        prompts_frame = ttk.LabelFrame(main_frame, text="📝 Content Prompts", padding="15", style='Header.TLabel')
        prompts_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        prompts_frame.columnconfigure(0, weight=1)
        prompts_frame.rowconfigure(0, weight=1)

        # Prompts text area with modern styling
        self.prompts_text = scrolledtext.ScrolledText(prompts_frame, height=12, width=80,
                                                     font=("Consolas", 10), wrap=tk.WORD)
        self.prompts_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Prompts buttons with modern styling
        prompts_buttons = ttk.Frame(prompts_frame)
        prompts_buttons.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        ttk.Button(prompts_buttons, text="📁 Load File",
                  command=self.load_prompts_file, style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(prompts_buttons, text="💾 Save File",
                  command=self.save_prompts_file, style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(prompts_buttons, text="🔄 Refresh",
                  command=self.load_prompts, style='Modern.TButton').pack(side=tk.LEFT)

        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuration", padding="15", style='Header.TLabel')
        config_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)

        # Wait time with modern styling
        ttk.Label(config_frame, text="Wait Time (seconds):", style='Status.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.delay_var = tk.StringVar(value="20")
        wait_spinbox = ttk.Spinbox(config_frame, from_=5, to=120, textvariable=self.delay_var, width=10)
        wait_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(15, 0))

        # Debug mode
        self.debug_var = tk.BooleanVar()
        debug_check = ttk.Checkbutton(config_frame, text="Debug Mode", variable=self.debug_var)
        debug_check.grid(row=0, column=2, sticky=tk.W, padx=(30, 0))

        # Control buttons with modern styling
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.start_chrome_btn = ttk.Button(control_frame, text="🚀 Start Chrome",
                                          command=self.start_chrome, style='Action.TButton')
        self.start_chrome_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.start_automation_btn = ttk.Button(control_frame, text="▶️ Start Automation",
                                              command=self.start_automation, state="disabled", style='Action.TButton')
        self.start_automation_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop",
                                  command=self.stop_automation, state="disabled", style='Action.TButton')
        self.stop_btn.pack(side=tk.LEFT)

        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="📋 Activity Log", padding="15", style='Header.TLabel')
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, width=80,
                                                 font=("Consolas", 9), wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def log(self, message):
        """Thêm message vào log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def load_prompts(self):
        """Tải prompts từ file"""
        try:
            if Path("prompts.txt").exists():
                with open("prompts.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                self.prompts_text.delete(1.0, tk.END)
                self.prompts_text.insert(1.0, content)
                self.log("✅ Đã tải prompts.txt")
            else:
                self.prompts_text.delete(1.0, tk.END)
                self.prompts_text.insert(1.0, "# Thêm prompts của bạn vào đây\n# Mỗi dòng là một prompt\n\nCreate a modern logo for tech startup\nDesign a mobile app interface for food delivery\nCreate a poster for music festival")
                self.log("⚠️ Không tìm thấy prompts.txt, sử dụng mẫu")
        except Exception as e:
            self.log(f"❌ Lỗi tải prompts: {e}")
            
    def save_prompts_file(self):
        """Lưu prompts vào file"""
        try:
            content = self.prompts_text.get(1.0, tk.END).strip()
            with open("prompts.txt", "w", encoding="utf-8") as f:
                f.write(content)
            self.log("✅ Đã lưu prompts.txt")
        except Exception as e:
            self.log(f"❌ Lỗi lưu prompts: {e}")
            
    def load_prompts_file(self):
        """Tải prompts từ file khác"""
        try:
            filename = filedialog.askopenfilename(
                title="Chọn file prompts",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                self.prompts_text.delete(1.0, tk.END)
                self.prompts_text.insert(1.0, content)
                self.log(f"✅ Đã tải {filename}")
        except Exception as e:
            self.log(f"❌ Lỗi tải file: {e}")
            
    def start_chrome(self):
        """Khởi động Chrome với debug mode"""
        def run_chrome():
            try:
                self.log("🌐 Đang khởi động Chrome...")
                
                system = platform.system()
                if system == "Windows":
                    chrome_paths = [
                        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
                    ]
                    
                    chrome_path = None
                    for path in chrome_paths:
                        if os.path.exists(path):
                            chrome_path = path
                            break
                    
                    if not chrome_path:
                        self.log("❌ Không tìm thấy Chrome!")
                        return
                    
                    temp_dir = os.path.join(os.environ.get('TEMP', ''), f'chrome-debug-{int(time.time())}')
                    cmd = [chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={temp_dir}"]
                    
                else:  # macOS/Linux
                    if system == "Darwin":
                        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                    else:
                        chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"]
                        chrome_path = None
                        for path in chrome_paths:
                            if os.path.exists(path):
                                chrome_path = path
                                break
                    
                    if not chrome_path or not os.path.exists(chrome_path):
                        self.log("❌ Không tìm thấy Chrome!")
                        return
                    
                    temp_dir = f"/tmp/chrome-debug-{int(time.time())}"
                    cmd = [chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={temp_dir}"]
                
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                self.chrome_started = True
                self.chrome_status.config(text="✅ Đã khởi động", style='Success.TLabel')
                self.start_automation_btn.config(state="normal")
                self.log("✅ Chrome đã khởi động với debug mode")
                self.log("📋 Vui lòng:")
                self.log("   1. Đăng nhập Google trong Chrome")
                self.log("   2. Truy cập: https://labs.google/fx/tools/whisk")
                self.log("   3. Đảm bảo thấy giao diện tạo design")
                
            except Exception as e:
                self.log(f"❌ Lỗi khởi động Chrome: {e}")
        
        threading.Thread(target=run_chrome, daemon=True).start()
        
    def start_automation(self):
        """Bắt đầu automation"""
        if self.is_running:
            return
            
        # Lưu prompts trước khi chạy
        self.save_prompts_file()
        
        # Kiểm tra prompts
        content = self.prompts_text.get(1.0, tk.END).strip()
        prompts = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        if not prompts:
            messagebox.showwarning("Cảnh báo", "Vui lòng thêm ít nhất 1 prompt!")
            return
        
        self.log(f"📊 Sẵn sàng xử lý {len(prompts)} prompts")
        
        def run_automation():
            try:
                self.is_running = True
                self.start_automation_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                
                # Import và chạy automation
                from whisk_session_takeover import WhiskAutomator, WhiskConfig, setup_logging
                
                # Setup logging
                log_level = "DEBUG" if self.debug_var.get() else "INFO"
                setup_logging(log_level)
                
                # Tạo config
                config = WhiskConfig(
                    generation_delay=int(self.delay_var.get()),
                    retry_attempts=3,
                    prompts_file="prompts.txt",
                    log_level=log_level
                )
                
                # Chạy automation
                async def run_async():
                    automator = WhiskAutomator(config)
                    success = await automator.run()
                    return success
                
                # Chạy async
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(run_async())
                loop.close()
                
                if success:
                    self.log("🎉 Automation hoàn thành thành công!")
                    messagebox.showinfo("Thành công", "Automation đã hoàn thành!\nKiểm tra kết quả trong Whisk.")
                else:
                    self.log("⚠️ Automation hoàn thành với một số lỗi")
                    messagebox.showwarning("Cảnh báo", "Automation hoàn thành nhưng có một số lỗi.\nKiểm tra log để biết chi tiết.")
                
            except Exception as e:
                self.log(f"❌ Lỗi automation: {e}")
                messagebox.showerror("Lỗi", f"Lỗi automation: {e}")
            finally:
                self.is_running = False
                self.start_automation_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
        
        threading.Thread(target=run_automation, daemon=True).start()
        
    def stop_automation(self):
        """Dừng automation"""
        self.is_running = False
        self.start_automation_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("⏹️ Đã dừng automation")


def main():
    """Main function"""
    root = tk.Tk()
    app = WhiskGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
