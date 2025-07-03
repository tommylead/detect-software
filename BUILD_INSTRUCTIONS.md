# 🔧 Build Instructions - Whisk Automation Tool

## 📋 Prerequisites

### 1. **Python Installation:**
- Install Python 3.8+ from [python.org](https://python.org)
- Make sure Python is added to PATH

### 2. **Required Packages:**
```bash
pip install -r requirements.txt
```

## 🚀 Build Methods

### **Method 1: PowerShell (Recommended)**
```powershell
.\build.ps1
```

### **Method 2: Batch File**
```cmd
build.bat
```

### **Method 3: Manual Build**
```bash
# Install dependencies
pip install -r requirements.txt

# Clean previous builds
rmdir /s dist
rmdir /s build

# Build with PyInstaller
pyinstaller whisk_tool.spec
```

## 📁 Output

After successful build:
- **Executable**: `dist/WhiskAutomationTool_Fixed.exe`
- **Size**: ~30-35 MB
- **Additional files**: `prompts.txt`, `ico_chuan.png`, `license.json`

## 🔍 Troubleshooting

### **Common Issues:**

1. **Python not found**
   - Install Python and add to PATH
   - Restart command prompt

2. **Package installation fails**
   - Update pip: `pip install --upgrade pip`
   - Use virtual environment

3. **Build fails**
   - Check all source files are present
   - Verify icon file exists
   - Check PyInstaller version

### **Required Files:**
- ✅ `whisk_gui_licensed.py`
- ✅ `license_auth.py`
- ✅ `whisk_session_takeover.py`
- ✅ `react_input_handler.py`
- ✅ `prompts.txt`
- ✅ `ico_chuan.png`
- ✅ `license.json`

## 🎯 Build Configuration

The build uses `whisk_tool.spec` which includes:
- **One-file executable**
- **Windowed mode** (no console)
- **Icon embedding**
- **Data file inclusion**
- **Hidden imports** for all dependencies

## 📞 Support

If build fails, contact:
- **Zalo**: 0379822057 (Nghĩa)

---

**Ready to build your automation tool!** 🚀
