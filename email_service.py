import os
import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

resend.api_key = os.environ.get("RESEND_API_KEY", "")

_jinja = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(["html"]),
)


def send_results_email(
    to_email: str,
    form_data: dict,
    form_version: str,
    is_test: bool,
) -> bool:
    try:
        template = _jinja.get_template("result_email.html")
        html_body = template.render(
            email=to_email,
            form_data=form_data,
            form_version=form_version,
            is_test=is_test,
        )

        params = {
            "from": os.environ.get("FROM_EMAIL", "noreply@yourdomain.com"),
            "to": [to_email],
            "subject": "Your Results" + (" [TEST]" if is_test else ""),
            "html": html_body,
        }

        bcc = os.environ.get("BCC_EMAIL", "")
        if bcc:
            params["bcc"] = [bcc]

        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
