import re
from typing import Literal, Optional

from pydantic import BaseModel, field_validator

CATEGORY_INFO = {
    "order_tracking": ("Customer wants to know where an order is or its shipping status.",
                       "Where is my package? Tracking has not updated."),
    "order_change_cancel": ("Customer wants to change or cancel an order that is not delivered yet.",
                            "Please cancel order 52944."),
    "delivery_problem": ("Something went wrong with the delivery itself: late, lost or wrong place.",
                         "The courier says delivered but nothing arrived."),
    "refund_request": ("Customer asks for a refund or asks about a refund that has not arrived.",
                       "I returned the shoes and still have no refund."),
    "payment_issue": ("Problems paying at checkout or being charged incorrectly.",
                      "I was charged twice for the same order."),
    "invoice_billing": ("Requests about invoices, receipts or billing details.",
                        "Please send me the invoice for order 44872."),
    "account_access": ("Customer cannot log in, reset a password or register.",
                       "The password reset email never arrives."),
    "account_update": ("Customer wants to change or delete account details and settings.",
                       "Please update my phone number."),
    "product_complaint": ("The product is damaged, defective or not as described.",
                          "The kettle leaks from the bottom."),
    "general_inquiry": ("General questions about the store, shipping rules or contacting support.",
                        "What are your support opening hours?"),
}

CATEGORIES = list(CATEGORY_INFO)
MAX_SUMMARY_WORDS = 30

ACTION_CLAIM = re.compile(
    r"\b(we|support|the agent|our team)\s+(have\s+|has\s+|'ve\s+)?"
    r"(refunded|cancell?ed|processed|updated|resolved|reset|fixed)\b",
    re.IGNORECASE,
)


class TicketRequest(BaseModel):
    ticket: str
    prompt_version: Literal["v1", "v2"] = "v2"
    simulate: Optional[Literal["backend_down", "bad_output"]] = None


class TicketResult(BaseModel):
    category: str
    summary: str

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, value):
        value = value.strip().lower()
        if value not in CATEGORIES:
            raise ValueError(f"unknown category: {value}")
        return value

    @field_validator("summary")
    @classmethod
    def summary_must_be_valid(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("summary is empty")
        if len(value.split()) > MAX_SUMMARY_WORDS:
            raise ValueError("summary is too long")
        if len(re.split(r"(?<=[.!?])\s+", value)) > 1:
            raise ValueError("summary must be one sentence")
        if ACTION_CLAIM.search(value):
            raise ValueError("summary claims an action was completed")
        return value


class AnalyzeResponse(BaseModel):
    category: str
    summary: str
    prompt_version: str
    mode: str
