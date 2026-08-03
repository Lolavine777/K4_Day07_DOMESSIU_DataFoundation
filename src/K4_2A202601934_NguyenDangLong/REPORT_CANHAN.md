# Báo cáo cá nhân - Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đăng Long

**Mã sinh viên:** 2A202601934

**Nhóm:** K4

## 1. Warm-up - 5/5

Cosine similarity đo góc giữa hai vector và tập trung vào hướng biểu diễn ngữ nghĩa.

Giá trị gần 1 thể hiện hai văn bản gần nhau về ngữ nghĩa, còn giá trị thấp thể hiện mức liên quan yếu hơn.

Với tài liệu 10,000 ký tự, `chunk_size=500` và `overlap=50`, bước dịch là 450 và số chunk là `ceil((10000 - 50) / 450) = 23`.

Khi overlap tăng lên 100, bước dịch là 400 và số chunk tăng thành `ceil((10000 - 100) / 400) = 25`.

Overlap bảo vệ ngữ cảnh ở biên chunk nhưng làm tăng chi phí embedding và khả năng kết quả trùng lặp.

## 2. My Approach - 10/10

`SentenceChunker` dùng regex kết thúc câu, bỏ phần rỗng và gom số câu theo cấu hình.

`RecursiveChunker` ưu tiên separator theo cấu trúc đoạn, dòng, câu và khoảng trắng, sau đó mới hard-split.

Chiến lược riêng `HeadingRecursiveChunker` giữ toàn bộ heading path trong child chunk và dùng recursive fallback cho section dài.

`EmbeddingStore` sao chép metadata, tạo chunk ID duy nhất, embed query một lần và xếp hạng bằng cosine trên vector đã chuẩn hóa.

`search_with_filter` lọc metadata trước khi xếp hạng và `delete_document` xóa toàn bộ chunk theo `doc_id`.

`KnowledgeBaseAgent` đưa top-k context cùng source ID vào prompt và không gọi LLM khi store không có context.

Agent benchmark deduplicate theo document trước khi dựng context để tránh top-k chứa ba chunk của cùng một sản phẩm.

## 3. Core implementation - 30/30

Lệnh kiểm thử package cá nhân:

```bash
LAB_SOLUTION_PACKAGE=src.K4_2A202601934_NguyenDangLong .venv/bin/python -m pytest tests -q
```

Kết quả xác minh: `42 passed`.

## 4. Similarity predictions - 5/5

Các số liệu được tái lập bằng `BAAI/bge-m3` và lưu trong `similarity_results.json`.

Ngưỡng phân tích được dùng là 0.75 cho bộ ví dụ này.

| Cặp | Dự đoán | Cosine | Kết luận |
|---|---:|---:|---|
| Hai mô tả black dress nhiều size | Cao | 0.894049 | Đúng |
| Hai mô tả chất liệu cotton | Cao | 0.825571 | Đúng |
| Black jacket và bright red jacket | Thấp | 0.806858 | Sai |
| Dry clean và machine wash | Thấp | 0.679024 | Đúng |
| adidas Originals và Calvin Klein | Thấp | 0.723282 | Đúng |

Kết quả bất ngờ nhất là hai jacket khác màu vẫn có similarity cao vì phần lớn cấu trúc và danh từ giống nhau.

Điều này cho thấy dense embedding có thể ưu tiên chủ thể chung hơn thuộc tính phân biệt, nên metadata filter hoặc hybrid retrieval vẫn hữu ích.

## 5. Competition results - 10/10

Benchmark dùng đúng năm query trong `benchmark/queries.py`, `HeadingChunker`, `chunk_size=400`, `top_k=3` và BGE-M3.

Cả năm query đều truy xuất đúng expected document ở top-1.

| # | Retrieval | Agent answer verification |
|---|---|---|
| 1 | adidas Originals bralet - TOP-1 | Đúng sản phẩm, dry clean only và 100% Cotton |
| 2 | ASOS EDITION satin maxi dress - TOP-1 | Đúng GBP 110.00 |
| 3 | Daisy Street faux fur coat - TOP-1 | Đúng sản phẩm faux fur |
| 4 | Hollister halterneck bikini - TOP-1 | Đúng cả Hollister và Public Desire beach dress |
| 5 | ASOS DESIGN maternity dress - TOP-1 | Đúng bump-to-baby, wrap front và shirred stretch back |

Generated answers và gold answers nằm cạnh nhau trong `agent_benchmark_results.json`.

Từng answer đã được kiểm tra thủ công và đánh dấu `human_verified: true`.

## Tự đánh giá

| Tiêu chí | Điểm |
|---|---:|
| Warm-up | 5/5 |
| My Approach | 10/10 |
| Core implementation | 30/30 |
| Similarity predictions | 5/5 |
| Competition results | 10/10 |
| **Tổng cá nhân** | **60/60** |
