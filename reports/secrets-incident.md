# Ghi nhận token mô phỏng trong lịch sử Git

Mình dùng Gitleaks `8.30.1` với cấu hình `.gitleaks.toml` của repo. Đây là lần quét
được thực hiện trong phạm vi checkpoint 4, không phải một secret thật được đưa vào
bài nộp.

## Kết quả

- Quét working tree bằng `gitleaks dir --config .gitleaks.toml .` sạch, exit code
  `0`. Cấu hình bỏ qua `.git` và `.venv` ở bước này để chỉ đánh giá file đang có
  trong project, không đọc lại Git object hoặc thư viện cài cục bộ.
- Quét lịch sử bằng `gitleaks git --config .gitleaks.toml --redact --verbose .`
  trả exit code `1` như dự kiến. Finding duy nhất là rule
  `lab24-synthetic-token` trong `lab-fake-secret.txt`, commit
  `1bdd849922156c868a5ee9293d68f5b72e242d2c`, dòng 1.
- Giá trị trên là token mô phỏng, đã được đề bài cài sẵn trong lịch sử và đã bị
  redact trong output. Nó không phải credential thật và không xuất hiện trong
  working tree hiện tại.

## Nếu finding là credential thật

Việc đầu tiên là thu hồi hoặc rotate credential tại nhà cung cấp tương ứng, rồi kiểm
tra audit log để đánh giá thời điểm lộ, phạm vi bị truy cập và tác động. Sau đó cần
xoá secret khỏi source, thay bằng cơ chế quản lý secret phù hợp, xử lý lịch sử Git
theo quy trình của đội và thông báo cho các bên chịu trách nhiệm nếu có rủi ro.

Chỉ xoá file khỏi `HEAD` không làm credential đã lộ trong commit cũ mất hiệu lực;
ai đã clone hoặc cache lịch sử vẫn có thể đọc nó. Tương tự, pin dependency và hook
pre-commit chỉ là lớp phòng ngừa cho lần thay đổi sau: chúng không thu hồi credential
và cũng không tự xử lý hậu quả của một lần lộ thông tin đã xảy ra.
