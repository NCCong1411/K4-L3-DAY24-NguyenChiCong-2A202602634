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

## Checkpoint 3d — Trifecta split và containment

Runner bây giờ tách việc xử lý thành các run có phạm vi riêng. Run A chỉ tìm
và đọc corpus; dữ liệu duy nhất đi sang Run B là ticket ID dạng số lấy từ tên
file. Run B tra `related_tickets` từ fixture trusted rồi mới xin quyền đọc
customer. Customer ID, URL và text trong lure bị bỏ lại ở Run A. Trước khi trả
summary, nội dung document cũng đi qua `redact()`.

Mình chạy `tests/test_split.py`, `tests/test_injection.py` và `tests/test_obo.py`.
Tất cả đều pass: khách `KH-000777` chỉ có trong free text không bị đọc, 4 lure
đều bị chặn dưới cả `support_l1` lẫn DPO, còn customer hợp lệ vẫn được DPO đọc.
Khi thấy injection, runner ghi một attempt egress riêng với record count thay
vì payload; policy deny call `http_post` trước khi tool chạy nên không có PII
đến sink.

## Checkpoint 3e — Tamper-evident ledger

Mình chạy `python -m pytest tests/test_ledger.py -v`; cả 3 test đều pass.
Mỗi dòng JSONL có `prev_hash` và `hash` SHA-256 tính từ JSON canonical, còn
`verify()` kiểm reason, liên kết với dòng trước và hash đã lưu. Ledger chỉ giữ
`args_hash`, không ghi argument hoặc PII thô.

Mình cũng tạo một ledger tạm gồm hai entry: trước khi sửa, `verify()` trả
`True`; sau khi đổi field `tool` của dòng đầu mà không tính lại hash, hàm trả
`False`. Hash chain này chỉ phát hiện sửa/chèn trong phần file còn lại. Nó
không tự phát hiện xoá dòng cuối hoặc ghi lại cả file với chain mới nếu không
có một mốc hash tin cậy bên ngoài; đó là giới hạn của lab và đã được ghi nhận.

## Checkpoint 4 — Supply chain và secret scanning

Mình tạo `requirements.lock` bằng `pip-compile --generate-hashes` từ
`requirements.txt`. File lock có hash SHA-256 cho toàn bộ dependency đã resolve,
bao gồm `requests` và `pytest`. Lệnh `python -m pip install --require-hashes -r
requirements.lock` chạy thành công, nên môi trường không cài một bản package không
nằm trong lock hoặc không khớp hash.

Gitleaks được dùng ở phiên bản `8.30.1`. Quét working tree bằng cấu hình của repo
trả exit code 0, không có finding. Quét lịch sử có đúng một finding mô phỏng tại
commit `1bdd849922156c868a5ee9293d68f5b72e242d2c`: file `lab-fake-secret.txt`, rule
`lab24-synthetic-token`, exit code 1 như kỳ vọng. Giá trị bị redact trong output và
không phải credential thật; chi tiết cùng hướng xử lý nếu đây là secret thật nằm ở
`reports/secrets-incident.md`.

Mình cũng chạy `pre-commit run --all-files`; hook `gitleaks-system` từ repository
Gitleaks chính thức pass. Hook giúp chặn secret mới trước khi commit, nhưng không
thay thế việc rotate/thu hồi credential nếu một secret thật đã từng bị lộ.

- OS / Python / Gitleaks version: Windows; Python 3.11.9; Gitleaks 8.30.1.
- `python -m pytest tests/ -q`: 33 passed.
- `pre-commit run --all-files`: pass (`gitleaks-system`).
- Ledger verify: `True` với `reports/ledger.jsonl` sau lần replay checkpoint 5.
- Checkpoint 5 replay: chạy đúng query ban đầu với `--mock --as dpo`; sink được reset
  trước khi chạy và `reports/attack-after.log` rỗng (0 byte). Ledger dòng 23 ghi
  `http_post` là `deny`, reason là `restricted data cannot be sent through an
  egress-enabled run`.
- Lỗi công cụ đã gặp và cách tái hiện:
  - Trên PowerShell Windows dùng encoding cp1252, chạy
    `python -m agent.loop --mock --as dpo "Tổng hợp các ticket còn mở tuần này"`
    hoặc `python -m agent.check_lure corpus/ticket-90*.md` có thể lỗi
    `UnicodeEncodeError` khi CLI in tiếng Việt. Chạy lại với `PYTHONIOENCODING=utf-8`
    thì exit code 0; evidence checkpoint 5 và self-check 4/4 lure được tạo từ các lần
    chạy UTF-8.
  - Khi gọi trực tiếp helper mock trong replay baseline, `get_llm(mock=True)` báo
    thiếu đối số `model`; điều kiện tái hiện là dùng helper này ngoài CLI. Truyền rõ
    `get_llm(mock=True, model=None)` khắc phục lỗi, sau đó 4 replay baseline đều exit
    code 0 và ghi 4 dòng vào `reports/attack-before.log`.
  - Trong sandbox, `pre-commit run --all-files` từng lỗi `OperationalError: attempt
    to write a readonly database` tại cache người dùng. Chạy lại với quyền ghi cache
    cục bộ thì hook `gitleaks-system` pass. Đây là giới hạn môi trường chạy, không
    phải finding của scanner hay lỗi cấu hình hook.
- Các lỗi còn lại: không có lỗi test hoặc finding trong working tree tại thời điểm kiểm tra.
