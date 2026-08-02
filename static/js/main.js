document.addEventListener("DOMContentLoaded", function () {
    initClock();
    initServerSideSearch(); // <-- Gọi hàm tìm kiếm AJAX siêu tốc
    initNameFormatter();
});

// 0. Hàm chuyển đổi qua lại giữa 2 Tab
function switchTab(tabId, btnElement) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.topbar-tab-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    btnElement.classList.add('active');
}
// 1. Đồng hồ
function initClock() {
    const clockElement = document.getElementById("clockDisplay");
    if (!clockElement) return;
    function updateTime() {
        const now = new Date();
        const days = ["Chủ nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"];
        clockElement.innerHTML = `<i class="fa-regular fa-clock"></i> ${days[now.getDay()]}, ${now.toLocaleDateString('vi-VN')} - <b>${now.toLocaleTimeString('vi-VN')}</b>`;
    }
    updateTime();
    setInterval(updateTime, 1000);
}

// 2. Điền nhanh triệu chứng
function addSymptom(text) {
    const symptomInput = document.getElementById("symptom");
    if (!symptomInput) return;
    let currentValue = symptomInput.value.trim();
    if (currentValue === "") {
        symptomInput.value = text;
    } else {
        if (!currentValue.endsWith(",") && !currentValue.endsWith(";")) {
            symptomInput.value = currentValue + ", " + text.toLowerCase();
        } else {
            symptomInput.value = currentValue + " " + text.toLowerCase();
        }
    }
    symptomInput.focus();
}

// 3. Tên chữ hoa
function initNameFormatter() {
    const nameInput = document.getElementById("full_name");
    if (!nameInput) return;
    nameInput.addEventListener("input", function (e) {
        e.target.value = e.target.value.toUpperCase();
    });
}

// 4. Tìm kiếm & Bộ lọc nâng cao (ID, Tên, Giới tính, Triệu chứng, Ngày Tiếp Nhận)
let searchTimeout = null;

function initServerSideSearch() {
    // Tải danh sách 30 bệnh nhân mới nhất ngay khi mở trang
    fetchPatientsFromServer();

    // Gắn sự kiện cho 5 ô lọc
    const inputs = ["filterId", "filterName", "filterGender", "filterSymptom", "filterDate"];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", function() {
                // Debounce: Chờ 250ms sau khi dừng gõ mới gửi request xuống DB
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(fetchPatientsFromServer, 250);
            });
            el.addEventListener("change", fetchPatientsFromServer);
        }
    });
}

function fetchPatientsFromServer() {
    const idVal = document.getElementById("filterId")?.value || "";
    const nameVal = document.getElementById("filterName")?.value || "";
    const genderVal = document.getElementById("filterGender")?.value || "";
    const symptomVal = document.getElementById("filterSymptom")?.value || "";
    const dateVal = document.getElementById("filterDate")?.value || "";

    // Tạo URL mang theo tham số tìm kiếm
    const url = `/api/patients/search?id=${encodeURIComponent(idVal)}&name=${encodeURIComponent(nameVal)}&gender=${encodeURIComponent(genderVal)}&symptom=${encodeURIComponent(symptomVal)}&date=${encodeURIComponent(dateVal)}`;

    const tbody = document.getElementById("patientTableBody");
    if (!tbody) return;

    // Hiển thị trạng thái đang tìm kiếm nếu mạng chậm
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 20px; color: #64748b;"><i class="fa-solid fa-spinner fa-spin"></i> Đang tra cứu cơ sở dữ liệu...</td></tr>`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = ""; // Xóa trắng bảng

            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 30px; color: #64748b;">Không tìm thấy bệnh nhân nào khớp với điều kiện lọc.</td></tr>`;
                return;
            }

            // Đổ các dòng kết quả từ DB ra bảng HTML
            data.forEach(p => {
                const badgeClass = p.gender === 'Nam' ? 'gender-nam' : 'gender-nu';
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td><b>#${p.id}</b></td>
                    <td style="font-weight: 600; color: var(--primary-color);">${p.full_name}</td>
                    <td>${p.age}</td>
                    <td><span class="badge-gender ${badgeClass}">${p.gender}</span></td>
                    <td>${p.symptom}</td>
                    <td style="font-size: 12.5px; color: #64748b;">${p.created_at}</td>
                    <td style="text-align: center; white-space: nowrap;">
                        <a href="/noisoi/${p.id}" class="btn-action" title="Tạo ca khám mới">
                            <i class="fa-solid fa-camera"></i> Khám Mới
                        </a>
                        <a href="/patient/${p.id}" class="btn-secondary" style="margin-left: 6px;" title="Xem lịch sử khám">
                            <i class="fa-solid fa-folder-open"></i> Hồ Sơ
                        </a>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Lỗi tải dữ liệu:", error);
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: red;">Lỗi kết nối máy chủ dữ liệu!</td></tr>`;
        });
}

// Hàm Xóa Lọc (Reset)
function resetFilters() {
    ["filterId", "filterName", "filterGender", "filterSymptom", "filterDate"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    fetchPatientsFromServer(); // Tải lại 30 bệnh nhân mới nhất
}
