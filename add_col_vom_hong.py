import sqlite3

# Kết nối thẳng vào file database.db đang có của phòng khám
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("==> ĐANG THÊM CỘT VÒM HỌNG VÀO DATABASE...")

try:
    # Lệnh thêm cột vom_hong vào bảng examinations (dữ liệu cũ giữ nguyên 100%)
    cursor.execute("ALTER TABLE examinations ADD COLUMN vom_hong TEXT;")
    conn.commit()
    print("✅ Đã thêm cột 'vom_hong' vào Database thành công! Toàn bộ hồ sơ cũ vẫn an toàn.")
except sqlite3.OperationalError:
    print("⚠️ Cột 'vom_hong' đã tồn tại sẵn trong Database rồi, không cần thêm nữa.")
except Exception as e:
    print(f"⚠️ Có lỗi xảy ra: {e}")
finally:
    conn.close()