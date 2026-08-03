# Báo cáo nhóm ĐỘ MESSIU - Lab 7: Embedding & Vector Store

**Nhóm:** ĐỘ MESSIU

**Ngày hoàn thiện:** 2026-08-03

| Thành viên | Mã sinh viên |
|---|---|
| Nguyễn Đăng Long | 2A202601934 |
| Đào Minh Chiến | 2A202601184 |
| Lương Minh Quân | 2A202601308 |
| Lê Đăng Tấn | 2A202601916 |
| Vũ Hữu An | 2A202601078 |

## Câu chuyện của dự án

Nhóm chọn bài toán tìm kiếm và tư vấn sản phẩm thời trang trên dữ liệu ASOS.

Một câu hỏi mua sắm thường kết hợp nhiều loại thông tin như loại sản phẩm, màu, giá, chất liệu, cách bảo quản và đối tượng sử dụng.

Thông tin trả lời không phải lúc nào cũng nằm trong cùng một đoạn văn, nên đây là ngữ cảnh phù hợp để quan sát ảnh hưởng của chunking, embedding, metadata filter và cách dựng context cho agent.

Nhóm giữ nguyên một corpus, một embedding model và năm golden queries cho tất cả thành viên.

Điểm khác biệt duy nhất trong bảng so sánh chính là chiến lược chunking.

Sau lượt đo ban đầu bằng mock, word-frequency và MiniLM, nhóm chạy lại toàn bộ năm chiến lược bằng `BAAI/bge-m3` để loại bỏ sai lệch do embedding backend.

## 1. Chất lượng bộ tài liệu - 10/10

### Phạm vi

Corpus gồm 20 product listing ASOS thuộc các nhóm dress, outerwear, top, underwear, beachwear và denim.

Tổng dung lượng văn bản là 41,343 ký tự, trung bình 2,067 ký tự cho mỗi tài liệu.

Mỗi file giữ cấu trúc Markdown gồm product details, features, size, care, material và brand.

### Nguồn và quyền sử dụng

Dữ liệu được lấy từ dataset công khai `UniqueData/asos-e-commerce-dataset` và giữ URL sản phẩm ASOS gốc cho từng record.

`data/k4_asos_products/sources.csv` ánh xạ một-một giữa 20 file, `doc_id`, URL, ngày lấy dữ liệu, phiên bản và căn cứ sử dụng.

License được ghi là `CC-BY-NC-ND-4.0` theo dataset nguồn.

Corpus không chứa credential, dữ liệu đăng nhập hay dữ liệu cá nhân của người dùng.

### Metadata schema

| Trường | Kiểu | Ví dụ | Vai trò retrieval |
|---|---|---|---|
| `doc_id` | string | `asos-daisy-street-...` | Truy vết document gốc và deduplicate kết quả |
| `source_url` | URL | Trang sản phẩm ASOS | Citation và kiểm chứng nguồn |
| `retrieved_at` | date | `2026-08-03` | Theo dõi thời điểm thu thập |
| `category_group` | string | `outerwear` | Pre-filter theo nhóm sản phẩm |
| `brand` | string | `adidas-originals` | Lọc và giải thích theo thương hiệu |
| `price_gbp` | number | `110.00` | Truy vấn giá và điều kiện số |
| `color` | string | `black` | Facet màu sắc |
| `fit_line` | string | `maternity` | Nhận diện đối tượng và dòng sản phẩm |
| `customer_role` | string | `buyer` | Filter bắt buộc của biến thể K4 |
| `language`, `region` | string | `en`, `uk` | Kiểm soát ngôn ngữ và thị trường |

## 2. Thiết kế chiến lược - 15/15

### Baseline

Nhóm chạy `ChunkingStrategyComparator` trên ba sản phẩm đại diện.

| Tài liệu | FixedSize | Sentence | Recursive |
|---|---:|---:|---:|
| adidas Originals bralet | 10 chunk, TB 195.6 | 2 chunk, TB 751.5 | 13 chunk, TB 114.4 |
| Amy Lynn chainmail dress | 10 chunk, TB 194.3 | 2 chunk, TB 745.0 | 12 chunk, TB 122.9 |
| ASOS DESIGN cowl-neck blouse | 10 chunk, TB 188.9 | 2 chunk, TB 718.0 | 11 chunk, TB 129.4 |

Fixed-size tạo kích thước tương đối đều nhưng có thể cắt ngang một dòng size hoặc tách care khỏi material.

Sentence chunking giữ câu hoàn chỉnh nhưng tạo chunk quá dài vì phần brand description thường chỉ có ít dấu kết câu.

Recursive chunking tạo nhiều chunk ngắn và tôn trọng ranh giới văn bản hơn, nhưng context liên quan có thể bị phân tán.

### Năm chiến lược cá nhân

#### Vũ Hữu An - HeadingChunker

Chiến lược tách theo heading Markdown, gộp các section nhỏ tới khoảng 400 ký tự và loại footer nguồn/license khỏi nội dung embedding.

Điểm mạnh là giảm boilerplate và giữ các mục product details, care, material có ranh giới rõ ràng.

Điểm yếu là Q1 cần đồng thời care và material ở hai section khác nhau, khiến document adidas không vào top-3.

#### Đào Minh Chiến - RecursiveChunker 500

Chiến lược ưu tiên ranh giới đoạn, dòng, câu và khoảng trắng trước khi hard split.

Chunk 500 ký tự đủ rộng để giữ nhiều thuộc tính liên quan mà vẫn tránh một context quá dài.

Trong lượt đo chung, đây là chiến lược đơn giản nhất đạt đủ 5/5 query.

#### Lương Minh Quân - FixedSize 500, overlap 50

Chiến lược dùng cửa sổ cố định để bảo đảm kích thước ổn định và overlap để giảm mất ngữ cảnh ở biên chunk.

Nó hoạt động tốt cho giá, outerwear, beachwear và maternity, nhưng Q1 vẫn miss vì care và material không được biểu diễn như một đơn vị cấu trúc.

#### Lê Đăng Tấn - PolicySectionChunker

Chiến lược nhận diện heading, mục và điều khoản đánh số, sau đó chỉ dùng recursive fallback khi section quá dài.

Trên product listing Markdown, nó tạo 179 chunk nhỏ và đưa đúng evidence lên top-1 cho cả năm query.

Số chunk lớn làm tăng chi phí embedding, nhưng đổi lại độ chi tiết và khả năng truy vết tốt.

#### Nguyễn Đăng Long - HeadingRecursiveChunker

Chiến lược giữ toàn bộ heading hierarchy trong mỗi child chunk và dùng recursive fallback cho section dài.

Pipeline agent deduplicate theo document rồi mở rộng full grounded product context, nhờ vậy câu hỏi đa-section và multi-product không bị thiếu evidence.

Chiến lược đạt đủ 5/5 query và tạo ra 192 chunk.

### So sánh chính thức

Tất cả kết quả dưới đây được tái lập bằng cùng corpus, cùng 5 query, `top_k=3` và `BAAI/bge-m3`.

| Thành viên | Chiến lược | Số chunk | Điểm | Điểm mạnh | Failure case |
|---|---|---:|---:|---|---|
| Vũ Hữu An | HeadingChunker | 71 | 8/10 | Ít chunk, bỏ boilerplate | Q1 care và material tách section |
| Đào Minh Chiến | Recursive 500 | 76 | 10/10 | Cân bằng context và chi phí | Có thể kém ổn định với section rất dài |
| Lương Minh Quân | Fixed 500, overlap 50 | 77 | 8/10 | Đơn giản, kích thước ổn định | Q1 bị cắt theo vị trí ký tự |
| Lê Đăng Tấn | PolicySectionChunker | 179 | 10/10 | Evidence chi tiết, top-1 tốt | Chi phí embedding cao hơn |
| Nguyễn Đăng Long | HeadingRecursiveChunker | 192 | 10/10 | Giữ hierarchy, context agent đầy đủ | Nhiều chunk và cần document deduplication |

Không có một chiến lược duy nhất tốt nhất trong mọi điều kiện.

Recursive 500 đạt 10/10 với chỉ 76 chunk nên có tỷ lệ chất lượng trên chi phí tốt nhất trong corpus hiện tại.

PolicySection và HeadingRecursive phù hợp hơn khi ưu tiên khả năng truy vết, câu hỏi đa-section và mở rộng hệ thống về sau.

## 3. Golden queries và chất lượng truy xuất - 10/10

| # | Query | Gold answer | Evidence |
|---|---|---|---|
| 1 | Sản phẩm nào phải dry clean only và làm từ gì? | adidas Originals bralet, 100% Cotton | `Look After Me` và `About Me` |
| 2 | Đầm ASOS EDITION satin maxi giá bao nhiêu? | GBP 110.00 | Front matter và Product details |
| 3 | Trong outerwear, coat nào làm từ faux fur? | Daisy Street faux fur coat | Filter `category_group=outerwear`, mục `About Me` |
| 4 | Món black halterneck đi biển có lựa chọn nào? | Hollister bikini top và Public Desire beach dress | Color, category và features của hai document |
| 5 | Có maternity dress không và fit thế nào? | ASOS DESIGN maternity dress, bump-to-baby, wrap front, shirred back | `Dac diem` và fit metadata |

Q3 dùng metadata filter trước khi xếp hạng.

Filter loại các sản phẩm ngoài `outerwear`, giữ đủ top-k trong tập ứng viên hợp lệ và đưa Daisy Street lên top-1 cho cả năm strategy.

Q4 cho thấy top-k theo chunk có thể bị một document chiếm nhiều vị trí.

Nhóm giải quyết vấn đề ở tầng agent bằng cách lấy nhiều candidate, deduplicate theo `doc_id`, rồi dựng context từ ba document khác nhau.

Kết quả generative được lưu trong `benchmark/team_results.json`.

Mỗi câu trả lời được so sánh với gold answer và kết quả review nằm trong `benchmark/team_review.json`.

Ba chiến lược đạt 10/10, hai chiến lược đạt 8/10 và team có ít nhất một chiến lược trả lời đúng cho cả năm golden queries.

## 4. Demo và bài học nhóm - 5/5

### Luồng demo

1. Mở UI và xác nhận catalog tải đủ 20 product listing.
2. Gửi query `Tìm blazer màu trắng` để quan sát pre-guardrail, query rewrite, BGE-M3 retrieval và cosine similarity.
3. Quan sát answer được stream theo nhiều delta thay vì đợi toàn bộ response.
4. Kiểm tra citation gồm `chunk_id` và `document_id` cho từng sản phẩm.
5. Gửi prompt injection để chứng minh deterministic guardrail chặn trước query-rewrite agent.
6. Chạy query outerwear để giải thích metadata pre-filter.
7. So sánh bảng năm strategy và phân tích Q1 là failure case của HeadingChunker và FixedSize.

### Bài học

Embedding model và chunking phải được đánh giá tách biệt.

Mock embedding hữu ích cho unit test nhưng không thể dùng để kết luận chất lượng retrieval.

Dense embedding nhận biết chủ đề tốt nhưng không đáng tin cậy cho điều kiện số như giá dưới một ngưỡng, nên metadata và structured filters vẫn cần thiết.

Top-k chunk không đồng nghĩa top-k document.

Document deduplication và context expansion là bước quan trọng trước generative LLM.

Guardrail phải chạy trước query rewrite để input không an toàn không bao giờ được gửi đến model.

### Nếu làm lại

Nhóm sẽ chuẩn hóa thêm metadata cho care, fabric, sizes và price range ngay từ bước ingest.

Hybrid retrieval kết hợp dense vector, lexical signals và metadata filter sẽ phù hợp hơn pure vector search cho product catalog.

Nhóm cũng sẽ cache document embeddings theo model và strategy để giảm thời gian benchmark lặp lại.

## Evidence và lệnh tái lập

```bash
.venv/bin/python -m pytest tests -q
.venv/bin/python -m pytest ui/test_ui.py benchmark/test_team_benchmark.py -q
.venv/bin/python -m benchmark.run_team_benchmark
```

Các artifact chính:

- `data/k4_asos_products/sources.csv`
- `benchmark/queries.py`
- `benchmark/team_results.json`
- `benchmark/team_review.json`
- `ui/`
- `src/K4_<MSSV>_<HoTen>/`

## Tự đánh giá phần nhóm

| Tiêu chí | Điểm |
|---|---:|
| Chất lượng bộ tài liệu | 10/10 |
| Thiết kế chiến lược | 15/15 |
| Chất lượng truy xuất | 10/10 |
| Demo và bài học nhóm | 5/5 |
| **Tổng** | **40/40** |
