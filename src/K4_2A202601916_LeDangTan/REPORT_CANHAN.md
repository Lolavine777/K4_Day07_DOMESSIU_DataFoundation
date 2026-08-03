# Báo cáo cá nhân - Lê Đăng Tấn

**Mã sinh viên:** 2A202601916

**Nhóm:** ĐỘ MESSIU

## Implementation

Package này pass toàn bộ 42 bài kiểm thử chung.

Chiến lược cá nhân là `PolicySectionChunker(chunk_size=500)`, nhận diện heading và clause trước khi dùng recursive fallback.

Chiến lược giữ nhãn section cùng nội dung, phù hợp với product details, care, material và features.

## Benchmark chung

Benchmark chính thức dùng corpus ASOS, năm golden queries, `BAAI/bge-m3`, `top_k=3` và metadata filter ở query outerwear.

Kết quả: cả 5 query đều đạt TOP-1 và agent answer có đủ evidence trong context.

Điểm mạnh là section-level grounding rõ ràng, đặc biệt với câu hỏi care/material và maternity fit.

Đánh đổi là strategy tạo 179 chunk, cao hơn Recursive 500, nên chi phí embedding lớn hơn.

**Điểm competition hiện tại:** 10/10.

## Tự đánh giá

| Hạng mục | Điểm |
|---|---:|
| Warm-up | 5/5 |
| My Approach | 10/10 |
| Core tests | 30/30 |
| Similarity predictions | 5/5 |
| Competition | 10/10 |
| **Tổng** | **60/60** |

Evidence benchmark chung được lưu tại `benchmark/team_results.json` và `benchmark/team_review.json`.
