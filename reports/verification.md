# Verification — điền trước khi nộp

## Checkpoint 3a — PII gate

Mình chạy `python -m pytest tests/test_pii.py -v -s` bằng Python 3.11 trong
virtual environment của repo. Testset có 118 entity: 45 CCCD, 41 số điện thoại,
15 số tài khoản và 17 email. Kết quả nhận diện là 118 dự đoán đúng trên 118
entity, tương ứng precision `1.000` và recall `1.000`.

Mình cũng thử thêm một chuỗi có SĐT và STK viết kèm dấu cách/gạch nối. Hàm
`redact()` thay từng giá trị bằng nhãn loại dữ liệu tương ứng; phần còn lại của
câu vẫn giữ nguyên. Regex ưu tiên số tài khoản có nhãn `STK` hoặc `số tài khoản`
trước khi nhận CCCD để tránh gắn nhầm dãy 12 chữ số.

Kết quả này là kiểm tra trên dữ liệu synthetic của lab, không phải đánh giá độ
bao phủ PII trong dữ liệu production.

- OS / Python / Gitleaks version:
- `python -m pytest tests/ -q`:
- `pre-commit run --all-files`:
- Ledger verify:
- Các lỗi còn lại:
