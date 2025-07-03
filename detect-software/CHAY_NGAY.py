#!/usr/bin/env python3
"""Ultra Simple Launcher - Không hỏi gì cả"""
import subprocess
import sys

def main():
    print("🎨 WHISK AUTOMATION TOOL - ULTRA SIMPLE")
    print("=" * 50)
    print("🤖 Tool tự động xử lý prompts")
    print()
    input("Nhấn Enter để bắt đầu...")

    try:
        subprocess.run([sys.executable, "ultra_simple_launcher.py"], check=True)
    except Exception as e:
        print(f"Lỗi: {e}")

    input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
