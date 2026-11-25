import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix

from baselines import TfidfNearest, keyword_baseline
from schemas import CATEGORIES
from service import analyze_ticket

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"


def main(live=False):
    df = pd.read_csv(ROOT / "data" / "tickets.csv")
    dev = df[df.split == "dev"]
    ev = df[df.split == "eval"].reset_index(drop=True)

    tfidf = TfidfNearest(dev.ticket, dev.expected_category)
    systems = {
        "keyword_baseline": keyword_baseline,
        "tfidf_nearest": tfidf.predict,
        "mock_v1": lambda t: analyze_ticket(t, "v1", mode="mock")["category"],
        "mock_v2": lambda t: analyze_ticket(t, "v2", mode="mock")["category"],
    }
    if live:
        systems["live_v1"] = lambda t: analyze_ticket(t, "v1", mode="live")["category"]
        systems["live_v2"] = lambda t: analyze_ticket(t, "v2", mode="live")["category"]

    RESULTS.mkdir(exist_ok=True)
    predictions = ev[["id", "ticket", "expected_category"]].copy()
    lines = ["# Evaluation results", "",
             f"Fixed evaluation set: {len(ev)} tickets (2 per category). "
             "mock_* rows are rule-based fixture results, not real LLM performance.", "",
             "| System | Correct | Accuracy |", "|---|---|---|"]

    for name, predict in systems.items():
        predictions[name] = ev.ticket.map(predict)
        correct = (predictions[name] == ev.expected_category).sum()
        acc = accuracy_score(ev.expected_category, predictions[name])
        lines.append(f"| {name} | {correct}/{len(ev)} | {acc:.0%} |")
        matrix = pd.DataFrame(confusion_matrix(ev.expected_category, predictions[name], labels=CATEGORIES),
                              index=CATEGORIES, columns=CATEGORIES)
        matrix.to_csv(RESULTS / f"confusion_matrix_{name}.csv")

    predictions.to_csv(RESULTS / "eval_predictions.csv", index=False)

    best = "mock_v2"
    lines += ["", f"## Errors for {best}", ""]
    wrong = predictions[predictions[best] != predictions.expected_category]
    for _, row in wrong.iterrows():
        lines.append(f"- {row.id}: expected `{row.expected_category}`, got `{row[best]}` - {row.ticket}")
    if wrong.empty:
        lines.append("- none")

    lines += ["", f"## Confusion matrix for {best} (rows = expected, columns = predicted)", ""]
    matrix = pd.read_csv(RESULTS / f"confusion_matrix_{best}.csv", index_col=0)
    lines.append("| expected \\ predicted | " + " | ".join(c[:8] for c in CATEGORIES) + " |")
    lines.append("|---|" + "---|" * len(CATEGORIES))
    for cat, row in matrix.iterrows():
        lines.append(f"| {cat} | " + " | ".join(str(v) for v in row) + " |")

    lines += ["", "## Sample summaries (mock_v2)", ""]
    for _, row in ev.head(4).iterrows():
        lines.append(f"- {row.id}: {analyze_ticket(row.ticket, 'v2', mode='mock')['summary']}")

    (RESULTS / "evaluation_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(live="--live" in sys.argv)
