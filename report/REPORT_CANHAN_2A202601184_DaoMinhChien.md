# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đào Minh Chiến

**Mã sinh viên:** 2A202601184

**Lớp/Nhóm:** K4

**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Mã nguồn cá nhân nằm trong package
> `src.K4_2A202601184_DaoMinhChien`. Các module trực tiếp dưới `src/` là lớp
> tương thích dùng chung để test và chạy demo của toàn nhóm.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn
thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất cá nhân (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) — Bài tập 1.1

**Độ tương tự cosine cao nghĩa là gì?**

Hai embedding có cosine similarity cao khi chúng hướng gần giống nhau trong
không gian vector. Với văn bản, điều này thường cho biết hai đoạn nói về nội
dung hoặc ý nghĩa gần nhau, ngay cả khi cách diễn đạt không hoàn toàn giống nhau.

**Ví dụ có độ tương tự cao:**

- Câu A: “Người mua có thể yêu cầu đổi trả khi hàng bị lỗi.”
- Câu B: “Khách hàng được trả lại sản phẩm nếu sản phẩm có lỗi.”
- Hai câu cùng diễn đạt quyền đổi trả khi sản phẩm bị lỗi.

**Ví dụ có độ tương tự thấp:**

- Câu A: “Chính sách đổi trả bảo vệ quyền lợi người mua.”
- Câu B: “Trời hôm nay có nhiều mây.”
- Hai câu thuộc hai chủ đề hoàn toàn khác nhau: chính sách TMĐT và thời tiết.

**Tại sao ưu tiên cosine similarity hơn Euclidean distance cho text embeddings?**

Cosine tập trung vào góc, tức hướng ngữ nghĩa của vector, và ít bị ảnh hưởng bởi
độ lớn của vector. Euclidean distance phụ thuộc nhiều vào độ lớn nên hai vector
có cùng hướng nhưng khác độ dài vẫn có thể bị xem là cách xa nhau.

### Bài toán tính toán Chunking — Bài tập 1.2

Với tài liệu dài 10.000 ký tự, `chunk_size=500`, `overlap=50`:

```text
step = 500 - 50 = 450
số chunk = ceil((10.000 - 50) / 450)
          = ceil(22,111...)
          = 23 chunk
```

Nếu tăng `overlap` lên 100:

```text
step = 500 - 100 = 400
số chunk = ceil((10.000 - 100) / 400)
          = ceil(24,75)
          = 25 chunk
```

Số chunk tăng từ 23 lên 25 vì mỗi lần dịch cửa sổ chỉ tiến 400 ký tự. Overlap
lớn hơn giúp bảo toàn ngữ cảnh nằm gần ranh giới hai chunk, nhưng làm tăng số
chunk, dung lượng lưu trữ và chi phí truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`**

Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng đứng sau dấu kết thúc
câu, nhờ đó dấu câu vẫn nằm trong nội dung. Các câu rỗng được bỏ qua, khoảng
trắng thừa được loại bỏ, sau đó tối đa `max_sentences_per_chunk` câu được ghép
thành một chunk. Chuỗi rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`**

Thuật toán thử separator theo thứ tự từ cấu trúc lớn đến nhỏ:
`["\n\n", "\n", ". ", " ", ""]`. Nếu đoạn hiện tại đã không lớn hơn
`chunk_size`, đó là base case và được trả về ngay; nếu vẫn quá lớn, thuật toán
chia bằng separator tiếp theo. Separator được gắn lại để không làm mất dấu câu
hoặc ranh giới đoạn; khi hết separator, thuật toán cắt cứng theo số ký tự.

**`compute_similarity` và `ChunkingStrategyComparator`**

`compute_similarity` tính tích vô hướng chia cho tích độ lớn hai vector và trả
`0.0` nếu một vector có độ lớn bằng không. Comparator chạy ba chiến thuật
`fixed_size`, `by_sentences`, `recursive`, rồi trả số chunk, độ dài trung bình và
danh sách chunk để có thể so sánh trực tiếp.

### Lớp EmbeddingStore

**`add_documents` + `search`**

Mỗi tài liệu được chuẩn hóa thành record gồm ID duy nhất, nội dung, metadata,
embedding và `doc_id` có thể truy vết. Store ưu tiên ChromaDB nếu khả dụng, nếu
không sẽ dùng danh sách trong bộ nhớ. Khi tìm kiếm, truy vấn được embed một lần,
điểm dot product được tính với từng record rồi sắp xếp giảm dần và giới hạn theo
`top_k`.

**`search_with_filter` + `delete_document`**

Metadata được lọc trước khi xếp hạng tương đồng; nhiều điều kiện trong filter
được kết hợp theo phép AND. `delete_document` tìm tất cả chunk có cùng
`metadata["doc_id"]`, xóa toàn bộ và trả `True` khi thực sự có dữ liệu bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`**

Agent truy xuất các chunk Top-k, đánh số từng context rồi đưa chúng cùng câu hỏi
vào prompt. Prompt yêu cầu chỉ trả lời dựa trên context và phải nói không đủ
thông tin nếu tài liệu không chứa câu trả lời; cuối cùng prompt được truyền vào
`llm_fn`, nhờ đó có thể thay LLM thật bằng hàm giả lập trong unit test.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Mã nguồn được đặt riêng tại:

```text
src/K4_2A202601184_DaoMinhChien/
├── __init__.py
├── agent.py
├── chunking.py
├── embeddings.py
├── evaluation.py
├── models.py
└── store.py
```

Lệnh kiểm thử:

```powershell
$env:LAB_SOLUTION_PACKAGE='src.K4_2A202601184_DaoMinhChien'
python -m pytest tests -v
```

Kết quả:

```text
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
collected 42 items
tests/test_solution.py .......................................... [100%]
============================= 42 passed in 0.07s =============================
```

**Số lượng bài test vượt qua:** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi tạo vector từ tần suất từ vựng đã chuẩn hóa để phép đo có thể tái lập hoàn
toàn khi chưa cài mô hình SentenceTransformers. Hai vector sau đó được đưa vào
`compute_similarity`; trong phép thử này, điểm từ `0,20` được phân loại là cao.
Toàn bộ phép đo có thể chạy lại bằng:

```powershell
$env:PYTHONUTF8='1'
python -m src.K4_2A202601184_DaoMinhChien.evaluation
```

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Người mua có thể yêu cầu đổi trả khi hàng bị lỗi. | Khách hàng được trả lại sản phẩm nếu sản phẩm có lỗi. | Cao | 0,2887 | Có |
| 2 | Người bán phải cung cấp mô tả sản phẩm chính xác. | Thông tin đăng bán cần phản ánh đúng sản phẩm. | Cao | 0,2860 | Có |
| 3 | Chính sách đổi trả bảo vệ quyền lợi người mua. | Trời hôm nay có nhiều mây. | Thấp | 0,0000 | Có |
| 4 | Sản phẩm bị cấm không được đăng bán. | Người bán không được đăng các mặt hàng bị cấm. | Cao | 0,6708 | Có |
| 5 | Yêu cầu đổi trả cần kèm bằng chứng. | Người bán cập nhật giá sản phẩm. | Thấp | 0,0000 | Có |

Kết quả đáng chú ý nhất là cặp 1 và 2 chỉ đạt khoảng 0,29 dù ý nghĩa khá gần
nhau. Nguyên nhân là vector từ vựng chỉ nhận biết các từ trùng nhau, chưa hiểu
tốt các quan hệ như “người mua” với “khách hàng”. Một embedding đa ngữ thực sự
có thể biểu diễn các quan hệ ngữ nghĩa này tốt hơn.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

### Phạm vi phép thử

Tôi chạy đúng năm câu hỏi chung trong `benchmark/queries.py` trên corpus chính
sách Etsy công khai `data/k4_ecommerce/`. Cấu hình cá nhân dùng
`RecursiveChunker(chunk_size=500)`, tạo 10 chunk, và vector tần suất từ vựng đã
chuẩn hóa để kết quả có thể tái lập offline. Câu 1 lọc
`{"customer_role": "buyer"}`; câu 3 lọc đồng thời seller và policy area, đúng
yêu cầu metadata của biến thể K4.

Script `src/K4_2A202601184_DaoMinhChien/evaluation.py` lưu cố định năm cặp câu,
năm truy vấn, vectorizer, cấu hình chunking, Top-3 và Agent stub trích xuất; vì
vậy các số liệu trong hai bảng có thể được kiểm tra lại độc lập.

| # | Câu hỏi | Top-1 chunk truy xuất được | Score | Liên quan? | Câu trả lời Agent (tóm tắt từ context) |
|---|---|---|---:|---|---|
| 1 | Vấn đề nào khiến buyer đủ điều kiện hoàn tiền? | `etsy-buyer-policy` | 0,0778 | Có (Top-2) | Chunk thứ hai nêu không đến, muộn, hỏng hoặc khác mô tả. |
| 2 | Trước khi mở case cần làm gì và chờ bao lâu? | `etsy-cases-policy` | 0,2231 | Có | Context nêu Help with Order và mốc 48 giờ. |
| 3 | Đơn tới Hoa Kỳ cần yêu cầu duty nào? | `etsy-shipping-policy` | 0,1150 | Có | Filter đưa policy shipping lên Top-1; context nêu DDP và ngoại lệ. |
| 4 | Phí listing và thời hạn listing? | `etsy-fees-policy` | 0,3074 | Có | Context nêu USD 0,20 và bốn tháng. |
| 5 | Vì sao không hoàn tất giao dịch ngoài Etsy? | `etsy-off-platform-policy` | 0,1624 | Có | Context nêu mất payment, purchase và case protection. |

Script tự động ghi nhận **5 / 5 document match trong Top-3**; kiểm tra nội dung
chunk cũng cho thấy cả năm có bằng chứng liên quan. Agent trong evaluation là
stub chỉ để kiểm tra prompt grounding, không phải LLM trả lời gold answer.

Metadata filter ở câu 3 có tác dụng rõ: nó giới hạn ứng viên bằng
`customer_role=seller` và `policy_area=fulfilment-and-shipping`, đưa đúng policy
lên Top-1. Câu 1 chỉ có hai chunk cùng tài liệu nên bằng chứng rơi ở Top-2; đây
là lý do cần kiểm tra toàn bộ Top-3 thay vì chỉ Top-1. Hướng cải thiện tiếp theo
là dùng multilingual semantic embedder và LLM thật để đánh giá câu trả lời.

**Điều học được từ benchmark chung:** cùng một corpus và năm câu hỏi cố định mới
cho phép so sánh công bằng giữa các thành viên. Retrieval đúng `doc_id` chưa đủ;
chunk Top-1 còn phải chứa đúng bằng chứng để Agent trả lời khớp gold answer.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code — 42/42 tests | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất trên benchmark chung | 5 / 10 |
| **Tổng phần cá nhân hiện tại** | **55 / 60** |

Phần retrieval tự đánh giá 5/10: cả năm câu có chunk liên quan trong Top-3,
nhưng chưa có LLM/semantic benchmark đủ tài nguyên để xác nhận điểm Agent answer
thứ hai của từng câu. Đây là kết quả offline có thể tái lập, chưa phải điểm cuối
khi dùng local multilingual embedder.

