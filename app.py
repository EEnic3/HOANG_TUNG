import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, g, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATABASE'] = 'database.db'

# Đảm bảo thư mục upload tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        schema_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "schema.sql"
        )

        if not os.path.exists(schema_path):
            print(f"❌ LỖI: Không tìm thấy file {schema_path}")
            return

        with open(schema_path, "r", encoding="utf-8") as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()
        print("✅ Đã khởi tạo database thành công!")

init_db()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- HÀM PHỤ TRỢ LẤY CẤU HÌNH & THUỐC TỦ (TỰ ĐỘNG TẠO BẢNG NẾU THIẾU) ---
def get_settings():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    rows = db.execute('SELECT key, value FROM settings').fetchall()
    return {r['key']: r['value'] for r in rows}

def get_quick_medicines():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS quick_medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            times_per_day TEXT DEFAULT '2',
            morning_dose TEXT DEFAULT '1 viên sau ăn',
            evening_dose TEXT DEFAULT '1 viên sau ăn'
        )
    ''')
    return db.execute('SELECT * FROM quick_medicines ORDER BY name ASC').fetchall()

# --- CÁC ROUTE CỦA ỨNG DỤNG ---

# 1. Trang Chủ / Tiếp Nhận Bệnh Nhân (4 Tab)
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        full_name = request.form['full_name']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        symptom = request.form['symptom']
        
        cursor = db.execute(
            'INSERT INTO patients (full_name, age, gender, address, symptom) VALUES (?, ?, ?, ?, ?)',
            (full_name, age, gender, address, symptom)
        )
        db.commit()
        return redirect(url_for('form_noisoi', patient_id=cursor.lastrowid))
        
    patients = db.execute('SELECT * FROM patients ORDER BY id DESC LIMIT 20').fetchall()
    # TRUYỀN ĐỦ settings VÀ quick_meds CHO TRANG INDEX
    return render_template(
        'index.html', 
        patients=patients, 
        settings=get_settings(), 
        quick_meds=get_quick_medicines()
    )

# 2. Cập Nhật Cài Đặt (Tab 3)
@app.route('/settings/update', methods=['POST'])
def update_settings():
    db = get_db()
    for key in ['clinic_name', 'clinic_address', 'clinic_phone', 'clinic_license', 'doctor_name']:
        if key in request.form:
            db.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, request.form[key]))
    db.commit()
    return redirect(url_for('index') + '#tab-settings')

# 3. Thêm Thuốc Nhanh (Tab 4)
@app.route('/settings/quick-med/add', methods=['POST'])
def add_quick_med():
    name = request.form.get('name', '').strip()
    times = request.form.get('times_per_day', '2').strip()
    morning = request.form.get('morning_dose', '1 viên sau ăn').strip()
    evening = request.form.get('evening_dose', '1 viên sau ăn').strip()
    
    if name:
        db = get_db()
        db.execute(
            'INSERT INTO quick_medicines (name, times_per_day, morning_dose, evening_dose) VALUES (?, ?, ?, ?)',
            (name, times, morning, evening)
        )
        db.commit()
    return redirect(url_for('index') + '#tab-medicines')

# 4. Xóa Thuốc Nhanh (Tab 4)
@app.route('/settings/quick-med/delete/<int:med_id>')
def delete_quick_med(med_id):
    db = get_db()
    db.execute('DELETE FROM quick_medicines WHERE id = ?', (med_id,))
    db.commit()
    return redirect(url_for('index') + '#tab-medicines')
# Route Xóa NHIỀU thuốc nhanh cùng lúc (Kiểu iPhone)
@app.route('/settings/quick-med/delete-bulk', methods=['POST'])
def delete_quick_med_bulk():
    med_ids = request.form.getlist('med_ids[]')
    if med_ids:
        db = get_db()
        # Chuyển danh sách ID sang dạng tuple để xóa an toàn
        params = [(int(mid),) for mid in med_ids if mid.isdigit()]
        db.executemany('DELETE FROM quick_medicines WHERE id = ?', params)
        db.commit()
    return redirect(url_for('index') + '#tab-medicines')
# 5. Form Tạo Phiếu Nội Soi & Lưu 4 Ảnh
@app.route('/noisoi/<int:patient_id>', methods=['GET', 'POST'])
def form_noisoi(patient_id):
    db = get_db()
    patient = db.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
    
    if request.method == 'POST':
        image_names = []
        for i in range(1, 5):
            file = request.files.get(f'image_{i}')
            if file and file.filename != '':
                filename = f"{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.jpg"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_names.append(filename)
            else:
                image_names.append('')
                
        cursor = db.execute('''
            INSERT INTO examinations 
            (patient_id, tai_p, tai_t, mui_p, mui_t, vong_hong, thanh_quan, conclusion,
             image_1, image_2, image_3, image_4, hut_mui_days, cham_hong_days, lam_thuoc_tai_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient_id,
            request.form['tai_p'], request.form['tai_t'],
            request.form['mui_p'], request.form['mui_t'],
            request.form['vong_hong'], request.form['thanh_quan'],
            request.form['conclusion'],
            image_names[0], image_names[1], image_names[2], image_names[3],
            request.form.get('hut_mui_days', ''),
            request.form.get('cham_hong_days', ''),
            request.form.get('lam_thuoc_tai_days', '')
        ))
        db.commit()
        return redirect(url_for('print_noisoi', exam_id=cursor.lastrowid))
        
    return render_template('form_noisoi.html', patient=patient, settings=get_settings())

# 6. Xem & In Phiếu Nội Soi
@app.route('/print/noisoi/<int:exam_id>')
def print_noisoi(exam_id):
    db = get_db()
    exam = db.execute('''
        SELECT e.*, p.full_name, p.age, p.gender, p.address, p.symptom 
        FROM examinations e JOIN patients p ON e.patient_id = p.id 
        WHERE e.id = ?
    ''', (exam_id,)).fetchone()
    return render_template('print_noisoi.html', exam=exam, settings=get_settings())

# 7. Form Kê Đơn Thuốc
@app.route('/donthuoc/<int:exam_id>', methods=['GET', 'POST'])
def form_donthuoc(exam_id):
    db = get_db()
    exam = db.execute('SELECT * FROM examinations WHERE id = ?', (exam_id,)).fetchone()
    patient = db.execute('SELECT * FROM patients WHERE id = ?', (exam['patient_id'],)).fetchone()

    if request.method == 'POST':
        re_exam_date = request.form.get('re_exam_date', '')
        cursor = db.execute('INSERT INTO prescriptions (examination_id, re_exam_date) VALUES (?, ?)', (exam_id, re_exam_date))
        prescription_id = cursor.lastrowid

        names = request.form.getlist('medicine_name[]')
        times = request.form.getlist('times_per_day[]')
        mornings = request.form.getlist('morning_dose[]')
        evenings = request.form.getlist('evening_dose[]')

        for i in range(len(names)):
            if names[i].strip() != '':
                db.execute('''
                    INSERT INTO prescription_items (prescription_id, medicine_name, times_per_day, morning_dose, evening_dose)
                    VALUES (?, ?, ?, ?, ?)
                ''', (prescription_id, names[i], times[i], mornings[i], evenings[i]))
        db.commit()
        return redirect(url_for('print_donthuoc', prescription_id=prescription_id))

    # Truyền thêm quick_meds để bác sĩ bấm chọn thuốc nhanh ngay tại form kê đơn
    return render_template(
        'form_donthuoc.html', 
        exam=exam, 
        patient=patient, 
        settings=get_settings(), 
        quick_meds=get_quick_medicines()
    )

# 8. Xem & In Đơn Thuốc (Khổ A4/A5)
@app.route('/print/donthuoc/<int:prescription_id>')
def print_donthuoc(prescription_id):
    db = get_db()
    prescription = db.execute('SELECT * FROM prescriptions WHERE id = ?', (prescription_id,)).fetchone()
    exam = db.execute('SELECT * FROM examinations WHERE id = ?', (prescription['examination_id'],)).fetchone()
    patient = db.execute('SELECT * FROM patients WHERE id = ?', (exam['patient_id'],)).fetchone()
    items = db.execute('SELECT * FROM prescription_items WHERE prescription_id = ?', (prescription_id,)).fetchall()
    
    return render_template(
        'print_donthuoc.html', 
        prescription=prescription, 
        exam=exam, 
        patient=patient, 
        items=items, 
        settings=get_settings()
    )

# 9. Xem Hồ Sơ & Lịch Sử Khám Bệnh Nhân
@app.route('/patient/<int:patient_id>')
def patient_detail(patient_id):
    db = get_db()
    patient = db.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
    
    examinations = db.execute('''
        SELECT * FROM examinations 
        WHERE patient_id = ? 
        ORDER BY id DESC
    ''', (patient_id,)).fetchall()
    
    history = []
    for exam in examinations:
        prescription = db.execute('SELECT * FROM prescriptions WHERE examination_id = ?', (exam['id'],)).fetchone()
        items = []
        if prescription:
            items = db.execute('SELECT * FROM prescription_items WHERE prescription_id = ?', (prescription['id'],)).fetchall()
        
        history.append({
            'exam': exam,
            'prescription': prescription,
            'medicines': items
        })
        
    return render_template('patient_detail.html', patient=patient, history=history, settings=get_settings())

# 10. API Tìm Kiếm Bệnh Nhân Server-Side (AJAX)
@app.route("/api/patients/search")
def api_search_patients():
    db = get_db()

    p_id = request.args.get("id", "").strip()
    name = request.args.get("name", "").strip().upper()
    gender = request.args.get("gender", "").strip()
    symptom = request.args.get("symptom", "").strip()
    date_str = request.args.get("date", "").strip()

    query = "SELECT * FROM patients WHERE 1=1 "
    params = []

    if p_id:
        query += " AND id = ?"
        params.append(p_id)
    if name:
        query += " AND full_name LIKE ?"
        params.append(f"%{name}%")
    if gender:
        query += " AND gender = ?"
        params.append(gender)
    if symptom:
        query += " AND symptom LIKE ?"
        params.append(f"%{symptom}%")
    if date_str:
        query += " AND created_at LIKE ?"
        params.append(f"{date_str}%")

    query += " ORDER BY id DESC LIMIT 30"
    rows = db.execute(query, params).fetchall()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "full_name": r["full_name"],
            "age": r["age"],
            "gender": r["gender"],
            "symptom": r["symptom"],
            "created_at": r["created_at"][:16],
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)