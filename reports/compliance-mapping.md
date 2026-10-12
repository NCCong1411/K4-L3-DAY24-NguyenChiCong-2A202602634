# Compliance mapping

Mình đã đối chiếu nguồn gốc của các văn bản dưới đây. Bản này chỉ map control kỹ
thuật trong lab vào chủ đề rủi ro liên quan; nó không phải ý kiến pháp lý hay kết
luận hệ thống production đã tuân thủ một điều khoản cụ thể.

## Nguồn đã đối chiếu

- Luật 91/2025/QH15 — Luật Bảo vệ dữ liệu cá nhân, hiệu lực từ 01/01/2026:
  https://vanban.chinhphu.vn/?classid=1&docid=214590&pageid=27160&typegroup=
- Nghị định 356/2025/NĐ-CP — quy định chi tiết một số điều và biện pháp thi hành
  Luật Bảo vệ dữ liệu cá nhân, hiệu lực từ 01/01/2026:
  https://vbpl.moj.gov.vn/bocongan/Pages/vbpq-thuoctinh.aspx?ItemID=187276
- Luật 134/2025/QH15 — Luật Trí tuệ nhân tạo, hiệu lực từ 01/03/2026:
  https://vanban.chinhphu.vn/?classid=1&docid=216334&orggroupid=1&pageid=27160
- OWASP Agentic Top 10: ASI01 là *Agent Goal Hijack*, ASI03 là *Identity &
  Privilege Abuse*, và ASI04 là *Agentic Supply Chain Vulnerabilities*:
  https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/

| Nguồn / chủ đề | Control và evidence của lab | Giới hạn cần ghi nhận |
|---|---|---|
| Luật 91/2025/QH15 — bảo vệ dữ liệu cá nhân | Dữ liệu mô phỏng được phân loại `restricted`; Run B chỉ nhận ticket ID đã chuẩn hoá và ledger không giữ PII thô. Evidence: `agent/runner.py:156-173`, `agent/pii.py:71-105`, `agent/ledger.py:55-105`. | Không có dữ liệu cá nhân thật. Lab không đánh giá căn cứ xử lý, quyền của chủ thể dữ liệu, thông báo/đồng ý, retention hoặc chuyển dữ liệu xuyên biên giới. |
| NĐ 356/2025/NĐ-CP — biện pháp thi hành Luật 91 | Policy kiểm tra principal, purpose, scope và TTL trước tool call; allow/deny đều có reason. Evidence: `agent/policy.py:61-118`, `reports/ledger.jsonl:1-23`. | `dpo` và `support_l1` là fixture của bài; đây không phải xác thực danh tính, bổ nhiệm DPO, hồ sơ đánh giá tác động hay quy trình báo cáo sự cố ngoài đời. |
| Luật 134/2025/QH15 — quản trị vòng đời AI | Hash-chain ledger tạo dấu vết cho tool decision; split ngăn prompt trong corpus quyết định customer ID hoặc egress. Evidence: `agent/runner.py:141-204`, `agent/ledger.py:73-105`, `reports/ledger.jsonl:23`. | Chưa có đánh giá rủi ro hệ thống AI, dữ liệu huấn luyện, kiểm thử bias, giám sát hoặc human oversight của sản phẩm triển khai thật. |
| OWASP ASI01 — Agent Goal Hijack | Lure trong document vẫn được phát hiện, nhưng Run B không nhận free text; entry `http_post` bị chặn trước khi tool chạy. Evidence: `agent/runner.py:156-204`, `reports/attack-after.log` (0 byte), `reports/ledger.jsonl:23`. | Control chỉ bao phủ luồng mock/corpus của lab; không chứng minh kháng prompt injection với mọi model, tool hoặc kênh input. |
| OWASP ASI03 — Identity & Privilege Abuse | Least privilege và OBO: `support_l1` không có `read_customer`, còn DPO chỉ được cấp quyền theo scope/purpose/TTL. Evidence: `agent/policy.py:68-118`, `tests/test_obo.py`, `reports/ledger.jsonl:1-23`. | Không tích hợp IdP, session, MFA, token rotation hay authorization server thực tế. |
| OWASP ASI04 — Agentic Supply Chain Vulnerabilities | Dependency lock có hash; hook Gitleaks được pin ở v8.30.1; incident note phân biệt token giả trong history với credential thật. Evidence: `requirements.lock`, `.pre-commit-config.yaml`, `reports/secrets-incident.md`. | Không có kiểm toán nhà cung cấp, SBOM, chữ ký artifact hay đánh giá MCP/A2A/tool bên thứ ba. |
