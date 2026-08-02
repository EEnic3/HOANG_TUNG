# HOANG_TUNG
phongkham_tmh/
├── app.py
├── database.db
├── schema.sql
├── static/
│   ├── css/
│   │   ├── style.css         # CSS cho Giao diện nhập liệu
│   │   └── print.css         # CSS riêng cho In Phiếu & Đơn thuốc (@media print)
│   ├── js/
│   │   └── main.js           # Xử lý chọn ảnh, chọn mẫu bệnh lý nhanh
│   └── uploads/              # Nơi lưu 4 ảnh của mỗi ca nội soi
└── templates/
    ├── index.html            # Trang tiếp nhận & Danh sách bệnh nhân
    ├── form_noisoi.html      # Form tạo phiếu nội soi + Chọn ảnh + Mẫu sẵn
    ├── print_noisoi.html     # Giao diện IN Phiếu nội soi theo mẫu
    ├── form_donthuoc.html    # Form kê đơn thuốc
    └── print_donthuoc.html   # Giao diện IN Đơn thuốc khổ A5