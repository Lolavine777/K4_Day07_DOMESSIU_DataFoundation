"""Bộ 5 câu hỏi đánh giá (benchmark) cho corpus K4 — chính sách Etsy công khai.

Gold answer + expected_doc_ids được đối chiếu trực tiếp từ các bản tóm lược có
nguồn trong `data/k4_ecommerce/` (đổi trả, tranh chấp, giao hàng, phí, an toàn thanh toán).

Mỗi mục:
  id                : số thứ tự (1..5)
  type              : loại câu hỏi — giữ đa dạng để không hỏi 5 câu giống nhau
  query             : câu hỏi (tiếng Anh, khớp `language: en` của corpus → retrieval tốt)
  query_vi          : bản tiếng Việt để trình bày trong REPORT_NHOM
  gold_answer       : câu trả lời chuẩn, kiểm chứng được từ tài liệu
  metadata_filter   : dict truyền vào search_with_filter(), hoặc None nếu không lọc
  expected_doc_ids  : doc_id GỐC (chưa ::chunk_i) chứa thông tin trả lời — dùng chấm top-3
  evidence          : trích/căn cứ trong tài liệu (mục nào) để người chấm verify nhanh
"""

BENCHMARK = [
    {
        "id": 1,
        "type": "buyer-refund-eligibility",
        "query": "Which order problems may qualify an Etsy buyer for a refund?",
        "query_vi": "Những vấn đề đơn hàng nào có thể khiến buyer Etsy đủ điều kiện hoàn tiền?",
        "gold_answer": "Hàng không đến, đến muộn, hư hỏng hoặc khác đáng kể so với mô tả.",
        "metadata_filter": {"customer_role": "buyer"},
        "expected_doc_ids": ["etsy-buyer-policy"],
        "evidence": "etsy-buyer-policy: phần order problem đủ điều kiện hoàn tiền.",
    },
    {
        "id": 2,
        "type": "case-escalation",
        "query": "What must a buyer do before opening an Etsy case, and how long must they wait?",
        "query_vi": "Buyer phải làm gì trước khi mở Etsy case và phải chờ bao lâu?",
        "gold_answer": "Dùng Help with Order để liên hệ seller; nếu chưa giải quyết sau 48 giờ thì có thể mở case.",
        "metadata_filter": None,
        "expected_doc_ids": ["etsy-cases-policy"],
        "evidence": "etsy-cases-policy: Help with Order và mốc 48 giờ.",
    },
    {
        "id": 3,
        "type": "metadata-filter-shipping",  # câu bắt buộc dùng metadata filter
        "query": "For a US-bound Etsy order, what shipping duty requirement applies to the seller?",
        "query_vi": "Với đơn Etsy gửi tới Hoa Kỳ, seller phải đáp ứng yêu cầu nào về thuế/phí nhập khẩu?",
        "gold_answer": "Phải áp dụng Delivery Duty Paid (DDP), trừ khi DDP thật sự không khả dụng và buyer đã xác nhận khoản phụ thu ước tính.",
        "metadata_filter": {"customer_role": "seller", "policy_area": "fulfilment-and-shipping"},
        "expected_doc_ids": ["etsy-shipping-policy"],
        "evidence": "etsy-shipping-policy: quy định DDP cho đơn U.S.-bound và ngoại lệ hẹp.",
    },
    {
        "id": 4,
        "type": "seller-fees",
        "query": "What are Etsy's stated listing fee and listing duration?",
        "query_vi": "Phí listing Etsy được nêu là bao nhiêu và listing kéo dài bao lâu?",
        "gold_answer": "0,20 USD cho mỗi lần tạo hoặc gia hạn listing; listing hết hạn sau bốn tháng.",
        "metadata_filter": {"customer_role": "seller"},
        "expected_doc_ids": ["etsy-fees-policy"],
        "evidence": "etsy-fees-policy: listing fee USD 0.20 và thời hạn bốn tháng.",
    },
    {
        "id": 5,
        "type": "payment-safety",
        "query": "Why must an Etsy transaction not be completed off the platform?",
        "query_vi": "Vì sao giao dịch Etsy không được hoàn tất ngoài nền tảng?",
        "gold_answer": "Vì payment, purchase protection và case protection của Etsy không bao phủ giao dịch ngoài nền tảng.",
        "metadata_filter": None,
        "expected_doc_ids": ["etsy-off-platform-policy"],
        "evidence": "etsy-off-platform-policy: giao dịch ngoài Etsy không có các lớp bảo vệ của nền tảng.",
    },
]
