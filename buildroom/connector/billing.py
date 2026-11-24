#!/usr/bin/env python3
"""Build Room access that follows payment. Standard library only.

Stripe sends payment events to POST /webhooks/stripe. Every Build Room payment passes through the one Stripe
account, whichever tool took it: Stripe subscriptions (made in Stripe or by GoHighLevel) arrive as invoices, and
Keap's own recurring charges arrive as plain charges named "Purchase of The Build Room via Keap".

The rule is small. A payment moves the member's paid-through date forward. A cancellation, refund or dispute
stops access at once. A failed payment changes nothing by itself: Stripe and Keap retry, and the existing grace
period (grace_days, 7 by default) ends access that many days after the paid-through date if no retry succeeds.

Settings (host variables, read each time so a change applies at once):
    STRIPE_WEBHOOK_SECRET       the endpoint's signing secret (whsec_...). Without it the webhook answers 503.
    BUILDROOM_BILLING_MODE      observe (default): record what payments say, change no one's access.
                                enforce: payments decide access. off: events are acknowledged and ignored.
    BUILDROOM_STRIPE_PRODUCTS   comma-separated Stripe product IDs that are Build Room (subscriptions, invoices).
    BUILDROOM_CHARGE_MATCH      a pattern matched against a charge's description, for payments taken outside
                                Stripe Billing (Keap). Default: The Build Room
    BUILDROOM_ANNUAL_MIN_CENTS  a matched one-off charge of at least this many cents buys a year; less buys a
                                month. Default 99700.
    BUILDROOM_BILLING_URL       optional link shown to a member whose access stopped for payment.
    STRIPE_API_KEY              optional restricted key with read access to customers and charges. Used only to
                                look up an email or a disputed charge an event does not carry, and by `sync`.
    BUILDROOM_DATA_DIR          billing.json is kept here, next to signups.json.

billing.json holds emails, Stripe customer IDs, dates and event types. Never card details or amounts beyond
what an event says, and never a member's key.

One-off check against Stripe (prints what it would change; writes only with --apply):
    STRIPE_API_KEY=rk_live_... python3 billing.py sync --members members.json --data-dir /data [--apply]
"""
import argparse, hashlib, hmac, json, os, re, sys, threading, time, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

MODES = ("off", "observe", "enforce")
TOLERANCE = 300  # seconds a signed event may be old
KEEP_SEEN, KEEP_LOG, KEEP_REVIEW = 5000, 500, 200
LAPSING_SUB_STATUSES = ("unpaid", "canceled", "incomplete_expired")


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def day(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).date()


def norm(email):
    return (email or "").strip().lower()


def mode():
    m = os.environ.get("BUILDROOM_BILLING_MODE", "observe").strip().lower()
    return m if m in MODES else "observe"


def products():
    return {p.strip() for p in os.environ.get("BUILDROOM_STRIPE_PRODUCTS", "").split(",") if p.strip()}


def charge_pattern():
    try:
        return re.compile(os.environ.get("BUILDROOM_CHARGE_MATCH") or r"\bThe Build Room\b", re.I)
    except re.error:
        return re.compile(r"\bThe Build Room\b", re.I)


def annual_min():
    try:
        return int(os.environ.get("BUILDROOM_ANNUAL_MIN_CENTS", "99700"))
    except ValueError:
        return 99700


def verify(payload, header, secret, now=None):
    """Stripe's signature check: header 't=...,v1=...'; HMAC-SHA256 of '<t>.<raw body>' with the signing secret."""
    if not (payload and header and secret):
        return False
    parts = [p.split("=", 1) for p in header.split(",") if "=" in p]
    try:
        t = int(next(v for k, v in parts if k.strip() == "t"))
    except (StopIteration, ValueError):
        return False
    if abs((now or time.time()) - t) > TOLERANCE:
        return False
    want = hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(want, v.strip()) for k, v in parts if k.strip() == "v1")


def sign(payload, secret, t=None):
    """The header Stripe would send. For tests and for checking a setup by hand."""
    t = int(t or time.time())
    return f"t={t},v1=" + hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()


def stripe_get(path, params=None):
    """GET from the Stripe API with STRIPE_API_KEY, or None when no key is set or the call fails."""
    key = os.environ.get("STRIPE_API_KEY", "").strip()
    if not key:
        return None
    url = "https://api.stripe.com/v1/" + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception:  # a lookup is a nice-to-have; the event still lands in the review list
        return None


def line_product(line):
    return ((line.get("price") or {}).get("product") or ((line.get("pricing") or {}).get("price_details") or {}).get("product")
            or (line.get("plan") or {}).get("product"))


class Billing:
    """billing.json: what payments say about each member, and the switches the host controls."""

    def __init__(self, data_dir, member_emails, fetch=stripe_get):
        self.path = Path(data_dir) / "billing.json" if data_dir else None
        self.member_emails = member_emails  # callable: every email on the host list or signed up
        self.fetch = fetch
        self.lock = threading.Lock()
        self._mem = None

    # -- storage
    @staticmethod
    def empty():
        return {"members": {}, "customers": {}, "manual": [], "review": [], "seen": [], "log": []}

    def load(self):
        if not self.path:
            return self._mem if self._mem is not None else self.empty()
        try:
            d = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return self.empty()
        for k, v in self.empty().items():
            d.setdefault(k, v)
        return d

    def save(self, d):
        d["seen"], d["log"], d["review"] = d["seen"][-KEEP_SEEN:], d["log"][-KEEP_LOG:], d["review"][-KEEP_REVIEW:]
        if not self.path:
            self._mem = d
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, indent=1), encoding="utf-8")
        tmp.replace(self.path)

    # -- what the access check asks
    def overlay(self, member):
        """The member as payments see them, in enforce mode only. Returns (member, decided_by_payment)."""
        if mode() != "enforce" or not member:
            return member, False
        email = norm(member.get("email"))
        d = self.load()
        rec = d["members"].get(email)
        if not rec or email in d["manual"]:
            return member, False
        out = dict(member)
        out["status"] = rec.get("status", member.get("status"))
        if rec.get("paid_through"):
            out["current_until"] = rec["paid_through"]
        return out, True

    # -- reading an event
    def interpret(self, event):
        """Turn one Stripe event into (change, email, customer, note). change is None, ("pay", date),
        ("failed", None), ("lapse", reason) or ("review", None)."""
        typ = event.get("type", "")
        obj = (event.get("data") or {}).get("object") or {}
        cust = obj.get("customer") if isinstance(obj.get("customer"), str) else (obj.get("customer") or {}).get("id")
        brp = products()

        if typ in ("invoice.paid", "invoice.payment_succeeded", "invoice.payment_failed"):
            lines = [l for l in ((obj.get("lines") or {}).get("data") or []) if line_product(l) in brp]
            if not lines:
                return None, None, cust, None
            email = obj.get("customer_email")
            if typ == "invoice.payment_failed":
                return ("failed", None), email, cust, "invoice payment failed"
            ends = [int((l.get("period") or {}).get("end") or 0) for l in lines]
            return ("pay", day(max(ends)) if max(ends) else day(event.get("created") or time.time()) + timedelta(days=31)), email, cust, "invoice paid"

        if typ in ("customer.subscription.updated", "customer.subscription.deleted"):
            items = ((obj.get("items") or {}).get("data") or [])
            if not any(((i.get("price") or {}).get("product") or (i.get("plan") or {}).get("product")) in brp for i in items):
                return None, None, cust, None
            st = obj.get("status")
            if typ == "customer.subscription.deleted" or st in LAPSING_SUB_STATUSES:
                return ("lapse", "subscription " + ("cancelled" if st == "canceled" or typ.endswith("deleted") else st)), None, cust, None
            if st == "past_due":
                return ("failed", None), None, cust, "subscription past due"
            return None, None, cust, None

        if typ in ("charge.succeeded", "charge.failed", "charge.refunded"):
            email = (obj.get("billing_details") or {}).get("email") or obj.get("receipt_email")
            matched = bool(charge_pattern().search(obj.get("description") or ""))
            if typ == "charge.refunded":
                if matched and obj.get("refunded"):
                    return ("lapse", "refunded"), email, cust, None
                if matched:
                    return ("review", None), email, cust, "partial refund of a Build Room charge"
                return ("review-if-member", None), email, cust, "refund on a customer who pays for Build Room"
            if not matched:
                return None, None, cust, None
            if typ == "charge.failed":
                return ("failed", None), email, cust, "charge failed"
            term = 365 if int(obj.get("amount") or 0) >= annual_min() else 31
            return ("pay", day(obj.get("created") or event.get("created") or time.time()) + timedelta(days=term)), email, cust, f"charge paid ({term} days)"

        if typ == "charge.dispute.created":
            ch = obj.get("charge")
            ch = ch if isinstance(ch, dict) else (self.fetch(f"charges/{ch}") if ch else None)
            if ch:
                email = (ch.get("billing_details") or {}).get("email") or ch.get("receipt_email")
                cust = ch.get("customer") if isinstance(ch.get("customer"), str) else cust
                if charge_pattern().search(ch.get("description") or ""):
                    return ("lapse", "disputed"), email, cust, None
                return ("review-if-member", None), email, cust, "dispute on a customer who pays for Build Room"
            return ("review", None), None, None, "dispute opened; set STRIPE_API_KEY to see which charge"
        return None, None, cust, None

    def resolve(self, d, email, cust):
        """The member's email for an event: the event's own email, a customer linked by hand or by an earlier
        payment, or (with STRIPE_API_KEY) the customer's email in Stripe."""
        members = {norm(e) for e in self.member_emails()}
        if cust and d["customers"].get(cust) in members:
            return d["customers"][cust]
        e = norm(email)
        if e in members:
            return e
        if cust:
            c = self.fetch(f"customers/{cust}")
            ce = norm((c or {}).get("email"))
            if ce in members:
                return ce
            e = e or ce
        return e or None

    # -- the webhook
    def handle(self, event):
        """Record one verified event. Returns a short outcome for the log and the HTTP reply."""
        eid, typ = event.get("id"), event.get("type")
        m = mode()
        if m == "off":
            return {"outcome": "off"}
        change, email, cust, note = self.interpret(event)
        if change is None:
            return {"outcome": "ignored", "type": typ}
        created = int(event.get("created") or time.time())
        with self.lock:
            d = self.load()
            if eid and eid in d["seen"]:
                return {"outcome": "duplicate"}
            if eid:
                d["seen"].append(eid)
            who = self.resolve(d, email, cust)
            members = {norm(e) for e in self.member_emails()}
            kind = change[0]
            if kind == "review-if-member":
                if who not in members or who not in d["members"]:
                    self.save(d)
                    return {"outcome": "ignored", "type": typ}
                kind = "review"
            if kind == "review" or who not in members:
                d["review"].append({"at": now_iso(), "type": typ, "event": eid, "customer": cust, "email": who,
                                    "note": note if kind == "review" else "Build Room payment from someone not on the member list"})
                self.save(d)
                return {"outcome": "review", "type": typ}
            rec = d["members"].setdefault(who, {})
            if cust:
                rec["customer"] = cust
                d["customers"].setdefault(cust, who)
            stale = created < int(rec.get("event_created") or 0)
            before = (rec.get("status"), rec.get("paid_through"))
            if kind == "pay":
                new = change[1].isoformat()
                rec["paid_through"] = max(new, rec.get("paid_through") or new)
                if not stale:
                    rec["status"] = "active"
                    rec.pop("reason", None)
                    rec.pop("failed_at", None)
            elif kind == "lapse" and not stale:
                rec["status"], rec["reason"] = "lapsed", change[1]
            elif kind == "failed":
                rec["failed_at"] = now_iso()
                rec.setdefault("status", "active")
            if not stale:
                rec["event_created"] = created
            rec["last"], rec["updated"] = typ, now_iso()
            entry = {"at": now_iso(), "email": who, "type": typ, "change": kind, "mode": m, "stale": stale,
                     "before": before, "after": (rec.get("status"), rec.get("paid_through"))}
            d["log"].append(entry)
            self.save(d)
            print("billing " + json.dumps(entry), flush=True)
            return {"outcome": kind, "type": typ, "stale": stale}

    # -- the host's view and switches (/admin)
    def view(self, grace_days, host_members, today=None):
        """Every member payments have spoken about, what they would get, and the review list."""
        today = today or date.today()
        d = self.load()
        rows = []
        for email, rec in sorted(d["members"].items()):
            pt = rec.get("paid_through")
            ok = rec.get("status") == "active" and (not pt or today <= date.fromisoformat(pt) + timedelta(days=grace_days))
            now_m = host_members.get(email) or {}
            rows.append({"email": email, "status": rec.get("status"), "paid_through": pt, "reason": rec.get("reason"),
                         "failed_at": rec.get("failed_at"), "last": rec.get("last"), "updated": rec.get("updated"),
                         "manual": email in d["manual"], "payments_say": "allowed" if ok else "stopped",
                         "list_says": now_m.get("status", "not on list")})
        return {"mode": mode(), "members": rows, "manual": d["manual"], "review": list(reversed(d["review"]))[:50],
                "log": list(reversed(d["log"]))[:50]}

    def admin(self, body):
        action, email = body.get("action"), norm(body.get("email"))
        with self.lock:
            d = self.load()
            if action == "manual" and email:
                if body.get("on") and email not in d["manual"]:
                    d["manual"].append(email)
                if not body.get("on"):
                    d["manual"] = [e for e in d["manual"] if e != email]
            elif action == "link" and email and str(body.get("customer", "")).startswith("cus_"):
                d["customers"][body["customer"]] = email
            elif action == "dismiss" and body.get("event"):
                d["review"] = [r for r in d["review"] if r.get("event") != body["event"]]
            else:
                return False
            self.save(d)
            return True


# ---------------------------------------------------------------------------- one-off sync against Stripe
def stripe_list(path, params):
    out, after = [], None
    while True:
        p = dict(params, limit=100, **({"starting_after": after} if after else {}))
        page = stripe_get(path, p)
        if not page:
            return out
        out += page.get("data", [])
        if not page.get("has_more") or not page.get("data"):
            return out
        after = page["data"][-1]["id"]


def sync_events(since_days=400):
    """Recent Build Room payments rebuilt as the events the webhook would have seen, oldest first."""
    since = int(time.time()) - since_days * 86400
    evs = []
    for inv in stripe_list("invoices", {"status": "paid", "created[gte]": since}):
        evs.append({"id": "sync_" + inv["id"], "type": "invoice.paid", "created": inv.get("created"), "data": {"object": inv}})
    for sub in stripe_list("subscriptions", {"status": "canceled"}):
        evs.append({"id": "sync_" + sub["id"], "type": "customer.subscription.deleted", "created": sub.get("ended_at") or sub.get("created"), "data": {"object": sub}})
    for ch in stripe_list("charges", {"created[gte]": since}):
        if ch.get("status") == "succeeded" and charge_pattern().search(ch.get("description") or ""):
            evs.append({"id": "sync_" + ch["id"], "type": "charge.succeeded", "created": ch.get("created"), "data": {"object": ch}})
            if ch.get("refunded"):
                evs.append({"id": "sync_r_" + ch["id"], "type": "charge.refunded", "created": ch.get("created"), "data": {"object": ch}})
    return sorted(evs, key=lambda e: int(e.get("created") or 0))


def host_member_emails(members_path, data_dir):
    emails = set()
    env = os.environ.get("BUILDROOM_MEMBERS_JSON")
    try:
        data = json.loads(env) if env else json.loads(Path(members_path).read_text(encoding="utf-8"))
        emails |= {norm(m.get("email")) for m in data.get("members", [])}
    except (OSError, ValueError):
        pass
    try:
        emails |= {norm(m.get("email")) for m in json.loads((Path(data_dir) / "signups.json").read_text(encoding="utf-8")).get("members", [])}
    except (OSError, ValueError, TypeError):
        pass
    return emails


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync", help="rebuild billing.json from Stripe; prints the result, writes only with --apply")
    s.add_argument("--members", default=str(Path(__file__).resolve().parent / "members.json"))
    s.add_argument("--data-dir", default=os.environ.get("BUILDROOM_DATA_DIR", ""))
    s.add_argument("--days", type=int, default=400)
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if not os.environ.get("STRIPE_API_KEY") or not products():
        print("Set STRIPE_API_KEY (read-only key) and BUILDROOM_STRIPE_PRODUCTS first.")
        return 1
    emails = host_member_emails(a.members, a.data_dir)
    target = Billing(a.data_dir if a.apply else None, lambda: emails)
    os.environ["BUILDROOM_BILLING_MODE"] = "observe"  # recording is the same in every mode; this only keeps "off" from skipping it
    if not a.apply and a.data_dir:  # start from what is already recorded, so the dry run shows the real result
        target._mem = Billing(a.data_dir, lambda: emails).load()
    for ev in sync_events(a.days):
        target.handle(ev)
    v = target.view(7, {e: {"status": "listed"} for e in emails})
    print(f"\n{'email':<40} {'payments say':<13} {'paid through':<12} reason")
    for r in v["members"]:
        print(f"{r['email']:<40} {r['payments_say']:<13} {r['paid_through'] or '-':<12} {r['reason'] or ''}")
    unpaid = sorted(emails - {r["email"] for r in v["members"]})
    print(f"\nOn the member list with no Build Room payment found in Stripe ({len(unpaid)}): mark them Manual on /admin if they are comped.")
    for e in unpaid:
        print("  " + e)
    print(f"\nNeeds a look: {len(v['review'])} payments (not on the member list, partial refunds, disputes).")
    print("Written to billing.json." if a.apply else "Dry run: nothing written. Add --apply to save.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
