#!/usr/bin/env python3
"""
Whisk Automation Tool - Setup Đơn Giản
Script setup hoạt động cho khách hàng
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def print_header():
    """In header"""
    print("=" * 50)
    print("🚀 WHISK AUTOMATION TOOL - SETUP")
    print("=" * 50)
    print("Công cụ tự động tạo design trên Whisk")
    print("=" * 50)


def install_dependencies():
    """Cài đặt dependencies"""
    print("\n📦 Cài đặt thư viện cần thiết...")
    
    packages = ["websockets>=11.0.3", "requests>=2.31.0"]
    
    for package in packages:
        print(f"Đang cài đặt {package}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package} - Thành công")
        except subprocess.CalledProcessError:
            print(f"❌ {package} - Thất bại")
            return False
    
    return True


def create_run_scripts():
    """Tạo scripts chạy automation"""
    print("\n🔗 Tạo scripts chạy automation...")

    # Script cho Windows với Python path detection
    batch_content = '''@echo off
chcp 65001 >nul
title Whisk Automation Tool
cd /d "%~dp0"

echo.
echo ================================================================
echo 🎨 WHISK AUTOMATION TOOL
echo ================================================================
echo.

echo 📋 QUY TRÌNH:
echo 1. Tool sẽ mở Chrome với debug mode
echo 2. Bạn đăng nhập Google và vào Whisk
echo 3. Tool tự động xử lý prompts
echo.

echo 🚀 Bắt đầu...
pause

REM Thử các đường dẫn Python khác nhau
echo 🔍 Tìm Python...

python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Sử dụng python
    python simple_launcher.py
    goto :end
)

py --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Sử dụng py
    py simple_launcher.py
    goto :end
)

python3 --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Sử dụng python3
    python3 simple_launcher.py
    goto :end
)

echo ❌ Không tìm thấy Python trong PATH!
echo.
echo 📋 CÁCH KHẮC PHỤC:
echo 1. Cài đặt Python từ: https://python.org
echo 2. Chọn "Add Python to PATH" khi cài đặt
echo 3. Khởi động lại máy tính
echo 4. Hoặc double-click file CHAY_AUTOMATION.py
echo.

:end
echo.
echo 🏁 Hoàn thành!
pause
'''

    try:
        with open("CHAY_AUTOMATION.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("✅ Tạo CHAY_AUTOMATION.bat")
    except Exception as e:
        print(f"⚠️ Lỗi tạo batch file: {e}")

    # Tạo Python launcher backup
    python_launcher = '''#!/usr/bin/env python3
"""
Whisk Automation Tool - Python Launcher
Backup launcher khi batch file không hoạt động
"""

import subprocess
import sys
import os

def print_header():
    print("=" * 60)
    print("🎨 WHISK AUTOMATION TOOL")
    print("=" * 60)
    print("Công cụ tự động tạo design trên Whisk platform")
    print("=" * 60)
    print()

def main():
    print_header()

    print("📋 QUY TRÌNH:")
    print("1. Tool sẽ mở Chrome với debug mode")
    print("2. Bạn đăng nhập Google và vào Whisk")
    print("3. Tool tự động xử lý prompts")
    print()

    input("🚀 Nhấn Enter để bắt đầu...")

    try:
        subprocess.run([sys.executable, "simple_launcher.py"], check=True)
        print("\\n🎉 Hoàn thành!")
    except Exception as e:
        print(f"\\n❌ Lỗi: {e}")

    input("\\nNhấn Enter để thoát...")

if __name__ == "__main__":
    main()
'''

    try:
        with open("CHAY_AUTOMATION.py", "w", encoding="utf-8") as f:
            f.write(python_launcher)
        print("✅ Tạo CHAY_AUTOMATION.py (backup)")
    except Exception as e:
        print(f"⚠️ Lỗi tạo Python launcher: {e}")

    # Tạo ultra simple launcher
    ultra_simple = '''#!/usr/bin/env python3
"""Ultra Simple Launcher - Không hỏi gì cả"""
import subprocess
import sys

def main():
    print("🎨 WHISK AUTOMATION TOOL - ULTRA SIMPLE")
    print("=" * 50)
    input("Nhấn Enter để bắt đầu...")

    try:
        subprocess.run([sys.executable, "ultra_simple_launcher.py"], check=True)
    except Exception as e:
        print(f"Lỗi: {e}")

    input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
'''

    try:
        with open("CHAY_NGAY.py", "w", encoding="utf-8") as f:
            f.write(ultra_simple)
        print("✅ Tạo CHAY_NGAY.py (ultra simple)")
    except Exception as e:
        print(f"⚠️ Lỗi tạo ultra simple launcher: {e}")
    
    # Script cho Mac/Linux
    shell_content = '''#!/bin/bash
cd "$(dirname "$0")"

echo
echo "================================================================"
echo "🎨 WHISK AUTOMATION TOOL"
echo "================================================================"
echo

echo "📋 QUY TRÌNH:"
echo "1. Tool sẽ mở Chrome với debug mode"
echo "2. Bạn đăng nhập Google và vào Whisk"
echo "3. Tool tự động xử lý prompts"
echo

echo "🚀 Bắt đầu..."
read -p "Nhấn Enter để tiếp tục..."

python3 run_automation.py

echo
echo "🏁 Hoàn thành!"
read -p "Nhấn Enter để thoát..."
'''
    
    try:
        with open("chay_automation.sh", "w") as f:
            f.write(shell_content)
        os.chmod("chay_automation.sh", 0o755)
        print("✅ Tạo chay_automation.sh")
    except Exception as e:
        print(f"⚠️ Lỗi tạo shell script: {e}")


def create_simple_guide():
    """Tạo hướng dẫn đơn giản"""
    print("\n📖 Tạo hướng dẫn sử dụng...")
    
    guide = """# HƯỚNG DẪN SỬ DỤNG WHISK AUTOMATION TOOL

## 🚀 CÁCH SỬ DỤNG

### BƯỚC 1: Chuẩn bị prompts
1. Mở file `prompts.txt`
2. Thêm các prompt của bạn (mỗi dòng một prompt)
3. Ví dụ:
   ```
   Create a modern logo for tech startup
   Design a mobile app interface
   Generate a poster for music festival
   ```

### BƯỚC 2: Chạy automation
- **Windows**: Double-click `CHAY_AUTOMATION.bat`
- **Mac/Linux**: Double-click `chay_automation.sh`

### BƯỚC 3: Làm theo hướng dẫn
1. Tool sẽ tự động mở Chrome
2. Đăng nhập Google và vào Whisk
3. Nhấn Enter khi sẵn sàng
4. Tool sẽ tự động xử lý prompts

## 🆘 KHI GẶP LỖI

- **Lỗi Python**: Cài Python từ https://python.org
- **Lỗi Chrome**: Cài Chrome từ https://chrome.google.com
- **Lỗi "No Whisk tab"**: Đảm bảo đã vào Whisk trong Chrome

## 🎯 THÀNH CÔNG!

Tool sẽ tự động xử lý tất cả prompts và báo cáo kết quả.
"""
    
    try:
        with open("HUONG_DAN.md", "w", encoding="utf-8") as f:
            f.write(guide)
        print("✅ Tạo HUONG_DAN.md")
    except Exception as e:
        print(f"⚠️ Lỗi tạo hướng dẫn: {e}")


def main():
    """Main setup function"""
    print_header()
    
    # Kiểm tra Python
    print(f"\n✅ Python {sys.version.split()[0]} - OK")
    
    # Cài đặt dependencies
    if not install_dependencies():
        print("\n❌ Cài đặt thất bại!")
        input("Nhấn Enter để thoát...")
        sys.exit(1)
    
    # Tạo scripts
    create_run_scripts()
    
    # Tạo hướng dẫn
    create_simple_guide()
    
    # Kết quả
    print("\n" + "=" * 50)
    print("🎉 SETUP HOÀN TẤT!")
    print("=" * 50)
    print("\n📋 CÁCH SỬ DỤNG:")
    
    system = platform.system()
    if system == "Windows":
        print("1. Double-click 'CHAY_AUTOMATION.bat'")
    else:
        print("1. Double-click 'chay_automation.sh'")
    
    print("2. Làm theo hướng dẫn trong tool")
    print("3. Đọc 'HUONG_DAN.md' nếu cần")
    
    print("\n🎯 Tool đã sẵn sàng!")
    input("\nNhấn Enter để thoát...")


if __name__ == "__main__":
    main()
