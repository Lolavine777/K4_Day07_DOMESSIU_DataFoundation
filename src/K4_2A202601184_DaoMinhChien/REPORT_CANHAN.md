# Báo cáo cá nhân - Đào Minh Chiến

**Mã sinh viên:** 2A202601184

**Nhóm:** ĐỘ MESSIU

## Implementation

Package này pass toàn bộ 42 bài kiểm thử chung.

Chiến lược cá nhân là `RecursiveChunker(chunk_size=500)`, ưu tiên paragraph, dòng, câu và khoảng trắng trước khi hard split.

Metadata được lọc trước khi xếp hạng, và vector từ vựng chuẩn hóa được dùng cho implementation evaluation riêng.

## Benchmark chung

Benchmark chính thức dùng corpus ASOS, năm golden queries, `BAAI/bge-m3`, `top_k=3` và metadata filter ở query outerwear.

Kết quả: cả 5 query đều có document và answer evidence đúng.

Các câu trả lời bao phủ dry-clean/material, giá ASOS EDITION, Daisy Street faux fur, hai lựa chọn black halterneck và maternity fit.

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
