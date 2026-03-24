"""
VehicleIQ – AI Vehicle Advisor
Deployment-ready version for Streamlit Community Cloud
"""

# ── 1. Normal imports (no proxy patch needed) ────────────────────────────────────
import json
import re
import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ── 2. Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VehicleIQ – AI Vehicle Advisor",
    page_icon="🚗",
    layout="wide",
)

# ── 3. Styles (unchanged) ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,600;1,9..40,300&display=swap');

:root {
    --bg:        #0c0e13;
    --surface:   #13161e;
    --card:      #181c26;
    --border:    #1f2435;
    --accent:    #e8502a;
    --accent2:   #f0a500;
    --green:     #22c55e;
    --red:       #ef4444;
    --text:      #e8e9ed;
    --muted:     #6b7280;
    --radius:    12px;
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.viq-header {
    display: flex; align-items: baseline; gap: 14px;
    padding: 6px 0 20px;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 28px;
}
.viq-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem; letter-spacing: 3px;
    color: var(--text); line-height: 1;
}
.viq-logo span { color: var(--accent); }
.viq-tagline {
    font-size: 0.75rem; color: var(--muted);
    letter-spacing: 2px; text-transform: uppercase; font-weight: 300;
}

.section-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.95rem; letter-spacing: 2px;
    color: var(--accent2); text-transform: uppercase;
    margin-bottom: 8px; margin-top: 18px;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus { border-color: var(--accent) !important; }
label {
    color: var(--muted) !important; font-size: 0.75rem !important;
    letter-spacing: 1px !important; text-transform: uppercase !important;
    font-weight: 600 !important;
}

.stButton > button {
    background: var(--accent) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.05rem !important; letter-spacing: 2px !important;
    padding: 12px 20px !important; width: 100% !important;
    transition: background .2s, transform .1s !important;
}
.stButton > button:hover {
    background: #c8401c !important; transform: translateY(-1px) !important;
}

/* ── Vehicle card ── */
.vcard {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    margin-bottom: 16px;
    position: relative;
    transition: border-color .2s;
}
.vcard:hover { border-color: var(--accent); }
.vcard.best-pick {
    border: 2px solid var(--accent2);
    background: #191c10;
}
.vcard-badge {
    position: absolute; top: 14px; right: 16px;
    background: var(--accent2); color: #000;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.75rem; letter-spacing: 1.5px;
    padding: 3px 10px; border-radius: 20px;
}
.vcard-rank {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.8rem; color: var(--muted);
    letter-spacing: 2px; margin-bottom: 4px;
}
.vcard-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.45rem; letter-spacing: 1px;
    color: var(--text); margin-bottom: 2px;
}
.vcard-price {
    font-size: 1.05rem; font-weight: 600;
    color: var(--accent2); margin-bottom: 12px;
}
.vcard-specs {
    display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;
}
.spec-chip {
    background: var(--border); color: var(--text);
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: .5px; padding: 4px 10px;
    border-radius: 20px; white-space: nowrap;
}
.vcard-why {
    font-size: 0.85rem; color: #a8adb8;
    margin-bottom: 10px; font-style: italic;
    border-left: 3px solid var(--accent); padding-left: 10px;
}
.vcard-pros-cons {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    font-size: 0.82rem;
}
.pro { color: var(--green); }
.con { color: var(--red); }
.pro::before { content: "✓  "; font-weight: 700; }
.con::before { content: "✗  "; font-weight: 700; }

.market-box {
    background: var(--surface); border: 1px solid var(--border);
    border-left: 4px solid var(--accent); border-radius: var(--radius);
    padding: 16px 20px; margin-bottom: 22px;
    font-size: 0.88rem; color: #a8adb8; line-height: 1.6;
}
.market-box strong { color: var(--text); }

.tips-box {
    background: var(--surface); border: 1px solid var(--border);
    border-left: 4px solid var(--accent2); border-radius: var(--radius);
    padding: 16px 20px; margin-top: 22px;
    font-size: 0.85rem; color: #a8adb8; line-height: 1.8;
}
.tips-box strong { color: var(--accent2); }

.stretch-box {
    background: #0f1420; border: 1px solid var(--border);
    border-radius: var(--radius); padding: 14px 18px; margin-top: 16px;
    font-size: 0.85rem; color: #a8adb8;
}

.placeholder {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 360px; color: var(--muted);
    text-align: center; gap: 14px;
}
.placeholder-icon { font-size: 3.5rem; opacity: .35; }
.placeholder-text { font-size: 0.88rem; line-height: 1.6; max-width: 300px; }

.hist-item {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 12px; margin-bottom: 10px;
    font-size: 0.8rem;
}
.hist-title { font-weight: 600; color: var(--text); margin-bottom: 3px; }
.hist-meta  { color: var(--muted); font-size: 0.72rem; }

.stSpinner > div { border-top-color: var(--accent) !important; }
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── 4. API key & model ────────────────────────────────────────────────────────
# Try to get the key from Streamlit secrets, then fall back to environment variable
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except (KeyError, FileNotFoundError):
    # For local testing: set GOOGLE_API_KEY in your environment or .env
    API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not API_KEY:
        st.error("❌ GOOGLE_API_KEY not found. Set it in Streamlit secrets or environment variable.")
        st.stop()

@st.cache_resource
def get_model():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=API_KEY,
        temperature=0.6,
    )

llm = get_model()

# ── 5. Prompt — strict JSON output (unchanged) ───────────────────────────────
JSON_PROMPT = PromptTemplate(
    template="""
You are VehicleIQ — a world-class vehicle expert and automotive market analyst.

A user wants help selecting the best vehicle. Their requirements:

Vehicle Type : {vehicle_type}
Country      : {country}
Budget (max) : {currency} {budget}
Purpose      : {purpose}
Seats        : {seats}
Transmission : {transmission}
Fuel Type    : {fuel_type}
Brand Pref   : {brand_pref}
Must-Haves   : {must_have}
Drive Type   : {drive_type}
Notes        : {extra_notes}

Respond ONLY with a valid JSON object. No markdown fences, no preamble, no trailing text.

{{
  "market_overview": "<2-3 sentence overview of this vehicle segment in this country at this budget>",
  "recommendations": [
    {{
      "rank": 1,
      "name": "<Make Model Variant>",
      "price": "<price with currency symbol>",
      "specs": {{
        "engine": "<e.g. 1.5L Turbo Petrol>",
        "power": "<e.g. 120 bhp>",
        "fuel_economy": "<e.g. 18 km/l or 35 mpg>",
        "transmission": "<e.g. 6-speed MT>",
        "drive": "<e.g. FWD>"
      }},
      "why_it_fits": "<one sentence on why this suits the user's purpose>",
      "strength": "<key strength>",
      "weakness": "<key weakness>",
      "best_pick": false
    }}
  ],
  "best_pick_rank": 1,
  "buying_tips": ["<tip 1>", "<tip 2>", "<tip 3>"],
  "stretch_picks": ["<Make Model — reason>", "<Make Model — reason>"]
}}

Rules:
- recommendations must contain exactly 5 items ranked 1-5.
- Set best_pick: true on the one vehicle you recommend most strongly; false on all others.
- best_pick_rank must match the rank of that vehicle.
- Use real make/model names, real prices, real specs for {country}.
- Keep all string values concise (no nested markdown or bullet points inside strings).
- Return ONLY the JSON object. Nothing else.
""",
    input_variables=[
        "vehicle_type", "country", "currency", "budget", "purpose",
        "seats", "transmission", "fuel_type", "brand_pref",
        "must_have", "drive_type", "extra_notes",
    ],
)

chain = JSON_PROMPT | llm | StrOutputParser()

# ── 6. Session state (unchanged) ──────────────────────────────────────────────
if "history"     not in st.session_state: st.session_state.history     = []
if "last_result" not in st.session_state: st.session_state.last_result = None
if "last_country" not in st.session_state: st.session_state.last_country = ""

# ── 7. Sidebar — search history (unchanged) ───────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">🕑 Search History</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('<p style="color:#6b7280;font-size:0.8rem;padding-top:6px;">No searches yet.</p>', unsafe_allow_html=True)
    else:
        for h in reversed(st.session_state.history):
            st.markdown(f"""
            <div class="hist-item">
                <div class="hist-title">{h['vehicle_type']} &mdash; {h['country']}</div>
                <div class="hist-meta">{h['currency']} {h['budget']:,} &nbsp;·&nbsp; {h['purpose']}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️  Clear History", key="clear_hist"):
            st.session_state.history     = []
            st.session_state.last_result = None
            st.rerun()

# ── 8. Header (unchanged) ─────────────────────────────────────────────────────
st.markdown("""
<div class="viq-header">
    <div class="viq-logo">Vehicle<span>IQ</span></div>
    <div class="viq-tagline">AI-Powered Vehicle Advisor &nbsp;·&nbsp; Market Intelligence</div>
</div>
""", unsafe_allow_html=True)

# ── 9. Two-column layout (unchanged) ──────────────────────────────────────────
left, right = st.columns([1, 1.65], gap="large")

# ─────────────────────────── LEFT: Input form ─────────────────────────────────
with left:
    st.markdown('<div class="section-label">🔧 Required Details</div>', unsafe_allow_html=True)

    vehicle_type = st.selectbox("Vehicle Type *", [
        "Car", "Bike / Motorcycle", "SUV", "Pickup Truck", "Van / Minivan",
        "Bus / Minibus", "Lorry / Truck", "Electric Vehicle", "3-Wheeler / Auto", "Other",
    ])
    country = st.text_input("Country / Market *", placeholder="e.g. India, USA, UK, Germany")

    col_curr, col_budget = st.columns([1, 2])
    with col_curr:
        currency = st.selectbox("Currency", [
            "INR ₹", "USD $", "GBP £", "AUD A$", "EUR €", "JPY ¥", "SGD $", "Other",
        ])
    with col_budget:
        budget = st.number_input(
            "Max Budget *", min_value=1_000, max_value=100_000_000,
            value=1_500_000, step=50_000,
            help="Upper limit — no vehicle above this price will be shown",
        )

    purpose = st.selectbox("Primary Purpose *", [
        "Daily Commute", "Family Use", "Off-Road / Adventure",
        "Business / Luxury", "Cargo / Utility", "Fun / Performance",
        "Showcase / Prestige", "Long-Distance Touring", "First Vehicle",
    ])

    st.markdown('<div class="section-label">⚙️ Optional Details</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        seats        = st.selectbox("Seats",        ["Any", "1", "2", "4", "5", "6", "7", "7+"])
        fuel_type    = st.selectbox("Fuel Type",    ["Any", "Petrol", "Diesel", "Electric", "Hybrid", "CNG / LPG", "Hydrogen"])
    with c2:
        transmission = st.selectbox("Transmission", ["Any", "Automatic", "Manual", "CVT", "DCT / DSG"])
        drive_type   = st.selectbox("Drive Type",   ["Any", "FWD", "RWD", "AWD / 4WD"])

    brand_pref  = st.text_input("Brand Preference",   placeholder="e.g. Toyota, Honda, BMW")
    must_have   = st.text_input("Must-Have Features",  placeholder="e.g. sunroof, ADAS, 360° camera")
    extra_notes = st.text_area("Additional Notes",     placeholder="e.g. low maintenance, good resale, avoid red colour", height=72)

    go = st.button("🔍  Find My Perfect Vehicle")

# ────────────────────────── RIGHT: Results panel ──────────────────────────────
with right:

    # Trigger generation
    if go:
        if not country.strip():
            st.warning("⚠️  Please enter a Country / Market.")
        else:
            invoke_params = {
                "vehicle_type": vehicle_type,
                "country":      country,
                "currency":     currency,
                "budget":       f"{budget:,}",
                "purpose":      purpose,
                "seats":        seats        if seats        != "Any" else "No preference",
                "transmission": transmission if transmission != "Any" else "No preference",
                "fuel_type":    fuel_type    if fuel_type    != "Any" else "No preference",
                "brand_pref":   brand_pref.strip()  or "No preference",
                "must_have":    must_have.strip()    or "None specified",
                "drive_type":   drive_type   if drive_type   != "Any" else "No preference",
                "extra_notes":  extra_notes.strip()  or "None",
            }

            with st.spinner("🔍  Scanning market data and curating your shortlist…"):
                raw = chain.invoke(invoke_params)

            # Strip accidental markdown fences
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()

            try:
                data = json.loads(raw)
                st.session_state.last_result  = data
                st.session_state.last_country = country
                st.session_state.history.append({
                    "vehicle_type": vehicle_type, "country": country,
                    "currency": currency, "budget": budget, "purpose": purpose,
                })
            except json.JSONDecodeError:
                st.error("⚠️  The AI returned an unexpected format. Please try again.")
                st.code(raw, language="text")
                st.stop()

    # ── Render results ────────────────────────────────────────────────────────
    data = st.session_state.last_result

    if data is None:
        st.markdown("""
        <div class="placeholder">
            <div class="placeholder-icon">🚗</div>
            <div class="placeholder-text">
                Fill in your requirements on the left and click<br>
                <strong style="color:#e8502a">Find My Perfect Vehicle</strong><br>
                to see AI-curated, market-specific recommendations here.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Market overview
        st.markdown(f"""
        <div class="market-box">
            <strong>📊 Market Overview</strong><br>{data.get("market_overview", "")}
        </div>
        """, unsafe_allow_html=True)

        best_rank = data.get("best_pick_rank", 1)

        # Vehicle cards
        for car in data.get("recommendations", []):
            rank     = car.get("rank", "")
            is_best  = (rank == best_rank)
            card_cls = "vcard best-pick" if is_best else "vcard"
            specs    = car.get("specs", {})

            spec_chips = "".join(
                f'<span class="spec-chip">{v}</span>'
                for v in specs.values() if v
            )
            badge = '<div class="vcard-badge">⭐ BEST PICK</div>' if is_best else ""

            st.markdown(f"""
            <div class="{card_cls}">
                {badge}
                <div class="vcard-rank">#{rank} &nbsp; RECOMMENDATION</div>
                <div class="vcard-name">{car.get("name","")}</div>
                <div class="vcard-price">{car.get("price","")}</div>
                <div class="vcard-specs">{spec_chips}</div>
                <div class="vcard-why">{car.get("why_it_fits","")}</div>
                <div class="vcard-pros-cons">
                    <div class="pro">{car.get("strength","")}</div>
                    <div class="con">{car.get("weakness","")}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Buying tips
        tips_html = "".join(f"<li>{t}</li>" for t in data.get("buying_tips", []))
        saved_country = st.session_state.last_country
        st.markdown(f"""
        <div class="tips-box">
            <strong>💡 Buying Tips for {vehicle_type}s in {saved_country}</strong>
            <ul style="margin:8px 0 0 0; padding-left:18px;">{tips_html}</ul>
        </div>
        """, unsafe_allow_html=True)

        # Stretch picks
        stretches = data.get("stretch_picks", [])
        if stretches:
            stretch_html = "".join(f"<li>{s}</li>" for s in stretches)
            st.markdown(f"""
            <div class="stretch-box">
                <strong style="color:var(--accent2);">🔼 Worth a Slight Budget Stretch (+10–15%)</strong>
                <ul style="margin:8px 0 0 0; padding-left:18px;">{stretch_html}</ul>
            </div>
            """, unsafe_allow_html=True)

# ── Footer (unchanged) ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#2a2f42;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;">
    VehicleIQ &nbsp;·&nbsp; AI Vehicle Advisor &nbsp;·&nbsp; Powered by Gemini
    &nbsp;·&nbsp; Prices are indicative — always verify with local dealers
</div>
""", unsafe_allow_html=True)
