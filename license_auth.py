#!/usr/bin/env python3
"""
License Authentication System for Whisk Automation Tool
Hệ thống xác thực license với Google Apps Script
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import hashlib
import platform
import subprocess
import uuid
import os
import sys
from datetime import datetime, timedelta
import threading
import time

class LicenseAuth:
    def __init__(self):
        # Real Google Apps Script URL
        self.apps_script_url = "https://script.google.com/macros/s/AKfycbylHE6Y7cRnQDU9E8t8WUBF-xFQSdz9fJVI0aprViMuarwHgnF4rjUAHaXFeKpbVK0FQQ/exec"
        self.hwid = self.get_hardware_id()
        self.license_file = "license.json"
        
    def get_hardware_id(self):
        """Lấy Hardware ID duy nhất của máy tính"""
        try:
            # Lấy thông tin hệ thống
            system_info = []
            
            # CPU ID
            try:
                if platform.system() == "Windows":
                    cpu_info = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode().strip()
                    cpu_id = cpu_info.split('\n')[1].strip()
                    system_info.append(cpu_id)
                else:
                    # Linux/Mac fallback
                    cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'processor'", shell=True).decode()
                    system_info.append(cpu_info[:50])
            except:
                pass
            
            # Motherboard serial
            try:
                if platform.system() == "Windows":
                    mb_info = subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode().strip()
                    mb_serial = mb_info.split('\n')[1].strip()
                    system_info.append(mb_serial)
            except:
                pass
            
            # MAC Address
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
                system_info.append(mac)
            except:
                pass
            
            # Machine name
            system_info.append(platform.node())
            
            # Tạo hash từ tất cả thông tin
            combined_info = '|'.join(system_info)
            hwid = hashlib.sha256(combined_info.encode()).hexdigest()[:16].upper()
            
            return hwid
            
        except Exception as e:
            # Fallback HWID
            fallback = f"{platform.system()}-{platform.node()}-{uuid.getnode()}"
            return hashlib.sha256(fallback.encode()).hexdigest()[:16].upper()
    
    def save_license_file(self, license_key):
        """Lưu license.json khi xác thực thành công"""
        try:
            license_data = {
                "key": license_key,
                "hwid": self.hwid,
                "authenticated_at": datetime.now().isoformat()
            }

            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)

        except Exception as e:
            print(f"Error saving license file: {e}")

    def load_license_file(self):
        """Load license.json"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading license file: {e}")

        return None
    
    def verify_license(self, license_key):
        """Xác thực license với Google Apps Script"""
        try:
            # Send GET request with parameters
            params = {
                "key": license_key,
                "hwid": self.hwid
            }

            response = requests.get(
                self.apps_script_url,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                response_text = response.text.strip()
                return {"success": True, "message": response_text}
            else:
                return {"success": False, "message": "Server error"}

        except requests.exceptions.Timeout:
            return {"success": False, "message": "Connection timeout"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "No internet connection"}
        except Exception as e:
            return {"success": False, "message": f"Network error: {str(e)}"}
    
    def handle_response(self, response_message, license_key):
        """Xử lý response từ Google Apps Script"""
        message = response_message.lower().strip()

        # Check for success messages (more flexible matching)
        if ("kích hoạt thành công" in message or
            "đã xác thực thành công" in message or
            "thành công" in message or
            "success" in message.lower()):
            # Save license file and return success
            self.save_license_file(license_key)
            return {"status": "success", "message": response_message}

        elif "hết hạn" in message or "expired" in message:
            return {"status": "expired", "message": response_message}

        elif ("chờ phê duyệt" in message or "pending" in message or
              "license đang chờ phê duyệt" in message):
            return {"status": "pending", "message": response_message}

        elif ("máy khác" in message or "hwid" in message or
              "license đã dùng trên máy khác" in message):
            return {"status": "hwid_mismatch", "message": response_message}

        else:
            return {"status": "error", "message": response_message}


class LicenseDialog:
    def __init__(self, parent=None):
        self.auth = LicenseAuth()
        self.result = False
        self.license_key = ""
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("Whisk Automation Tool - License Authentication")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)

        # Set custom icon (remove feather icon, use ico_chuan.ico)
        self.set_window_icon(self.dialog)
        
        # Center window
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Setup UI
        self.setup_ui()
        
        # Focus on license key entry
        self.key_entry.focus_set()

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
                        elif icon_path.endswith('.png'):
                            # Try to use PNG as icon
                            try:
                                from PIL import Image, ImageTk
                                img = Image.open(icon_path)
                                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                                photo = ImageTk.PhotoImage(img)
                                window.iconphoto(True, photo)
                            except ImportError:
                                # PIL not available, skip PNG
                                continue
                        icon_set = True
                        print(f"✅ License dialog icon loaded from: {icon_path}")
                        break
                    except Exception as e:
                        print(f"⚠️ Failed to load license dialog icon from {icon_path}: {e}")
                        continue

            if not icon_set:
                # Remove default icon to avoid feather icon
                try:
                    window.iconbitmap("")
                    print("🚫 Removed default icon from license dialog")
                except:
                    pass

        except Exception as e:
            print(f"❌ License dialog icon setup error: {e}")
            try:
                window.iconbitmap("")
            except:
                pass

    def setup_ui(self):
        """Thiết lập giao diện đăng nhập"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo/Title
        title_label = ttk.Label(header_frame, text="Whisk Automation Tool",
                               font=("Segoe UI", 16, "bold"), foreground="#2196F3")
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Professional Edition - License Authentication", 
                                  font=("Segoe UI", 10), foreground="#666666")
        subtitle_label.pack()
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 20))
        
        # License info
        info_frame = ttk.LabelFrame(main_frame, text="📋 License Information", padding="15")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Hardware ID display
        hwid_label = ttk.Label(info_frame, text="Hardware ID:")
        hwid_label.pack(anchor=tk.W)
        
        hwid_value = ttk.Label(info_frame, text=self.auth.hwid, 
                              font=("Consolas", 9), foreground="#2196F3")
        hwid_value.pack(anchor=tk.W, pady=(0, 10))
        
        # License key input
        key_label = ttk.Label(info_frame, text="License Key:")
        key_label.pack(anchor=tk.W)
        
        self.key_entry = ttk.Entry(info_frame, font=("Consolas", 11), width=40)
        self.key_entry.pack(fill=tk.X, pady=(5, 10))
        self.key_entry.bind('<Return>', lambda e: self.verify_license())
        
        # Status
        self.status_label = ttk.Label(info_frame, text="Please enter your license key", 
                                     foreground="#666666")
        self.status_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.verify_btn = ttk.Button(button_frame, text="🔐 Verify License", 
                                    command=self.verify_license)
        self.verify_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Remove request button - not needed for this setup
        
        exit_btn = ttk.Button(button_frame, text="❌ Exit", command=self.exit_app)
        exit_btn.pack(side=tk.RIGHT)
        
        # Remove demo mode indicator

        # Support info
        support_frame = ttk.Frame(main_frame)
        support_frame.pack(fill=tk.X, pady=(20, 0))

        support_label = ttk.Label(support_frame, text="📞 Support: Zalo 0379822057 (Nghĩa)",
                                 font=("Segoe UI", 9), foreground="#2196F3")
        support_label.pack()
        
        # Progress bar (hidden initially)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        
    def show_error_and_exit(self, title, message):
        """Hiển thị lỗi và thoát ứng dụng"""
        messagebox.showerror(title, message)
        sys.exit(1)
    
    def verify_license(self):
        """Xác thực license"""
        license_key = self.key_entry.get().strip()
        if not license_key:
            messagebox.showerror("Error", "Please enter a license key")
            return

        self.license_key = license_key
        self.set_loading(True)

        # Run verification in thread
        threading.Thread(target=self.verify_license_thread, daemon=True).start()
    
    def verify_license_thread(self):
        """Thread xác thực license"""
        try:
            result = self.auth.verify_license(self.license_key)

            # Update UI in main thread
            self.dialog.after(0, self.handle_verify_result, result)

        except Exception as e:
            self.dialog.after(0, self.handle_verify_result,
                            {"success": False, "message": f"Error: {str(e)}"})
    
    def handle_verify_result(self, result):
        """Xử lý kết quả xác thực"""
        self.set_loading(False)

        if result.get("success"):
            # Handle response from Google Apps Script
            response_result = self.auth.handle_response(result.get("message", ""), self.license_key)

            if response_result["status"] == "success":
                self.status_label.config(text="✅ License verified successfully!", foreground="green")

                # Close dialog and allow access to main application
                self.result = True

                # Use after() to ensure UI updates before destroying
                self.dialog.after(500, self.close_dialog)

            elif response_result["status"] == "expired":
                self.show_error_and_exit("License Expired", response_result["message"])

            elif response_result["status"] == "pending":
                self.show_error_and_exit("License Pending", response_result["message"])

            elif response_result["status"] == "hwid_mismatch":
                self.show_error_and_exit("Hardware Mismatch", response_result["message"])

            else:
                self.show_error_and_exit("License Error", response_result["message"])

        else:
            # Network error or server error
            message = result.get("message", "Unknown error")
            self.show_error_and_exit("Connection Error", f"Cannot connect to license server: {message}")
    
    # Remove request license functionality - not needed
    
    def set_loading(self, loading):
        """Hiển thị/ẩn loading"""
        if loading:
            self.progress.pack(fill=tk.X, pady=(10, 0))
            self.progress.start()
            self.verify_btn.config(state="disabled")
        else:
            self.progress.stop()
            self.progress.pack_forget()
            self.verify_btn.config(state="normal")
    
    def close_dialog(self):
        """Đóng dialog và chuyển đến main app"""
        try:
            self.dialog.quit()  # Stop mainloop
            self.dialog.destroy()  # Destroy window
        except:
            pass

    def exit_app(self):
        """Thoát ứng dụng"""
        sys.exit(1)
    
    def show(self):
        """Hiển thị dialog và trả về kết quả"""
        self.dialog.mainloop()
        return self.result


def authenticate_license():
    """Hàm chính để xác thực license"""
    dialog = LicenseDialog()
    return dialog.show()


if __name__ == "__main__":
    # Test license authentication
    if authenticate_license():
        print("License verified successfully!")
    else:
        print("License verification failed!")
