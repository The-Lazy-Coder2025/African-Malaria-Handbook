from flask import Flask, render_template, request, redirect, url_for, abort, flash
import json, pathlib
from flask_mail import Mail, Message

app = Flask(__name__)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='tryhardpython635@gmail.com',  # use an app password, not your real password!
    MAIL_PASSWORD='brxz yvwz bqxs adbs',       # see below
    MAIL_DEFAULT_SENDER='tryhardpython635@gmail.com'
)

mail = Mail(app)

app.config['SECRET_KEY'] = "something-unique-and-secret"

# --------- Load JSON once at startup ---------
DATA_DIR = pathlib.Path(__file__).parent / "data"

PAPER_FILE = DATA_DIR / "thesis_extracted.json"
TABLE_FILE = DATA_DIR / "table.json"

with PAPER_FILE.open(encoding="utf-8") as fp:
    J = json.load(fp)
PAPERS = J["drug_interactions"]
INDEX = {p["slug"]: p for p in PAPERS}

with TABLE_FILE.open(encoding="utf-8") as fp:
    TABLES = json.load(fp)
TABLE_INDEX = {t["slug"]: t for t in TABLES}


# ----- Risk badge helper -----
def badge_class(risk):
    if risk <= 3: return "low"
    if risk <= 6: return "mod"
    return "high"
app.jinja_env.globals['badge_class'] = badge_class

# ----- Standard pages -----
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")

# ----- Search -----
@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return render_template("search.html")
    q_low = q.lower()
    # Exact slug? redirect to paper
    if q_low in INDEX:
        return redirect(url_for("paper", slug=q_low))
    # Else search by substring in title
    hits = [p for p in PAPERS if q_low in p["title"].lower()]
    return render_template("results.html", query=q, hits=hits)

# ----- Paper details (with table if available) -----
@app.route("/paper/<path:slug>")
def paper(slug):
    rec = INDEX.get(slug)
    table = TABLE_INDEX.get(slug)
    if not rec:
        abort(404)
    return render_template("paper.html", rec=rec, table=table)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        msgbody = request.form.get("message")
        subject = f"New contact form submission from {name or 'No Name'}"
        if not msgbody:
            flash("Please enter a message.", "danger")
            return render_template("contact.html")
        try:
            msg = Message(
                subject=subject,
                sender=email or app.config['MAIL_DEFAULT_SENDER'],
                recipients=["tryhardpython635@gmail.com"],
                body=f"From: {name} <{email}>\n\n{msgbody}"
            )
            mail.send(msg)
            flash("Message sent! Thank you for reaching out.", "success")
            return redirect(url_for("contact"))
        except Exception as e:
            flash(f"Error sending message: {e}", "danger")
            return render_template("contact.html")
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
