# Evaluation results

Fixed evaluation set: 20 tickets (2 per category). mock_* rows are rule-based fixture results, not real LLM performance.

| System | Correct | Accuracy |
|---|---|---|
| keyword_baseline | 13/20 | 65% |
| tfidf_nearest | 12/20 | 60% |
| mock_v1 | 17/20 | 85% |
| mock_v2 | 13/20 | 65% |

## Errors for mock_v2

- T019: expected `order_change_cancel`, got `general_inquiry` - Could you swap the sneakers in order 58320 for size 43 instead of 42? It hasn't shipped yet.
- T029: expected `delivery_problem`, got `general_inquiry` - Delivery says completed yesterday, but I never received anything and no one rang my bell.
- T030: expected `delivery_problem`, got `general_inquiry` - My shipment is over a week late and the promised delivery date has passed twice.
- T039: expected `refund_request`, got `general_inquiry` - I sent back my jacket three weeks ago and the money has still not been returned to me.
- T049: expected `payment_issue`, got `general_inquiry` - I see two identical charges on my card statement for one purchase.
- T070: expected `account_access`, got `general_inquiry` - My registration keeps failing at the confirm email step and I never get the confirmation link.
- T090: expected `product_complaint`, got `general_inquiry` - The shoes arrived with the sole coming off. This product is clearly defective.

## Confusion matrix for mock_v2 (rows = expected, columns = predicted)

| expected \ predicted | order_tr | order_ch | delivery | refund_r | payment_ | invoice_ | account_ | account_ | product_ | general_ |
|---|---|---|---|---|---|---|---|---|---|---|
| order_tracking | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| order_change_cancel | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| delivery_problem | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| refund_request | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| payment_issue | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| invoice_billing | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| account_access | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| account_update | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| product_complaint | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| general_inquiry | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

## Sample summaries (mock_v2)

- T009: Customer message: Please help me track my order number 61007.
- T010: Customer message: Has my order been dispatched yet.
- T019: Customer message: Could you swap the sneakers in order 58320 for size 43 instead of 42.
- T020: Customer message: I want to cancel my order placed two hours ago because I changed my mind.
