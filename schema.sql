-- Bảng Bệnh nhân
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    address TEXT,
    symptom TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Phiếu Nội Soi TMH
CREATE TABLE IF NOT EXISTS examinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    tai_p TEXT,
    tai_t TEXT,
    mui_p TEXT,
    mui_t TEXT,
    vong_hong TEXT,
    thanh_quan TEXT,
    conclusion TEXT,
    image_1 TEXT,
    image_2 TEXT,
    image_3 TEXT,
    image_4 TEXT,
    hut_mui_days TEXT,
    cham_hong_days TEXT,
    lam_thuoc_tai_days TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Bảng Đơn Thuốc
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    examination_id INTEGER,
    re_exam_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (examination_id) REFERENCES examinations(id)
);

-- Bảng Chi Tiết Thuốc
CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER,
    medicine_name TEXT,
    times_per_day TEXT,
    morning_dose TEXT,
    evening_dose TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
);
-- Tạo Index cho các trường thường xuyên tìm kiếm (Giúp tăng tốc gấp 1000 lần)
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(full_name);
CREATE INDEX IF NOT EXISTS idx_patients_symptom ON patients(symptom);
CREATE INDEX IF NOT EXISTS idx_patients_created ON patients(created_at);
CREATE INDEX IF NOT EXISTS idx_patients_gender ON patients(gender);
-- Bảng Cấu Hình Phòng Khám & Bác Sĩ (Lưu cấu hình động)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
-- Bảng Danh Sách Thuốc Hay Dùng (Thuốc tủ của Bác sĩ)
CREATE TABLE IF NOT EXISTS quick_medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    times_per_day TEXT DEFAULT '2',
    morning_dose TEXT DEFAULT '1 viên sau ăn',
    evening_dose TEXT DEFAULT '1 viên sau ăn'
);

-- Thêm giá trị mặc định ban đầu nếu chưa có
INSERT OR IGNORE INTO settings (key, value) VALUES ('clinic_name', 'PHÒNG KHÁM TÂM ĐỨC');
INSERT OR IGNORE INTO settings (key, value) VALUES ('clinic_address', 'Số 71 Vĩnh Hưng, Hoàng Mai - Hà Nội');
INSERT OR IGNORE INTO settings (key, value) VALUES ('clinic_phone', '0827.668.222');
INSERT OR IGNORE INTO settings (key, value) VALUES ('clinic_license', '4066/ HNO – GPHĐ');
INSERT OR IGNORE INTO settings (key, value) VALUES ('doctor_name', 'BS: CK1 Nguyễn Thế Tùng');

-- Thêm sẵn một vài thuốc mẫu ban đầu (Nếu chưa có)
INSERT OR IGNORE INTO quick_medicines (id, name, times_per_day, morning_dose, evening_dose) 
VALUES 
(1, 'Amoksiklav 1g x 14 viên', '2', '1 viên sau ăn', '1 viên sau ăn'),
(2, 'Klacid 500mg x 10 viên', '2', '1 viên sau ăn', '1 viên sau ăn'),
(3, 'Alpha Choay x 20 viên', '2', '2 viên ngậm dưới lưỡi', '2 viên ngậm dưới lưỡi'),
(4, 'Xịt mũi Otrivin 0.1%', '2', 'Xịt 2 nhát/bên', 'Xịt 2 nhát/bên'),
(5, 'Paracetamol 500mg x 10 viên', '2', '1 viên khi sốt/đau', '1 viên khi sốt/đau');