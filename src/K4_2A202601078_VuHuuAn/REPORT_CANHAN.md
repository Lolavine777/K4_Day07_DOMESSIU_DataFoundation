# Báo cáo cá nhân - Vũ Hữu An

**Mã sinh viên:** 2A202601078

**Nhóm:** ĐỘ MESSIU

## Implementation

Package này pass toàn bộ 42 bài kiểm thử chung.

Chiến lược cá nhân là `HeadingChunker`, chia theo heading Markdown, gộp section nhỏ và loại footer nguồn để giảm nhiễu.

Package có cả `BGEM3Embedder` và `LocalEmbedder` cho benchmark semantic.

## Benchmark chung

Benchmark dùng corpus ASOS, năm golden queries, `BAAI/bge-m3`, `top_k=3` và metadata filter ở query outerwear.

Kết quả: 4/5 query đạt answer có evidence đúng.

Q1 là failure case vì `Dry clean only` và `100% Cotton` nằm ở hai section khác nhau và không cùng xuất hiện trong top-3.

Các query còn lại trả lời đúng giá, faux fur, hai lựa chọn halterneck beachwear và maternity fit.

**Điểm competition hiện tại:** 8/10.

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
