# DPIA-lite

## 1. Loại dữ liệu và phân loại

Corpus, customer fixture và các log trong bài đều là dữ liệu synthetic. Customer
record mô phỏng các trường định danh, số điện thoại, email và số tài khoản nên được
xử lý như `restricted` trong policy. Ledger không ghi raw PII hay request body; nó
chỉ giữ `args_hash`, quyết định và reason.

## 2. Mục đích xử lý và principal

Mục đích của lần replay là tổng hợp ticket mở trong lab. Principal `dpo` chỉ là vai
mô phỏng có quyền `read_customer` với purpose `support-reply`; `support_l1` không
được đọc customer record. Quyền có TTL và được kiểm tra trước từng tool call.

## 3. Luồng dữ liệu và endpoint

Run A gọi `search_docs` trên corpus untrusted, phát hiện lure nhưng chỉ chuyển ticket
ID lấy từ tên file. Run B dùng `related_tickets` trong fixture tin cậy để tìm customer
và chỉ khi policy allow mới gọi `read_customer`. Run C chỉ nhận số lượng record để
attempt `http_post` đến localhost `127.0.0.1:10024/reconcile`; policy chặn call này
vì dữ liệu restricted không được đi cùng egress.

## 4. Bằng chứng và giới hạn

Lần replay checkpoint 5 chạy với `dpo`: `reports/attack-after.log` có kích thước 0
byte, còn `reports/ledger.jsonl:23` là entry `http_post` bị deny, có reason và hash
chain hợp lệ. Đây là bằng chứng containment cho mock, không chứng minh an toàn cho
model thật, cơ chế xác thực production, consent/căn cứ pháp lý, retention, hay các
endpoint ngoài localhost.
