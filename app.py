import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
import re
import time
from multiprocessing import Pool, cpu_count

st.set_page_config(page_title="ParText — Sentiment Processor", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════
# CSS + PARTICLE ANIMATION via components.html
# ══════════════════════════════════════════════════════════
def inject_css():
    components.html("""<!DOCTYPE html><html><head><script>
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

  :root {
    --cyan:   #00d4ff;
    --cyan2:  #0099cc;
    --green:  #00ff88;
    --red:    #ff3d6e;
    --yellow: #ffc94d;
    --bg:     #03080f;
    --card:   rgba(0,20,40,0.92);
    --border: rgba(0,212,255,0.18);
  }

  *, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

  html, body { background:var(--bg) !important; }

  [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(ellipse 60% 40% at 20% 20%, rgba(0,100,200,0.09) 0%, transparent 60%),
      radial-gradient(ellipse 50% 40% at 80% 80%, rgba(0,180,255,0.07) 0%, transparent 60%),
      radial-gradient(ellipse 80% 60% at 50% 0%,  rgba(0,212,255,0.06) 0%, transparent 55%),
      var(--bg) !important;
    font-family:'Exo 2',sans-serif !important;
    color:#cce8f8 !important;
  }

  [data-testid="stHeader"] { background:transparent !important; }
  #MainMenu, footer, header { visibility:hidden !important; }
  [data-testid="stToolbar"] { display:none !important; }
  .block-container { padding:1.5rem 2.5rem 4rem !important; max-width:100% !important; }

  /* ── Scanlines ── */
  [data-testid="stAppViewContainer"]::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,212,255,0.012) 3px,rgba(0,212,255,0.012) 4px);
    animation:scan 12s linear infinite;
  }
  @keyframes scan { from{background-position:0 0} to{background-position:0 100px} }

  /* ── Corner vignette ── */
  [data-testid="stAppViewContainer"]::after {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:radial-gradient(ellipse 100% 100% at 50% 50%, transparent 50%, rgba(0,5,12,0.7) 100%);
  }

  /* ═══════════════════════════
     SIDEBAR
  ═══════════════════════════ */
  [data-testid="stSidebar"] {
    background:linear-gradient(160deg,#010a14 0%,#020d1a 60%,#010810 100%) !important;
    border-right:1px solid rgba(0,212,255,0.12) !important;
    width:250px !important; min-width:250px !important;
    box-shadow:4px 0 40px rgba(0,212,255,0.04) !important;
  }
  [data-testid="stSidebarContent"] { padding:0 !important; }
  [data-testid="stSidebarCollapseButton"] { display:none !important; }
  section[data-testid="stSidebar"] { transform:none !important; display:block !important; visibility:visible !important; }

  [data-testid="stSidebar"] .stButton > button {
    width:100% !important; background:transparent !important;
    border:none !important; border-left:2px solid transparent !important;
    color:rgba(0,180,220,0.4) !important;
    font-family:'Exo 2',sans-serif !important; font-size:12px !important;
    font-weight:600 !important; letter-spacing:2.5px !important;
    text-transform:uppercase !important; padding:13px 20px !important;
    text-align:left !important; border-radius:0 !important;
    box-shadow:none !important; transition:all 0.25s !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(0,212,255,0.06) !important;
    border-left-color:rgba(0,212,255,0.4) !important;
    color:var(--cyan) !important; box-shadow:none !important;
  }
  [data-testid="stSidebar"] .stButton > button:focus { box-shadow:none !important; outline:none !important; }

  /* ═══════════════════════════
     HEADER
  ═══════════════════════════ */
  .hdr-wrap { text-align:center; padding:2.8rem 0 2.2rem; position:relative; }
  .hdr-eyebrow {
    display:inline-flex; align-items:center; gap:8px;
    font-family:'Exo 2',sans-serif; font-size:10px; font-weight:700;
    letter-spacing:5px; color:var(--cyan); text-transform:uppercase;
    border:1px solid rgba(0,212,255,0.25); padding:5px 18px 5px 14px;
    border-radius:20px; margin-bottom:20px;
    background:rgba(0,212,255,0.04);
    box-shadow:0 0 20px rgba(0,212,255,0.08);
  }
  .hdr-eyebrow-dot {
    width:6px; height:6px; border-radius:50%; background:var(--cyan);
    box-shadow:0 0 8px var(--cyan); animation:blink 2s ease-in-out infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  .hdr-title {
    font-family:'Orbitron',sans-serif;
    font-size:clamp(26px,4.5vw,52px); font-weight:900;
    line-height:1.05; letter-spacing:1px; color:#fff;
    text-shadow:0 0 40px rgba(0,212,255,0.5), 0 0 100px rgba(0,212,255,0.15);
    margin-bottom:14px;
  }
  .hdr-title .accent { color:var(--cyan); position:relative; }
  .hdr-title .accent::after {
    content:''; position:absolute; bottom:-3px; left:0; right:0; height:2px;
    background:linear-gradient(90deg,transparent,var(--cyan),transparent);
    box-shadow:0 0 10px var(--cyan);
  }
  .hdr-sub {
    font-size:13px; color:rgba(160,210,240,0.5);
    letter-spacing:2px; text-transform:uppercase; font-weight:300;
  }
  .hdr-sub span { color:rgba(0,212,255,0.5); margin:0 8px; }

  /* ═══════════════════════════
     SECTION HEADER
  ═══════════════════════════ */
  .sec-hdr {
    font-family:'Orbitron',sans-serif; font-size:10px; font-weight:700;
    letter-spacing:4px; color:rgba(0,212,255,0.6); text-transform:uppercase;
    margin:30px 0 16px; display:flex; align-items:center; gap:14px;
  }
  .sec-hdr::before { content:''; width:8px; height:8px; border:1.5px solid var(--cyan); transform:rotate(45deg); flex-shrink:0; box-shadow:0 0 6px rgba(0,212,255,0.5); }
  .sec-hdr::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(0,212,255,0.3),transparent); }

  /* ═══════════════════════════
     UPLOAD CARD
  ═══════════════════════════ */
  .upload-card {
    position:relative;
    background:linear-gradient(135deg,rgba(0,16,32,0.97) 0%,rgba(0,10,22,0.99) 100%);
    border:1px solid var(--border); border-radius:6px;
    padding:40px 48px 36px; margin-bottom:24px; overflow:hidden;
  }
  .upload-card::before {
    content:''; position:absolute; top:0; left:15%; right:15%; height:1px;
    background:linear-gradient(90deg,transparent,var(--cyan),rgba(0,212,255,0.3),transparent);
    box-shadow:0 0 25px 3px rgba(0,212,255,0.3);
  }
  .upload-card::after {
    content:''; position:absolute; bottom:0; right:0; width:80px; height:80px;
    border-bottom:1px solid rgba(0,212,255,0.2); border-right:1px solid rgba(0,212,255,0.2);
  }
  .corner-tr { position:absolute; top:0; right:0; width:80px; height:80px; border-top:1px solid rgba(0,212,255,0.2); border-right:1px solid rgba(0,212,255,0.2); }
  .corner-bl { position:absolute; bottom:0; left:0; width:80px; height:80px; border-bottom:1px solid rgba(0,212,255,0.2); border-left:1px solid rgba(0,212,255,0.2); }
  .corner-tl { position:absolute; top:0; left:0; width:80px; height:80px; border-top:1px solid rgba(0,212,255,0.2); border-left:1px solid rgba(0,212,255,0.2); }

  /* animated grid bg inside card */
  .upload-card-bg {
    position:absolute; inset:0; pointer-events:none; opacity:0.025;
    background-image:linear-gradient(rgba(0,212,255,1) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,1) 1px,transparent 1px);
    background-size:40px 40px;
  }

  .upload-label {
    font-family:'Orbitron',sans-serif; font-size:9px; font-weight:700;
    letter-spacing:4px; color:rgba(0,212,255,0.5); text-transform:uppercase;
    margin-bottom:20px; display:flex; align-items:center; gap:12px;
  }
  .upload-label::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(0,212,255,0.25),transparent); }

  .upload-icon-wrap { text-align:center; margin-bottom:10px; }
  .upload-icon-wrap svg { filter:drop-shadow(0 0 16px rgba(0,212,255,0.6)); animation:float 4s ease-in-out infinite; }
  @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }

  /* file uploader overrides */
  [data-testid="stFileUploader"] { background:transparent !important; }
  [data-testid="stFileUploader"] > div {
    background:rgba(0,212,255,0.025) !important;
    border:1.5px dashed rgba(0,212,255,0.25) !important;
    border-radius:6px !important; padding:28px !important; transition:all .3s !important;
  }
  [data-testid="stFileUploader"] > div:hover {
    border-color:rgba(0,212,255,0.6) !important;
    background:rgba(0,212,255,0.05) !important;
    box-shadow:0 0 40px rgba(0,212,255,0.08) inset, 0 0 40px rgba(0,212,255,0.05) !important;
  }
  [data-testid="stFileUploader"] section { background:transparent !important; border:none !important; }
  [data-testid="stFileUploaderDropzoneInstructions"] { color:rgba(160,210,240,0.45) !important; font-family:'Exo 2',sans-serif !important; font-size:14px !important; font-weight:300 !important; }
  [data-testid="stFileUploaderDropzoneInstructions"] span { color:var(--cyan) !important; font-weight:600 !important; }
  [data-testid="stBaseButton-secondary"] {
    background:rgba(0,212,255,0.08) !important; border:1px solid rgba(0,212,255,0.35) !important;
    color:var(--cyan) !important; font-family:'Exo 2',sans-serif !important;
    font-size:11px !important; font-weight:600 !important; letter-spacing:2px !important; border-radius:4px !important;
    transition:all .2s !important;
  }
  [data-testid="stBaseButton-secondary"]:hover { background:rgba(0,212,255,0.15) !important; box-shadow:0 0 20px rgba(0,212,255,0.2) !important; }

  /* ═══════════════════════════
     CHIPS
  ═══════════════════════════ */
  .chips-row { display:flex; gap:10px; justify-content:center; margin-top:20px; flex-wrap:wrap; }
  .chip {
    display:inline-flex; align-items:center; gap:7px;
    font-family:'Exo 2',sans-serif; font-size:10px; font-weight:600; letter-spacing:2px;
    color:rgba(0,200,240,0.55); border:1px solid rgba(0,212,255,0.12);
    background:rgba(0,212,255,0.03); padding:6px 16px; border-radius:20px; text-transform:uppercase;
  }
  .chip-dot { width:5px; height:5px; border-radius:50%; background:var(--cyan); box-shadow:0 0 8px var(--cyan); animation:blink 3s ease-in-out infinite; }

  /* ═══════════════════════════
     MAIN BUTTONS
  ═══════════════════════════ */
  [data-testid="stMain"] .stButton > button {
    width:100%;
    background:linear-gradient(135deg,rgba(0,212,255,0.12) 0%,rgba(0,120,200,0.08) 100%) !important;
    border:1px solid rgba(0,212,255,0.45) !important; color:var(--cyan) !important;
    font-family:'Orbitron',sans-serif !important; font-size:11px !important;
    font-weight:700 !important; letter-spacing:4px !important;
    padding:16px 0 !important; border-radius:4px !important;
    transition:all .3s !important; text-transform:uppercase !important;
    box-shadow:0 0 25px rgba(0,212,255,0.08), inset 0 0 25px rgba(0,212,255,0.03) !important;
    position:relative !important; overflow:hidden !important;
  }
  [data-testid="stMain"] .stButton > button:hover {
    background:linear-gradient(135deg,rgba(0,212,255,0.2) 0%,rgba(0,140,220,0.15) 100%) !important;
    box-shadow:0 0 50px rgba(0,212,255,0.25), inset 0 0 30px rgba(0,212,255,0.06) !important;
    border-color:var(--cyan) !important; transform:translateY(-1px) !important;
  }

  /* ═══════════════════════════
     SELECTBOX & INPUT
  ═══════════════════════════ */
  [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {
    font-family:'Exo 2',sans-serif !important; font-size:10px !important;
    letter-spacing:3px !important; color:rgba(0,212,255,0.5) !important;
    text-transform:uppercase !important; font-weight:700 !important;
  }
  [data-testid="stSelectbox"] > div > div {
    background:rgba(0,10,25,0.95) !important; border:1px solid rgba(0,212,255,0.2) !important;
    border-radius:4px !important; color:#cce8f8 !important; font-family:'Exo 2',sans-serif !important;
    transition:border-color .2s !important;
  }
  [data-testid="stSelectbox"] > div > div:focus-within { border-color:rgba(0,212,255,0.5) !important; box-shadow:0 0 15px rgba(0,212,255,0.08) !important; }
  [data-testid="stTextInput"] input {
    background:rgba(0,10,25,0.95) !important; border:1px solid rgba(0,212,255,0.2) !important;
    border-radius:4px !important; color:#cce8f8 !important; font-family:'Exo 2',sans-serif !important;
  }
  [data-testid="stTextInput"] input:focus { border-color:rgba(0,212,255,0.5) !important; box-shadow:0 0 15px rgba(0,212,255,0.08) !important; outline:none !important; }

  /* ═══════════════════════════
     METRICS
  ═══════════════════════════ */
  [data-testid="stMetric"] {
    background:linear-gradient(135deg,rgba(0,16,34,0.96),rgba(0,10,24,0.98)) !important;
    border:1px solid var(--border) !important; border-radius:5px !important;
    padding:20px 22px !important; position:relative; overflow:hidden;
    transition:transform .2s, box-shadow .2s !important;
  }
  [data-testid="stMetric"]:hover { transform:translateY(-2px) !important; box-shadow:0 8px 30px rgba(0,212,255,0.1) !important; }
  [data-testid="stMetric"]::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--cyan),rgba(0,212,255,0.2),transparent); }
  [data-testid="stMetric"]::after { content:''; position:absolute; bottom:0; right:0; width:30px; height:30px; border-bottom:1px solid rgba(0,212,255,0.2); border-right:1px solid rgba(0,212,255,0.2); }
  [data-testid="stMetricLabel"] { font-family:'Exo 2',sans-serif !important; font-size:9px !important; font-weight:700 !important; letter-spacing:3px !important; color:rgba(0,212,255,0.45) !important; text-transform:uppercase !important; }
  [data-testid="stMetricValue"] { font-family:'Orbitron',sans-serif !important; font-size:28px !important; font-weight:700 !important; color:#fff !important; text-shadow:0 0 25px rgba(0,212,255,0.4) !important; }

  /* ═══════════════════════════
     BARS
  ═══════════════════════════ */
  .bar-section { background:linear-gradient(135deg,rgba(0,16,32,0.96),rgba(0,10,22,0.98)); border:1px solid var(--border); border-radius:5px; padding:24px 28px; margin-bottom:16px; position:relative; overflow:hidden; }
  .bar-section::before { content:''; position:absolute; top:0; left:15%; right:15%; height:1px; background:linear-gradient(90deg,transparent,rgba(0,212,255,0.2),transparent); }
  .bar-wrap { margin-bottom:18px; }
  .bar-wrap:last-child { margin-bottom:0; }
  .bar-label { font-family:'Exo 2',sans-serif; font-size:11px; font-weight:700; letter-spacing:2px; color:rgba(0,200,240,0.7); text-transform:uppercase; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; }
  .bar-label .bar-val { font-family:'Orbitron',sans-serif; font-size:13px; font-weight:700; }
  .bar-track { background:rgba(255,255,255,0.04); border-radius:3px; height:12px; overflow:hidden; position:relative; }
  .bar-track::before { content:''; position:absolute; inset:0; background:repeating-linear-gradient(90deg,transparent,transparent 20px,rgba(255,255,255,0.02) 20px,rgba(255,255,255,0.02) 21px); }
  .bar-fill { height:100%; border-radius:3px; position:relative; transition:width 1s ease; }
  .bar-fill::after { content:''; position:absolute; top:0; right:0; bottom:0; width:4px; background:rgba(255,255,255,0.4); border-radius:3px; }
  .bar-pos { background:linear-gradient(90deg,rgba(0,180,100,0.7),var(--green)); box-shadow:0 0 12px rgba(0,255,136,0.35); }
  .bar-neg { background:linear-gradient(90deg,rgba(180,30,60,0.7),var(--red));   box-shadow:0 0 12px rgba(255,61,110,0.35); }
  .bar-neu { background:linear-gradient(90deg,rgba(180,140,0,0.7),var(--yellow)); box-shadow:0 0 12px rgba(255,201,77,0.35); }

  /* ═══════════════════════════
     DB BADGE
  ═══════════════════════════ */
  .db-badge {
    display:inline-flex; align-items:center; gap:10px;
    background:linear-gradient(135deg,rgba(0,255,136,0.05),rgba(0,200,100,0.03));
    border:1px solid rgba(0,255,136,0.2); border-radius:4px;
    padding:12px 20px; margin-bottom:8px;
    font-family:'Exo 2',sans-serif; font-size:13px; font-weight:600;
    color:rgba(0,255,136,0.75); letter-spacing:1px;
  }
  .db-badge svg { flex-shrink:0; opacity:0.8; }

  /* ═══════════════════════════
     PROGRESS
  ═══════════════════════════ */
  [data-testid="stProgress"] > div { background:rgba(0,212,255,0.08) !important; border-radius:3px !important; height:6px !important; }
  [data-testid="stProgress"] > div > div { background:linear-gradient(90deg,var(--cyan2),var(--cyan)) !important; box-shadow:0 0 15px rgba(0,212,255,0.6) !important; border-radius:3px !important; }

  /* ═══════════════════════════
     DATAFRAME
  ═══════════════════════════ */
  [data-testid="stDataFrame"] { border:1px solid rgba(0,212,255,0.12) !important; border-radius:5px !important; overflow:hidden !important; }

  /* ═══════════════════════════
     ALERTS
  ═══════════════════════════ */
  [data-testid="stAlert"] { border-radius:4px !important; font-family:'Exo 2',sans-serif !important; font-size:14px !important; font-weight:600 !important; }

  /* ═══════════════════════════
     DOWNLOAD BUTTON
  ═══════════════════════════ */
  [data-testid="stDownloadButton"] > button {
    background:rgba(0,255,136,0.05) !important; border:1px solid rgba(0,255,136,0.25) !important;
    color:var(--green) !important; font-family:'Exo 2',sans-serif !important;
    font-size:11px !important; font-weight:700 !important; letter-spacing:2px !important;
    border-radius:4px !important; transition:all .2s !important;
  }
  [data-testid="stDownloadButton"] > button:hover { background:rgba(0,255,136,0.1) !important; box-shadow:0 0 20px rgba(0,255,136,0.15) !important; }

  /* ═══════════════════════════
     TIMING STAT
  ═══════════════════════════ */
  .time-stat {
    display:inline-flex; align-items:center; gap:8px; margin-top:16px;
    font-family:'Exo 2',sans-serif; font-size:11px; font-weight:600;
    letter-spacing:2px; color:rgba(0,212,255,0.35); text-transform:uppercase;
  }
  .time-stat::before { content:''; width:5px; height:5px; border-radius:50%; background:var(--cyan); box-shadow:0 0 8px var(--cyan); flex-shrink:0; }

  /* ═══════════════════════════
     FOOTER
  ═══════════════════════════ */
  .footer {
    text-align:center; color:rgba(0,180,220,0.2); margin-top:60px;
    font-family:'Exo 2',sans-serif; font-size:10px; letter-spacing:4px; text-transform:uppercase;
  }
  .footer b { color:rgba(0,212,255,0.3); font-weight:600; }
`;
const el = window.parent.document.createElement('style');
el.id = 'partext-theme';
if (!window.parent.document.getElementById('partext-theme')) {
  el.innerHTML = css;
  window.parent.document.head.appendChild(el);
} else {
  window.parent.document.getElementById('partext-theme').innerHTML = css;
}
</script></head><body style="background:transparent;margin:0;padding:0;height:0;overflow:hidden;"></body></html>""",
    height=0, scrolling=False)


# ══════════════════════════════════════════
# SCORING ENGINE
# ══════════════════════════════════════════
PATTERN_RULES = [
    (r"highly recommend|must buy|worth every penny|value for money", 4),
    (r"excellent product|superb product|loved the product|very satisfied", 4),
    (r"best purchase|works perfectly|awesome product|great quality", 3),
    (r"good quality|nice product|happy with the product", 2),
    (r"waste of money|do not buy|not worth|very disappointed", -4),
    (r"worst product|poor quality|stopped working|defective product", -4),
    (r"bad experience|totally useless|very bad|extremely bad", -3),
    (r"damaged product|received damaged|fake product", -3),
    (r"late delivery|delivery was late|poor delivery", -2),
    (r"fast delivery|quick delivery|delivered on time", 2),
    (r"works great|works fine|working perfectly", 3),
    (r"not working|does not work|stopped working", -3),
    (r"as expected|met expectations", 2),
    (r"not as expected|did not meet expectations", -2),
]
WORD_SCORES = {
    "good":1,"nice":1,"excellent":2,"amazing":2,"perfect":2,"satisfied":2,
    "happy":1,"love":2,"great":2,"awesome":2,"best":2,"bad":-1,"poor":-2,
    "worst":-3,"waste":-2,"disappointed":-2,"defective":-2,"damaged":-2,
    "useless":-2,"hate":-2,"problem":-1,"issue":-1,
}
NEGATIONS    = {"not","no","never","none"}
INTENSIFIERS = {"very","extremely","really","too"}

def calculate_score(text):
    original = str(text); low = original.lower(); score = 0
    for pattern, value in PATTERN_RULES:
        if re.search(pattern, low): score += value
    words = re.findall(r"\b\w+\b", low)
    negate, boost = False, 1
    for w in words:
        if w in NEGATIONS:    negate = True; continue
        if w in INTENSIFIERS: boost = 2;     continue
        ws = WORD_SCORES.get(w, 0)
        if negate: ws *= -1; negate = False
        score += ws * boost; boost = 1
    sentiment = "Positive" if score > 1 else ("Negative" if score < -1 else "Neutral")
    return (original, score, sentiment)


# ══════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════
DB_NAME = "flipkart_sentiment.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT,
        score INTEGER, sentiment TEXT, run_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit(); conn.close()

def store_results(rows, run_id):
    conn = sqlite3.connect(DB_NAME)
    conn.executemany(
        "INSERT INTO results (text, score, sentiment, run_id) VALUES (?, ?, ?, ?)",
        [(r[0], r[1], r[2], run_id) for r in rows])
    conn.commit(); conn.close()

init_db()

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
for key, default in {
    "page":"upload","df":None,"selected_col":None,
    "results":None,"filename":"","elapsed":0,"run_id":""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
<div style="padding:32px 22px 22px; border-bottom:1px solid rgba(0,212,255,0.1); margin-bottom:6px;">
  <div style="font-family:'Orbitron',sans-serif; font-size:18px; font-weight:900;
              letter-spacing:2px; color:#00d4ff;
              text-shadow:0 0 30px rgba(0,212,255,0.6),0 0 60px rgba(0,212,255,0.2);">
    PARTEXT
  </div>
  <div style="font-family:'Exo 2',sans-serif; font-size:9px; letter-spacing:3px;
              color:rgba(0,180,220,0.3); text-transform:uppercase; margin-top:6px; font-weight:600;">
    Sentiment Processor &nbsp;v2.0
  </div>
  <div style="margin-top:14px; display:flex; align-items:center; gap:8px;">
    <div style="width:5px;height:5px;border-radius:50%;background:#00ff88;
                box-shadow:0 0 8px #00ff88; animation:blink 2s infinite;"></div>
    <span style="font-family:'Exo 2',sans-serif; font-size:9px; letter-spacing:2px;
                 color:rgba(0,255,136,0.5); text-transform:uppercase; font-weight:600;">System Online</span>
  </div>
</div>
""", unsafe_allow_html=True)

        # Nav label
        st.markdown("""
<div style="font-family:'Exo 2',sans-serif; font-size:8px; font-weight:700;
            letter-spacing:4px; color:rgba(0,180,220,0.25); text-transform:uppercase;
            padding:14px 22px 6px;">Navigation</div>
""", unsafe_allow_html=True)

        # Upload button
        is_upload = st.session_state.page == "upload"
        if is_upload:
            st.markdown("""<style>[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(1) button
            { border-left:2px solid #00d4ff !important; background:rgba(0,212,255,0.07) !important; color:#00d4ff !important; }</style>""",
            unsafe_allow_html=True)
        if st.button("  Upload CSV", key="nav_upload", use_container_width=True):
            st.session_state.page = "upload"; st.session_state.results = None
            st.session_state.df = None; st.rerun()

        # Results button
        has_results = st.session_state.results is not None
        is_results  = st.session_state.page == "results"
        if is_results:
            st.markdown("""<style>[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(2) button
            { border-left:2px solid #00d4ff !important; background:rgba(0,212,255,0.07) !important; color:#00d4ff !important; }</style>""",
            unsafe_allow_html=True)
        if st.button("  Results", key="nav_results", use_container_width=True, disabled=not has_results):
            st.session_state.page = "results"; st.rerun()

        # Divider
        st.markdown("""
<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.12),transparent);margin:16px 0;"></div>
<div style="font-family:'Exo 2',sans-serif;font-size:8px;font-weight:700;
            letter-spacing:4px;color:rgba(0,180,220,0.25);text-transform:uppercase;padding:0 22px 8px;">Status</div>
""", unsafe_allow_html=True)

        # Status
        if st.session_state.df is not None:
            rows = len(st.session_state.df)
            st.markdown(f"""
<div style="padding:8px 22px;font-family:'Exo 2',sans-serif;font-size:11px;font-weight:600;
            letter-spacing:1px;color:rgba(0,255,136,0.6);display:flex;align-items:center;gap:8px;">
  <div style="width:5px;height:5px;border-radius:50%;background:#00ff88;box-shadow:0 0 6px #00ff88;flex-shrink:0;"></div>
  File loaded &middot; {rows:,} rows
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="padding:8px 22px;font-family:'Exo 2',sans-serif;font-size:11px;font-weight:600;
            letter-spacing:1px;color:rgba(0,180,220,0.2);">No file loaded</div>""", unsafe_allow_html=True)

        if has_results:
            total = len(st.session_state.results)
            pos = sum(1 for r in st.session_state.results if r[2]=="Positive")
            neg = sum(1 for r in st.session_state.results if r[2]=="Negative")
            st.markdown(f"""
<div style="padding:6px 22px 4px;font-family:'Exo 2',sans-serif;font-size:11px;font-weight:600;
            letter-spacing:1px;color:rgba(0,255,136,0.6);display:flex;align-items:center;gap:8px;">
  <div style="width:5px;height:5px;border-radius:50%;background:#00ff88;box-shadow:0 0 6px #00ff88;flex-shrink:0;"></div>
  {total:,} records scored
</div>
<div style="padding:4px 22px 4px 35px;font-family:'Exo 2',sans-serif;font-size:10px;
            letter-spacing:1px;color:rgba(0,255,136,0.35);">
  +{pos:,} pos &nbsp; &minus;{neg:,} neg
</div>""", unsafe_allow_html=True)

        # Footer
        st.markdown("""
<div style="position:absolute;bottom:18px;left:0;right:0;text-align:center;
            font-family:'Exo 2',sans-serif;font-size:9px;letter-spacing:3px;
            color:rgba(0,180,220,0.15);text-transform:uppercase;">
  Internship Project
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE 1 — UPLOAD
# ══════════════════════════════════════════
def page_upload():
    inject_css()
    render_sidebar()

    st.markdown("""
<div class='hdr-wrap'>
  <div class='hdr-eyebrow'>
    <div class='hdr-eyebrow-dot'></div>
    Sentiment Analysis System
  </div>
  <div class='hdr-title'>Parallel <span class='accent'>Text</span> Processor</div>
  <div class='hdr-sub'>Upload <span>·</span> Select Column <span>·</span> Run Analysis</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class='upload-card'>
  <div class='upload-card-bg'></div>
  <div class='corner-tl'></div><div class='corner-tr'></div>
  <div class='corner-bl'></div>
  <div class='upload-label'>01 — File Input</div>
  <div class='upload-icon-wrap'>
    <svg width='52' height='52' viewBox='0 0 52 52' fill='none'>
      <rect x='6' y='12' width='40' height='30' rx='3' stroke='#00d4ff' stroke-width='1.5' stroke-dasharray='4 3' fill='none'/>
      <path d='M26 22 L26 38' stroke='#00d4ff' stroke-width='2' stroke-linecap='round'/>
      <path d='M19 29 L26 22 L33 29' stroke='#00d4ff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>
      <circle cx='26' cy='15' r='4' fill='rgba(0,212,255,0.1)' stroke='#00d4ff' stroke-width='1.5'/>
      <circle cx='10' cy='38' r='2' fill='rgba(0,212,255,0.3)'/>
      <circle cx='42' cy='16' r='1.5' fill='rgba(0,212,255,0.2)'/>
    </svg>
  </div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Drop CSV here", type=["csv"], label_visibility="collapsed")

    st.markdown("""
  <div class='chips-row'>
    <div class='chip'><div class='chip-dot'></div>CSV Format</div>
    <div class='chip'><div class='chip-dot'></div>Text Columns</div>
    <div class='chip'><div class='chip-dot'></div>Max 200 MB</div>
    <div class='chip'><div class='chip-dot'></div>UTF-8 / Latin-1</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if uploaded_file is not None:
        df = None
        for enc in ["utf-8", "latin1"]:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc, engine="python"); break
            except UnicodeDecodeError: continue
            except Exception as e: st.error(f"Error reading file: {e}"); break

        if df is None:
            st.error("Could not decode file. Please ensure it is a valid CSV."); return

        text_cols    = df.select_dtypes(exclude=["number"]).columns.tolist()
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        st.success(f"**{uploaded_file.name}** loaded — {len(df):,} rows · {len(df.columns)} columns")
        if numeric_cols:
            st.info(f"{len(numeric_cols)} numeric column(s) excluded. Showing {len(text_cols)} text column(s).")
        if not text_cols:
            st.error("No text columns found in this file."); return

        st.markdown("<div class='sec-hdr'>02 — Select Text Column</div>", unsafe_allow_html=True)
        col_choice = st.selectbox("Choose the column to analyse", text_cols)

        st.markdown("<div class='sec-hdr'>03 — Launch Analysis</div>", unsafe_allow_html=True)
        if st.button("RUN SENTIMENT ANALYSIS"):
            st.session_state.df           = df
            st.session_state.selected_col = col_choice
            st.session_state.filename     = uploaded_file.name
            st.session_state.results      = None
            st.session_state.page         = "results"
            st.rerun()

    st.markdown("<div class='footer'>Built with <b>Streamlit</b> &nbsp;&middot;&nbsp; Internship Project &nbsp;&middot;&nbsp; ParText v2.0</div>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE 2 — RESULTS
# ══════════════════════════════════════════
def page_results():
    inject_css()
    render_sidebar()

    df = st.session_state.df
    col = st.session_state.selected_col
    filename = st.session_state.filename

    st.markdown(f"""
<div class='hdr-wrap'>
  <div class='hdr-eyebrow'>
    <div class='hdr-eyebrow-dot'></div>
    Analysis Complete
  </div>
  <div class='hdr-title'><span class='accent'>Sentiment</span> Report</div>
  <div class='hdr-sub'>{filename} <span>·</span> Column: {col}</div>
</div>
""", unsafe_allow_html=True)

    # ── Process ──
    if st.session_state.results is None:
        texts = df[col].dropna().astype(str).str.strip().tolist()
        st.markdown("<div class='sec-hdr'>Processing Data</div>", unsafe_allow_html=True)
        prog = st.progress(0, text="Initialising parallel workers…")
        status = st.empty(); start = time.time()

        try:
            cores = cpu_count()
            status.markdown(f"<p style='font-family:Exo 2,sans-serif;color:rgba(0,212,255,0.5);font-size:13px;letter-spacing:1px;'>Running across {cores} CPU cores…</p>", unsafe_allow_html=True)
            with Pool(cores) as pool: results = pool.map(calculate_score, texts)
        except Exception:
            status.markdown("<p style='font-family:Exo 2,sans-serif;color:rgba(0,212,255,0.5);font-size:13px;letter-spacing:1px;'>Running in single-process mode…</p>", unsafe_allow_html=True)
            results = [calculate_score(t) for t in texts]

        elapsed = time.time() - start
        prog.progress(0.75, text="Storing to SQLite database…")
        run_id = f"run_{int(time.time())}"
        store_results(results, run_id)
        prog.progress(1.0, text="Complete!")
        time.sleep(0.4); prog.empty(); status.empty()
        st.session_state.results = results
        st.session_state.elapsed = elapsed
        st.session_state.run_id  = run_id

    results   = st.session_state.results
    elapsed   = st.session_state.elapsed
    run_id    = st.session_state.run_id
    res_df    = pd.DataFrame(results, columns=["Text","Score","Sentiment"])
    total     = len(res_df)
    pos_count = (res_df["Sentiment"]=="Positive").sum()
    neg_count = (res_df["Sentiment"]=="Negative").sum()
    neu_count = (res_df["Sentiment"]=="Neutral").sum()
    avg_score = res_df["Score"].mean()
    pos_pct   = (pos_count/total*100) if total else 0
    neg_pct   = (neg_count/total*100) if total else 0
    neu_pct   = (neu_count/total*100) if total else 0

    # DB badge
    st.markdown(f"""
<div class='db-badge'>
  <svg width='15' height='15' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'>
    <ellipse cx='12' cy='5' rx='9' ry='3'/><path d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3'/><path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'/>
  </svg>
  {total:,} records persisted &nbsp;&middot;&nbsp; SQLite &nbsp;&middot;&nbsp; Run: {run_id}
</div>
<div class='time-stat'>Processed {total:,} texts in {elapsed:.3f}s using parallel execution</div>
""", unsafe_allow_html=True)

    # KPIs
    st.markdown("<div class='sec-hdr'>01 — Summary Metrics</div>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Records", f"{total:,}")
    c2.metric("Positive", f"{pos_count:,}")
    c3.metric("Negative", f"{neg_count:,}")
    c4.metric("Neutral",  f"{neu_count:,}")
    c5.metric("Avg Score", f"{avg_score:+.2f}")

    # Bars
    st.markdown("<div class='sec-hdr'>02 — Sentiment Breakdown</div>", unsafe_allow_html=True)
    st.markdown(f"""
<div class='bar-section'>
  <div class='bar-wrap'>
    <div class='bar-label'>
      <span>Positive</span>
      <span class='bar-val' style='color:#00ff88'>{pos_count:,} &nbsp; {pos_pct:.1f}%</span>
    </div>
    <div class='bar-track'><div class='bar-fill bar-pos' style='width:{pos_pct}%'></div></div>
  </div>
  <div class='bar-wrap'>
    <div class='bar-label'>
      <span>Negative</span>
      <span class='bar-val' style='color:#ff3d6e'>{neg_count:,} &nbsp; {neg_pct:.1f}%</span>
    </div>
    <div class='bar-track'><div class='bar-fill bar-neg' style='width:{neg_pct}%'></div></div>
  </div>
  <div class='bar-wrap'>
    <div class='bar-label'>
      <span>Neutral</span>
      <span class='bar-val' style='color:#ffc94d'>{neu_count:,} &nbsp; {neu_pct:.1f}%</span>
    </div>
    <div class='bar-track'><div class='bar-fill bar-neu' style='width:{neu_pct}%'></div></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Table
    st.markdown("<div class='sec-hdr'>03 — Scored Records</div>", unsafe_allow_html=True)
    fc1, fc2 = st.columns([1, 3])
    with fc1: sentiment_filter = st.selectbox("Filter by sentiment", ["All","Positive","Negative","Neutral"])
    with fc2: search_term = st.text_input("Search text", placeholder="Type keywords to filter records…")

    display_df = res_df.copy()
    if sentiment_filter != "All":
        display_df = display_df[display_df["Sentiment"]==sentiment_filter]
    if search_term:
        display_df = display_df[display_df["Text"].str.contains(search_term, case=False, na=False)]

    def colour_sentiment(val):
        if val=="Positive": return "color:#00ff88;font-weight:700"
        if val=="Negative": return "color:#ff3d6e;font-weight:700"
        return "color:#ffc94d;font-weight:700"

    pd.set_option("styler.render.max_elements", len(display_df) * len(display_df.columns) + 1)
    st.dataframe(display_df.style.map(colour_sentiment, subset=["Sentiment"]),
                 use_container_width=True, height=440)

    # Export
    st.markdown("<div class='sec-hdr'>04 — Export Results</div>", unsafe_allow_html=True)
    st.download_button(
        label="  Download Full Results as CSV",
        data=res_df.to_csv(index=False).encode("utf-8"),
        file_name=f"sentiment_{run_id}.csv", mime="text/csv")

    st.markdown("<div class='footer'>Built with <b>Streamlit</b> &nbsp;&middot;&nbsp; Internship Project &nbsp;&middot;&nbsp; ParText v2.0</div>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════
if st.session_state.page == "upload":
    page_upload()
else:
    page_results()