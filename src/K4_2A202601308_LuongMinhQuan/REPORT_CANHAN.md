# Báo cáo cá nhân - Lương Minh Quân

**Mã sinh viên:** 2A202601308

**Nhóm:** ĐỘ MESSIU

## Implementation

Package này pass toàn bộ 42 bài kiểm thử chung.

Chiến lược cá nhân là `FixedSizeChunker(chunk_size=500, overlap=50)`, tạo các cửa sổ kích thước ổn định và giữ ngữ cảnh ở biên bằng overlap.

`EmbeddingStore` lọc metadata trước khi xếp hạng similarity, còn `KnowledgeBaseAgent` dựng context có source ID để truy vết.

## Benchmark chung

Benchmark chính thức dùng cùng corpus ASOS, cùng năm golden queries, `BAAI/bge-m3`, `top_k=3` và metadata filter ở query outerwear.

Kết quả: query 2, 3, 4 và 5 có evidence đúng; query 1 miss vì fixed-size boundary tách `Dry clean only` khỏi `100% Cotton`.

**Điểm competition hiện tại:** 8/10.

## Similarity reflection

Cosine similarity giúp so sánh hướng ngữ nghĩa, nhưng không thay thế metadata cho giá, care hoặc thuộc tính số.

Overlap cải thiện ngữ cảnh ở ranh giới nhưng không bảo đảm hai section xa nhau cùng vào một chunk.

## Tự đánh giá

| Hạng mục | Điểm |
|---|---:|
| Warm-up | 5/5 |
| My Approach | 10/10 |
| Core tests | 30/30 |
| Similarity predictions | 5/5 |
| Competition | 8/10 |
| **Tổng** | **58/60** |

Evidence benchmark chung được lưu tại `benchmark/team_results.json` và `benchmark/team_review.json`.
