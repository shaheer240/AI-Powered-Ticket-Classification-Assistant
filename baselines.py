from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASIC_KEYWORDS = {
    "order_tracking": ["track", "status", "where is"],
    "order_change_cancel": ["cancel", "change my order", "modify"],
    "delivery_problem": ["delivered", "courier", "late"],
    "refund_request": ["refund", "money back"],
    "payment_issue": ["payment", "charged", "declined"],
    "invoice_billing": ["invoice", "receipt"],
    "account_access": ["password", "log in", "sign in"],
    "account_update": ["update my", "delete my account", "profile"],
    "product_complaint": ["broken", "damaged", "defective"],
    "general_inquiry": ["do you", "hours"],
}


def keyword_baseline(text):
    text = text.lower()
    best, best_hits = "general_inquiry", 0
    for category, words in BASIC_KEYWORDS.items():
        hits = sum(1 for w in words if w in text)
        if hits > best_hits:
            best, best_hits = category, hits
    return best


class TfidfNearest:
    # finds the most similar development ticket and copies its category
    def __init__(self, texts, labels):
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(texts)
        self.labels = list(labels)

    def predict(self, text):
        sims = cosine_similarity(self.vectorizer.transform([text]), self.matrix)[0]
        return self.labels[sims.argmax()]
