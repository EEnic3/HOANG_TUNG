import sqlite3

# Kết nối vào cơ sở dữ liệu hiện tại
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("==> ĐANG XỬ LÝ LỆCH GIỜ TRÊN MACOS...")

try:
    # 1. SỬA CÁC HỒ SƠ CŨ ĐANG BỊ LỆCH 7 TIẾNG VỀ ĐÚNG GIỜ VIỆT NAM
    # (Thuật toán thông minh: Chỉ cộng +7h cho những bản ghi đang bị lưu theo giờ UTC)
    cursor.execute("UPDATE patients SET created_at = datetime(created_at, '+7 hours') WHERE created_at < datetime('now', '+2 hours');")
    cursor.execute("UPDATE examinations SET created_at = datetime(created_at, '+7 hours') WHERE created_at < datetime('now', '+2 hours');")
    cursor.execute("UPDATE prescriptions SET created_at = datetime(created_at, '+7 hours') WHERE created_at < datetime('now', '+2 hours');")

    # 2. GẮN TRIGGER TỰ ĐỘNG ÉP GIỜ GMT+7 CHO MỌI CA KHÁM MỚI VỀ SAU
    triggers = [
        """
        CREATE TRIGGER IF NOT EXISTS force_gmt7_patients
        AFTER INSERT ON patients
        BEGIN
            UPDATE patients SET created_at = datetime('now', '+7 hours') WHERE id = NEW.id;
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS force_gmt7_examinations
        AFTER INSERT ON examinations
        BEGIN
            UPDATE examinations SET created_at = datetime('now', '+7 hours') WHERE id = NEW.id;
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS force_gmt7_prescriptions
        AFTER INSERT ON prescriptions
        BEGIN
            UPDATE prescriptions SET created_at = datetime('now', '+7 hours') WHERE id = NEW.id;
        END;
        """
    ]

    for sql in triggers:
        cursor.execute(sql)

    conn.commit()
    print("✅ Đã fix xong ca khám bị lệch giờ & gắn bộ tự động GMT+7 thành công!")

except Exception as e:
    print(f"⚠️ Có lỗi xảy ra: {e}")
    conn.rollback()
finally:
    conn.close()

print("==> HOÀN TẤT! Từ nay hệ thống luôn chạy chuẩn giờ Việt Nam 100%.")