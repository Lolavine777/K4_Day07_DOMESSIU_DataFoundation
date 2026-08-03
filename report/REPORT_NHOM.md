# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Độ MESSIU (K4)
**Thành viên:** Nguyễn Đăng Long (2A202601934), Đào Minh Chiến (2A202601184),
Lương Minh Quân (2A202601308), Lê Đăng Tấn (2A202601916), Vũ Hữu An (2A202601078)
**Ngày kiểm thử:** 2026-08-03

> Báo cáo này dùng corpus chính sách Etsy công khai trong `data/k4_ecommerce/`.
> Nội dung mỗi file là bản tóm lược/paraphrase ngắn, không sao chép nguyên văn;
> URL gốc, ngày lấy và phiên bản được giữ trong front matter và `sources.csv`.

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm

### Phạm vi

Nhóm tập trung vào **chính sách TMĐT và hỗ trợ khách hàng của Etsy**: quyền buyer,
tranh chấp/hoàn tiền, nghĩa vụ seller, giao hàng, thanh toán, phí, chống giao dịch
ngoài nền tảng, quyền riêng tư và hủy giao dịch. Đây là một phạm vi thống nhất,
đúng biến thể K4 và đủ để thử metadata `customer_role`.

### Danh sách tài liệu

| # | Tài liệu | Nguồn chính thức | Ngày lấy / phiên bản | Ký tự | Metadata hữu ích |
|---|---|---|---|---:|---|
| 1 | Buyer Policy | [Etsy](https://www.etsy.com/legal/buyers/) | 2026-08-03 / 2026-06-09 | 504 | buyer, buyer-rights-and-order-problems |
| 2 | Cases Policy | [Etsy](https://www.etsy.com/legal/policy/cases-policy/243306189901) | 2026-08-03 / 2026-07-09 | 412 | both, disputes-and-refunds |
| 3 | Seller Policy | [Etsy](https://www.etsy.com/legal/sellers/) | 2026-08-03 / 2026-07-09 | 384 | seller, seller-listing-and-account |
| 4 | Shipping Policy | [Etsy](https://www.etsy.com/legal/shipping/) | 2026-08-03 / 2026-07-09 | 424 | seller, fulfilment-and-shipping |
| 5 | Payments Policy | [Etsy](https://www.etsy.com/legal/etsy-payments/) | 2026-08-03 / truy cập web | 445 | seller, payments-and-disbursements |
| 6 | Fees & Payments Policy | [Etsy](https://www.etsy.com/legal/fees/) | 2026-08-03 / 2026-02-13 | 408 | seller, fees-and-taxes |
| 7 | Off-Platform Transactions | [Etsy](https://www.etsy.com/legal/policy/off-platform-transactions/1254654515806) | 2026-08-03 / 2026-06-09 | 492 | both, fraud-prevention-and-payment-safety |
| 8 | Privacy Policy | [Etsy](https://www.etsy.com/legal/privacy) | 2026-08-03 / 2025-11-20 | 431 | both, privacy-and-data-use |
| 9 | How to Cancel a Sale | [Etsy Help](https://help.etsy.com/hc/en-us/articles/115015587347-How-to-Cancel-a-Sale) | 2026-08-03 / truy cập web | 438 | seller, cancellation-and-refunds |

Corpus có **9 tài liệu**, nằm trong giới hạn 5–10. `benchmark/test_corpus_contract.py`
kiểm tra số lượng, metadata, inventory và tính grounded của năm câu hỏi.

### Metadata schema

| Trường | Ví dụ | Mục đích |
|---|---|---|
| `doc_id` | `etsy-shipping-policy` | Định danh ổn định và truy vết chunk gốc |
| `source_url` | URL Etsy chính thức | Kiểm chứng nguồn |
| `retrieved_at` | `2026-08-03` | Kiểm tra độ mới |
| `document_version` | `effective-2026-07-09` | Xác định phiên bản policy |
| `customer_role` | `buyer`, `seller`, `both` | Lọc theo đối tượng câu hỏi |
| `policy_area` | `fulfilment-and-shipping` | Thu hẹp truy xuất theo chủ đề |
| `language` | `en` | Mô tả ngôn ngữ nguồn |

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm

### Baseline trên ba tài liệu đầu

`ChunkingStrategyComparator().compare(..., chunk_size=180)`:

| Tài liệu | FixedSize (count / avg) | Sentence (count / avg) | Recursive (count / avg) |
|---|---:|---:|---:|
| Buyer Policy | 4 / 163,5 | 2 / 251,0 | 5 / 99,6 |
| Cancellation Help | 3 / 179,3 | 2 / 218,0 | 5 / 86,4 |
| Cases Policy | 3 / 170,7 | 2 / 205,0 | 5 / 81,2 |

Fixed-size tạo đoạn gần giới hạn nhưng có thể cắt giữa ý. Sentence giữ câu đầy đủ
nhưng các câu policy dài. Recursive tạo nhiều mảnh ngắn hơn, phù hợp khi cần đưa
đúng điều kiện/ngoại lệ vào context.

### Chiến lược từng thành viên

| Thành viên | Chiến lược | Lý do |
|---|---|---|
| Đào Minh Chiến | `RecursiveChunker(400)` | Tách theo paragraph, câu rồi từ để giữ các điều kiện policy trong giới hạn context. |
| Nguyễn Đăng Long | `HeadingChunker(400)` | Giữ heading Markdown với nội dung bên dưới, giúp context nêu rõ tên policy. |
| Vũ Hữu An | `HeadingChunker(400)` | Gộp theo section và giữ heading để giảm mất ngữ cảnh cấu trúc. |
| Lương Minh Quân | `SentenceChunker` | Mỗi chunk là nhóm câu hoàn chỉnh, dễ đọc khi trả lời hướng dẫn. |
| Lê Đăng Tấn | `PolicySectionChunker(400)` | Chiến lược tùy chỉnh theo section policy, ưu tiên giữ title cùng quy tắc/ngoại lệ. |

### So sánh smoke benchmark

Tất cả chạy cùng `benchmark/queries.py`, `data/k4_ecommerce/`, `top_k=3` và
`MockEmbedder`. Kết quả chỉ xác nhận pipeline; mock không dùng để kết luận chất
lượng ngữ nghĩa.

| Thành viên | Chiến lược | Document match tự động (/5) | Nhận xét |
|---|---|---:|---|
| Đào Minh Chiến | Recursive | 3 | Filter Q1/Q3 hoạt động; Q2/Q4 nhiễu mock. |
| Nguyễn Đăng Long | Heading | 3 | Giữ tên policy nhưng mock vẫn miss Q2/Q5. |
| Vũ Hữu An | Heading | 4 | Cao nhất trong smoke run, chưa phải kết luận semantic. |
| Lương Minh Quân | Sentence | 3 | Đúng Q1/Q3/Q4; miss Q2/Q5. |
| Lê Đăng Tấn | Policy section | 3 | Đúng Q1/Q3/Q5; miss Q2/Q4. |

Để kết luận chiến lược tốt nhất cần chạy lại cùng local embedder đa ngữ. Môi
trường kiểm thử đã có thư viện `sentence-transformers`, nhưng checkpoint chưa
có cache và tải model vượt giới hạn memory/virtual memory của máy; vì vậy nhóm
không gán điểm semantic từ mock.

## 3. Câu hỏi đánh giá & Chất lượng truy xuất — Nhóm

| # | Câu hỏi | Gold answer rút gọn | Tài liệu chứa bằng chứng |
|---|---|---|---|
| 1 | Vấn đề nào khiến buyer có thể hoàn tiền? | Không đến, muộn, hỏng hoặc khác đáng kể mô tả. | `etsy-buyer-policy` |
| 2 | Trước khi mở case cần làm gì và chờ bao lâu? | Help with Order; chờ 48 giờ. | `etsy-cases-policy` |
| 3 | Đơn tới Hoa Kỳ cần yêu cầu duty nào? | DDP, trừ ngoại lệ hẹp có buyer xác nhận. | `etsy-shipping-policy` |
| 4 | Phí listing và thời hạn listing? | USD 0,20; bốn tháng. | `etsy-fees-policy` |
| 5 | Vì sao không hoàn tất giao dịch ngoài Etsy? | Mất payment, purchase và case protection. | `etsy-off-platform-policy` |

Câu 1 lọc `customer_role=buyer`; câu 3 lọc đồng thời
`customer_role=seller` và `policy_area=fulfilment-and-shipping`; câu 4 lọc
`customer_role=seller`. Trong smoke run, Q3 luôn lên Top-1 vì filter thu hẹp
đúng một policy. Đây là bằng chứng rõ rằng metadata hữu ích, đồng thời cho thấy
filter cần được thiết kế đủ cụ thể để không lẫn nhiều seller policy.

Grounding được kiểm tra bằng `expected_doc_ids` và nội dung evidence ghi trong
`benchmark/queries.py`; điểm thứ hai của mỗi câu chỉ được tính khi Agent trả lời
đúng gold answer. Chưa có LLM/semantic-run đáng tin cậy trong môi trường này nên
nhóm không tự nhận điểm Agent từ mock.

## 4. Demo & bài học nhóm

Demo tái lập:

```powershell
python main.py "What must a buyer do before opening an Etsy case?"
python -m benchmark.run_benchmark --package src.K4_2A202601184_DaoMinhChien --provider mock --chunker recursive --markdown
```

Khi có đủ RAM và checkpoint local, thay `--provider mock` bằng `--provider local`
để đo semantic retrieval; không dùng mock để công bố điểm cuối.

- Metadata role và policy area làm Q1/Q3 có thể kiểm chứng, thay vì chỉ dựa vào
  từ khóa chung như “buyer” hoặc “payment”.
- Heading/section chunker giúp giữ tên policy, còn recursive/sentence đánh đổi
  giữa độ đầy đủ và kích thước context.
- Failure case của mock là Q2: từ “case” và “buyer” không đủ để xếp đúng Cases
  Policy; đây là lý do cần embedding đa ngữ thật.

## Tự đánh giá (provisional)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Lựa chọn tài liệu | 10 / 10 |
| Thiết kế chiến lược | 14 / 15 |
| Chất lượng truy xuất | 5 / 10 |
| Thuyết trình / demo | 4 / 5 |
| **Tổng phần nhóm hiện tại** | **33 / 40** |

Điểm retrieval là provisional: corpus, metadata, năm query và smoke pipeline đã
đủ; semantic benchmark và xác nhận Agent answer cần chạy lại sau khi có model
local và đủ bộ nhớ.
