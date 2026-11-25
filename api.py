from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from schemas import AnalyzeResponse, CATEGORY_INFO, TicketRequest
from service import (BackendUnavailable, EmptyTicketError, InvalidModelOutput,
                     analyze_ticket, get_mode)

app = FastAPI(title="Ticket Classification Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "mode": get_mode()}


@app.get("/categories")
def categories():
    return [{"name": n, "meaning": m, "example": e} for n, (m, e) in CATEGORY_INFO.items()]


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: TicketRequest):
    try:
        return analyze_ticket(req.ticket, req.prompt_version, simulate=req.simulate)
    except EmptyTicketError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except InvalidModelOutput as err:
        raise HTTPException(status_code=502, detail=str(err))
    except BackendUnavailable as err:
        raise HTTPException(status_code=503, detail=str(err))


app.mount("/", StaticFiles(directory=Path(__file__).parent / "frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
