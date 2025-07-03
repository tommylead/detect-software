#!/usr/bin/env python3
"""
Whisk Automation Tool - Ultra Simple Launcher
Launcher siêu đơn giản - không hỏi gì cả, chạy thẳng với config mặc định
"""

import asyncio
import subprocess
import sys
import os
import time
import platform
from pathlib import Path


def print_header():
    """In header của tool"""
    print("=" * 60)
    print("🎨 WHISK AUTOMATION TOOL - ULTRA SIMPLE")
    print("=" * 60)
    print("🤖 Tool tự động xử lý prompts")
    print("=" * 60)


def start_chrome():
    """Khởi động Chrome với debug mode"""
    print("\n🌐 KHỞI ĐỘNG CHROME...")
    
    system = platform.system()
    
    try:
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
                print("❌ Không tìm thấy Chrome!")
                return False
            
            temp_dir = os.path.join(os.environ.get('TEMP', ''), f'chrome-debug-{int(time.time())}')
            cmd = [chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={temp_dir}"]
            
        else:  # macOS/Linux
            if system == "Darwin":
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            else:
                chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium-browser"]
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
            
            if not chrome_path or not os.path.exists(chrome_path):
                print("❌ Không tìm thấy Chrome!")
                return False
            
            temp_dir = f"/tmp/chrome-debug-{int(time.time())}"
            cmd = [chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={temp_dir}"]
        
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Chrome đã khởi động với debug mode")
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khởi động Chrome: {e}")
        return False


def setup_user():
    """Hướng dẫn user setup ngắn gọn"""
    print("\n" + "=" * 60)
    print("📋 THIẾT LẬP NHANH")
    print("=" * 60)
    print("✅ Chrome đã mở với debug mode")
    print("\n🔥 VUI LÒNG:")
    print("1. Đăng nhập Google trong Chrome")
    print("2. Vào: https://labs.google/fx/tools/whisk")
    print("3. Đảm bảo thấy giao diện tạo design")
    print("=" * 60)
    
    input("\n🚀 Nhấn Enter khi đã vào Whisk...")


def check_prompts_quick():
    """Kiểm tra prompts nhanh"""
    print("\n📝 KIỂM TRA PROMPTS...")
    
    if not Path("prompts.txt").exists():
        print("❌ Không tìm thấy prompts.txt")
        return False
    
    with open("prompts.txt", "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    print(f"📊 Sẵn sàng xử lý {len(prompts)} prompts")
    return len(prompts) > 0


async def run_automation_direct():
    """Chạy automation với config mặc định"""
    try:
        from whisk_session_takeover import WhiskAutomator, WhiskConfig, setup_logging
        
        # Config mặc định
        setup_logging("INFO")
        
        config = WhiskConfig(
            generation_delay=20,
            retry_attempts=3,
            prompts_file="prompts.txt",
            log_level="INFO"
        )
        
        # Chạy automation
        automator = WhiskAutomator(config)
        success = await automator.run()
        
        return success
        
    except Exception as e:
        print(f"❌ Lỗi automation: {e}")
        return False


def main():
    """Main function"""
    print_header()
    
    # Kiểm tra files nhanh
    required_files = ["whisk_session_takeover.py", "react_input_handler.py", "prompts.txt"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Thiếu files: {', '.join(missing_files)}")
        input("Nhấn Enter để thoát...")
        sys.exit(1)
    
    print("✅ Files OK")
    
    # Khởi động Chrome
    if not start_chrome():
        input("Nhấn Enter để thoát...")
        sys.exit(1)
    
    # Setup user nhanh
    setup_user()
    
    # Kiểm tra prompts nhanh
    if not check_prompts_quick():
        input("Nhấn Enter để thoát...")
        sys.exit(1)
    
    # Hiển thị config mặc định
    print("\n⚙️ CẤU HÌNH MẶC ĐỊNH:")
    print("   • Delay: 20 giây")
    print("   • Debug: Tắt")
    print("   • Retries: 3 lần")
    
    input("\n🎯 Nhấn Enter để bắt đầu automation...")
    
    # Chạy automation
    print("\n🎯 BẮT ĐẦU AUTOMATION...")
    print("=" * 40)
    print("📊 Đang xử lý prompts...")
    print("⏹️ Nhấn Ctrl+C để dừng")
    print()
    
    try:
        success = asyncio.run(run_automation_direct())
        
        if success:
            print("\n🎉 AUTOMATION HOÀN THÀNH!")
            print("✅ Tất cả prompts đã được xử lý")
            print("📁 Kiểm tra kết quả trong Whisk")
        else:
            print("\n⚠️ AUTOMATION HOÀN THÀNH VỚI MỘT SỐ LỖI")
            print("📋 Một số prompts có thể không thành công")
            
    except KeyboardInterrupt:
        print("\n⏹️ DỪNG BỞI USER")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 HOÀN TẤT!")
    print("=" * 60)
    input("Nhấn Enter để thoát...")


if __name__ == "__main__":
    main()
