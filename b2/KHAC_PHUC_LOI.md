# 🆘 KHẮC PHỤC LỖI - WHISK AUTOMATION TOOL

## ❌ LỖI "PYTHON WAS NOT FOUND"

### 🔍 Nguyên nhân:
Python chưa được cài đặt hoặc chưa được thêm vào PATH

### ✅ Giải pháp:

#### CÁCH DUY NHẤT - Sử dụng Ultra Simple Launcher:
```
Double-click file: CHAY_NGAY.py
```
File này có workflow siêu đơn giản, không hỏi gì cả.

#### CÁCH 2 - Cài đặt Python đúng cách:
1. **Tải Python:**
   - Truy cập: https://python.org
   - Tải Python 3.11 hoặc mới hơn

2. **Cài đặt Python:**
   - Chạy file installer
   - **QUAN TRỌNG**: Chọn "Add Python to PATH"
   - Click "Install Now"

3. **Khởi động lại máy tính**

4. **Test Python:**
   - Mở Command Prompt
   - Gõ: `python --version`
   - Nếu hiển thị version → OK

5. **Chạy lại automation:**
   - Double-click `CHAY_AUTOMATION.bat`

#### CÁCH 3 - Sử dụng đường dẫn đầy đủ:
Nếu Python đã cài nhưng không có trong PATH:

1. Tìm đường dẫn Python:
   - Thường ở: `C:\Users\[TÊN]\AppData\Local\Programs\Python\Python3XX\python.exe`
   - Hoặc: `C:\Python3XX\python.exe`

2. Chỉnh sửa `CHAY_AUTOMATION.bat`:
   - Thay `python run_automation.py`
   - Bằng: `"C:\đường\dẫn\đầy\đủ\python.exe" run_automation.py`

---

## ❌ LỖI "NO WHISK TAB FOUND"

### 🔍 Nguyên nhân:
- Chrome chưa mở Whisk
- Tab Whisk bị đóng
- URL không chứa "whisk"

### ✅ Giải pháp:
1. **Mở Chrome** (tool sẽ tự động mở)
2. **Đăng nhập Google**
3. **Truy cập:** https://labs.google/fx/tools/whisk
4. **Đảm bảo URL chứa "whisk"**
5. **Giữ tab mở** và chạy lại automation

---

## ❌ LỖI "FAILED TO CONNECT TO CHROME"

### 🔍 Nguyên nhân:
- Chrome chưa khởi động với debug mode
- Port 9222 bị chặn
- Chrome đã mở trước đó

### ✅ Giải pháp:
1. **Đóng tất cả Chrome:**
   - Task Manager → End tất cả Chrome processes
   - Hoặc: Ctrl+Shift+Esc → Tìm Chrome → End task

2. **Chạy lại automation:**
   - Tool sẽ tự động mở Chrome với debug mode

3. **Nếu vẫn lỗi:**
   - Kiểm tra firewall có chặn port 9222
   - Thử port khác: `--port 9223`

---

## ❌ LỖI "BUTTON NOT ENABLED"

### 🔍 Nguyên nhân:
- Tài khoản Whisk hết credits
- Prompt không hợp lệ
- Whisk đang overload

### ✅ Giải pháp:
1. **Kiểm tra credits:**
   - Vào Whisk → Kiểm tra số credits còn lại
   - Nạp thêm credits nếu cần

2. **Kiểm tra prompt:**
   - Prompt phải bằng tiếng Anh
   - Không quá dài (< 200 ký tự)
   - Không chứa ký tự đặc biệt

3. **Tăng delay time:**
   - Chọn delay 30-40 giây thay vì 20 giây
   - Chạy vào giờ thấp điểm

---

## ❌ LỖI "AUTOMATION THẤT BẠI"

### 🔍 Nguyên nhân:
- Mạng không ổn định
- Whisk server lỗi
- Prompt file có vấn đề

### ✅ Giải pháp:
1. **Kiểm tra mạng:**
   - Test kết nối internet
   - Thử refresh Whisk manually

2. **Kiểm tra prompts.txt:**
   - Mở file prompts.txt
   - Đảm bảo mỗi dòng 1 prompt
   - Không có dòng trống ở cuối

3. **Chạy với debug mode:**
   - Chọn "y" khi tool hỏi debug
   - Xem log chi tiết trong console

4. **Thử từng prompt:**
   - Tạo file prompts.txt chỉ có 1 prompt
   - Test xem prompt nào gây lỗi

---

## 🔧 TROUBLESHOOTING NÂNG CAO

### Debug Mode:
```
Khi tool hỏi "Bật debug mode? (y/n)"
→ Chọn "y"
→ Xem log chi tiết
```

### Log Files:
```
Kiểm tra file: whisk_automation.log
→ Chứa thông tin lỗi chi tiết
→ Gửi file này khi cần support
```

### Manual Test:
```
1. Mở Chrome manually
2. Vào Whisk
3. Thử tạo 1 design manual
4. Nếu OK → Chạy lại automation
```

---

## 📞 HỖ TRỢ

### Khi cần hỗ trợ, cung cấp:
1. **Screenshot lỗi**
2. **File log:** `whisk_automation.log`
3. **Hệ điều hành:** Windows/Mac/Linux
4. **Python version:** `python --version`
5. **Chrome version**
6. **Mô tả chi tiết vấn đề**

### Thông tin hệ thống:
```
- OS: Windows 10/11, macOS, Ubuntu...
- Python: 3.11.x, 3.12.x...
- Chrome: Version xxx
- Whisk account: Free/Paid
```

---

## 🎯 TÓM TẮT NHANH

### Lỗi Python:
→ Double-click `CHAY_NGAY.py` (file duy nhất)

### Lỗi Chrome:
→ Đóng Chrome → Chạy lại tool

### Lỗi Whisk:
→ Kiểm tra đã vào Whisk chưa

### Lỗi Button:
→ Kiểm tra credits → Tăng delay

### Lỗi khác:
→ Chạy debug mode → Gửi log

**Trong 90% trường hợp, sử dụng `CHAY_AUTOMATION.py` sẽ giải quyết được vấn đề!** 🚀
