import os
import datetime
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import PlainTextResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import io

load_dotenv()

from models import SubmissionRequest
from db import init_db, insert_submission, export_leads_csv
from email_service import send_results_email

app = FastAPI(title="Lead Capture API", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.mount("/scorecard", StaticFiles(directory="static/scorecard", html=True), name="scorecard")
app.mount("/form-legacy", StaticFiles(directory="static/form", html=True), name="form_legacy")


@app.get("/form")
@app.get("/form/")
def form_redirect():
    return RedirectResponse(url="/scorecard/", status_code=307)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}


@app.post("/submit")
async def submit(payload: SubmissionRequest, request: Request):
    timestamp = datetime.datetime.utcnow().isoformat()
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else None)
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    row_id = insert_submission(
        email=payload.email,
        form_data=payload.form_data,
        form_version=payload.form_version,
        is_test=payload.is_test,
        timestamp=timestamp,
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer,
    )

    email_ok = send_results_email(
        to_email=payload.email,
        form_data=payload.form_data,
        form_version=payload.form_version,
        is_test=payload.is_test,
    )

    return {
        "success": True,
        "id": row_id,
        "email_sent": email_ok,
        "is_test": payload.is_test,
    }


@app.get("/export")
def export(key: str = "", authorization: str = Header(default="")):
    secret = os.environ.get("EXPORT_SECRET", "")
    bearer = authorization.replace("Bearer ", "").strip()
    if not secret or (key != secret and bearer != secret):
        raise HTTPException(status_code=403, detail="Invalid export key")

    csv_data = export_leads_csv(include_test=False)
    filename = f"leads_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
