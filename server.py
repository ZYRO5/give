import base64
import json
import os
import random
import re
import smtplib
import ssl
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8000"))
OTP_STORE = {}
PAYMENT_STORE = {}
BANK_ACCOUNT_DETAILS = {
    "bank_name": "State Bank of India",
    "account_holder_name": "Pallapu Vinod",
    "account_number": "42818590419",
    "account_type": "Savings Account",
    "ifsc_code": "SBIN0021400",
    "bank_branch": "VENKATARAMANA COLONY,KURNOOL",
    "upi_id": "optional_upi_id",
    "recipient_email": "vinod1914581@gmail.com",
}


def normalize_identifier(identifier: str) -> str:
    return str(identifier or "").strip().lower()


def normalize_phone_number(identifier: str) -> str:
    value = str(identifier or "").strip()
    if not value:
        return ""

    if value.startswith("+"):
        digits = re.sub(r"\D", "", value)
        return f"+{digits}" if digits else value

    digits = re.sub(r"\D", "", value)
    if not digits:
        return value

    if digits.startswith("00"):
        digits = digits[2:]

    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 11 and digits.startswith("0"):
        return f"+91{digits[1:]}"
    if len(digits) >= 12 and digits.startswith("91"):
        return f"+{digits}"
    if len(digits) > 8:
        return f"+{digits}"

    return value


def build_otp(identifier: str = "") -> str:
    normalized = normalize_identifier(identifier)
    if not normalized:
        return f"{random.randint(100000, 999999)}"

    seed = 0
    for char in normalized:
        seed = (seed * 31 + ord(char)) % 1000000
    return f"{(seed % 900000) + 100000}"


def is_email_identifier(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))


def get_payment_details(amount: Optional[float] = None) -> dict:
    payment_amount = round(float(amount or 0), 2)
    return {
        "success": True,
        "payment_method": "bank_transfer",
        "currency": "INR",
        "amount": payment_amount,
        "amount_label": f"₹{payment_amount:.2f}",
        "bank_account": BANK_ACCOUNT_DETAILS,
        "payment_instructions": [
            "Transfer the full donation amount to the bank account shared on the website.",
            "Use your name and email as the transfer reference, if the bank app allows it.",
            "After the transfer, share the payment UTR for confirmation.",
            "Send proof of payment to vinod1914581@gmail.com for confirmation.",
        ],
    }


def build_payment_window(expires_in_minutes: int = 15) -> dict:
    import time

    expires_at = int(time.time()) + max(1, int(expires_in_minutes)) * 60
    return {
        "success": True,
        "expires_in_minutes": int(expires_in_minutes),
        "expires_at": expires_at,
        "payment_modes": [
            "Razorpay Cards",
            "UPI QR",
            "UPI Intent",
            "UPI",
            "Net Banking",
            "Wallets"
        ],
        "notes": [
            "Complete payment within 15 minutes to secure your donation confirmation.",
            "After payment, share the Razorpay UTR or transaction reference for confirmation."
        ],
    }


def build_payment_receipt(
    transaction_id: str,
    amount: float,
    donor_name: str,
    donor_email: str,
    donor_phone: str,
    donor_address: str,
    donor_pan: str = "",
) -> str:
    details = get_payment_details(amount)
    pan_line = f"PAN: {donor_pan}" if donor_pan else "PAN: Not provided"
    return "\n".join(
        [
            "Give Donation Receipt",
            "----------------------",
            f"Transaction ID: {transaction_id}",
            f"Donor: {donor_name}",
            f"Email: {donor_email}",
            f"Phone: {donor_phone}",
            f"Address: {donor_address}",
            pan_line,
            f"Amount to transfer: {details['amount_label']}",
            "Payment method: Bank Transfer",
            "Please transfer the amount using the bank details shared on the website.",
            "Payment UTR: To be shared after transfer",
            "Proof of payment should be sent to vinod1914581@gmail.com.",
        ]
    )


def deliver_email_otp(address: str, otp: str) -> None:
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM") or smtp_user or "no-reply@give.local"

    if not smtp_host or not smtp_user or not smtp_password:
        raise RuntimeError("SMTP credentials are not configured")

    message = EmailMessage()
    message["Subject"] = "Your Give login OTP"
    message["From"] = smtp_from
    message["To"] = address
    message.set_content(
        f"Your Give login OTP is {otp}. It expires in 5 minutes."
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)


def build_ssl_context() -> ssl.SSLContext:
    try:
        import certifi
    except Exception:
        certifi = None

    if certifi:
        try:
            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            pass

    return ssl._create_unverified_context()


def build_delivery_error_message(exc: Exception) -> str:
    text = str(exc or "")
    lower = text.lower()
    if "21608" in text or "unverified" in lower or "trial accounts cannot" in lower:
        return (
            "Twilio could not send the SMS because this trial account cannot deliver to the current phone number. "
            "Please verify the phone number in your Twilio account or use a verified number."
        )
    if "403" in text or "forbidden" in lower:
        return "Twilio rejected the OTP request. Please check the Twilio account configuration and phone verification settings."
    return str(exc) or "Unable to deliver the OTP right now."


def deliver_sms_otp(to: str, otp: str) -> None:
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    service_sid = os.environ.get("TWILIO_VERIFY_SERVICE_SID")

    if not account_sid or not auth_token or not service_sid:
        raise RuntimeError("Twilio credentials are not configured")

    import urllib.request
    import urllib.parse

    body = urllib.parse.urlencode({"To": to, "Channel": "sms"}).encode("utf-8")
    request = urllib.request.Request(
        f"https://verify.twilio.com/v2/Services/{service_sid}/Verifications",
        data=body,
        headers={
            "Authorization": "Basic " + __import__("base64").b64encode(f"{account_sid}:{auth_token}".encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15, context=build_ssl_context()) as response:
        if response.status >= 400:
            raise RuntimeError("Twilio verification request failed")


def twilio_configured() -> bool:
    return bool(
        os.environ.get("TWILIO_ACCOUNT_SID")
        and os.environ.get("TWILIO_AUTH_TOKEN")
        and os.environ.get("TWILIO_VERIFY_SERVICE_SID")
    )


def smtp_configured() -> bool:
    return bool(
        os.environ.get("SMTP_HOST")
        and os.environ.get("SMTP_USERNAME")
        and os.environ.get("SMTP_PASSWORD")
    )


def verify_sms_otp(to: str, code: str) -> None:
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    service_sid = os.environ.get("TWILIO_VERIFY_SERVICE_SID")

    if not account_sid or not auth_token or not service_sid:
        raise RuntimeError("Twilio credentials are not configured")

    import urllib.request
    import urllib.parse

    body = urllib.parse.urlencode({"To": to, "Code": code}).encode("utf-8")
    request = urllib.request.Request(
        f"https://verify.twilio.com/v2/Services/{service_sid}/VerificationCheck",
        data=body,
        headers={
            "Authorization": "Basic " + base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15, context=build_ssl_context()) as response:
        data = json.loads(response.read().decode("utf-8"))
        if response.status >= 400 or data.get("status") != "approved":
            raise RuntimeError(data.get("message") or "Invalid OTP.")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        pathname = parsed.path

        if pathname in ("/", "/app.html"):
            self.serve_file(ROOT_DIR / "app.html")
            return

        if pathname == "/owner.html":
            self.serve_file(ROOT_DIR / "owner.html")
            return

        if pathname == "/health":
            self.send_json(200, {"ok": True, "service": "donor-otp-demo"})
            return

        self.send_text(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        pathname = parsed.path

        if pathname == "/api/send-otp":
            self.handle_send_otp()
            return

        if pathname == "/api/verify-otp":
            self.handle_verify_otp()
            return

        if pathname == "/api/payment-details":
            self.handle_payment_details()
            return

        if pathname == "/api/confirm-payment":
            self.handle_confirm_payment()
            return

        if pathname == "/api/payment-window":
            self.handle_payment_window()
            return

        self.send_text(404, "Not found")

    def handle_send_otp(self):
        body = self.read_body()
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Bad request."})
            return

        identifier = normalize_identifier(payload.get("identifier"))
        channel = payload.get("channel")
        if not identifier:
            self.send_json(400, {"success": False, "message": "Identifier is required."})
            return

        if channel == "phone":
            identifier = normalize_phone_number(identifier)

        otp = build_otp(identifier)
        delivery_mode = "local"
        message = "OTP generated locally for testing. Configure SMTP or Twilio for real delivery."
        response_payload = {
            "success": True,
            "delivery": delivery_mode,
        }

        if channel == "email" and is_email_identifier(identifier):
            if not smtp_configured():
                print(f"[otp-delivery-missing-config] email delivery is not configured for {identifier}")
            else:
                try:
                    deliver_email_otp(identifier, otp)
                    delivery_mode = "email"
                    message = "OTP sent to your email address."
                except Exception as exc:
                    print(f"[otp-delivery-fallback] {identifier} => {otp} ({exc})")
        elif channel == "phone":
            if not twilio_configured():
                print(f"[otp-delivery-missing-config] SMS delivery is not configured for {identifier}")
            else:
                try:
                    deliver_sms_otp(identifier, otp)
                    delivery_mode = "sms"
                    message = "OTP sent to your phone number."
                except Exception as exc:
                    message = build_delivery_error_message(exc)
                    print(f"[otp-delivery-fallback] {identifier} => {otp} ({exc})")
                    delivery_mode = "error"

        OTP_STORE[identifier] = {"code": otp, "expires_at": self._now_ms() + 5 * 60 * 1000}
        if delivery_mode in {"local", "error"}:
            response_payload["otp"] = otp

        response_payload["message"] = message
        response_payload["delivery"] = delivery_mode
        print(f"[otp] {identifier} => {otp} [{delivery_mode}]")
        self.send_json(200, response_payload)

    def handle_verify_otp(self):
        body = self.read_body()
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Bad request."})
            return

        identifier = normalize_identifier(payload.get("identifier"))
        code = str(payload.get("code") or "").strip()
        if not identifier or not code:
            self.send_json(400, {"success": False, "message": "Identifier and OTP are required."})
            return

        if not is_email_identifier(identifier) and twilio_configured():
            identifier = normalize_phone_number(identifier)
            try:
                verify_sms_otp(identifier, code)
                self.send_json(200, {"success": True, "message": "Login successful."})
                return
            except Exception:
                pass

        record = OTP_STORE.get(identifier)
        if record and record["code"] == code and self._now_ms() < record["expires_at"]:
            OTP_STORE.pop(identifier, None)
            self.send_json(200, {"success": True, "message": "Login successful."})
            return

        self.send_json(401, {"success": False, "message": "Invalid or expired OTP."})

    def handle_payment_details(self):
        amount = self.read_body()
        try:
            payload = json.loads(amount or "{}") if amount else {}
        except json.JSONDecodeError:
            payload = {}
        amount_value = payload.get("amount")
        self.send_json(200, get_payment_details(amount_value))

    def handle_payment_window(self):
        body = self.read_body()
        try:
            payload = json.loads(body or "{}") if body else {}
        except json.JSONDecodeError:
            payload = {}
        minutes = payload.get("expires_in_minutes", 15)
        self.send_json(200, build_payment_window(minutes))

    def handle_confirm_payment(self):
        body = self.read_body()
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Bad request."})
            return

        donor_name = str(payload.get("donor_name") or "").strip()
        donor_email = str(payload.get("donor_email") or "").strip()
        donor_phone = str(payload.get("donor_phone") or "").strip()
        donor_address = str(payload.get("donor_address") or "").strip()
        donor_pan = str(payload.get("donor_pan") or "").strip()
        try:
            amount = float(payload.get("amount") or 0)
        except (TypeError, ValueError):
            amount = 0

        if amount <= 0 or not donor_name or not donor_email or not donor_phone or not donor_address:
            self.send_json(400, {"success": False, "message": "Please provide a valid donation amount and donor details."})
            return

        transaction_id = f"PAY-{self._now_ms()}"
        payment_details = get_payment_details(amount)
        receipt_text = build_payment_receipt(
            transaction_id=transaction_id,
            amount=amount,
            donor_name=donor_name,
            donor_email=donor_email,
            donor_phone=donor_phone,
            donor_address=donor_address,
            donor_pan=donor_pan,
        )
        PAYMENT_STORE[transaction_id] = {
            "amount": amount,
            "donor_name": donor_name,
            "donor_email": donor_email,
            "donor_phone": donor_phone,
            "donor_address": donor_address,
            "donor_pan": donor_pan,
            "created_at": self._now_ms(),
        }
        self.send_json(
            200,
            {
                "success": True,
                "message": "Payment instructions prepared. Please transfer the amount to the bank account below.",
                "transaction_id": transaction_id,
                "payment_details": payment_details,
                "receipt": receipt_text,
            },
        )

    def read_body(self) -> str:
        content_length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(content_length).decode("utf-8") if content_length else ""

    def serve_file(self, path: Path):
        if not path.exists():
            self.send_text(404, "File not found")
            return

        content = path.read_bytes()
        ext = path.suffix.lower()
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
        }.get(ext, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status: int, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, status: int, text: str):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _now_ms() -> int:
        import time
        return int(time.time() * 1000)


def enable_https(server: ThreadingHTTPServer) -> None:
    cert_path = ROOT_DIR / "ssl" / "cert.pem"
    key_path = ROOT_DIR / "ssl" / "key.pem"
    if not cert_path.exists() or not key_path.exists():
        return

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_path, key_path)
    server.socket = context.wrap_socket(server.socket, server_side=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    enable_https(server)
    scheme = "https" if server.socket.__class__.__name__ == "SSLSocket" else "http"
    print(f"OTP backend listening on {scheme}://127.0.0.1:{PORT}")
    server.serve_forever()
