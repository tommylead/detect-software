import tkinter as tk
import os

def test_icon():
    root = tk.Tk()
    root.title("Test Icon - Should show ico_chuan.ico")
    root.geometry("400x200")
    
    # Test icon loading
    try:
        # Try different paths
        paths_to_try = [
            "ico_chuan.ico",
            os.path.join(os.path.dirname(__file__), "ico_chuan.ico"),
            os.path.join("dist", "ico_chuan.ico")
        ]
        
        icon_loaded = False
        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    root.iconbitmap(path)
                    print(f"✅ Icon loaded successfully from: {path}")
                    icon_loaded = True
                    break
                except Exception as e:
                    print(f"❌ Failed to load icon from {path}: {e}")
        
        if not icon_loaded:
            print("❌ No icon could be loaded")
            root.iconbitmap("")  # Remove default icon
            
    except Exception as e:
        print(f"❌ Icon loading error: {e}")
    
    # Add some content
    label = tk.Label(root, text="Icon Test Window\nCheck title bar for ico_chuan.ico", 
                     font=("Arial", 12), justify="center")
    label.pack(expand=True)
    
    # Check what files exist
    print("\n📁 Files in current directory:")
    for file in os.listdir("."):
        if file.endswith((".ico", ".png")):
            print(f"  - {file}")
    
    if os.path.exists("dist"):
        print("\n📁 Files in dist directory:")
        for file in os.listdir("dist"):
            if file.endswith((".ico", ".png")):
                print(f"  - {file}")
    
    root.mainloop()

if __name__ == "__main__":
    test_icon()
