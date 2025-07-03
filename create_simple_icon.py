"""
Create a simple icon from PNG for testing
"""
try:
    from PIL import Image
    
    def create_simple_icon():
        # Load the PNG
        img = Image.open("ico_chuan.png")
        
        # Resize to standard icon sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        
        # Create a simple icon with multiple sizes
        img.save("ico_chuan_simple.ico", format='ICO', sizes=sizes)
        print("✅ Created ico_chuan_simple.ico")
        
        # Also create a single size version
        img_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
        img_32.save("ico_chuan_32.ico", format='ICO')
        print("✅ Created ico_chuan_32.ico")
        
    if __name__ == "__main__":
        create_simple_icon()
        
except ImportError:
    print("PIL not available, cannot create icon")
except Exception as e:
    print(f"Error creating icon: {e}")
