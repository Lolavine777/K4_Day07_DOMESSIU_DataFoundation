# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Đăng Tân
**Nhóm:** K4
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Cosine cao nghĩa là hai vector embedding **chỉ về cùng một hướng** trong không gian ngữ nghĩa, tức hai đoạn text nói về cùng một chủ đề/ý — bất kể chúng dài ngắn khác nhau hay dùng từ ngữ khác nhau. Giá trị chạy từ -1 (ngược hướng) qua 0 (không liên quan) đến 1 (trùng hướng); kiểm chứng bằng code: vector giống hệt → 1.0, vuông góc → 0.0, ngược dấu → -1.0 (4 test `TestComputeSimilarity` pass).

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi muốn đổi trả sản phẩm trong vòng 30 ngày."
- Câu B: "Chính sách hoàn hàng cho phép gửi lại đơn hàng trong vòng một tháng."
- Tại sao tương đồng: gần như không dùng chung từ nào ("đổi trả" vs "hoàn hàng", "30 ngày" vs "một tháng") nhưng cùng một **ý định**: thời hạn trả hàng. Embedding mã hoá ngữ nghĩa chứ không mã hoá mặt chữ, nên hai câu nằm gần nhau về hướng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi muốn đổi trả sản phẩm trong vòng 30 ngày."
- Câu B: "Hướng dẫn cài đặt driver máy in trên Windows."
- Tại sao khác: khác hoàn toàn miền chủ đề (chính sách TMĐT vs kỹ thuật thiết bị), không chia sẻ chủ thể, hành động hay mục tiêu nào, nên hai vector gần như trực giao (cosine ≈ 0).

> **Lưu ý khi tự kiểm bằng code:** `MockEmbedder` trong package cá nhân sinh vector xác định từ `hashlib.md5`, nên không mang ngữ nghĩa. Vì vậy các điểm mock ở Mục 4 chỉ dùng để kiểm chứng hàm cosine và minh hoạ một failure case; để đánh giá retrieval nghiêm túc cần dùng `LocalEmbedder` hoặc `OpenAIEmbedder`.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ dài (norm) của vector embedding phần lớn phản ánh **độ dài / số token** của đoạn text chứ không phải nội dung, nên khoảng cách Euclid sẽ phạt oan một chunk dài và một câu ngắn dù chúng nói cùng một điều. Cosine chuẩn hoá norm đi và chỉ giữ lại **hướng** — tức phần ngữ nghĩa — nên phù hợp hơn khi so một câu hỏi ngắn với các chunk tài liệu dài, đúng tình huống retrieval của Lab này.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Mỗi chunk dài 500, hai chunk liền nhau chồng nhau 50 ký tự, nên mỗi bước tiến (`step`) chỉ đi được `500 - 50 = 450` ký tự. Chunk đầu tiên "tiêu thụ" trọn 500 ký tự, các chunk sau mỗi cái thêm 450 ký tự mới:
> `ceil((length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / 450) = ceil(9950 / 450) = ceil(22.11) = 23`
> *Đáp án:* **23 chunks** — đã đối chiếu bằng code: `len(FixedSizeChunker(500, 50).chunk("x" * 10000)) == 23`.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk **tăng**: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25` chunk (kiểm bằng code: 25). Overlap lớn hơn ⇒ step nhỏ hơn ⇒ cần nhiều chunk hơn để phủ hết tài liệu. Đánh đổi: overlap nhiều giúp một câu/ý bị cắt ngang ranh giới vẫn xuất hiện nguyên vẹn trong ít nhất một chunk (đỡ mất ngữ cảnh khi truy xuất), nhưng phải trả giá bằng nhiều bản ghi hơn trong store, nhiều lần gọi embedding hơn, và kết quả top-k dễ bị trùng lặp nội dung.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi tách câu bằng regex `(?<=[.!?])\s+`, vì lookbehind giữ dấu kết thúc ở lại với câu đứng trước. Sau khi `strip`, các câu được gom theo `max_sentences_per_chunk`; chuỗi rỗng/chỉ có khoảng trắng trả `[]`, còn tham số số câu nhỏ hơn 1 được chuẩn hoá thành 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán ưu tiên `\n\n`, `\n`, `. `, khoảng trắng rồi mới cắt theo ký tự. Nếu đoạn đã không vượt `chunk_size` thì đây là base case; nếu không còn separator hoặc gặp một token quá dài, hàm cắt theo độ dài để luôn kết thúc. Tôi nối lại separator vào đoạn trước để không làm mất dấu câu/ngắt dòng.

**`PolicySectionChunker` — chiến lược cá nhân:**
> Với corpus product listing, tôi thêm chiến lược chia theo heading Markdown, `Điều/Mục` hoặc điều khoản đánh số trước; chỉ chia đệ quy khi một mục dài. Khi phải tách mục lớn, heading được lặp lại trên các chunk con. Cách này giữ tên sản phẩm, thuộc tính, kích cỡ và hướng dẫn bảo quản đi cùng nhau, dễ truy vết hơn kiểu cắt ký tự cố định.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` tạo record trong bộ nhớ gồm `id`, `content`, bản sao `metadata` và vector embedding; nếu metadata chưa có thì bổ sung `doc_id`. `search` embedding câu hỏi một lần, tính dot product với từng vector và sắp xếp giảm dần theo score. Với mock embedder vector đã chuẩn hoá, dot product chính là cosine similarity.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi lọc metadata **trước** khi xếp hạng: record chỉ là ứng viên khi tất cả cặp key/value trong `metadata_filter` khớp. `delete_document` lọc lại danh sách lưu trữ, loại toàn bộ record có `metadata["doc_id"]` bằng id cần xóa và trả về `True` khi kích thước thực sự giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunk, đánh số nguồn kèm `id` và score rồi ghép vào phần **Ngữ cảnh** của prompt. Prompt yêu cầu LLM chỉ trả lời bằng bằng chứng đã truy xuất và phải nói rõ khi thiếu ngữ cảnh; sau đó agent gửi prompt tới `llm_fn` và trả về chuỗi trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
LAB_SOLUTION_PACKAGE=src.K4_2A202601916_LeDangTan
python -m unittest tests.test_solution -v

Ran 42 tests in 0.007s
OK
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

> Tôi chạy đúng test suite của đề với package cá nhân qua `LAB_SOLUTION_PACKAGE`. Môi trường `.venv` của repo đang trỏ tới Python 3.11 không còn khả dụng, nên lần xác minh này dùng Python 3.12 và `unittest`; kết quả vẫn là toàn bộ 42 test đạt.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Tôi muốn đổi trả sản phẩm trong vòng 30 ngày. | Chính sách hoàn hàng cho phép gửi lại đơn hàng trong vòng một tháng. | Cao | 0.0896 (mock) | Không |
| 2 | Người bán phải mô tả sản phẩm chính xác. | Người bán chịu trách nhiệm cung cấp giá và tình trạng hàng đúng. | Cao | -0.0242 (mock) | Không |
| 3 | Tôi muốn đổi trả sản phẩm trong vòng 30 ngày. | Hướng dẫn cài đặt driver máy in trên Windows. | Thấp | 0.0104 (mock) | Có |
| 4 | Hàng bị lỗi cần kèm bằng chứng khi đổi trả. | Yêu cầu đổi trả phải có bằng chứng phù hợp khi hàng không đúng mô tả. | Cao | -0.0527 (mock) | Không |
| 5 | Sản phẩm bị cấm không được đăng bán. | Người mua gửi yêu cầu hoàn hàng theo chính sách của sàn. | Thấp | 0.0686 (mock) | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 4 cùng nói về điều kiện đổi trả nhưng score mock âm. Điều này xác nhận `MockEmbedder` chỉ là hash xác định để unit test, không biểu diễn ý nghĩa. Dự đoán ngữ nghĩa của tôi vẫn hữu ích để đặt giả thuyết, nhưng kết luận retrieval phải dựa trên embedding đa ngữ thật và bộ benchmark chung.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | adidas bralet đen giá bao nhiêu? | ASOS LUXE cotton corset xanh nhạt (không liên quan) | 0.2899 | Không (top-3 không có adidas bralet) | Không chấm câu trả lời LLM vì evidence không đúng |
| 2 | Áo khoác teddy JDY beige còn size nào? | Noisy May legging shorts (không liên quan) | 0.2813 | Không | Không chấm câu trả lời LLM vì evidence không đúng |
| 3 | Váy midi đen có chi tiết cut out là sản phẩm nào? | ASYOU PU corset đen (không liên quan) | 0.2763 | Không | Không chấm câu trả lời LLM vì evidence không đúng |
| 4 | ASOS LUXE corset xanh nhạt có đặc điểm gì? | In The Style straight-leg jean (top-1 không liên quan); ASOS LUXE xuất hiện top-2 | 0.2741 | Có (top-2) | Có thể trả lời từ chunk top-2; chưa dùng LLM thật để chấm chính xác |
| 5 | Bikini top Hollister đen có thông tin gì? | ASOS LUXE corset xanh nhạt (không liên quan) | 0.3107 | Không | Không chấm câu trả lời LLM vì evidence không đúng |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **1 / 5**

> Lần chạy smoke test này dùng 20 product listing ASOS, 179 chunk và `_mock_embed`; vì vậy 1/5 không phải chất lượng semantic thực tế của chiến lược. Nó là failure case rõ ràng: điểm mock có thể cao cho sản phẩm sai và không nên dùng để kết luận. Bước tiếp theo của tôi là chạy đúng 5 query mà nhóm thống nhất với `LocalEmbedder`, đồng thời dùng filter `brand`, `color`, `category_group` hoặc `customer_role` khi câu hỏi đã nêu rõ điều kiện.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua việc tự so sánh, tôi rút ra rằng chất lượng retrieval không chỉ do vector store mà còn phụ thuộc mạnh vào dữ liệu, metadata và cách tạo chunk. Một chiến lược phù hợp domain như giữ heading sản phẩm có thể làm chunk dễ đọc hơn, nhưng không thể cứu một embedding không có ngữ nghĩa. Tôi cũng học được rằng phải xem trực tiếp top-3 và failure case, thay vì tin vào score cao nhất.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 2 / 10 |
| **Tổng phần cá nhân** | **52 / 60** |
