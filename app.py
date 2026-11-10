import re
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from seed import LISTINGS, A

app = Flask(__name__)
app.secret_key = "change-me-in-production"
USER_LISTINGS, USERS = [], {}
LOCS = ["Lekki", "Ikeja", "Yaba", "Surulere", "Ajah", "Victoria Island", "Ikoyi"]
KEY = {"stay": "nightly", "rent": "rent", "buy": "sale"}
AMEN = {"wifi": ["wifi", "wi-fi", "internet"], "gym": ["gym", "fitness"], "generator": ["generator", "power", "electric"],
        "parking": ["parking", "car"], "security": ["security", "gated", "safe"], "water": ["water", "borehole"], "ac": [" ac", "air con"]}

def all_listings(): return LISTINGS + USER_LISTINGS
def safe_next(n): return n if n and n.startswith("/") and not n.startswith("//") else None

@app.context_processor
def inject(): return {"user": session.get("user")}

def page(name, tpl=None, **kw): return render_template(tpl or f"{name}.html", page=name, **kw)

@app.route("/")
def home(): return page("home", "index.html")
@app.route("/search")
def search(): return page("search")
@app.route("/ai-search")
def ai_page(): return page("ai", "ai-search.html")
@app.route("/favourites")
def favourites(): return page("favourites")
@app.route("/list-property")
def list_property(): return page("list", "list-property.html")

@app.route("/property/<int:pid>")
def property_page(pid):
    if pid < 1000 and not any(p["id"] == pid for p in LISTINGS): abort(404)
    return page("property", pid=pid)

@app.route("/dashboard")
def dashboard():
    if not session.get("user"): return redirect(url_for("auth", next="/dashboard"))
    return page("dashboard")

@app.route("/auth", methods=["GET", "POST"])
def auth():
    err, action = None, request.form.get("action", "login")
    if request.method == "POST":
        email, pw = request.form.get("email", "").strip().lower(), request.form.get("password", "")
        if "@" not in email or len(pw) < 6:
            err = "Enter a valid email and a password of at least 6 characters."
        elif action == "signup":
            if email in USERS: err = "That email already has an account. Log in instead."
            else: USERS[email] = {"name": request.form.get("name", "").strip() or email.split("@")[0].title(), "pw": generate_password_hash(pw)}
        else:
            u = USERS.get(email)
            if not u or not check_password_hash(u["pw"], pw): err = "Incorrect email or password."
        if not err:
            session["user"] = USERS[email]["name"]
            return redirect(safe_next(request.args.get("next")) or url_for("dashboard"))
    return page("auth", error=err, tab=action)

@app.route("/auth/google")
def google():  # Placeholder: wire to real Google OAuth before launch
    session["user"] = "Google User"
    return redirect(safe_next(request.args.get("next")) or url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))

@app.route("/api/listings", methods=["GET", "POST"])
def api_listings():
    if request.method == "GET": return jsonify(all_listings())
    d = request.get_json(silent=True) or {}
    if not d.get("title") or not d.get("location"): return jsonify(error="Title and location are required"), 400
    num = lambda k: int(d[k]) if str(d.get(k) or "").isdigit() else None
    p = dict(id=1000 + len(USER_LISTINGS), title=str(d["title"])[:90], location=d["location"], type=d.get("type", "Flat"),
             beds=num("beds") or 1, baths=num("baths") or 1, area=num("area") or 50, nightly=num("nightly"),
             rent=num("rent"), service=round((num("rent") or 0) * 0.1, -3), sale=num("sale"), badges=["New"],
             amenities=[a for a in d.get("amenities", []) if a in A], vs_avg=0, roi=8.0, rating=4.5,
             images=(d.get("images") or [])[:4] or LISTINGS[0]["images"][:1], desc=str(d.get("desc", ""))[:600])
    USER_LISTINGS.append(p)
    return jsonify(p), 201

@app.route("/api/listings/<int:pid>")
def api_listing(pid):
    p = next((x for x in all_listings() if x["id"] == pid), None)
    return jsonify(p) if p else (jsonify(error="Not found"), 404)

def money(m):
    n = float(m.group(1).replace(",", ""))
    u = (m.group(2) or "").lower()
    return n * (1e9 if u.startswith("b") else 1e6 if u.startswith("m") else 1e3 if u == "k" else 1)

@app.route("/api/ai-search", methods=["POST"])
def ai_search():
    q = " " + ((request.get_json(silent=True) or {}).get("q", "")).lower() + " "
    loc = next((l for l in LOCS if l.lower() in q), None)
    bm = re.search(r"(\d)\s*[- ]?\s*(?:bed|br)", q)
    beds = int(bm.group(1)) if bm else (1 if re.search(r"studio|self.?contain", q) else None)
    bud = re.search(r"(?:under|below|max|budget|within|up to|less than|₦|ngn)\s*₦?\s*(\d[\d,]*(?:\.\d+)?)\s*(million|billion|m|b|k)?\b", q)
    budget = money(bud) if bud else None
    dm = re.search(r"(\d+)\s*(night|week|month|day)", q)
    days = int(dm.group(1)) * {"night": 1, "day": 1, "week": 7, "month": 30}[dm.group(2)] if dm else None
    if re.search(r"\b(buy|purchase|invest|for sale|own)\b", q): mode = "buy"
    elif re.search(r"year|annual|/yr|\brent\b", q): mode = "rent"
    elif dm or re.search(r"short.?let|stay|holiday|vacation|night", q): mode = "stay"
    else: mode = "rent"
    amen = [a for a, ws in AMEN.items() if any(w in q for w in ws)]
    k = KEY[mode]
    def run(use_loc, use_beds, use_bud, use_am):
        r = []
        for p in all_listings():
            if not p.get(k): continue
            if use_loc and loc and p["location"] != loc: continue
            if use_beds and beds and (p["beds"] < 4 if beds >= 4 else p["beds"] != beds): continue
            if use_bud and budget and p[k] * (days if mode == "stay" and budget > 500000 and days else 1) > budget: continue
            if use_am and not all(a in p["amenities"] for a in amen): continue
            r.append(p)
        return sorted(r, key=lambda p: p[k])
    relaxed, res = [], run(1, 1, 1, 1)
    for step, label in [((1, 1, 1, 0), "amenities"), ((1, 0, 1, 0), "bedrooms"), ((1, 0, 0, 0), "budget"), ((0, 0, 0, 0), "location")]:
        if res: break
        res = run(*step); relaxed.append(label)
    return jsonify(mode=mode, ids=[p["id"] for p in res], plan=dict(location=loc, beds=beds, budget=budget, amenities=amen, days=days), relaxed=relaxed)

if __name__ == "__main__":
    app.run(debug=True)
