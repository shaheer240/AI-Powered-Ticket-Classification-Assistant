import os
import sys
from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schemas import CATEGORIES, TicketResult
from service import (BackendUnavailable, EmptyTicketError, InvalidModelOutput,
                     analyze_ticket)

DATA = Path(__file__).resolve().parent.parent / "data"


def test_ten_categories_match_csv():
    assert len(CATEGORIES) == 10
    defined = pd.read_csv(DATA / "categories.csv")["category"].tolist()
    assert defined == CATEGORIES


def test_dataset_size_and_split():
    df = pd.read_csv(DATA / "tickets.csv")
    assert len(df) >= 100
    assert (df.split == "eval").sum() >= 20
    assert set(df.expected_category) == set(CATEGORIES)


def test_valid_ticket():
    out = analyze_ticket("Please cancel my order 52944, I found it cheaper elsewhere.", "v2", mode="mock")
    assert out["category"] == "order_change_cancel"
    assert out["summary"].endswith(".")
    assert out["mode"] == "mock"


def test_both_prompt_versions_return_known_category():
    for version in ("v1", "v2"):
        out = analyze_ticket("Where is my package?", version, mode="mock")
        assert out["category"] in CATEGORIES


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_blank_ticket(text):
    with pytest.raises(EmptyTicketError):
        analyze_ticket(text, mode="mock")


def test_invalid_model_output():
    with pytest.raises(InvalidModelOutput):
        analyze_ticket("Where is my parcel?", mode="mock", simulate="bad_output")


def test_backend_down():
    with pytest.raises(BackendUnavailable):
        analyze_ticket("Where is my parcel?", mode="mock", simulate="backend_down")


def test_live_mode_without_key():
    os.environ.pop("ANTHROPIC_API_KEY", None)
    with pytest.raises(BackendUnavailable):
        analyze_ticket("Where is my parcel?", mode="live")


def test_schema_rejects_unknown_category():
    with pytest.raises(ValidationError):
        TicketResult(category="shipping_help", summary="Customer asks about a parcel.")


def test_schema_rejects_long_summary():
    with pytest.raises(ValidationError):
        TicketResult(category="order_tracking", summary=" ".join(["word"] * 40) + ".")


def test_schema_rejects_two_sentences():
    with pytest.raises(ValidationError):
        TicketResult(category="order_tracking", summary="Customer asks about a parcel. They are upset.")


def test_schema_rejects_completed_action():
    with pytest.raises(ValidationError):
        TicketResult(category="refund_request", summary="We have refunded the customer for order 43990.")


def test_schema_allows_customer_describing_own_action():
    ok = TicketResult(category="refund_request", summary="Customer says they sent back a jacket and has no refund.")
    assert ok.category == "refund_request"
