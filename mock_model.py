import json
import re

RULES_V1 = {
    "order_tracking": ["track", "status", "where is", "transit"],
    "order_change_cancel": ["cancel", "change", "modify", "remove"],
    "delivery_problem": ["deliver", "courier", "late", "driver", "missing"],
    "refund_request": ["refund", "money back", "return"],
    "payment_issue": ["payment", "charged", "card", "checkout", "declined"],
    "invoice_billing": ["invoice", "receipt", "vat", "billing"],
    "account_access": ["password", "log in", "login", "sign in", "locked", "verification"],
    "account_update": ["update", "delete", "unsubscribe", "profile", "account"],
    "product_complaint": ["broken", "damaged", "quality", "stopped working"],
    "general_inquiry": ["do you", "what are", "hours", "contact"],
}

RULES_V2 = {
    "order_tracking": {"tracking": 2, "where is my": 3, "status of": 3, "in transit": 3,
                       "live location": 3, "shipped out": 2, "left your warehouse": 3, "track": 1},
    "order_change_cancel": {"cancel my order": 4, "cancel the whole order": 4, "cancel": 2,
                            "change the size": 3, "change the color": 3, "modify my order": 4,
                            "add one more item": 4, "remove one item": 4, "placed by mistake": 3,
                            "before it ships": 2, "before it gets packed": 2, "wrong quantity": 2},
    "delivery_problem": {"marked my parcel as delivered": 4, "delivered to the wrong": 4,
                         "days late": 3, "courier": 2, "driver": 2, "missing": 2, "depot": 3,
                         "delivery person": 3, "arrive on": 2, "left my package": 3},
    "refund_request": {"refund": 3, "money back": 3, "sending it back": 2, "returned the": 2,
                       "store credit": 2},
    "payment_issue": {"payment": 2, "charged twice": 4, "declined": 3, "checkout": 2,
                      "pay now": 3, "apple pay": 3, "credit card": 1, "discount code": 2,
                      "cash on delivery": 3},
    "invoice_billing": {"invoice": 4, "receipt": 3, "vat": 3, "billing": 3, "bill": 1,
                        "tax number": 3, "line item": 3},
    "account_access": {"password": 3, "can't log in": 4, "unable to sign in": 4, "login": 3,
                       "locked": 3, "two-factor": 3, "verification code": 1,
                       "email already in use": 3, "reset": 1},
    "account_update": {"update my": 3, "change the email address": 4, "change my account": 4,
                       "delete my account": 4, "unsubscribe": 4, "profile": 3, "my account": 1,
                       "saved credit card": 3, "newsletter": 2},
    "product_complaint": {"broken": 3, "damaged": 3, "quality": 3, "stopped working": 3,
                          "crackling": 3, "misleading": 3, "looks nothing like": 4,
                          "unhappy": 2, "missing the": 1, "shrank": 3, "cracked": 3},
    "general_inquiry": {"do you offer": 3, "do you have": 3, "do you ship": 3,
                        "opening hours": 3, "hours": 2, "contact a human": 3,
                        "reach your support": 3, "back in stock": 3, "physical store": 3,
                        "discount program": 3, "phone number or email": 3, "what are your": 2},
}

GREETING = re.compile(r"^(hi|hello|hey|dear [^,]+)[,!.]?\s+", re.IGNORECASE)


def classify_v1(text):
    text = text.lower()
    best, best_score = "general_inquiry", 0
    for category, words in RULES_V1.items():
        score = sum(1 for w in words if w in text)
        if score > best_score:
            best, best_score = category, score
    return best


def classify_v2(text):
    text = text.lower()
    best, best_score = "general_inquiry", 0
    for category, phrases in RULES_V2.items():
        score = sum(weight for phrase, weight in phrases.items() if phrase in text)
        if score > best_score:
            best, best_score = category, score
    return best


def make_summary(ticket):
    text = GREETING.sub("", " ".join(ticket.split()))
    first = re.split(r"(?<=[.!?])\s+", text)[0]
    words = first.rstrip(".!?").split()[:20]
    return "Customer message: " + " ".join(words) + "."


def run_mock(ticket, version):
    classify = classify_v1 if version == "v1" else classify_v2
    return json.dumps({"category": classify(ticket), "summary": make_summary(ticket)})
