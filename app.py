from flask import Flask, render_template, request, redirect, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import secrets
import hmac
from sqlalchemy import text
from database import engine, init_db

app = Flask(__name__)

RATE_LIMIT_STORAGE_URI = os.environ.get(
    "RATE_LIMIT_STORAGE_URI", "memory://"
)

if os.environ.get("APP_ENV") == "production" and RATE_LIMIT_STORAGE_URI == "memory://":
    raise RuntimeError("A shared rate-limit storage must be configured in production.")

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri=RATE_LIMIT_STORAGE_URI
)
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be configured.")

app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1"
)

os.makedirs("database", exist_ok=True)

TEXTS = {
    "fa": {
        "welcome": "به افغان تاپ‌آپ خوش آمدید",
        "subtitle": "شارژ آسان برای افغانستان",
        "phone": "شماره تلفن افغانستان",
        "operator": "انتخاب اپراتور",
        "amount": "مبلغ شارژ (افغانی)",
        "buy": "ثبت سفارش",
        "orders": "سفارش‌های من",
        "notice": "پرداخت USDT به‌زودی فعال می‌شود",
        "success": "سفارش آزمایشی ثبت شد!"
    },
    "ps": {
        "welcome": "افغان ټاپ اپ ته ښه راغلاست",
        "subtitle": "د افغانستان لپاره اسانه چارج",
        "phone": "د افغانستان تلیفون شمېره",
        "operator": "د شبکې انتخاب",
        "amount": "د چارج اندازه",
        "buy": "غوښتنه ثبت کړئ",
        "orders": "زما غوښتنې",
        "notice": "د USDT تادیه به وروسته فعاله شي",
        "success": "ازمایښتي غوښتنه ثبت شوه!"
    },
    "uz": {
        "welcome": "Afghan TopUp xizmatiga xush kelibsiz",
        "subtitle": "Afg‘oniston uchun oson to‘ldirish",
        "phone": "Telefon raqami",
        "operator": "Operatorni tanlang",
        "amount": "To‘ldirish miqdori",
        "buy": "Buyurtma berish",
        "orders": "Buyurtmalarim",
        "notice": "USDT to‘lovi keyinroq yoqiladi",
        "success": "Sinov buyurtmasi saqlandi!"
    }
}

OPERATORS = ["Roshan", "AWCC", "Etisalat", "Salaam"]

@app.route("/", methods=["GET", "POST"])
def home():
    lang = session.get("lang", "fa")
    t = TEXTS[lang]
    message = ""

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        operator = request.form.get("operator", "")
        amount = request.form.get("amount", "")

        try:
            amount = int(amount)
        except ValueError:
            amount = 0

        if (phone.isdigit() and 7 <= len(phone) <= 15
                and operator in OPERATORS
                and 1 <= amount <= 100000):
            with engine.begin() as db:
                db.execute(
                    text("INSERT INTO orders (phone, operator, amount, status) VALUES (:phone, :operator, :amount, :status)"),
                    {"phone": phone, "operator": operator, "amount": amount, "status": "DEMO"}
                )
            message = t["success"]
        else:
            message = "اطلاعات واردشده صحیح نیست."

    return render_template(
        "index.html",
        t=t,
        lang=lang,
        operators=OPERATORS,
        message=message
    )

@app.route("/language/<lang>")
def language(lang):
    if lang in TEXTS:
        session["lang"] = lang
    return redirect("/")

@app.route("/orders")
def orders():
    return render_template("orders.html", orders=[])


import hmac

@app.route("/admin", methods=["GET", "POST"])
def admin():
    password = os.environ.get("ADMIN_PASSWORD")

    if not password:
        return "Admin password is not configured.", 503

    csrf_token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
    message = ""

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        if not hmac.compare_digest(
            submitted_token.encode("utf-8"),
            csrf_token.encode("utf-8")
        ):
            return "درخواست نامعتبر است. صفحه را دوباره باز کنید.", 400

    if not session.get("is_admin"):
        if request.method == "POST":
            supplied = request.form.get("password", "")

            if request.form.get("action") == "login" and hmac.compare_digest(
                supplied.encode("utf-8"),
                password.encode("utf-8")
            ):
                session.clear()
                session["is_admin"] = True
                session["csrf_token"] = secrets.token_urlsafe(32)
                return redirect("/admin")

            message = "رمز عبور اشتباه است."

        return render_template(
            "admin.html",
            logged_in=False,
            orders=[],
            message=message,
            csrf_token=csrf_token
        )

    if request.method == "POST":
        if request.form.get("action") == "status":
            try:
                order_id = int(request.form.get("order_id", "0"))
                status = request.form.get("status")

                if status in ("DEMO", "REVIEWED", "CANCELLED"):
                    with engine.begin() as db:
                        db.execute(
                            text("UPDATE orders SET status=:status WHERE id=:id"),
                            {"status": status, "id": order_id}
                        )
            except ValueError:
                pass

            return redirect("/admin")

    filter_status = request.args.get("status", "ALL")
    allowed_filters = ("ALL", "DEMO", "REVIEWED", "CANCELLED")
    if filter_status not in allowed_filters:
        filter_status = "ALL"

    with engine.connect() as db:
        if filter_status == "ALL":
            orders = db.execute(
                text("SELECT id, phone, operator, amount, status FROM orders ORDER BY id DESC")
            ).fetchall()
        else:
            orders = db.execute(
                text("SELECT id, phone, operator, amount, status FROM orders WHERE status=:status ORDER BY id DESC"),
                {"status": filter_status}
            ).fetchall()

        stats_row = db.execute(
            text("""
                SELECT COUNT(*) AS total,
                    COALESCE(SUM(CASE WHEN status='DEMO' THEN 1 ELSE 0 END), 0) AS pending,
                    COALESCE(SUM(CASE WHEN status='REVIEWED' THEN 1 ELSE 0 END), 0) AS reviewed,
                    COALESCE(SUM(CASE WHEN status='CANCELLED' THEN 1 ELSE 0 END), 0) AS cancelled
                FROM orders
            """)
        ).one()

    total, pending, reviewed, cancelled = stats_row
    stats = {
        "total": total or 0,
        "pending": pending or 0,
        "reviewed": reviewed or 0,
        "cancelled": cancelled or 0
    }

    return render_template(
        "admin.html",
        logged_in=True,
        orders=orders,
        message=message,
        filter_status=filter_status,
        stats=stats,
        csrf_token=csrf_token
    )

@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    submitted_token = request.form.get("csrf_token", "")
    saved_token = session.get("csrf_token", "")

    if not saved_token or not hmac.compare_digest(
        submitted_token.encode("utf-8"),
        saved_token.encode("utf-8")
    ):
        return "درخواست نامعتبر است.", 400

    session.clear()
    return redirect("/admin")




# AfghanTopUp Demo API
from flask import jsonify

@app.route("/api/demo-orders", methods=["GET"])
def api_demo_orders():
    return jsonify({"success": False, "error": "Access disabled"}), 403


@app.route("/api/demo-orders", methods=["POST"])
@limiter.limit("5 per minute")
def api_create_demo_order():
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON required"}), 400

    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    operator = str(data.get("operator", "")).strip()
    amount = data.get("amount")

    if not phone.isdigit() or not 7 <= len(phone) <= 15:
        return jsonify({"success": False, "error": "Invalid phone"}), 400

    if operator not in OPERATORS:
        return jsonify({"success": False, "error": "Invalid operator"}), 400

    if isinstance(amount, bool) or not isinstance(amount, int) or not 1 <= amount <= 100000:
        return jsonify({"success": False, "error": "Invalid amount"}), 400

    with engine.begin() as db:
        order_id = db.execute(
            text("INSERT INTO orders (phone, operator, amount, status) VALUES (:phone, :operator, :amount, :status) RETURNING id"),
            {"phone": phone, "operator": operator, "amount": amount, "status": "DEMO"}
        ).scalar_one()

    return jsonify({
        "success": True,
        "order": {
            "id": order_id,
            "operator": operator,
            "amount": amount,
            "status": "DEMO"
        }
    }), 201

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
