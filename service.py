import json
import os

from pydantic import ValidationError

from mock_model import run_mock
from prompts import SYSTEM_PROMPTS, build_user_message
from schemas import TicketResult

LIVE_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")


class EmptyTicketError(Exception):
    pass


class InvalidModelOutput(Exception):
    pass


class BackendUnavailable(Exception):
    pass


def get_mode():
    return "live" if os.getenv("TICKET_MODE", "mock").lower() == "live" else "mock"


def call_live_model(ticket, version):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise BackendUnavailable("ANTHROPIC_API_KEY is not set")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key, timeout=30)
        reply = client.messages.create(
            model=LIVE_MODEL,
            max_tokens=300,
            system=SYSTEM_PROMPTS[version],
            messages=[{"role": "user", "content": build_user_message(ticket)}],
        )
        return reply.content[0].text
    except Exception as err:
        raise BackendUnavailable(f"model backend failed: {err}")


def parse_output(raw):
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise InvalidModelOutput("model did not return JSON")
    try:
        data = json.loads(raw[start:end + 1])
        return TicketResult(**data)
    except (json.JSONDecodeError, TypeError, ValidationError) as err:
        raise InvalidModelOutput(f"model output failed validation: {err}")


def analyze_ticket(ticket, version="v2", mode=None, simulate=None):
    if not ticket or not ticket.strip():
        raise EmptyTicketError("Ticket text is empty.")
    mode = mode or get_mode()

    if simulate == "backend_down":
        raise BackendUnavailable("simulated backend failure")
    if simulate == "bad_output":
        raw = '{"category": "shipping_help", "summary": "Customer asks about a parcel."}'
    elif mode == "live":
        raw = call_live_model(ticket, version)
    else:
        raw = run_mock(ticket, version)

    result = parse_output(raw)
    return {"category": result.category, "summary": result.summary,
            "prompt_version": version, "mode": mode}
