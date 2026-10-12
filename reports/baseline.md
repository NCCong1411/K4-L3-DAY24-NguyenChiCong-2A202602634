# Baseline — checkpoint 1

1. **Agent chưa có identity riêng cho mỗi run.** `_naive_loop()` chỉ nhận
   `message` và `llm`, sau đó gọi thẳng các tool; không có `agent_id`, `run_id`,
   principal hay thời hạn của run (`agent/loop.py:27-54`).

2. **Chưa có thành phần nào thực sự cấp quyền cho `http_post`.**
   `_naive_loop()` tự gọi `tools.http_post()` ngay khi tìm được dữ liệu khách
   hàng (`agent/loop.py:39-44`). `http_post()` chỉ giới hạn đích đến ở
   `127.0.0.1:10024` (`agent/tools.py:68-84`); đây là giới hạn an toàn của lab,
   không phải policy kiểm tra người gọi, mục đích hoặc loại dữ liệu.

3. **Bằng chứng dữ liệu đã bị gửi sai nằm trong `reports/sink.log`.** Trong
   `sink/sink.py`, `Handler.do_POST()` đọc request body rồi ghi nguyên nội dung
   thành một dòng JSON (`sink/sink.py:42-47`). Bản log trước containment sẽ
   được lưu thành `reports/attack-before.log` ở checkpoint 2.
