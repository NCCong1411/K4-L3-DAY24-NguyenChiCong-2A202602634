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

## Checkpoint 3b — Policy enforcement point

Mình chạy `python -m pytest tests/test_policy.py -v` và cả 4 test đều pass.
Rule `restricted + egress` được kiểm tra trước các rule khác, nên kể cả DPO có
đủ quyền đọc customer thì call vẫn bị chặn nếu run đang cho phép egress.

Policy đọc principal từ fixture mô phỏng `data/principals.json` và deny mặc
định khi thiếu principal, tool, purpose, scope hoặc expiry. Mình kiểm tra thêm
thủ công: DPO được phép `read_customer` cho `support-reply`; `support_l1` bị
chặn cùng call đó; purpose sai, TTL hết hạn và agent con có scope vượt parent
đều bị deny với reason cụ thể. Đây là authorization mô phỏng trong lab, không
phải cơ chế xác thực production.

## Checkpoint 3c — On-behalf-of (OBO)

Mình chạy `python -m pytest tests/test_obo.py -v`; cả 5 test đều pass. Runner
tạo `run_id` và expiry UTC cho mỗi lần chạy, sau đó kiểm policy ngay trước từng
tool call. Với cùng query có lure, `support_l1` vẫn có entry deny trong ledger
nhưng không hề chạm vào `read_customer`; DPO hợp lệ vẫn đọc được record gắn với
ticket và các entry đều có `on_behalf_of`, `agent_id`, `run_id`, `expires_at`.

Phần `append()` của ledger được bổ sung sớm để có audit evidence cho OBO. Ở
checkpoint ledger sau, mình sẽ hoàn thiện `verify()` và kiểm tra đầy đủ hash
chain/tampering. Split để không dùng customer ID từ free text sẽ được thực hiện
ở checkpoint trifecta tiếp theo.

- OS / Python / Gitleaks version:
- `python -m pytest tests/ -q`:
- `pre-commit run --all-files`:
- Ledger verify:
- Các lỗi còn lại:
