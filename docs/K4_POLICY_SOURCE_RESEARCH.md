# K4 policy-corpus source research

**Scope.** Candidate public, first-party sources for the K4 e-commerce
policy/customer-support corpus.  All are published by Etsy, so terminology and
policy context stay consistent across the 5–10 resulting Markdown documents.
The proposed corpus text must be a concise Vietnamese paraphrase, not a copied
policy.  Source pages were retrieved on **2026-08-03**.

Each eventual corpus file should preserve at least this front matter:
`customer_role`, `policy_area`, `source_url`, `retrieved_at: 2026-08-03`, and
`document_version` below.

| Suggested ID | Official document | Role | Policy area | Version/date | Source |
|---|---|---|---|---|---|
| `etsy_buyer_policy` | Buyer Policy | buyer | buyer-rights-and-order-problems | `last-updated-2026-06-09` | [Etsy Buyer Policy](https://www.etsy.com/legal/buyers/) |
| `etsy_cases` | Cases Policy | both | disputes-and-refunds | `effective-2026-07-09` | [Etsy Cases Policy](https://www.etsy.com/legal/policy/cases-policy/243306189901) |
| `etsy_seller_policy` | Seller Policy | seller | seller-listing-and-account | `effective-2026-07-09` | [Etsy Seller Policy](https://www.etsy.com/legal/sellers/) |
| `etsy_shipping` | Shipping Policy | seller | fulfilment-and-shipping | `effective-2026-07-09` | [Etsy Shipping Policy](https://www.etsy.com/legal/shipping/) |
| `etsy_payments` | Etsy Payments Policy | seller | payments-and-disbursements | `web-accessed-2026-08-03` | [Etsy Payments Policy](https://www.etsy.com/legal/etsy-payments/) |
| `etsy_fees` | Fees & Payments Policy | seller | fees-and-taxes | `last-updated-2026-02-13` | [Etsy Fees & Payments Policy](https://www.etsy.com/legal/fees/) |
| `etsy_off_platform` | Off-Platform Transactions | both | fraud-prevention-and-payment-safety | `last-updated-2026-06-09` | [Etsy Off-Platform Transactions](https://www.etsy.com/legal/policy/off-platform-transactions/1254654515806) |
| `etsy_privacy` | Privacy Policy | both | privacy-and-data-use | `last-updated-2025-11-20` | [Etsy Privacy Policy](https://www.etsy.com/legal/privacy) |
| `etsy_cancellation` | How to Cancel a Sale | seller | cancellation-and-refunds | `web-accessed-2026-08-03` | [Etsy Help: How to Cancel a Sale](https://help.etsy.com/hc/en-us/articles/115015587347-How-to-Cancel-a-Sale) |

## Paraphrased facts for the corpus and benchmark

### `etsy_buyer_policy`

- Before purchase, a buyer must read the listing and shop policies, submit
  appropriate payment, and give accurate delivery information.
- Sellers set their own processing times, shipping methods, and shop policies.
- A qualifying order problem can lead to a refund when an item is absent, late,
  damaged, or materially different from its description; exclusions include
  off-platform/standalone-PayPal transactions and accurately described items
  that merely disappoint the buyer.
- Only the seller can cancel a transaction; a buyer can request cancellation
  through Messages.

### `etsy_cases`

- The buyer first uses **Help with Order** to contact the seller.  If no
  resolution is reached within 48 hours, the buyer may open an Etsy case.
- A case needs an eligible order/timeframe and a problem such as non-delivery,
  late delivery, damage, or a mismatch with the listing.
- A buyer cannot pursue an Etsy case and a card chargeback for the same dispute;
  a subsequent chargeback closes the Etsy case.

### `etsy_seller_policy`

- A seller may list goods that they made, designed, handpicked, or sourced,
  subject to Etsy's marketplace rules.
- Listings must accurately state how and by whom an item was made and its ship
  origin; relevant production partners must be disclosed.
- A seller must disclose AI-created items in the relevant listing and use their
  own images/video subject to the stated exceptions.

### `etsy_shipping`

- Sellers remain responsible for packing and shipping sold goods even when a
  fulfilment service is used.
- They must provide a correct ship-from address, state shipping costs and
  processing time, and ship to the checkout address.
- For U.S.-bound orders, the policy requires Delivery Duty Paid (DDP), with a
  narrow exception only when DDP is genuinely unavailable and the buyer has
  explicitly confirmed the estimated extra charge.
- Proof of shipping must show shipment to the buyer's Etsy checkout address.

### `etsy_payments`

- Etsy Payments lets sellers accept specified methods (for example cards and,
  where available, PayPal and bank-transfer services) and receive the funds in
  a seller payment account before disbursement.
- The seller authorises Etsy to charge its saved card for amounts owed where the
  available payment-account funds are insufficient.
- The sales contract is between the seller and buyer; Etsy acts as the seller's
  payment collection agent for the defined payment role.

### `etsy_fees`

- Etsy's stated listing fee is USD 0.20 per listing creation or renewal; Etsy
  listings expire after four months.
- The stated transaction fee is 6.5% of the displayed listing price plus
  shipping and gift-wrapping charges.
- A seller with insufficient payment-account funds must settle owed fees within
  15 days of the monthly statement date; Etsy may suspend selling privileges
  while the balance remains unpaid.

### `etsy_off_platform`

- Communications and transactions moved off Etsy are prohibited because the
  platform's payment, purchase-protection, and case protections do not cover
  them.
- An Etsy-initiated transaction cannot be completed elsewhere, including by
  seeking extra post-checkout payment for shipping, returns, import duties,
  tax, customs, or another unquoted fee.
- Sellers may not change a post-sale price to avoid transaction fees or falsely
  state the item's location.

### `etsy_privacy`

- The policy covers registered buyers and sellers, guests, and other visitors
  using Etsy's sites and services.
- Etsy says it shares certain account and usage data with group companies for
  operations including identity checks, fraud prevention, payment processing,
  customer support, and compliance.
- Sellers can receive aggregate buyer-use information; some seller information,
  such as business name or shop location, may be publicly displayed.

### `etsy_cancellation`

- Only the seller can cancel a completed sale; the buyer receives a full refund
  when the transaction is cancelled.
- Sellers should notify the buyer through Etsy Messages before cancelling when
  they cannot complete the transaction.
- A cancellation can take up to 48 hours to fully process; an Etsy Payments
  refund/cancellation normally returns the related listing and transaction
  fees, while a non-Etsy-Payments refund must use that original payment method.

## Benchmark coverage suggested by these sources

Use five short questions whose gold answers stay inside this corpus:

1. **Buyer, cases:** What must a buyer do before opening an Etsy case?  (Use
   `customer_role: buyer`.)
2. **Seller, shipping:** Which address and customs/DDP duties does a seller
   have for a U.S.-bound shipment?  (Use `customer_role: seller`.)
3. **Seller, fees:** What is the stated listing fee and how long does a listing
   last?  (Use `customer_role: seller`.)
4. **Both, off-platform:** Why must an Etsy order not be completed off the
   platform?  (No role filter or `both`.)
5. **Seller, cancellation:** Who can cancel a sale and what happens to the
   buyer?  (Use `customer_role: seller`.)

All values above are policy facts as viewed on 2026-08-03.  Before submission,
re-check the source URLs and update `document_version` if Etsy changes a page.
