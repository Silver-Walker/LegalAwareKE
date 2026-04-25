from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import mysql.connector
import os
import smtplib
import secrets
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this"  # Change this in production!

# Load .env file (if present) so local development picks up secrets.
def load_local_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key:
                os.environ.setdefault(key, value)


load_local_env()

# 2FA settings (set these in environment variables / .env)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", os.getenv("SMTP_PASSWORD", ""))
ADMIN_2FA_EMAIL = os.getenv("ADMIN_2FA_EMAIL", "")
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))

# In-memory pending 2FA challenges (token -> challenge data).
# For production deployments with multiple workers, move this to shared storage.
PENDING_2FA = {}

# ==========================
# Database connection
# ==========================
import os
import mysql.connector
from urllib.parse import urlparse

def get_db():
    db_url = os.getenv("DB_URL")

    if not db_url:
        raise Exception("DB_URL not set")

    from urllib.parse import urlparse
    result = urlparse(db_url)

    return mysql.connector.connect(
        host=result.hostname,
        user=result.username,
        password=result.password,
        database=result.path.replace("/", ""),
        port=result.port
    )

# ==========================
# Admin login required decorator
# ==========================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please login to access the admin panel.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


def send_two_factor_email(recipient, code, username):
    subject = "Your LegalAwareKE Admin Login Code"
    body = (
        f"Hello {username},\n\n"
        f"Your LegalAwareKE admin verification code is: {code}\n"
        f"This code expires in {OTP_EXPIRY_MINUTES} minutes.\n\n"
        "If you did not request this login, you can ignore this email.\n"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def cleanup_expired_2fa():
    now = datetime.now(timezone.utc)
    expired_tokens = [token for token, data in PENDING_2FA.items() if data["expires_at"] < now]
    for token in expired_tokens:
        PENDING_2FA.pop(token, None)


# ==========================
# PUBLIC ROUTES
# ==========================

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Stats
    cursor.execute("SELECT COUNT(*) AS total FROM offences")
    total_offences = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM laws")
    total_laws = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM categories")
    total_categories = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM civic_education")
    total_civic = cursor.fetchone()["total"]

    # Recent offences
    cursor.execute("""
        SELECT o.id, o.title, o.penalty, l.title AS law_title, c.name AS category_name
        FROM offences o
        LEFT JOIN laws l ON o.law_id = l.id
        LEFT JOIN categories c ON o.category_id = c.id
        ORDER BY o.created_at DESC
        LIMIT 5
    """)
    recent_offences = cursor.fetchall()

    cursor.close()
    db.close()

    stats = {
        "total_offences": total_offences,
        "total_laws": total_laws,
        "total_categories": total_categories,
        "total_civic": total_civic,
    }
    return render_template("index.html", stats=stats, recent_offences=recent_offences)


@app.route("/laws")
def laws():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.*, COUNT(o.id) AS offence_count
        FROM laws l
        LEFT JOIN offences o ON o.law_id = l.id
        GROUP BY l.id
        ORDER BY l.title
    """)
    laws_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("laws.html", laws=laws_list)


@app.route("/law/<int:law_id>")
def law_detail(law_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM laws WHERE id = %s", (law_id,))
    law = cursor.fetchone()

    cursor.execute("""
        SELECT o.*, c.name AS category_name
        FROM offences o
        LEFT JOIN categories c ON o.category_id = c.id
        WHERE o.law_id = %s
        ORDER BY o.title
    """, (law_id,))
    offences = cursor.fetchall()

    cursor.close()
    db.close()
    return render_template("law_detail.html", law=law, offences=offences)


@app.route("/offences")
def offences():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    category_id = request.args.get("category")

    if category_id:
        cursor.execute("""
            SELECT o.*, l.title AS law_title, c.name AS category_name
            FROM offences o
            LEFT JOIN laws l ON o.law_id = l.id
            LEFT JOIN categories c ON o.category_id = c.id
            WHERE o.category_id = %s
            ORDER BY o.title
        """, (category_id,))
    else:
        cursor.execute("""
            SELECT o.*, l.title AS law_title, c.name AS category_name
            FROM offences o
            LEFT JOIN laws l ON o.law_id = l.id
            LEFT JOIN categories c ON o.category_id = c.id
            ORDER BY o.title
        """)
    offences_list = cursor.fetchall()

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    cursor.close()
    db.close()
    return render_template("offences.html", offences=offences_list, categories=categories)


@app.route("/offence/<int:offence_id>")
def offence_detail(offence_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, l.title AS law_title, l.year AS law_year, c.name AS category_name
        FROM offences o
        LEFT JOIN laws l ON o.law_id = l.id
        LEFT JOIN categories c ON o.category_id = c.id
        WHERE o.id = %s
    """, (offence_id,))
    offence = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template("offence_detail.html", offence=offence)


@app.route("/civic")
def civic():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ce.*, l.title AS law_title, c.name AS category_name
        FROM civic_education ce
        LEFT JOIN laws l ON ce.related_law = l.id
        LEFT JOIN categories c ON ce.category_id = c.id
        ORDER BY ce.created_at DESC
    """)
    articles = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("civic.html", articles=articles)


@app.route("/civic/<int:article_id>")
def civic_detail(article_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ce.*, l.title AS law_title, c.name AS category_name
        FROM civic_education ce
        LEFT JOIN laws l ON ce.related_law = l.id
        LEFT JOIN categories c ON ce.category_id = c.id
        WHERE ce.id = %s
    """, (article_id,))
    article = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template("civic_detail.html", article=article)


@app.route("/constitution")
def constitution():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT chapter_id, chapter_number, title, summary, articles_range
        FROM constitution_chapters
        ORDER BY chapter_number ASC
    """)
    chapters = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("constitution.html", chapters=chapters)


@app.route("/constitution/chapter/<int:chapter_id>")
def constitution_chapter(chapter_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM constitution_chapters WHERE chapter_id = %s", (chapter_id,))
    chapter = cursor.fetchone()
    cursor.close()
    db.close()
    if not chapter:
        abort(404)
    return render_template("constitution_chapter.html", chapter=chapter)


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = {"offences": [], "laws": [], "civic": []}

    if query:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        like = f"%{query}%"

        cursor.execute("""
            SELECT o.*, l.title AS law_title, c.name AS category_name
            FROM offences o
            LEFT JOIN laws l ON o.law_id = l.id
            LEFT JOIN categories c ON o.category_id = c.id
            WHERE o.title LIKE %s OR o.description LIKE %s OR o.penalty LIKE %s
        """, (like, like, like))
        results["offences"] = cursor.fetchall()

        cursor.execute("SELECT * FROM laws WHERE title LIKE %s OR description LIKE %s", (like, like))
        results["laws"] = cursor.fetchall()

        cursor.execute("SELECT * FROM civic_education WHERE title LIKE %s OR content LIKE %s", (like, like))
        results["civic"] = cursor.fetchall()

        cursor.close()
        db.close()

    return render_template("search_results.html", query=query, results=results)


# ==========================
# API ROUTES
# ==========================

@app.route("/api/stats")
def api_stats():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.title AS law, COUNT(o.id) AS offence_count
        FROM laws l
        LEFT JOIN offences o ON o.law_id = l.id
        GROUP BY l.id
        ORDER BY offence_count DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify({
        "labels": [r["law"] for r in rows],
        "counts": [r["offence_count"] for r in rows]
    })


# ==========================
# ADMIN ROUTES
# ==========================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    cleanup_expired_2fa()

    if request.method == "POST":
        otp_code = request.form.get("otp_code", "").strip()
        pending_token = session.get("pending_2fa_token")

        # Step 2: Verify emailed OTP
        if otp_code and pending_token:
            pending = PENDING_2FA.get(pending_token)
            if not pending:
                session.pop("pending_2fa_token", None)
                flash("Verification session expired. Please sign in again.", "warning")
                return redirect(url_for("admin_login"))

            if pending["expires_at"] < datetime.now(timezone.utc):
                PENDING_2FA.pop(pending_token, None)
                session.pop("pending_2fa_token", None)
                flash("Verification code expired. Please sign in again.", "warning")
                return redirect(url_for("admin_login"))

            if otp_code != pending["otp_code"]:
                flash("Invalid verification code.", "danger")
                return render_template("admin/login.html", two_factor_required=True)

            session["admin_id"] = pending["admin_id"]
            session["admin_username"] = pending["admin_username"]
            PENDING_2FA.pop(pending_token, None)
            session.pop("pending_2fa_token", None)
            flash("Welcome back, " + session["admin_username"] + "!", "success")
            return redirect(url_for("admin_dashboard"))

        # Step 1: Verify username/password and send OTP
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("admin/login.html")

        if not SMTP_USER or not SMTP_PASS or not ADMIN_2FA_EMAIL:
            flash("2FA email is not configured on the server. Set SMTP_USER, SMTP_PASS and ADMIN_2FA_EMAIL.", "danger")
            return render_template("admin/login.html")

        otp_code = f"{secrets.randbelow(1_000_000):06d}"
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
        PENDING_2FA[token] = {
            "admin_id": user["id"],
            "admin_username": user["username"],
            "otp_code": otp_code,
            "expires_at": expires_at,
        }
        session["pending_2fa_token"] = token

        try:
            send_two_factor_email(ADMIN_2FA_EMAIL, otp_code, user["username"])
        except Exception as e:
            PENDING_2FA.pop(token, None)
            session.pop("pending_2fa_token", None)
            if app.debug:
                flash(f"Could not send verification email: {e}", "danger")
            else:
                flash("Could not send verification email. Check SMTP settings and try again.", "danger")
            return render_template("admin/login.html")

        flash(f"Verification code sent to {ADMIN_2FA_EMAIL}. Enter it below.", "info")
        return render_template("admin/login.html", two_factor_required=True)

    if session.get("pending_2fa_token"):
        return render_template("admin/login.html", two_factor_required=True)
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    pending_token = session.get("pending_2fa_token")
    if pending_token:
        PENDING_2FA.pop(pending_token, None)
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM offences")
    total_offences = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM laws")
    total_laws = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM civic_education")
    total_civic = cursor.fetchone()["total"]

    cursor.close()
    db.close()

    return render_template("admin/dashboard.html", 
        total_offences=total_offences,
        total_laws=total_laws,
        total_civic=total_civic
    )


# --- ADMIN: LAWS ---

@app.route("/admin/laws")
@login_required
def admin_laws():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM laws ORDER BY title")
    laws_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/laws.html", laws=laws_list)


@app.route("/admin/laws/add", methods=["GET", "POST"])
@login_required
def admin_add_law():
    if request.method == "POST":
        title = request.form["title"]
        year = request.form["year"]
        description = request.form["description"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO laws (title, year, description) VALUES (%s, %s, %s)",
                       (title, year, description))
        db.commit()
        cursor.close()
        db.close()
        flash("Law added successfully!", "success")
        return redirect(url_for("admin_laws"))

    return render_template("admin/law_form.html", law=None)


@app.route("/admin/laws/edit/<int:law_id>", methods=["GET", "POST"])
@login_required
def admin_edit_law(law_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        year = request.form["year"]
        description = request.form["description"]
        cursor.execute("UPDATE laws SET title=%s, year=%s, description=%s WHERE id=%s",
                       (title, year, description, law_id))
        db.commit()
        cursor.close()
        db.close()
        flash("Law updated successfully!", "success")
        return redirect(url_for("admin_laws"))

    cursor.execute("SELECT * FROM laws WHERE id = %s", (law_id,))
    law = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template("admin/law_form.html", law=law)


@app.route("/admin/laws/delete/<int:law_id>", methods=["POST"])
@login_required
def admin_delete_law(law_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM laws WHERE id = %s", (law_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Law deleted.", "warning")
    return redirect(url_for("admin_laws"))


# --- ADMIN: OFFENCES ---

@app.route("/admin/offences")
@login_required
def admin_offences():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, l.title AS law_title, c.name AS category_name
        FROM offences o
        LEFT JOIN laws l ON o.law_id = l.id
        LEFT JOIN categories c ON o.category_id = c.id
        ORDER BY o.title
    """)
    offences_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/offences.html", offences=offences_list)


@app.route("/admin/offences/add", methods=["GET", "POST"])
@login_required
def admin_add_offence():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        section_number = request.form["section_number"]
        penalty = request.form["penalty"]
        law_id = request.form["law_id"] or None
        category_id = request.form["category_id"] or None

        cursor.execute("""
            INSERT INTO offences (title, description, section_number, penalty, law_id, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, section_number, penalty, law_id, category_id))
        db.commit()
        cursor.close()
        db.close()
        flash("Offence added successfully!", "success")
        return redirect(url_for("admin_offences"))

    cursor.execute("SELECT id, title FROM laws ORDER BY title")
    laws = cursor.fetchall()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/offence_form.html", offence=None, laws=laws, categories=categories)


@app.route("/admin/offences/edit/<int:offence_id>", methods=["GET", "POST"])
@login_required
def admin_edit_offence(offence_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        section_number = request.form["section_number"]
        penalty = request.form["penalty"]
        law_id = request.form["law_id"] or None
        category_id = request.form["category_id"] or None

        cursor.execute("""
            UPDATE offences SET title=%s, description=%s, section_number=%s,
            penalty=%s, law_id=%s, category_id=%s WHERE id=%s
        """, (title, description, section_number, penalty, law_id, category_id, offence_id))
        db.commit()
        cursor.close()
        db.close()
        flash("Offence updated!", "success")
        return redirect(url_for("admin_offences"))

    cursor.execute("SELECT * FROM offences WHERE id = %s", (offence_id,))
    offence = cursor.fetchone()
    cursor.execute("SELECT id, title FROM laws ORDER BY title")
    laws = cursor.fetchall()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/offence_form.html", offence=offence, laws=laws, categories=categories)


@app.route("/admin/offences/delete/<int:offence_id>", methods=["POST"])
@login_required
def admin_delete_offence(offence_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM offences WHERE id = %s", (offence_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Offence deleted.", "warning")
    return redirect(url_for("admin_offences"))


# --- ADMIN: CIVIC EDUCATION ---

@app.route("/admin/civic")
@login_required
def admin_civic():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ce.*, l.title AS law_title
        FROM civic_education ce
        LEFT JOIN laws l ON ce.related_law = l.id
        ORDER BY ce.created_at DESC
    """)
    articles = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/civic.html", articles=articles)


@app.route("/admin/civic/add", methods=["GET", "POST"])
@login_required
def admin_add_civic():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category_id = request.form["category_id"] or None
        related_law = request.form["related_law"] or None

        cursor.execute("""
            INSERT INTO civic_education (title, content, category_id, related_law)
            VALUES (%s, %s, %s, %s)
        """, (title, content, category_id, related_law))
        db.commit()
        cursor.close()
        db.close()
        flash("Civic education article added!", "success")
        return redirect(url_for("admin_civic"))

    cursor.execute("SELECT id, title FROM laws ORDER BY title")
    laws = cursor.fetchall()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/civic_form.html", article=None, laws=laws, categories=categories)


@app.route("/admin/civic/edit/<int:article_id>", methods=["GET", "POST"])
@login_required
def admin_edit_civic(article_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category_id = request.form["category_id"] or None
        related_law = request.form["related_law"] or None

        cursor.execute("""
            UPDATE civic_education SET title=%s, content=%s, category_id=%s, related_law=%s
            WHERE id=%s
        """, (title, content, category_id, related_law, article_id))
        db.commit()
        cursor.close()
        db.close()
        flash("Article updated!", "success")
        return redirect(url_for("admin_civic"))

    cursor.execute("SELECT * FROM civic_education WHERE id = %s", (article_id,))
    article = cursor.fetchone()
    cursor.execute("SELECT id, title FROM laws ORDER BY title")
    laws = cursor.fetchall()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/civic_form.html", article=article, laws=laws, categories=categories)


@app.route("/admin/civic/delete/<int:article_id>", methods=["POST"])
@login_required
def admin_delete_civic(article_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM civic_education WHERE id = %s", (article_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Article deleted.", "warning")
    return redirect(url_for("admin_civic"))


# ==========================
# Run
# ==========================
if __name__ == "__main__":
    app.run(debug=True)