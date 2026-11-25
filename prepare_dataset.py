import sys
from pathlib import Path

import pandas as pd

from schemas import CATEGORIES, CATEGORY_INFO

ROOT = Path(__file__).parent
DATA = ROOT / "data"

# Bitext intents mapped to my 10 categories (delivery_problem has no Bitext intent)
BITEXT_MAP = {
    "track_order": "order_tracking",
    "cancel_order": "order_change_cancel", "change_order": "order_change_cancel",
    "get_refund": "refund_request", "track_refund": "refund_request",
    "payment_issue": "payment_issue", "check_payment_methods": "payment_issue",
    "check_invoice": "invoice_billing", "get_invoice": "invoice_billing",
    "recover_password": "account_access", "registration_problems": "account_access",
    "edit_account": "account_update", "delete_account": "account_update",
    "switch_account": "account_update", "newsletter_subscription": "account_update",
    "complaint": "product_complaint",
    "contact_customer_service": "general_inquiry", "contact_human_agent": "general_inquiry",
    "delivery_options": "general_inquiry", "check_refund_policy": "general_inquiry",
}


def write_categories():
    rows = [{"category": c, "meaning": m, "example": e} for c, (m, e) in CATEGORY_INFO.items()]
    pd.DataFrame(rows).to_csv(DATA / "categories.csv", index=False)


def check_tickets():
    df = pd.read_csv(DATA / "tickets.csv")
    problems = []
    if len(df) < 100:
        problems.append(f"only {len(df)} tickets, need at least 100")
    if df.id.duplicated().any():
        problems.append("duplicate ids")
    if df.ticket.duplicated().any():
        problems.append("duplicate ticket texts")
    if set(df.expected_category) != set(CATEGORIES):
        problems.append("categories in the CSV do not match the 10 defined categories")
    if (df.split == "eval").sum() < 20:
        problems.append("fewer than 20 eval tickets")

    print(f"Tickets: {len(df)}")
    print(pd.crosstab(df.expected_category, df.split))
    print("Problems:", problems or "none")
    return not problems


def build_kaggle_sample(path):
    df = pd.read_csv(path)
    if not {"instruction", "intent"}.issubset(df.columns):
        sys.exit(f"Expected columns 'instruction' and 'intent', found: {list(df.columns)}")
    df["expected_category"] = df.intent.map(BITEXT_MAP)
    df = df.dropna(subset=["expected_category"]).drop_duplicates("instruction")
    sample = df.groupby("expected_category").sample(n=10, random_state=42)
    out = pd.DataFrame({
        "id": [f"K{i:03d}" for i in range(1, len(sample) + 1)],
        "ticket": sample.instruction.values,
        "expected_category": sample.expected_category.values,
        "split": "dev",
    })
    out.to_csv(DATA / "kaggle_sample.csv", index=False)
    print(f"Wrote {len(out)} rows to data/kaggle_sample.csv")


if __name__ == "__main__":
    write_categories()
    if "--kaggle" in sys.argv:
        build_kaggle_sample(sys.argv[sys.argv.index("--kaggle") + 1])
    check_tickets()
