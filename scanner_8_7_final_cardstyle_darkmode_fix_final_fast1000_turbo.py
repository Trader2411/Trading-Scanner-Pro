from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List
import hashlib
import pickle

import pandas as pd
import requests
import streamlit as st
import yfinance as yf
import os

st.set_page_config(page_title="Trading Scanner 8.7 FINAL PRO", layout="wide")

import os

st.markdown("""
<style>
:root {
    --bg-main:#f7f7f8;
    --bg-soft:#ffffff;
    --text-main:#111827;
    --text-soft:#6b7280;
    --border-soft:rgba(15,23,42,0.10);
}

/* Gesamtfläche neutral */
html, body, [data-testid="stAppViewContainer"]{
    background: linear-gradient(180deg, #ffffff 0%, #f3f4f6 100%);
    color: var(--text-main);
}

.block-container{
    max-width:1460px;
    padding-top:0.9rem;
    padding-bottom:2rem;
}

/* Suchfeld und Eingaben */
input, textarea,
.stTextInput input,
.stNumberInput input,
div[data-baseweb="input"] input,
div[data-baseweb="select"] input{
    background:#ffffff !important;
    color:#111827 !important;
    -webkit-text-fill-color:#111827 !important;
}

/* Dunkle Hauptkarten */
.dark-card{
    background:linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
    border:1px solid rgba(148,163,184,0.20) !important;
    border-radius:18px !important;
    padding:16px !important;
    margin-bottom:10px !important;
    color:#e5e7eb !important;
    box-shadow:0 8px 22px rgba(15,23,42,0.10) !important;
}
.dark-card *{
    color:#e5e7eb !important;
}

/* Helle Infoboxen */
.info-card{
    background:#ffffff !important;
    color:#111827 !important;
    border:1px solid var(--border-soft) !important;
    border-radius:18px !important;
}

.event-box{
    background:#eff6ff !important;
    color:#1e3a8a !important;
    border:1px solid #bfdbfe !important;
    border-radius:10px !important;
    padding:0.6rem 0.8rem !important;
    margin:0.4rem 0 0.8rem 0 !important;
}

.mini-link a{
    color:#2563eb !important;
    text-decoration:none !important;
    font-weight:700 !important;
    margin-right:12px !important;
}
.mini-link a:hover{ text-decoration:underline !important; }

/* Tabellen / Metriken */
div[data-testid="stMetric"]{
    background:#ffffff !important;
    border:1px solid var(--border-soft) !important;
    border-radius:16px !important;
}
div[data-testid="stMetric"] *{ color:#111827 !important; }
div[data-testid="stDataFrame"]{
    border-radius:16px !important;
    overflow:hidden !important;
    border:1px solid var(--border-soft) !important;
}
div[data-testid="stDataFrame"] *{ color:#111827 !important; }

/* Header */
.ts-header{
    background:linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(250,250,250,0.98) 100%);
    border:1px solid rgba(148,163,184,0.18);
    border-radius:24px;
    padding:18px 22px;
    margin-bottom:0.8rem;
    box-shadow:0 16px 40px rgba(15,23,42,0.06);
}
.ts-kicker{
    color:#2563eb;
    font-size:0.82rem;
    font-weight:800;
    letter-spacing:0.12em;
    text-transform:uppercase;
    margin-bottom:0.15rem;
}
.ts-title{
    color:#111827;
    font-size:2.15rem;
    font-weight:900;
    line-height:1.05;
    margin:0;
}
.ts-sub{
    color:#6b7280;
    font-size:0.98rem;
    margin-top:0.35rem;
}
.ts-logo-box{
    background:linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border:1px solid rgba(148,163,184,0.18);
    border-radius:22px;
    padding:10px;
}

/* Aktualisieren Button sichtbar */
div.stButton > button{
    background:#0f172a !important;
    color:#ffffff !important;
    border:1px solid #0f172a !important;
    border-radius:14px !important;
    font-weight:800 !important;
}
div.stButton > button p, div.stButton > button span{
    color:#ffffff !important;
}

@media (max-width:900px){
    .ts-title{ font-size:1.55rem; }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
:root { --bg1:#ffffff; --bg2:#f8fafc; --border:rgba(15,23,42,0.10); }
.block-container { max-width:1360px; padding-top:0.8rem; padding-bottom:2rem; }
.badge { display:inline-block; border-radius:999px; padding:0.34rem 0.82rem; color:white; font-size:0.76rem; font-weight:800; white-space:nowrap; }
.dark-card { background:linear-gradient(180deg,var(--bg1) 0%,var(--bg2) 100%); border:1px solid var(--border); border-radius:18px; padding:16px; margin-bottom:10px; color:#0f172a; box-shadow:0 8px 22px rgba(15,23,42,0.06); }
.info-card { background:linear-gradient(180deg,var(--bg1) 0%,var(--bg2) 100%); border:1px solid var(--border); border-radius:18px; padding:14px 16px; margin-bottom:12px; color:#0f172a; }
.info-red { border-color:rgba(220,38,38,0.45); } .info-blue { border-color:rgba(37,99,235,0.45); }
.event-box { background:#eff6ff; color:#1e3a8a; border:1px solid #dbeafe; border-radius:10px; padding:0.6rem 0.8rem; margin:0.4rem 0 0.8rem 0; font-size:0.9rem; }
.card-top { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; }
.metrics-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px; }
.card-col { font-size:0.95rem; line-height:1.65; }
.ampel-box { display:flex; gap:8px; margin-top:8px; margin-bottom:8px; }
.ampel-dot { width:16px; height:16px; border-radius:50%; opacity:0.25; border:1px solid rgba(255,255,255,0.2); }
.ampel-active { opacity:1; box-shadow:0 0 12px rgba(255,255,255,0.25); }
.mini-link a { color:#2563eb; text-decoration:none; font-weight:700; margin-right:12px; }
.mini-link a:hover { text-decoration:underline; }
@media (max-width: 900px) { .metrics-grid { grid-template-columns:1fr; } }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
:root{
  --ts-bg:#f4f7fb;
  --ts-card:#ffffff;
  --ts-border:rgba(15,23,42,0.08);
  --ts-text:#172033;
  --ts-soft:#6b7280;
  --ts-accent:#2563eb;
  --ts-accent-2:#0ea5e9;
}
html, body, [data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, #ffffff 0%, #f3f4f6 100%);
}
.block-container{
  max-width:1460px;
  padding-top:0.9rem;
  padding-bottom:2rem;
}
.ts-header{
  background:linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(250,250,250,0.98) 100%);
  border:1px solid rgba(148,163,184,0.18);
  border-radius:24px;
  padding:18px 22px;
  margin-bottom:0.8rem;
  box-shadow:0 18px 40px rgba(15,23,42,0.06);
}
.ts-kicker{
  color:var(--ts-accent);
  font-size:0.82rem;
  font-weight:800;
  letter-spacing:0.12em;
  text-transform:uppercase;
  margin-bottom:0.15rem;
}
.ts-title{
  color:var(--ts-text);
  font-size:2.25rem;
  font-weight:900;
  line-height:1.05;
  margin:0;
}
.ts-sub{
  color:var(--ts-soft);
  font-size:0.98rem;
  margin-top:0.35rem;
}
.ts-logo-box{
  background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);
  border:1px solid rgba(148,163,184,0.18);
  border-radius:22px;
  padding:10px;
  box-shadow:0 10px 28px rgba(15,23,42,0.05);
}
div[data-testid="stMetric"]{
  background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);
  border:1px solid var(--ts-border);
  box-shadow:0 10px 30px rgba(15,23,42,0.04);
}
div[data-testid="stDataFrame"]{
  border-radius:16px;
  overflow:hidden;
  border:1px solid var(--ts-border);
  box-shadow:0 10px 30px rgba(15,23,42,0.04);
}
div[data-testid="stExpander"]{
  background:rgba(255,255,255,0.92);
  border:1px solid var(--ts-border);
  border-radius:16px;
}
button[data-baseweb="tab"]{
  background:#ffffff;
  border:1px solid rgba(148,163,184,0.22);
  border-radius:999px;
  color:#64748b;
  font-weight:700;
}
button[data-baseweb="tab"][aria-selected="true"]{
  background:linear-gradient(180deg, rgba(37,99,235,0.10), rgba(14,165,233,0.08));
  border-color:rgba(37,99,235,0.35);
  color:#0f172a;
}
div.stButton > button{
  border-radius:14px;
  font-weight:700;
}
</style>
""", unsafe_allow_html=True)

APP_TITLE = "Trading Scanner 8.7 FINAL PRO"

st.markdown("""
<style>
/* --- Final Card / Darkmode Fix --- */
:root{
  --card-bg:#081225;
  --card-bg-2:#0d1a31;
  --card-border:rgba(148,163,184,0.16);
  --card-text:#f8fafc;
  --card-soft:#cbd5e1;
  --card-muted:#94a3b8;
  --panel-bg:rgba(255,255,255,0.04);
  --panel-border:rgba(148,163,184,0.12);
}

@media (prefers-color-scheme: dark){
  html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"]{
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%) !important;
    color:#f8fafc !important;
  }
  .ts-header, .info-card, div[data-testid="stMetric"], div[data-testid="stDataFrame"], div[data-testid="stExpander"]{
    background:linear-gradient(180deg,#111827 0%,#0f172a 100%) !important;
    color:#f8fafc !important;
    border-color:rgba(148,163,184,0.18) !important;
  }
  .ts-title, .ts-sub, .ts-kicker,
  h1, h2, h3, h4, h5, h6, p, span, label, small,
  .stMarkdown, .stCaption, .stSelectbox label, .stNumberInput label, .stToggle label,
  [data-testid="stWidgetLabel"], [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
  [data-testid="stText"], [data-testid="stCaptionContainer"], .st-emotion-cache-10trblm,
  .st-emotion-cache-16idsys, .st-emotion-cache-q8sbsg {
    color:#f8fafc !important;
    -webkit-text-fill-color:#f8fafc !important;
  }
  input, textarea, .stTextInput input, .stNumberInput input,
  div[data-baseweb="input"] input, div[data-baseweb="select"] input,
  div[data-baseweb="select"] > div, div[data-baseweb="base-input"] > div,
  div[data-baseweb="input"] > div {
    background:#0f172a !important;
    color:#f8fafc !important;
    -webkit-text-fill-color:#f8fafc !important;
    border-color:rgba(148,163,184,0.2) !important;
  }
  div[data-baseweb="select"] svg, .stSelectbox svg, .stNumberInput button svg {
    fill:#f8fafc !important;
    color:#f8fafc !important;
  }
  table, thead, tbody, tr, td, th, div[data-testid="stDataFrame"] *,
  [data-testid="stDataFrameResizable"] *, [data-testid="stTable"] *{
    color:#f8fafc !important;
    -webkit-text-fill-color:#f8fafc !important;
  }
}

.scanner-card{
  background:#081a3a !important;
  background-image:radial-gradient(circle at top left, rgba(37,99,235,0.14), transparent 28%), linear-gradient(180deg, #04132d 0%, #081a3a 100%) !important;
  border:1px solid rgba(148,163,184,0.24) !important;
  border-radius:22px !important;
  padding:18px 18px 14px 18px !important;
  color:#f8fafc !important;
  -webkit-text-fill-color:#f8fafc !important;
  box-shadow:0 18px 38px rgba(2,6,23,0.20) !important;
  margin-bottom:10px !important;
}
.scanner-card, .scanner-card *{
  color:#f8fafc !important;
  -webkit-text-fill-color:#f8fafc !important;
}
.scanner-card-top{ display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }
.scanner-title{ font-size:1.7rem; font-weight:900; line-height:1.0; margin:0; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; }
.scanner-subtitle{ color:#dbeafe !important; -webkit-text-fill-color:#dbeafe !important; font-size:0.98rem; margin-top:0.15rem; font-weight:600; }
.scanner-links{ margin-top:0.7rem; }
.scanner-links a{ color:#60a5fa !important; -webkit-text-fill-color:#60a5fa !important; text-decoration:none; font-weight:800; margin-right:12px; }
.scanner-links a:hover{ text-decoration:underline; }
.scanner-trend-badge{ display:inline-flex; align-items:center; gap:6px; margin-top:0.85rem; padding:0.38rem 0.82rem; border-radius:999px; font-size:0.76rem; font-weight:900; letter-spacing:0.02em; text-transform:uppercase; }
.scanner-score-wrap{ text-align:right; min-width:120px; }
.scanner-score-label{ color:#bfdbfe !important; -webkit-text-fill-color:#bfdbfe !important; font-size:0.75rem; font-weight:800; text-transform:uppercase; }
.scanner-score-value{ font-size:2rem; line-height:1; font-weight:900; margin-top:0.2rem; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; }
.scanner-signal-label{ font-size:0.95rem; font-weight:900; margin-top:0.35rem; }
.scanner-grid{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px; }
.scanner-panel{
  background:#0f172a !important;
  background-image:linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(15,23,42,0.94) 100%) !important;
  border:1px solid rgba(148,163,184,0.18) !important;
  border-radius:16px !important;
  padding:14px 16px !important;
  min-height:auto !important;
}
.scanner-panel-label{ color:#bfdbfe !important; -webkit-text-fill-color:#bfdbfe !important; font-size:0.78rem; text-transform:uppercase; font-weight:800; letter-spacing:0.04em; margin-bottom:0.45rem; }
.scanner-panel-row{ margin:0.32rem 0; font-size:0.96rem; color:#f8fafc !important; -webkit-text-fill-color:#f8fafc !important; }
.scanner-row-label{ color:#93c5fd !important; -webkit-text-fill-color:#93c5fd !important; font-size:0.84rem; display:block; margin-bottom:2px; }
.scanner-row-value, .scanner-row-value b{ color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; }
.scanner-panel, .scanner-panel *{ color:#f8fafc !important; -webkit-text-fill-color:#f8fafc !important; }
.scanner-event-strip{ margin-top:10px; background:linear-gradient(90deg, rgba(37,99,235,0.18), rgba(14,165,233,0.08)) !important; border:1px solid rgba(96,165,250,0.24) !important; color:#dbeafe !important; -webkit-text-fill-color:#dbeafe !important; border-radius:12px; padding:0.7rem 0.85rem; font-size:0.9rem; }
.scanner-meta-caption{ color:#94a3b8 !important; -webkit-text-fill-color:#94a3b8 !important; font-size:0.84rem; margin:0.2rem 0 0.65rem 0.15rem; }
label, .stMarkdown, .stMarkdown p, .stTextInput label, .stSelectbox label, .stNumberInput label,
[data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"], .stCaption,
div[data-testid="stMetricLabel"] *, div[data-testid="stMetricValue"] *,
h1, h2, h3, h4, h5, h6 { color:#0f172a !important; -webkit-text-fill-color:#0f172a !important; }
@media (prefers-color-scheme: dark){
  label, .stMarkdown, .stMarkdown p, .stTextInput label, .stSelectbox label, .stNumberInput label,
  [data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"], .stCaption,
  div[data-testid="stMetricLabel"] *, div[data-testid="stMetricValue"] *,
  h1, h2, h3, h4, h5, h6 { color:#f8fafc !important; -webkit-text-fill-color:#f8fafc !important; }
}
@media (max-width: 900px){
  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stSidebar"]{
    background:#f8fafc !important;
    background-image:none !important;
    color:#0f172a !important;
  }
  .block-container{ padding-top:0.35rem !important; }
  .ts-header, .info-card, div[data-testid="stMetric"], div[data-testid="stDataFrame"], div[data-testid="stExpander"]{
    background:#ffffff !important;
    background-image:none !important;
    color:#0f172a !important;
    border-color:rgba(15,23,42,0.10) !important;
  }
  .ts-title, .ts-sub, .ts-kicker,
  label, .stMarkdown, .stMarkdown p, .stTextInput label, .stSelectbox label, .stNumberInput label,
  [data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"], .stCaption,
  div[data-testid="stMetricLabel"] *, div[data-testid="stMetricValue"] *,
  h1, h2, h3, h4, h5, h6 {
    color:#0f172a !important; -webkit-text-fill-color:#0f172a !important;
  }
  input, textarea, .stTextInput input, .stNumberInput input,
  div[data-baseweb="input"] input, div[data-baseweb="select"] input,
  div[data-baseweb="select"] > div, div[data-baseweb="base-input"] > div,
  div[data-baseweb="input"] > div {
    background:#ffffff !important; color:#0f172a !important; -webkit-text-fill-color:#0f172a !important;
  }
  .ts-header{
    padding:12px 12px 14px 12px !important;
    border-radius:18px !important;
    position:relative !important;
    z-index:1 !important;
  }
  .ts-title{ font-size:1.15rem !important; line-height:1.02 !important; }
  .ts-sub{ font-size:0.72rem !important; }
  .scanner-card{ padding:12px 12px 10px 12px !important; border-radius:18px !important; }
  .scanner-card-top{ flex-direction:row !important; align-items:flex-start !important; gap:8px !important; }
  .scanner-title{ font-size:0.96rem !important; }
  .scanner-subtitle{ font-size:0.72rem !important; }
  .scanner-links{ margin-top:0.45rem !important; }
  .scanner-links a{ font-size:0.68rem !important; margin-right:8px !important; }
  .scanner-grid{ grid-template-columns:1fr 1fr !important; gap:8px !important; margin-top:10px !important; }
  .scanner-panel{ padding:8px 9px !important; border-radius:14px !important; }
  .scanner-panel-label{ font-size:0.62rem !important; margin-bottom:0.22rem !important; }
  .scanner-panel-row{ display:grid !important; grid-template-columns:1fr auto !important; column-gap:6px !important; align-items:start !important; font-size:0.60rem !important; line-height:1.15 !important; margin:0.10rem 0 !important; }
  .scanner-row-label{ font-size:0.56rem !important; margin-bottom:0 !important; }
  .scanner-row-value, .scanner-row-value b{ font-size:0.62rem !important; text-align:right !important; }
  .scanner-score-wrap{ text-align:right !important; min-width:72px !important; }
  .scanner-score-label{ font-size:0.56rem !important; }
  .scanner-score-value{ font-size:1.05rem !important; }
  .scanner-signal-label, .scanner-trend-badge{ transform:scale(0.92); transform-origin:left center; }
  .scanner-event-strip{ font-size:0.68rem !important; padding:0.5rem 0.6rem !important; border-radius:10px !important; background:#e0f2fe !important; color:#0f172a !important; -webkit-text-fill-color:#0f172a !important; border-color:#93c5fd !important; }
  .scanner-event-strip *{ color:#0f172a !important; -webkit-text-fill-color:#0f172a !important; }
  .scanner-meta-caption{ font-size:0.62rem !important; margin-left:0.05rem !important; color:#475569 !important; -webkit-text-fill-color:#475569 !important; }
  .stSelectbox label, .stNumberInput label, .stTextInput label, .stToggle label, .stSlider label,
  [data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3,
  .stCaption, [data-testid="stCaptionContainer"], .stSubheader, h1, h2, h3, h4, h5, h6 {
    color:#0f172a !important; -webkit-text-fill-color:#0f172a !important;
  }
  div[data-baseweb="select"] *, div[data-baseweb="base-input"] *, div[data-baseweb="input"] *,
  .stSelectbox *, .stNumberInput *, .stTextInput *, .stToggle *, .stExpander *, summary, details {
    color:#0f172a !important; -webkit-text-fill-color:#0f172a !important;
  }
  div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary *{
    color:#0f172a !important; -webkit-text-fill-color:#0f172a !important; font-weight:700 !important;
  }
  div.stButton > button{
    min-height:42px !important;
    position:relative !important;
    z-index:9999 !important;
    pointer-events:auto !important;
  }
  [data-testid="stHorizontalBlock"]{ gap:0.35rem !important; }
  .mobile-portfolio-banner{ display:flex; flex-direction:column; gap:6px; margin:0.45rem 0 0.7rem 0; }
  .mobile-portfolio-list{ display:none !important; }
  div[data-testid="stDataFrame"]{ display:none !important; }
  .mobile-portfolio-banner .mobile-portfolio-item{ box-shadow:0 6px 16px rgba(15,23,42,0.06); }
  .mobile-portfolio-item{ background:#ffffff; border:1px solid rgba(15,23,42,0.10); border-radius:14px; padding:10px 12px; }
  .mobile-portfolio-top{ display:flex; justify-content:space-between; align-items:center; gap:8px; }
  .mobile-portfolio-symbol{ font-weight:900; color:#0f172a; }
  .mobile-portfolio-reason{ font-size:0.78rem; color:#64748b; margin-top:4px; }
}
@media (max-width: 520px){
  .scanner-grid{ grid-template-columns:1fr 1fr !important; }
  .scanner-panel{ min-width:0 !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ts-header">', unsafe_allow_html=True)
header_left, header_mid, header_right = st.columns([1.0, 5.2, 1.2])

with header_left:
    st.markdown('<div class="ts-logo-box">', unsafe_allow_html=True)
    try:
        for logo_file in ["logo.png", "trading_app_logo.png", "logo.jpg", "logo.jpeg", "logo.webp"]:
            if os.path.exists(logo_file):
                st.image(logo_file, width=120)
                break
    except Exception:
        pass
    st.markdown('</div>', unsafe_allow_html=True)

with header_mid:
    st.markdown('<div class="ts-kicker">Smart Market Scanner</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ts-title">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ts-sub">Saubere Version mit dunklen Hauptkarten, robuster Darkmode-Lesbarkeit, separaten Top-3-Blöcken, schnellerem Chunk-Download und erweitertem 1000+ Scan-Universum.</div>',
        unsafe_allow_html=True
    )

with header_right:
    st.write("")
    if st.button("🔄 Aktualisieren", use_container_width=True, key="refresh_top_header"):
        st.cache_data.clear()
        st.session_state.refresh_counter += 1
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

def load_finnhub_api_key() -> str:
    try:
        secret_val = str(st.secrets["FINNHUB_API_KEY"]).strip()
        if secret_val:
            return secret_val
    except Exception:
        pass

    env_val = os.getenv("FINNHUB_API_KEY", "").strip()
    if env_val:
        return env_val

    for file_name in ["Finnhub API.txt", "finnhub_api.txt", "finnhub_api_key.txt"]:
        path = Path(file_name)
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8", errors="ignore").strip()
                if "=" in content:
                    content = content.split("=", 1)[1].strip().strip('\"').strip("'")
                if content:
                    return content
            except Exception:
                continue

    return "DEIN_FINNHUB_API_KEY_HIER"

FINNHUB_API_KEY = load_finnhub_api_key()

US_TECH = {
    "AAPL":{"name":"Apple","wkn":"865985","type":"Aktie","region":"USA"},
    "MSFT":{"name":"Microsoft","wkn":"870747","type":"Aktie","region":"USA"},
    "NVDA":{"name":"NVIDIA","wkn":"918422","type":"Aktie","region":"USA"},
    "AMD":{"name":"Advanced Micro Devices","wkn":"863186","type":"Aktie","region":"USA"},
    "AMZN":{"name":"Amazon","wkn":"906866","type":"Aktie","region":"USA"},
    "META":{"name":"Meta Platforms","wkn":"A1JWVX","type":"Aktie","region":"USA"},
    "GOOGL":{"name":"Alphabet A","wkn":"A14Y6F","type":"Aktie","region":"USA"},
    "NFLX":{"name":"Netflix","wkn":"552484","type":"Aktie","region":"USA"},
    "TSLA":{"name":"Tesla","wkn":"A1CX3T","type":"Aktie","region":"USA"},
    "AVGO":{"name":"Broadcom","wkn":"A2JG9Z","type":"Aktie","region":"USA"},
    "ADBE":{"name":"Adobe","wkn":"871981","type":"Aktie","region":"USA"},
    "CSCO":{"name":"Cisco","wkn":"878841","type":"Aktie","region":"USA"},
    "INTC":{"name":"Intel","wkn":"855681","type":"Aktie","region":"USA"},
    "QCOM":{"name":"Qualcomm","wkn":"883121","type":"Aktie","region":"USA"},
    "AMAT":{"name":"Applied Materials","wkn":"865177","type":"Aktie","region":"USA"},
    "MU":{"name":"Micron","wkn":"869020","type":"Aktie","region":"USA"},
}
US_MARKET = {
    "XOM":{"name":"Exxon Mobil","wkn":"852549","type":"Aktie","region":"USA"},
    "CAT":{"name":"Caterpillar","wkn":"850598","type":"Aktie","region":"USA"},
    "JPM":{"name":"JPMorgan Chase","wkn":"850628","type":"Aktie","region":"USA"},
    "GS":{"name":"Goldman Sachs","wkn":"920332","type":"Aktie","region":"USA"},
    "BAC":{"name":"Bank of America","wkn":"858388","type":"Aktie","region":"USA"},
    "WMT":{"name":"Walmart","wkn":"860853","type":"Aktie","region":"USA"},
    "COST":{"name":"Costco","wkn":"888351","type":"Aktie","region":"USA"},
    "LLY":{"name":"Eli Lilly","wkn":"858560","type":"Aktie","region":"USA"},
    "UNH":{"name":"UnitedHealth","wkn":"869561","type":"Aktie","region":"USA"},
    "GE":{"name":"GE Aerospace","wkn":"851144","type":"Aktie","region":"USA"},
    "NKE":{"name":"Nike","wkn":"866993","type":"Aktie","region":"USA"},
    "DE":{"name":"Deere","wkn":"850866","type":"Aktie","region":"USA"},
    "CVX":{"name":"Chevron","wkn":"852552","type":"Aktie","region":"USA"},
}
EUROPE = {
    "DTE.DE":{"name":"Deutsche Telekom","wkn":"555750","type":"Aktie","region":"Europa"},
    "SAP.DE":{"name":"SAP","wkn":"716460","type":"Aktie","region":"Europa"},
    "SIE.DE":{"name":"Siemens","wkn":"723610","type":"Aktie","region":"Europa"},
    "MUV2.DE":{"name":"Munich Re","wkn":"843002","type":"Aktie","region":"Europa"},
    "ALV.DE":{"name":"Allianz","wkn":"840400","type":"Aktie","region":"Europa"},
    "BAS.DE":{"name":"BASF","wkn":"BASF11","type":"Aktie","region":"Europa"},
    "BMW.DE":{"name":"BMW","wkn":"519000","type":"Aktie","region":"Europa"},
    "MBG.DE":{"name":"Mercedes-Benz","wkn":"710000","type":"Aktie","region":"Europa"},
    "VOW3.DE":{"name":"Volkswagen Vz","wkn":"766403","type":"Aktie","region":"Europa"},
    "AIR.PA":{"name":"Airbus","wkn":"938914","type":"Aktie","region":"Europa"},
    "MC.PA":{"name":"LVMH","wkn":"853292","type":"Aktie","region":"Europa"},
    "ASML.AS":{"name":"ASML","wkn":"A1J4U4","type":"Aktie","region":"Europa"},
    "RHM.DE":{"name":"Rheinmetall","wkn":"703000","type":"Aktie","region":"Europa"},
    "IFX.DE":{"name":"Infineon","wkn":"623100","type":"Aktie","region":"Europa"},
    "NOKIA.HE":{"name":"Nokia","wkn":"870737","type":"Aktie","region":"Europa"},
    "ADS.DE":{"name":"Adidas","wkn":"A1EWWW","type":"Aktie","region":"Europa"},
    "PRY.MI":{"name":"Prysmian","wkn":"A0MP84","type":"Aktie","region":"Europa"},
}
EM_CHINA = {
    "BABA":{"name":"Alibaba","wkn":"A117ME","type":"Aktie","region":"Emerging"},
    "PDD":{"name":"PDD Holdings","wkn":"A2JRK6","type":"Aktie","region":"Emerging"},
    "JD":{"name":"JD.com","wkn":"A112ST","type":"Aktie","region":"Emerging"},
    "BIDU":{"name":"Baidu","wkn":"A0F5DE","type":"Aktie","region":"Emerging"},
    "NIO":{"name":"NIO","wkn":"A2N4PB","type":"Aktie","region":"Emerging"},
    "XPEV":{"name":"XPeng","wkn":"A2QBX7","type":"Aktie","region":"Emerging"},
    "LI":{"name":"Li Auto","wkn":"A2P93Z","type":"Aktie","region":"Emerging"},
    "TSM":{"name":"TSMC ADR","wkn":"909800","type":"Aktie","region":"Emerging"},
}
ROHSTOFFE = {
    "GC=F":{"name":"Gold","wkn":"-","type":"Rohstoff","region":"Rohstoff"},
    "SI=F":{"name":"Silber","wkn":"-","type":"Rohstoff","region":"Rohstoff"},
    "CL=F":{"name":"WTI Öl","wkn":"-","type":"Rohstoff","region":"Rohstoff"},
    "BZ=F":{"name":"Brent Öl","wkn":"-","type":"Rohstoff","region":"Rohstoff"},
    "NG=F":{"name":"Erdgas","wkn":"-","type":"Rohstoff","region":"Rohstoff"},
    "HG=F":{"name":"Kupfer","wkn":"-","type":"Rohstoff","region":"Rohstoff"},
}
KRYPTO = {
    "BTC-USD":{"name":"Bitcoin","wkn":"-","type":"Krypto","region":"Krypto"},
    "ETH-USD":{"name":"Ethereum","wkn":"-","type":"Krypto","region":"Krypto"},
    "SOL-USD":{"name":"Solana","wkn":"-","type":"Krypto","region":"Krypto"},
    "LINK-USD":{"name":"Chainlink","wkn":"-","type":"Krypto","region":"Krypto"},
}

SMALL_CAPS = {
    "PLTR":{"name":"Palantir","wkn":"A2QA4J","type":"Small Cap / Hot Stock","region":"USA"},
    "SOUN":{"name":"SoundHound AI","wkn":"A3CMVV","type":"Small Cap / Hot Stock","region":"USA"},
    "IONQ":{"name":"IonQ","wkn":"A3C4QT","type":"Small Cap / Hot Stock","region":"USA"},
    "RKLB":{"name":"Rocket Lab","wkn":"A3CUPJ","type":"Small Cap / Hot Stock","region":"USA"},
    "SOFI":{"name":"SoFi Technologies","wkn":"A2QPMG","type":"Small Cap / Hot Stock","region":"USA"},
    "HIMS":{"name":"Hims & Hers Health","wkn":"A2QMYY","type":"Small Cap / Hot Stock","region":"USA"},
    "RIOT":{"name":"Riot Platforms","wkn":"A2H51D","type":"Small Cap / Hot Stock","region":"USA"},
    "MARA":{"name":"MARA Holdings","wkn":"A2QQ4A","type":"Small Cap / Hot Stock","region":"USA"},
    "LMND":{"name":"Lemonade","wkn":"A2P7Z1","type":"Small Cap / Hot Stock","region":"USA"},
    "UPST":{"name":"Upstart","wkn":"A2QJL7","type":"Small Cap / Hot Stock","region":"USA"},
    "ASTS":{"name":"AST SpaceMobile","wkn":"A3DEXX","type":"Small Cap / Hot Stock","region":"USA"},
    "CLOV":{"name":"Clover Health","wkn":"A2QJX9","type":"Small Cap / Hot Stock","region":"USA"},
}
HOT_STOCKS = {
    "SMCI":{"name":"Super Micro Computer","wkn":"A0MKJF","type":"Hot Stock","region":"USA"},
    "ARM":{"name":"Arm Holdings ADR","wkn":"A3EUCD","type":"Hot Stock","region":"USA"},
    "APP":{"name":"AppLovin","wkn":"A2QR0K","type":"Hot Stock","region":"USA"},
    "CAVA":{"name":"CAVA Group","wkn":"A3DSVY","type":"Hot Stock","region":"USA"},
    "RGTI":{"name":"Rigetti Computing","wkn":"A3C3N3","type":"Hot Stock","region":"USA"},
    "QBTS":{"name":"D-Wave Quantum","wkn":"A3C5JL","type":"Hot Stock","region":"USA"},
    "SERV":{"name":"Serve Robotics","wkn":"A40X9Q","type":"Hot Stock","region":"USA"},
    "BBAI":{"name":"BigBear.ai","wkn":"A3CWRM","type":"Hot Stock","region":"USA"},
    "OKLO":{"name":"Oklo","wkn":"A40YFM","type":"Hot Stock","region":"USA"},
    "LUNR":{"name":"Intuitive Machines","wkn":"A3ESN2","type":"Hot Stock","region":"USA"},
}

BENCHMARK_SYMBOL = "URTH"
EURUSD_SYMBOL = "EURUSD=X"
DATA_DIR = Path("data")
PORTFOLIO_FILE = DATA_DIR / "scanner_7_4_final_portfolio.csv"
WATCHLIST_FILE = DATA_DIR / "scanner_7_4_final_watchlist.csv"
PORTFOLIO_COLUMNS = ["Symbol","Name","WKN","Typ","Kaufdatum","Kaufkurs €","Stück","Stop €","Ziel €","Notiz"]

EXTENDED_US_TARGET = 1200
DOWNLOAD_CHUNK_SIZE = 300
PREFILTER_PERIOD = "2mo"
FULL_SCAN_PERIOD = "1y"
CACHE_VERSION = "fast1000_turbo_v1"
RAW_CACHE_MAX_AGE_MINUTES = 180
ANALYSIS_CACHE_MAX_AGE_MINUTES = 60
CACHE_DIR = DATA_DIR / "cache"
RAW_CACHE_DIR = CACHE_DIR / "raw_downloads"
ANALYSIS_CACHE_DIR = CACHE_DIR / "analysis"

def _clean_yahoo_symbol(symbol: str) -> str:
    cleaned = str(symbol).strip().upper().replace(".", "-")
    if not cleaned:
        return ""
    blocked_tokens = ["/", "^", "=", "WARRANT", "RIGHT", "UNIT"]
    if any(token in cleaned for token in blocked_tokens):
        return ""
    return cleaned


def _ensure_cache_dirs():
    ensure_data_dir()
    RAW_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _stable_cache_key(prefix: str, payload: str) -> str:
    digest = hashlib.md5(f"{CACHE_VERSION}|{prefix}|{payload}".encode("utf-8")).hexdigest()
    return digest


def _cache_is_fresh(path: Path, max_age_minutes: int) -> bool:
    if not path.exists():
        return False
    age_seconds = (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds()
    return age_seconds <= max_age_minutes * 60


def _load_pickled_dataframe(path: Path) -> pd.DataFrame:
    try:
        with open(path, "rb") as f:
            obj = pickle.load(f)
        return obj if isinstance(obj, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _save_pickled_dataframe(path: Path, df: pd.DataFrame) -> None:
    try:
        with open(path, "wb") as f:
            pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        pass


@st.cache_data(show_spinner=False, ttl=86400)
def get_extended_us_universe(target_size: int = EXTENDED_US_TARGET) -> Dict[str, Dict[str, str]]:
    if not finnhub_available():
        return {}

    try:
        r = requests.get(
            "https://finnhub.io/api/v1/stock/symbol",
            params={"exchange": "US", "token": FINNHUB_API_KEY},
            timeout=20,
        )
        data = r.json() if r.ok else []
    except Exception:
        return {}

    if not isinstance(data, list):
        return {}

    preferred_names = ["common stock", "adr", "american depositary share", "ordinary shares"]
    blocked_names = ["etf", "fund", "warrant", "rights", "unit", "preferred", "trust", "bond", "note", "debenture"]

    def sort_key(item: dict):
        symbol = str(item.get("displaySymbol") or item.get("symbol") or "").upper()
        desc = str(item.get("description") or "")
        is_preferred = 0 if any(tag in desc.lower() for tag in preferred_names) else 1
        return (is_preferred, len(symbol), symbol)

    filtered: Dict[str, Dict[str, str]] = {}
    for item in sorted(data, key=sort_key):
        raw_symbol = str(item.get("displaySymbol") or item.get("symbol") or "")
        symbol = _clean_yahoo_symbol(raw_symbol)
        if not symbol or symbol in filtered:
            continue

        description = str(item.get("description") or symbol).strip()
        desc_lower = description.lower()
        if any(tag in desc_lower for tag in blocked_names):
            continue
        if len(symbol) > 6 or len(symbol) < 1:
            continue
        if symbol.count("-") > 1:
            continue
        if not any(ch.isalpha() for ch in symbol):
            continue

        filtered[symbol] = {
            "name": description,
            "wkn": "-",
            "type": "Aktie",
            "region": "USA",
        }
        if len(filtered) >= target_size:
            break

    return filtered


def build_extended_universe(base_assets: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    extended = dict(base_assets)
    extended.update(get_extended_us_universe(EXTENDED_US_TARGET))
    return extended


def ensure_multiindex_download(raw: pd.DataFrame, symbols_chunk: List[str]) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        return raw
    if not symbols_chunk:
        return raw
    symbol = symbols_chunk[0]
    wrapped = raw.copy()
    wrapped.columns = pd.MultiIndex.from_product([[symbol], wrapped.columns])
    return wrapped


def chunked_symbols(symbols: List[str], chunk_size: int = DOWNLOAD_CHUNK_SIZE):
    for i in range(0, len(symbols), chunk_size):
        yield symbols[i:i + chunk_size]


def download_history_in_chunks(symbols_tuple, period: str) -> pd.DataFrame:
    symbols = [str(s) for s in symbols_tuple if str(s).strip()]
    if not symbols:
        return pd.DataFrame()

    _ensure_cache_dirs()
    frames: List[pd.DataFrame] = []

    for chunk in chunked_symbols(symbols, DOWNLOAD_CHUNK_SIZE):
        chunk_symbols = tuple(sorted(chunk))
        cache_key = _stable_cache_key("raw", f"{period}|{'|'.join(chunk_symbols)}")
        cache_path = RAW_CACHE_DIR / f"{cache_key}.pkl"

        if _cache_is_fresh(cache_path, RAW_CACHE_MAX_AGE_MINUTES):
            cached_df = _load_pickled_dataframe(cache_path)
            if not cached_df.empty:
                frames.append(cached_df)
                continue

        try:
            raw = yf.download(
                list(chunk_symbols),
                period=period,
                interval="1d",
                group_by="ticker",
                progress=False,
                auto_adjust=False,
                threads=True,
                repair=False,
            )
            raw = ensure_multiindex_download(raw, list(chunk_symbols))
            if raw is not None and not raw.empty:
                _save_pickled_dataframe(cache_path, raw)
                frames.append(raw)
        except Exception:
            if cache_path.exists():
                cached_df = _load_pickled_dataframe(cache_path)
                if not cached_df.empty:
                    frames.append(cached_df)
            continue

    if not frames:
        return pd.DataFrame()
    if len(frames) == 1:
        return frames[0]
    return pd.concat(frames, axis=1)


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_portfolio():
    ensure_data_dir()
    if not PORTFOLIO_FILE.exists():
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS)
    try:
        df = pd.read_csv(PORTFOLIO_FILE)
    except Exception:
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS)
    for c in PORTFOLIO_COLUMNS:
        if c not in df.columns:
            df[c] = None
    return df[PORTFOLIO_COLUMNS].copy()

def save_portfolio(df):
    ensure_data_dir()
    out = df.copy()
    for c in PORTFOLIO_COLUMNS:
        if c not in out.columns:
            out[c] = None
    out[PORTFOLIO_COLUMNS].to_csv(PORTFOLIO_FILE, index=False)

def load_watchlist():
    ensure_data_dir()
    if not WATCHLIST_FILE.exists():
        return pd.DataFrame(columns=["Symbol","Name","Typ"])
    try:
        df = pd.read_csv(WATCHLIST_FILE)
    except Exception:
        return pd.DataFrame(columns=["Symbol","Name","Typ"])
    for c in ["Symbol","Name","Typ"]:
        if c not in df.columns:
            df[c] = None
    return df[["Symbol","Name","Typ"]].copy()

def save_watchlist(df):
    ensure_data_dir()
    out = df.copy()
    for c in ["Symbol","Name","Typ"]:
        if c not in out.columns:
            out[c] = None
    out[["Symbol","Name","Typ"]].to_csv(WATCHLIST_FILE, index=False)

def add_to_watchlist(row):
    df = load_watchlist()
    symbol = str(row["Symbol"])
    if symbol not in df["Symbol"].astype(str).values:
        new = pd.DataFrame([{"Symbol":symbol,"Name":str(row["Name"]),"Typ":str(row.get("Typ",""))}])
        save_watchlist(pd.concat([df,new], ignore_index=True))

def build_assets(selection: str) -> Dict[str, Dict[str, str]]:
    assets: Dict[str, Dict[str, str]] = {}
    if selection in ("Alle", "Smart Scanner Pro"):
        for d in [US_TECH, US_MARKET, EUROPE, EM_CHINA, ROHSTOFFE, KRYPTO, SMALL_CAPS, HOT_STOCKS]:
            assets.update(d)
        return build_extended_universe(assets)
    mapping = {
        "US Tech": build_extended_universe(dict(US_TECH | US_MARKET | SMALL_CAPS | HOT_STOCKS)),
        "US Markt": build_extended_universe(dict(US_MARKET)),
        "Europa": EUROPE,
        "Emerging / China": EM_CHINA,
        "Rohstoffe": ROHSTOFFE,
        "Krypto": KRYPTO,
        "Small Caps": SMALL_CAPS,
        "Hot Stocks": HOT_STOCKS,
    }
    return dict(mapping.get(selection, {}))

def normalize_df(df):
    if df is None or df.empty:
        return pd.DataFrame()
    result = df.copy()
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = [c[0] if isinstance(c, tuple) else c for c in result.columns]
    rename_map = {}
    for col in result.columns:
        low = str(col).strip().lower()
        if low == "open": rename_map[col] = "Open"
        elif low == "high": rename_map[col] = "High"
        elif low == "low": rename_map[col] = "Low"
        elif low == "close": rename_map[col] = "Close"
        elif low == "adj close": rename_map[col] = "Adj Close"
        elif low == "volume": rename_map[col] = "Volume"
    result = result.rename(columns=rename_map)
    keep = [c for c in ["Open","High","Low","Close","Adj Close","Volume"] if c in result.columns]
    result = result[keep].copy()
    for c in result.columns:
        result[c] = pd.to_numeric(result[c], errors="coerce")
    if "Close" not in result.columns:
        return pd.DataFrame()
    return result.dropna(subset=["Close"]).sort_index()

def as_series(obj):
    if isinstance(obj, pd.DataFrame):
        if obj.shape[1] == 0:
            return pd.Series(dtype=float)
        return pd.to_numeric(obj.iloc[:,0], errors="coerce")
    return pd.to_numeric(obj, errors="coerce")

def safe_float(v):
    try:
        if v is None or pd.isna(v):
            return None
        return float(v)
    except Exception:
        return None

def clamp(value, low, high):
    return max(low, min(high, float(value)))

def fmt_eur(v):
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.2f} €"

def fmt_num(v):
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.2f}"

def is_eur_symbol(symbol):
    return symbol.endswith((".DE",".PA",".AS",".MI",".MC",".BR",".VI"))

def analyse_link_de(name):
    from requests.utils import quote
    return f"https://www.finanzen.net/suchergebnis.asp?_search={quote(str(name))}"

def finanzen_search_link(name):
    from requests.utils import quote
    return f"https://www.finanzen.net/suchergebnis.asp?_search={quote(str(name))}"

def onvista_link(wkn):
    return "#" if not wkn or wkn == "-" else f"https://www.onvista.de/suche?searchValue={wkn}"

@st.cache_data(show_spinner=False, ttl=1800)
def get_fx_eurusd():
    try:
        df = yf.download(EURUSD_SYMBOL, period="10d", interval="1d", progress=False, auto_adjust=False, threads=False)
        df = normalize_df(df)
        close = as_series(df["Close"]).dropna()
        if close.empty:
            return 1.0
        val = safe_float(close.iloc[-1])
        return val if val and val > 0 else 1.0
    except Exception:
        return 1.0

def to_eur(price, symbol):
    if price is None:
        return None
    if is_eur_symbol(symbol):
        return price
    fx = get_fx_eurusd()
    return price / fx if fx else price

def from_eur_to_native(value_eur, symbol):
    if value_eur is None:
        return None
    if is_eur_symbol(symbol):
        return value_eur
    fx = get_fx_eurusd()
    return value_eur * fx if fx else value_eur

def fmt_dual_price(value_eur, symbol):
    if value_eur is None or pd.isna(value_eur):
        return "-"
    native = from_eur_to_native(value_eur, symbol)
    return f"{float(value_eur):.2f} € ({float(native):.2f} $)" if native is not None else fmt_eur(value_eur)

def risk_reward_ratio(price_eur, stop_eur, target_eur, trend):
    if None in (price_eur, stop_eur, target_eur):
        return None
    if trend == "Long":
        risk = price_eur - stop_eur
        reward = target_eur - price_eur
    elif trend == "Short":
        risk = stop_eur - price_eur
        reward = price_eur - target_eur
    else:
        return None
    if risk is None or reward is None or risk <= 0:
        return None
    return reward / risk

def calculate_position_size(account_size, risk_pct, entry_eur, stop_eur):
    if None in (account_size, risk_pct, entry_eur, stop_eur):
        return (None, None, None)
    risk_amount = account_size * (risk_pct / 100.0)
    risk_per_unit = abs(entry_eur - stop_eur)
    if risk_per_unit <= 0:
        return (risk_amount, None, None)
    units = risk_amount / risk_per_unit
    position_value = units * entry_eur if entry_eur is not None else None
    return (risk_amount, units, position_value)

@st.cache_data(show_spinner=False, ttl=1800)
def batch_download_history(symbols_tuple):
    return download_history_in_chunks(symbols_tuple, FULL_SCAN_PERIOD)

def extract_symbol_history(raw, symbol):
    try:
        if isinstance(raw.columns, pd.MultiIndex) and symbol in raw.columns.get_level_values(0):
            return normalize_df(raw[symbol].copy())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def finnhub_available():
    return FINNHUB_API_KEY.strip() not in ("", "DEIN_FINNHUB_API_KEY_HIER")

@st.cache_data(show_spinner=False, ttl=90)
def finnhub_get_quote(symbol):
    if not finnhub_available():
        return {}
    try:
        r = requests.get("https://finnhub.io/api/v1/quote", params={"symbol":symbol,"token":FINNHUB_API_KEY}, timeout=6)
        return r.json() if r.ok else {}
    except Exception:
        return {}

@st.cache_data(show_spinner=False, ttl=1200)
def finnhub_get_news(symbol):
    if not finnhub_available():
        return []
    try:
        to_dt = datetime.now(timezone.utc).date()
        from_dt = to_dt - timedelta(days=5)
        r = requests.get("https://finnhub.io/api/v1/company-news", params={"symbol":symbol,"from":str(from_dt),"to":str(to_dt),"token":FINNHUB_API_KEY}, timeout=6)
        data = r.json() if r.ok else []
        return data if isinstance(data, list) else []
    except Exception:
        return []

@st.cache_data(show_spinner=False, ttl=1200)
def finnhub_get_recommendation(symbol):
    if not finnhub_available():
        return []
    try:
        r = requests.get("https://finnhub.io/api/v1/stock/recommendation", params={"symbol":symbol,"token":FINNHUB_API_KEY}, timeout=6)
        data = r.json() if r.ok else []
        return data if isinstance(data, list) else []
    except Exception:
        return []

@st.cache_data(show_spinner=False, ttl=1200)
def finnhub_get_earnings(symbol):
    if not finnhub_available():
        return []
    try:
        today = datetime.now(timezone.utc).date()
        future = today + timedelta(days=7)
        r = requests.get("https://finnhub.io/api/v1/calendar/earnings", params={"from":str(today),"to":str(future),"symbol":symbol,"token":FINNHUB_API_KEY}, timeout=6)
        data = r.json() if r.ok else {}
        return data.get("earningsCalendar", []) if isinstance(data, dict) else []
    except Exception:
        return []

def ema(series, period):
    s = as_series(series).dropna()
    return s.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    s = as_series(series).dropna()
    delta = s.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return (100 - (100 / (1 + rs))).fillna(50)

def tsi(series, long=25, short=13):
    s = as_series(series).dropna()
    m = s.diff()
    ema1 = m.ewm(span=long, adjust=False).mean()
    ema2 = ema1.ewm(span=short, adjust=False).mean()
    abs1 = m.abs().ewm(span=long, adjust=False).mean()
    abs2 = abs1.ewm(span=short, adjust=False).mean()
    return (100 * (ema2 / abs2.replace(0, pd.NA))).fillna(0)

def momentum_pct(series, lookback):
    s = as_series(series).dropna()
    if len(s) <= lookback:
        return None
    start = safe_float(s.iloc[-lookback-1]); end = safe_float(s.iloc[-1])
    if start is None or end is None or start == 0:
        return None
    return ((end / start) - 1.0) * 100.0

def atr(df, period=14):
    if df.empty or len(df) < period + 1:
        return None
    high = as_series(df["High"]).dropna()
    low = as_series(df["Low"]).dropna()
    close = as_series(df["Close"]).dropna()
    prev_close = close.shift(1)
    tr = pd.concat([(high-low).abs(), (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    out = tr.rolling(period).mean()
    return safe_float(out.iloc[-1]) if not out.empty else None

def avg_volume(df):
    if "Volume" not in df.columns:
        return None
    vol = as_series(df["Volume"]).dropna()
    if len(vol) < 21:
        return None
    return safe_float(vol.tail(20).mean())

def volume_factor(df):
    avg = avg_volume(df)
    if avg is None or avg == 0:
        return None
    vol = as_series(df["Volume"]).dropna()
    if vol.empty:
        return None
    last = safe_float(vol.iloc[-1])
    return float(last / avg) if last is not None else None

def breakout(df):
    close = as_series(df["Close"]).dropna()
    if len(close) < 55:
        return False
    return bool(safe_float(close.iloc[-1]) > safe_float(close.iloc[-51:-1].max()))

def breakdown(df):
    close = as_series(df["Close"]).dropna()
    if len(close) < 55:
        return False
    return bool(safe_float(close.iloc[-1]) < safe_float(close.iloc[-51:-1].min()))

def near_level(price, level, tolerance=0.02):
    if price is None or level is None or level == 0:
        return False
    return abs(price / level - 1.0) <= tolerance

def trend_channel_position(close, lookback=20):
    s = as_series(close).dropna()
    if len(s) < lookback:
        return "-"
    upper = safe_float(s.tail(lookback).max()); lower = safe_float(s.tail(lookback).min()); current = safe_float(s.iloc[-1])
    if None in (upper, lower, current) or upper == lower:
        return "-"
    pos = (current - lower) / (upper - lower)
    if pos <= 0.33: return "unten"
    if pos >= 0.67: return "oben"
    return "mitte"

def calc_relative_strength(close, bench_close, lookback=63):
    s = as_series(close).rename("s"); b = as_series(bench_close).rename("b")
    joined = pd.concat([s,b], axis=1).dropna()
    if len(joined) <= lookback:
        return None
    s1 = safe_float(joined["s"].iloc[-lookback-1]); s2 = safe_float(joined["s"].iloc[-1]); b1 = safe_float(joined["b"].iloc[-lookback-1]); b2 = safe_float(joined["b"].iloc[-1])
    if None in (s1,s2,b1,b2) or min(s1,s2,b1,b2) <= 0:
        return None
    diff = ((s2/s1)-1)-((b2/b1)-1)
    return clamp(50 + diff * 250, 0, 100)

def score_bucket(value, low, high):
    if value is None or high == low:
        return 50.0
    return clamp((value - low)/(high-low)*100.0, 0, 100)

def deutsches_signal(signal):
    return {
        "EARLY LONG":"Top Trade Long",
        "STRONG BUY":"Bestätigt Long",
        "EARLY SHORT":"Top Trade Short",
        "STRONG SHORT":"Bestätigt Short",
        "SETUP":"Beobachten",
        "NO TRADE":"Kein Signal"
    }.get(signal, signal)

def badge_color(signal):
    return {
        "EARLY LONG":"#22c55e",
        "STRONG BUY":"#22c55e",
        "EARLY SHORT":"#ef4444",
        "STRONG SHORT":"#ef4444",
        "SETUP":"#f59e0b",
        "NO TRADE":"#94a3b8"
    }.get(signal, "#94a3b8")

def trend_badge_colors(trend):
    trend = str(trend)
    if trend == "Long":
        return {"text": "#dcfce7", "bg": "#16a34a", "border": "#22c55e"}
    if trend == "Short":
        return {"text": "#fee2e2", "bg": "#dc2626", "border": "#ef4444"}
    return {"text": "#e2e8f0", "bg": "#475569", "border": "#64748b"}

def signal_label_color(signal):
    return {
        "EARLY LONG": "#22c55e",
        "STRONG BUY": "#22c55e",
        "EARLY SHORT": "#ef4444",
        "STRONG SHORT": "#ef4444",
        "SETUP": "#f59e0b",
        "NO TRADE": "#94a3b8",
    }.get(str(signal), "#94a3b8")

def signal_to_ampel(signal):
    if signal in ("EARLY LONG", "STRONG BUY"): return "GRÜN"
    if signal in ("EARLY SHORT", "STRONG SHORT"): return "ROT"
    if signal == "SETUP": return "GELB"
    return "GRAU"

def fear_greed_label(value):
    if value < 25: return "Extreme Angst"
    if value < 45: return "Angst"
    if value < 55: return "Neutral"
    if value < 75: return "Gier"
    return "Extreme Gier"

def calc_fear_greed(scan_df):
    if scan_df.empty:
        return 50.0, "Neutral"
    score_mean = safe_float(scan_df["Swing-Score Event"].mean()) or 50.0
    rsi_mean = safe_float(scan_df["RSI"].mean()) or 50.0
    rs_mean = safe_float(scan_df["Relative Stärke"].mean()) or 50.0
    vol_mean = safe_float(scan_df["Volumenfaktor"].mean()) or 1.0
    val = score_mean*0.40 + rsi_mean*0.15 + rs_mean*0.25 + clamp(vol_mean*50, 0, 100)*0.20
    return round(clamp(val,0,100),1), fear_greed_label(val)

def entry_text(signal, long_trend, short_trend, is_breakout, is_breakdown, pullback_long, pullback_short):
    if is_breakout and long_trend: return "Ausbruch Long"
    if pullback_long and long_trend: return "Rücksetzer Long"
    if is_breakdown and short_trend: return "Ausbruch Short"
    if pullback_short and short_trend: return "Rücksetzer Short"
    if signal == "EARLY LONG": return "Früher Trendaufbau Long"
    if signal == "EARLY SHORT": return "Früher Trendaufbau Short"
    if signal == "SETUP" and long_trend: return "Trendaufbau Long"
    if signal == "SETUP" and short_trend: return "Trendaufbau Short"
    return "Noch kein sauberer Einstieg"

POSITIVE_NEWS_WORDS = ["beats","beat","surges","upgrade","raises","strong","record","wins","approval","outperform","buyback","partnership"]
NEGATIVE_NEWS_WORDS = ["misses","miss","downgrade","cuts","lawsuit","probe","warning","falls","drop","weaker","sell","hold"]

def get_event_overlay(symbol, assets):
    overlay = {
        "earnings_warning":"","earnings_today":False,"news_note":"","news_url":"",
        "analyst_note":"","analyst_url":"",
        "score_adjustment":0,"position_size_note":"","event_data_status":""
    }
    used_any = False
    earnings = finnhub_get_earnings(symbol)
    if earnings:
        used_any = True
        try:
            e_date = pd.to_datetime(earnings[0].get("date")).date()
            today = datetime.now(timezone.utc).date()
            delta = (e_date - today).days
            if delta == 0:
                overlay["earnings_today"] = True
                overlay["earnings_warning"] = "Quartalszahlen heute"
                overlay["score_adjustment"] -= 12
                overlay["position_size_note"] = "Berichtssaison heute: Positionsgröße reduzieren."
            elif 0 < delta <= 3:
                overlay["earnings_warning"] = f"Quartalszahlen in {delta} Tagen"
                overlay["score_adjustment"] -= 5
        except Exception:
            pass
    recs = finnhub_get_recommendation(symbol)
    if recs:
        used_any = True
        try:
            latest = recs[0]
            positive = int(latest.get("buy",0) or 0) + int(latest.get("strongBuy",0) or 0)
            negative = int(latest.get("hold",0) or 0) + int(latest.get("sell",0) or 0) + int(latest.get("strongSell",0) or 0)
            if negative > positive:
                overlay["analyst_note"] = "Analysten eher schwächer / Downgrade-Risiko"
                overlay["score_adjustment"] -= 8
            elif positive > negative:
                overlay["analyst_note"] = "Analysten eher positiv"
                overlay["score_adjustment"] += 4
        except Exception:
            pass
    news = finnhub_get_news(symbol)
    if news:
        used_any = True
        try:
            titles = " ".join(str(i.get("headline","")).lower() for i in news[:8])
            overlay["news_url"] = ""
            pos_hits = sum(1 for w in POSITIVE_NEWS_WORDS if w in titles)
            neg_hits = sum(1 for w in NEGATIVE_NEWS_WORDS if w in titles)
            if pos_hits > neg_hits and pos_hits > 0:
                overlay["news_note"] = "Frische positive News"
                overlay["score_adjustment"] += 5
            elif neg_hits > pos_hits and neg_hits > 0:
                overlay["news_note"] = "Frische negative News"
                overlay["score_adjustment"] -= 5
        except Exception:
            pass
    overlay["event_data_status"] = "Event-Daten aktiv" if used_any else "Keine Event-Daten verfügbar"
    return overlay

@st.cache_data(show_spinner=False, ttl=1800)
def get_benchmark_close():
    raw = batch_download_history((BENCHMARK_SYMBOL,))
    if raw is None or raw.empty:
        return pd.Series(dtype=float)
    if isinstance(raw.columns, pd.MultiIndex):
        try:
            return as_series(raw["Close"][BENCHMARK_SYMBOL]).dropna()
        except Exception:
            pass
    df = normalize_df(raw)
    return as_series(df["Close"]).dropna() if not df.empty else pd.Series(dtype=float)

def select_balanced_symbols(assets: Dict[str, Dict[str, str]], max_symbols: int) -> List[str]:
    stocks, commodities, crypto = [], [], []
    for sym, meta in assets.items():
        typ = str(meta.get("type",""))
        if typ == "Rohstoff":
            commodities.append(sym)
        elif typ == "Krypto":
            crypto.append(sym)
        else:
            stocks.append(sym)
    if len(assets) <= max_symbols:
        return list(assets.keys())
    comm_n = min(len(commodities), max(2, max_symbols // 10))
    crypto_n = min(len(crypto), max(2, max_symbols // 10))
    stock_n = max_symbols - comm_n - crypto_n
    return (stocks[:stock_n] + commodities[:comm_n] + crypto[:crypto_n])[:max_symbols]

def enrich_top_candidates_with_events(df: pd.DataFrame, assets: Dict[str, Dict[str, str]], top_n: int = 10) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    candidate_idx = out.sort_values(["Swing-Score Event","Day-Score Event"], ascending=False).head(top_n).index
    for idx in candidate_idx:
        symbol = str(out.at[idx, "Symbol"])
        event = get_event_overlay(symbol, assets)
        quote = finnhub_get_quote(symbol)
        q_price = safe_float(quote.get("c")) if quote else None
        if q_price:
            out.at[idx, "Preis €"] = to_eur(q_price, symbol)
        out.at[idx, "Earnings Hinweis"] = event["earnings_warning"]
        out.at[idx, "News Hinweis"] = event["news_note"]
        out.at[idx, "News URL"] = event["news_url"]
        out.at[idx, "Analysten Hinweis"] = event["analyst_note"]
        out.at[idx, "Analysten URL"] = event["analyst_url"]
        out.at[idx, "Positionsgröße Hinweis"] = event["position_size_note"]
        out.at[idx, "Event Status"] = event["event_data_status"]
        adj = float(event.get("score_adjustment", 0) or 0)
        out.at[idx, "Swing-Score Event"] = round(clamp(float(out.at[idx, "Swing-Score"]) + adj, 0, 100), 2)
        out.at[idx, "Day-Score Event"] = round(clamp(float(out.at[idx, "Day-Score"]) + adj, 0, 100), 2)
    return out.sort_values(["Swing-Score Event","Day-Score Event"], ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False, ttl=900)
def batch_download_prefilter(symbols_tuple):
    return download_history_in_chunks(symbols_tuple, PREFILTER_PERIOD)

def _balanced_prefilter_selection(score_rows: List[dict], max_symbols: int) -> List[str]:
    if not score_rows:
        return []
    stocks = [r for r in score_rows if r.get("Typ") not in ("Rohstoff", "Krypto")]
    rohstoffe = [r for r in score_rows if r.get("Typ") == "Rohstoff"]
    kryptos = [r for r in score_rows if r.get("Typ") == "Krypto"]

    if len(score_rows) <= max_symbols:
        return [r["Symbol"] for r in score_rows]

    roh_n = min(len(rohstoffe), max(3, max_symbols // 10))
    kry_n = min(len(kryptos), max(4, max_symbols // 8))
    akt_n = max_symbols - roh_n - kry_n

    selected = stocks[:akt_n] + rohstoffe[:roh_n] + kryptos[:kry_n]
    return [r["Symbol"] for r in selected[:max_symbols]]

def prefilter_assets(assets: Dict[str, Dict[str, str]], prefilter_top_n: int) -> List[str]:
    if not assets:
        st.session_state["prefilter_total"] = 0
        st.session_state["prefilter_selected"] = 0
        return []

    symbols_all = list(assets.keys())
    st.session_state["prefilter_total"] = len(symbols_all)

    if len(symbols_all) <= prefilter_top_n:
        st.session_state["prefilter_selected"] = len(symbols_all)
        return symbols_all

    raw = batch_download_prefilter(tuple(symbols_all))
    rows: List[dict] = []

    for symbol in symbols_all:
        meta = assets[symbol]
        df = extract_symbol_history(raw, symbol)
        if df.empty or len(df) < 40:
            continue

        try:
            close = as_series(df["Close"]).dropna()
            if len(close) < 40:
                continue

            price_native = safe_float(close.iloc[-1])
            if price_native is None or price_native <= 0:
                continue

            avg_vol = avg_volume(df)
            vol_factor_val = volume_factor(df)
            mom1 = momentum_pct(close, 21)
            mom3 = momentum_pct(close, 63)
            atr_native = atr(df, 14)

            atr_pct = None
            if atr_native is not None and price_native > 0:
                atr_pct = (atr_native / price_native) * 100.0

            turnover = None
            if avg_vol is not None:
                turnover = avg_vol * price_native

            if meta["type"] == "Aktie" and avg_vol is not None and avg_vol < 150000:
                continue
            if meta["type"] == "Aktie" and price_native < 1.0:
                continue

            liquidity_score = score_bucket(turnover, 1_000_000, 100_000_000)
            momentum_score = score_bucket(abs(mom1) if mom1 is not None else None, 0, 20) * 0.45 + score_bucket(abs(mom3) if mom3 is not None else None, 0, 35) * 0.55
            volatility_score = score_bucket(atr_pct, 1.0, 10.0)
            volume_score = score_bucket(vol_factor_val, 0.8, 3.0)

            if meta["type"] == "Rohstoff":
                pre_score = momentum_score * 0.45 + volatility_score * 0.35 + volume_score * 0.20
            elif meta["type"] == "Krypto":
                pre_score = momentum_score * 0.45 + volatility_score * 0.30 + volume_score * 0.25
            else:
                pre_score = liquidity_score * 0.35 + momentum_score * 0.30 + volatility_score * 0.20 + volume_score * 0.15

            rows.append({
                "Symbol": symbol,
                "Typ": meta["type"],
                "Vorfilter-Score": round(clamp(pre_score, 0, 100), 2),
            })
        except Exception:
            continue

    rows = sorted(rows, key=lambda x: x["Vorfilter-Score"], reverse=True)
    selected = _balanced_prefilter_selection(rows, prefilter_top_n)
    st.session_state["prefilter_selected"] = len(selected)
    return selected

def _analyze_assets_cache_key(assets: Dict[str, Dict[str, str]], max_symbols: int, top_event_candidates: int, smart_prefilter: bool, prefilter_top_n: int) -> Path:
    _ensure_cache_dirs()
    payload = f"{max_symbols}|{top_event_candidates}|{int(smart_prefilter)}|{prefilter_top_n}|" + "|".join(sorted(assets.keys()))
    return ANALYSIS_CACHE_DIR / f"{_stable_cache_key('analysis', payload)}.pkl"


def analyze_assets(assets: Dict[str, Dict[str, str]], max_symbols: int, top_event_candidates: int, smart_prefilter: bool, prefilter_top_n: int):
    cache_path = _analyze_assets_cache_key(assets, max_symbols, top_event_candidates, smart_prefilter, prefilter_top_n)
    if _cache_is_fresh(cache_path, ANALYSIS_CACHE_MAX_AGE_MINUTES):
        cached_df = _load_pickled_dataframe(cache_path)
        if not cached_df.empty:
            return cached_df

    bench_close = get_benchmark_close()
    prefiltered_symbols = prefilter_assets(assets, prefilter_top_n) if smart_prefilter else list(assets.keys())
    symbols = select_balanced_symbols({s: assets[s] for s in prefiltered_symbols if s in assets}, max_symbols)
    raw = batch_download_history(tuple(symbols))
    rows: List[dict] = []
    for symbol in symbols:
        meta = assets[symbol]
        df = extract_symbol_history(raw, symbol)
        if df.empty or len(df) < 220:
            continue
        try:
            close = as_series(df["Close"]).dropna()
            if len(close) < 220:
                continue
            price_native = safe_float(close.iloc[-1])
            ema50_series = ema(close, 50)
            ema200_series = ema(close, 200)
            ema50 = safe_float(ema50_series.iloc[-1]) if len(ema50_series) else None
            ema200 = safe_float(ema200_series.iloc[-1]) if len(ema200_series) else None
            if price_native is None or ema50 is None or ema200 is None:
                continue

            avg_vol = avg_volume(df)
            vol_factor = volume_factor(df)
            if meta["type"] == "Aktie" and price_native < 5:
                continue
            if meta["type"] == "Aktie" and avg_vol is not None and avg_vol < 500000:
                continue

            rsi_val = safe_float(rsi(close).iloc[-1]) if len(close) else None
            tsi_val = safe_float(tsi(close).iloc[-1]) if len(close) else None
            mom5 = momentum_pct(close, 5)
            mom10 = momentum_pct(close, 10)
            mom21 = momentum_pct(close, 21)
            mom63 = momentum_pct(close, 63)
            rs = calc_relative_strength(close, bench_close, 63)
            is_bo = breakout(df)
            is_bd = breakdown(df)
            kanal = trend_channel_position(close, 20)

            price_eur = to_eur(price_native, symbol)
            atr_eur = to_eur(atr(df, 14), symbol)
            ema50_eur = to_eur(ema50, symbol)

            long_trend = bool(price_native > ema50 > ema200)
            short_trend = bool(price_native < ema50 < ema200)
            early_long = bool(price_native > ema50 and ema50 >= ema200 * 0.985)
            early_short = bool(price_native < ema50 and ema50 <= ema200 * 1.015)

            prev_close = safe_float(close.iloc[-2]) if len(close) >= 2 else None
            pull_long = near_level(price_native, ema50, 0.03) and prev_close is not None and price_native > prev_close
            pull_short = near_level(price_native, ema50, 0.03) and prev_close is not None and price_native < prev_close

            kanal_score = 100.0 if (kanal == "unten" and (long_trend or early_long)) or (kanal == "oben" and (short_trend or early_short)) else 60.0 if kanal == "mitte" else 50.0
            base_swing = (
                (100 if (long_trend or short_trend or early_long or early_short) else 0) * 0.18
                + score_bucket(abs(mom5) if mom5 is not None else None, 0, 8) * 0.14
                + score_bucket(abs(mom10) if mom10 is not None else None, 0, 12) * 0.16
                + score_bucket(abs(mom21) if mom21 is not None else None, 0, 20) * 0.14
                + (rs if rs is not None else 50) * 0.12
                + score_bucket(vol_factor, 0.7, 2.5) * 0.10
                + (100 if (is_bo or is_bd or pull_long or pull_short) else 0) * 0.10
                + kanal_score * 0.06
            )
            base_day = (
                score_bucket(rsi_val, 30, 72) * 0.22
                + (100 if (is_bo or is_bd) else 45) * 0.20
                + score_bucket(vol_factor, 0.7, 2.5) * 0.18
                + score_bucket(tsi_val, -15, 15) * 0.15
                + score_bucket(abs(mom5) if mom5 is not None else None, 0, 8) * 0.15
                + kanal_score * 0.10
            )

            swing_score = round(clamp(base_swing, 0, 100), 2)
            day_score = round(clamp(base_day, 0, 100), 2)

            long_ready = ((mom5 or 0) > 0.8 and (mom10 or 0) > 1.5 and (tsi_val or 0) > -1 and (vol_factor or 0) >= 0.8 and 46 <= (rsi_val or 50) <= 76)
            short_ready = ((mom5 or 0) < -0.8 and (mom10 or 0) < -1.5 and (tsi_val or 0) < 1 and (vol_factor or 0) >= 0.8 and 24 <= (rsi_val or 50) <= 54)

            if long_trend and long_ready and ((is_bo or pull_long) or (mom21 or 0) > 3.0) and (rs or 0) >= 58:
                signal = "STRONG BUY"
            elif short_trend and short_ready and ((is_bd or pull_short) or (mom21 or 0) < -3.0) and (rs or 100) <= 45:
                signal = "STRONG SHORT"
            elif early_long and long_ready and ((mom5 or 0) > 1.2 or pull_long or is_bo):
                signal = "EARLY LONG"
            elif early_short and short_ready and ((mom5 or 0) < -1.2 or pull_short or is_bd):
                signal = "EARLY SHORT"
            elif swing_score >= 54:
                signal = "SETUP"
            else:
                signal = "NO TRADE"

            entry = entry_text(signal, long_trend or early_long, short_trend or early_short, is_bo, is_bd, pull_long, pull_short)

            if signal in ("EARLY LONG","STRONG BUY","SETUP") and (long_trend or early_long):
                stop = price_eur - 1.6 * atr_eur if price_eur is not None and atr_eur is not None else None
                ziel = price_eur + 2.8 * atr_eur if price_eur is not None and atr_eur is not None else None
            elif signal in ("EARLY SHORT","STRONG SHORT","SETUP") and (short_trend or early_short):
                stop = price_eur + 1.6 * atr_eur if price_eur is not None and atr_eur is not None else None
                ziel = price_eur - 2.8 * atr_eur if price_eur is not None and atr_eur is not None else None
            else:
                stop = None
                ziel = None

            rr = risk_reward_ratio(price_eur, stop, ziel, "Long" if (long_trend or early_long) else "Short" if (short_trend or early_short) else "Neutral")
            if rr is not None and rr < 1.2 and signal in ("EARLY LONG","EARLY SHORT","STRONG BUY","STRONG SHORT"):
                signal = "SETUP"

            rows.append({
                "Symbol":symbol,"Name":meta["name"],"WKN":meta.get("wkn","-"),"Typ":meta.get("type",""),"Region":meta.get("region",""),
                "Preis €":price_eur,"EMA50 €":to_eur(ema50, symbol),"RSI":rsi_val,"TSI":tsi_val,"Volumenfaktor":vol_factor,"Relative Stärke":rs,"Trendkanal":kanal,
                "Signal":signal,"Signal Deutsch":deutsches_signal(signal),"Ampel":signal_to_ampel(signal),"Einstieg":entry,"Trend":"Long" if (long_trend or early_long) else "Short" if (short_trend or early_short) else "Neutral",
                "Swing-Score":round(base_swing,2),"Day-Score":round(base_day,2),"Swing-Score Event":swing_score,"Day-Score Event":day_score,
                "Stop €":stop,"Ziel €":ziel,"CRV":rr,"Earnings Hinweis":"","News Hinweis":"","News URL":"","Analysten Hinweis":"",
                "Analysten URL":analyse_link_de(meta["name"]),"Positionsgröße Hinweis":"","Event Status":""
            })
        except Exception:
            continue

    if not rows:
        return pd.DataFrame()
    base_df = pd.DataFrame(rows).sort_values(["Swing-Score Event","Day-Score Event"], ascending=False).reset_index(drop=True)
    result_df = enrich_top_candidates_with_events(base_df, assets, top_n=min(top_event_candidates, len(base_df)))
    _save_pickled_dataframe(cache_path, result_df)
    return result_df

@st.cache_data(show_spinner=False, ttl=1800)
def analyze_top3_block(assets_subset: Dict[str, Dict[str, str]]):
    if not assets_subset:
        return pd.DataFrame()
    subset_max = max(3, len(assets_subset))
    return analyze_assets(
        assets_subset,
        max_symbols=subset_max,
        top_event_candidates=min(3, subset_max),
        smart_prefilter=False,
        prefilter_top_n=subset_max,
    )

def add_to_portfolio(row):
    df = load_portfolio()
    new_row = {"Symbol":row["Symbol"],"Name":row["Name"],"WKN":row["WKN"],"Typ":row["Typ"],"Kaufdatum":str(date.today()),"Kaufkurs €":safe_float(row["Preis €"]) or 0.0,"Stück":1.0,"Stop €":safe_float(row["Stop €"]),"Ziel €":safe_float(row["Ziel €"]),"Notiz":"Aus Signal übernommen"}
    save_portfolio(pd.concat([df,pd.DataFrame([new_row])], ignore_index=True))

def portfolio_signal(symbol, buy_price_eur, shares, all_df):
    match = all_df[all_df["Symbol"] == symbol]
    if match.empty:
        return None
    row = match.iloc[0]
    current = row["Preis €"]; stop = row["Stop €"]
    pnl_pct = ((current / buy_price_eur) - 1.0) * 100.0 if current is not None and buy_price_eur else None
    action = "Halten"; reasons = []
    if current is not None and stop is not None and row["Trend"] != "Short" and current < stop:
        action = "SOFORT VERKAUFEN"; reasons.append("Kurs unter ATR-Stop")
    elif row["Signal"] in ("EARLY SHORT","STRONG SHORT"):
        action = "Verkaufen"; reasons.append("Scanner meldet Short-Signal")
    elif row["Trend"] == "Neutral":
        action = "Verkaufen"; reasons.append("Trend gebrochen")
    elif row["Signal"] in ("EARLY LONG","STRONG BUY") and pnl_pct is not None and pnl_pct < 5:
        action = "Aufstocken"; reasons.append("Long-Signal erneut aktiv")
    elif pnl_pct is not None and row["RSI"] is not None and row["RSI"] > 75:
        action = "Gewinne sichern"; reasons.append("Hoher Gewinn bei hohem RSI")
    else:
        reasons.append("Trend intakt")
    if row["Earnings Hinweis"]:
        reasons.append(row["Earnings Hinweis"])
    return {"Symbol":symbol,"Aktuell €":current,"Stop €":row["Stop €"],"Ziel €":row["Ziel €"],"CRV":row["CRV"],"P&L %":pnl_pct,"Aktion":action,"Grund":" | ".join(reasons)}

def build_portfolio_signals(all_df):
    df = load_portfolio()
    rows = []
    for _, pos in df.iterrows():
        symbol = str(pos.get("Symbol","")).strip().upper()
        if not symbol:
            continue
        row = portfolio_signal(symbol, safe_float(pos.get("Kaufkurs €")) or 0.0, safe_float(pos.get("Stück")) or 0.0, all_df)
        if row:
            rows.append(row)
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    order = {"SOFORT VERKAUFEN":0,"Verkaufen":1,"Gewinne sichern":2,"Aufstocken":3,"Halten":4}
    mapped_sort = out["Aktion"].map(order)
    out["Sort"] = pd.to_numeric(mapped_sort, errors="coerce")
    out["Sort"] = out["Sort"].where(out["Sort"].notna(), 9).astype(int)
    return out.sort_values(["Sort","P&L %"], ascending=[True,False]).drop(columns=["Sort"]).reset_index(drop=True)

def render_fear_greed(value, label):
    value = max(0.0, min(100.0, float(value)))
    html = '<div style="margin-top:6px;max-width:360px;"><div style="position:relative;"><div style="display:flex;height:18px;border-radius:999px;overflow:hidden;border:1px solid #cbd5e1;background:#fff;"><div style="background:#991b1b;width:20%;"></div><div style="background:#dc2626;width:20%;"></div><div style="background:#d97706;width:20%;"></div><div style="background:#16a34a;width:20%;"></div><div style="background:#166534;width:20%;"></div></div>' + f'<div style="position:absolute;left:calc({value}% - 7px);top:20px;width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:12px solid #0f172a;"></div></div><div style="margin-top:16px;color:#64748b;font-size:0.84rem;">{label}</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_ampel(signal):
    active = signal_to_ampel(signal)
    dots = [("#16a34a","GRÜN"),("#d97706","GELB"),("#dc2626","ROT")]
    html = '<div class="ampel-box">'
    for color, name in dots:
        html += f'<div class="ampel-dot {"ampel-active" if name == active else ""}" style="background:{color};"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_card(row, key_suffix):
    trend = str(row["Trend"])
    is_long = trend == "Long"
    is_short = trend == "Short"
    trend_text = "LONG" if is_long else "SHORT" if is_short else str(trend).upper()
    trend_badge_bg = "#16a34a" if is_long else "#dc2626" if is_short else "#64748b"
    trend_badge_border = "#15803d" if is_long else "#b91c1c" if is_short else "#475569"

    signal_key = str(row.get("Signal", "NO TRADE"))
    signal_text = str(row.get("Signal Deutsch", "Signal"))
    signal_bg_map = {
        "EARLY LONG": "#16a34a",
        "STRONG BUY": "#16a34a",
        "EARLY SHORT": "#dc2626",
        "STRONG SHORT": "#dc2626",
        "SETUP": "#f59e0b",
        "NO TRADE": "#64748b",
    }
    signal_bg = signal_bg_map.get(signal_key, "#f59e0b" if "Beobachten" in signal_text else "#64748b")
    signal_border = {
        "#16a34a": "#15803d",
        "#dc2626": "#b91c1c",
        "#f59e0b": "#d97706",
        "#64748b": "#475569",
    }.get(signal_bg, signal_bg)

    final_score = safe_float(row.get("Score Final", row.get("Score", row.get("Swing-Score Event"))))
    rs_display = float(row["Relative Stärke"]) if pd.notna(row["Relative Stärke"]) else 50.0

    left_rows = [
        ("Richtung", f'<b style="color:{trend_badge_bg};">{trend_text}</b>'),
        ("Setup", f'<b>{row["Einstieg"]}</b>'),
        ("Entry", f'<b>{fmt_dual_price(row["Preis €"], row["Symbol"])}</b>'),
        ("Stop", f'<b>{fmt_dual_price(row["Stop €"], row["Symbol"])}</b>'),
        ("Target", f'<b>{fmt_dual_price(row["Ziel €"], row["Symbol"])}</b>'),
        ("CRV", f'<b>{fmt_num(row["CRV"])}</b>'),
    ]
    right_rows = [
        ("Swing Score", f'<b>{fmt_num(row["Swing-Score Event"])} </b>'),
        ("Day Score", f'<b>{fmt_num(row["Day-Score Event"])} </b>'),
        ("RSI", f'<b>{fmt_num(row["RSI"])} </b>'),
        ("TSI", f'<b>{fmt_num(row["TSI"])} </b>'),
        ("Relative Stärke", f'<b>{rs_display:.2f}</b>'),
        ("Trendkanal", f'<b>{row["Trendkanal"]}</b>'),
    ]

    left_html = ''.join([f'<div class="scanner-panel-row"><span class="scanner-row-label">{label}</span><span class="scanner-row-value">{value}</span></div>' for label, value in left_rows])
    right_html = ''.join([f'<div class="scanner-panel-row"><span class="scanner-row-label">{label}</span><span class="scanner-row-value">{value}</span></div>' for label, value in right_rows])
    score_html = fmt_num(final_score) if final_score is not None else "-"

    trend_badge_style = (
        f'display:inline-flex;align-items:center;justify-content:center;'
        f'padding:6px 12px;border-radius:999px;margin-top:12px;'
        f'font-size:12px;font-weight:900;letter-spacing:0.03em;text-transform:uppercase;'
        f'background-color:{trend_badge_bg};border:1px solid {trend_badge_border};'
        f'color:#ffffff;line-height:1;box-shadow:0 4px 10px rgba(0,0,0,0.18);'
    )
    signal_badge_style = (
        f'display:inline-flex;align-items:center;justify-content:center;'
        f'padding:6px 12px;border-radius:999px;margin-top:8px;'
        f'font-size:14px;font-weight:900;line-height:1;'
        f'background-color:{signal_bg};border:1px solid {signal_border};'
        f'color:#ffffff;box-shadow:0 4px 10px rgba(0,0,0,0.18);'
    )

    links_html = f'<a href="{analyse_link_de(row["Name"])}" target="_blank">Finanzen.net</a>'
    if str(row["WKN"]) != "-":
        links_html += f'<a href="{onvista_link(str(row["WKN"]))}" target="_blank">Onvista / WKN {row["WKN"]}</a>'

    html = f"""
    <div class="scanner-card">
        <div class="scanner-card-top">
            <div>
                <div class="scanner-title">{row["Symbol"]}</div>
                <div class="scanner-subtitle">{row["Name"]}</div>
                <span class="scanner-trend-badge" style="{trend_badge_style}">{trend_text}</span>
                <div class="scanner-links">{links_html}</div>
            </div>
            <div class="scanner-score-wrap">
                <div class="scanner-score-label">Final Score</div>
                <div class="scanner-score-value">{score_html}</div>
                <span class="scanner-signal-label" style="{signal_badge_style}">{signal_text}</span>
            </div>
        </div>
        <div class="scanner-grid">
            <div class="scanner-panel">
                <div class="scanner-panel-label">Trade Setup</div>
                {left_html}
            </div>
            <div class="scanner-panel">
                <div class="scanner-panel-label">Momentum & Qualität</div>
                {right_html}
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    render_ampel(str(row["Signal"]))
    notes = []
    if row["Earnings Hinweis"]:
        notes.append(f'📅 {row["Earnings Hinweis"]}')
    if row["Positionsgröße Hinweis"]:
        notes.append(f'⚠️ {row["Positionsgröße Hinweis"]}')
    if row["Analysten Hinweis"]:
        notes.append(f'🏦 Finnhub Konsens: {row["Analysten Hinweis"]}')
    if row["News Hinweis"]:
        notes.append(f'📰 Finnhub News: {row["News Hinweis"]}')
    if notes:
        st.markdown(f'<div class="scanner-event-strip">{" | ".join(notes)}</div>', unsafe_allow_html=True)
    elif str(row["Event Status"]):
        st.markdown(f'<div class="scanner-event-strip">ℹ️ {row["Event Status"]}</div>', unsafe_allow_html=True)
    risk_amount, units, position_value = calculate_position_size(st.session_state.get("account_size_value",10000.0), st.session_state.get("risk_pct_value",1.0), safe_float(row["Preis €"]), safe_float(row["Stop €"]))
    meta = f'Positionsgröße: Risiko {fmt_eur(risk_amount)} | Stück {fmt_num(units)} | Positionswert {fmt_eur(position_value)}' if risk_amount is not None else 'Positionsgröße: -'
    st.markdown(f'<div class="scanner-meta-caption">{meta}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Ins Portfolio", key=f'add_{key_suffix}_{row["Symbol"]}', use_container_width=True):
            add_to_portfolio(row); st.success(f'{row["Symbol"]} wurde ins Portfolio gespeichert.'); st.rerun()
    with c2:
        if st.button("👁️ Auf Watchlist", key=f'watch_{key_suffix}_{row["Symbol"]}', use_container_width=True):
            add_to_watchlist(row); st.success(f'{row["Symbol"]} zur Watchlist hinzugefügt.'); st.rerun()

def portfolio_action_badge(action: str) -> str:
    a = str(action or "").strip()
    low = a.lower()
    if "verkauf" in low:
        bg = "#dc2626"
        border = "#b91c1c"
    elif "aufstock" in low or "nachkauf" in low:
        bg = "#16a34a"
        border = "#15803d"
    else:
        bg = "#f59e0b"
        border = "#d97706"
    return (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;padding:6px 10px;'
        f'border-radius:999px;background:{bg};border:1px solid {border};color:#fff;font-size:12px;font-weight:900;">{a}</span>'
    )

def render_portfolio_signal_banner(df):
    if df is None or df.empty:
        return
    top = df.drop_duplicates(subset=["Symbol"]).head(3).copy()
    chips = []
    for _, r in top.iterrows():
        chips.append(f'<div class="mobile-portfolio-item"><div class="mobile-portfolio-top"><div class="mobile-portfolio-symbol">{r["Symbol"]}</div>{portfolio_action_badge(r.get("Aktion", ""))}</div><div class="mobile-portfolio-reason">{r.get("Grund", "")}</div></div>')
    st.markdown('<div class="mobile-portfolio-banner">' + ''.join(chips) + '</div>', unsafe_allow_html=True)

def render_portfolio_signal_cards(df):
    if df is None or df.empty:
        return
    cards = []
    for _, r in df.head(5).iterrows():
        cards.append(
            '<div class="mobile-portfolio-item">'
            '<div class="mobile-portfolio-top">'
            f'<div class="mobile-portfolio-symbol">{r["Symbol"]}</div>'
            f'{portfolio_action_badge(r.get("Aktion", ""))}'
            '</div>'
            f'<div class="mobile-portfolio-reason">{r.get("Grund", "")}</div>'
            '</div>'
        )
    st.markdown('<div class="mobile-portfolio-list">' + ''.join(cards) + '</div>', unsafe_allow_html=True)

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0
if "account_size_value" not in st.session_state:
    st.session_state.account_size_value = 10000.0
if "risk_pct_value" not in st.session_state:
    st.session_state.risk_pct_value = 1.0



c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    market_selection = st.selectbox("Markt", ["Smart Scanner Pro","Alle","US Tech","US Markt","Europa","Emerging / China","Rohstoffe","Krypto","Small Caps","Hot Stocks"], index=0)
with c2:
    smart_prefilter = st.toggle("🧠 Smart-Vorfilter", value=True)
with c3:
    quick_mode = st.toggle("⚡ Nur Top Trades", value=False)
with c4:
    prefilter_top_n = st.selectbox("Vorselektion", [80,100,120,150,200,250,300], index=4)
with c5:
    max_symbols = st.selectbox("Finaler Scan", [30,50,80,100,120,150], index=3)

top_event_candidates = st.selectbox("Live-Events für Top", [6,8,10,12], index=2)

r1, r2 = st.columns(2)
with r1:
    st.session_state.account_size_value = st.number_input("Kontogröße €", min_value=100.0, value=float(st.session_state.account_size_value), step=100.0)
with r2:
    st.session_state.risk_pct_value = st.number_input("Risiko je Trade %", min_value=0.1, max_value=10.0, value=float(st.session_state.risk_pct_value), step=0.1)

assets = build_assets(market_selection)
all_df = analyze_assets(assets, max_symbols=max_symbols, top_event_candidates=top_event_candidates, smart_prefilter=smart_prefilter, prefilter_top_n=prefilter_top_n)
if quick_mode and not all_df.empty:
    all_df = all_df[all_df["Signal"].isin(["EARLY LONG","STRONG BUY","EARLY SHORT","STRONG SHORT"])].reset_index(drop=True)

portfolio_signal_df = build_portfolio_signals(all_df) if not all_df.empty else pd.DataFrame()
if not portfolio_signal_df.empty:
    urgent = portfolio_signal_df[portfolio_signal_df["Aktion"].isin(["SOFORT VERKAUFEN","Verkaufen"])]
    text = "Es gibt dringende Verkaufssignale. Bitte zuerst prüfen." if not urgent.empty else "Aktuell überwiegend Halten / Gewinne sichern / Aufstocken."
    st.markdown(f'<div class="info-card {"info-red" if not urgent.empty else "info-blue"}"><b>Portfolio zuerst:</b> {text}</div>', unsafe_allow_html=True)
    render_portfolio_signal_banner(portfolio_signal_df)
    tmp = portfolio_signal_df.head(5).copy()
    tmp["Aktuell Anzeige"] = tmp.apply(lambda r: fmt_dual_price(r["Aktuell €"], r["Symbol"]), axis=1)
    tmp["Stop Anzeige"] = tmp.apply(lambda r: fmt_dual_price(r["Stop €"], r["Symbol"]), axis=1)
    tmp["Ziel Anzeige"] = tmp.apply(lambda r: fmt_dual_price(r["Ziel €"], r["Symbol"]), axis=1)
    st.dataframe(tmp[["Symbol","Aktuell Anzeige","Stop Anzeige","Ziel Anzeige","CRV","P&L %","Aktion","Grund"]], use_container_width=True, hide_index=True)

fg_value, fg_label = calc_fear_greed(all_df if not all_df.empty else pd.DataFrame())
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Fear & Greed", f"{fg_value:.1f}")
    render_fear_greed(fg_value, fg_label)
with m2:
    st.metric("Sentiment", fg_label)
with m3:
    relation = "-"
    if not all_df.empty:
        avg_price = safe_float(all_df["Preis €"].mean()); avg_ema50 = safe_float(all_df["EMA50 €"].mean())
        if avg_price is not None and avg_ema50 is not None:
            relation = "Preis über EMA50" if avg_price > avg_ema50 else "Preis unter EMA50"
    st.metric("Preis / EMA50", relation)

prefilter_total = int(st.session_state.get("prefilter_total", len(assets)))
prefilter_selected = int(st.session_state.get("prefilter_selected", min(len(assets), prefilter_top_n if "prefilter_top_n" in locals() else len(assets))))
scan_mode_label = "Smart-Vorfilter aktiv" if smart_prefilter else "Direktscan aktiv"
st.caption(f"Aktives Universum: {len(assets)} Werte | Vorfilter: {prefilter_total} → {prefilter_selected} | Final gescannt: {min(prefilter_selected if smart_prefilter else len(assets), max_symbols)} | {scan_mode_label} | Smart-Cache aktiv | Chunk-Download aktiv | Live-Events für Top {min(top_event_candidates, len(all_df)) if not all_df.empty else 0}")

st.markdown("---")
st.subheader("Suche")
search_text = st.text_input("Nach Unternehmensname, Rohstoff oder Krypto suchen", value="")
if search_text.strip():
    mask = all_df["Name"].str.contains(search_text.strip(), case=False, na=False) if not all_df.empty else pd.Series(dtype=bool)
    search_df = all_df[mask].copy() if not all_df.empty else pd.DataFrame()
    if search_df.empty:
        st.info("Kein Treffer.")
    else:
        for idx, row in search_df.head(10).iterrows():
            render_card(row, f"search_{idx}")

aktien_df = all_df[all_df["Typ"] == "Aktie"].copy() if not all_df.empty else pd.DataFrame()
rohstoffe_df = analyze_top3_block(ROHSTOFFE)
krypto_df = analyze_top3_block(KRYPTO)

st.subheader("Top 3 Aktien")
if aktien_df.empty:
    st.info("Keine Aktien-Treffer.")
else:
    for idx, row in aktien_df.head(3).iterrows():
        render_card(row, f"stock_{idx}")

st.subheader("Top 3 Rohstoffe")
if rohstoffe_df.empty:
    st.info("Keine Rohstoff-Treffer.")
else:
    for idx, row in rohstoffe_df.head(3).iterrows():
        render_card(row, f"comm_{idx}")

st.subheader("Top 3 Kryptowährungen")
if krypto_df.empty:
    st.info("Keine Krypto-Treffer.")
else:
    for idx, row in krypto_df.head(3).iterrows():
        render_card(row, f"crypto_{idx}")

with st.expander("👁️ Watchlist (gespeichert)", expanded=False):
    watch_saved = load_watchlist()
    if watch_saved.empty:
        st.info("Noch keine Werte gespeichert.")
    else:
        st.dataframe(watch_saved, use_container_width=True, hide_index=True)
        delete_symbol = st.selectbox("Von Watchlist entfernen", watch_saved["Symbol"])
        if st.button("Entfernen"):
            save_watchlist(watch_saved[watch_saved["Symbol"] != delete_symbol])
            st.success("Entfernt")
            st.rerun()

with st.expander("Scanner-Tabelle", expanded=False):
    if all_df.empty:
        st.info("Keine Daten.")
    else:
        table_df = all_df.copy()
        table_df["Preis Anzeige"] = table_df.apply(lambda r: fmt_dual_price(r["Preis €"], r["Symbol"]), axis=1)
        table_df["Stop Anzeige"] = table_df.apply(lambda r: fmt_dual_price(r["Stop €"], r["Symbol"]), axis=1)
        table_df["Ziel Anzeige"] = table_df.apply(lambda r: fmt_dual_price(r["Ziel €"], r["Symbol"]), axis=1)
        table_df["Risiko €"] = table_df.apply(lambda r: calculate_position_size(st.session_state.account_size_value, st.session_state.risk_pct_value, safe_float(r["Preis €"]), safe_float(r["Stop €"]))[0], axis=1)
        table_df["Stück"] = table_df.apply(lambda r: calculate_position_size(st.session_state.account_size_value, st.session_state.risk_pct_value, safe_float(r["Preis €"]), safe_float(r["Stop €"]))[1], axis=1)
        st.dataframe(table_df[["Name","Symbol","Region","Typ","Ampel","Signal Deutsch","Trend","Einstieg","CRV","Preis Anzeige","Stop Anzeige","Ziel Anzeige","Risiko €","Stück"]], use_container_width=True, hide_index=True)
        selected_name = st.selectbox("Aus Scanner-Tabelle ins Portfolio", table_df["Name"].tolist())
        if st.button("Ausgewählten Wert ins Portfolio"):
            row = table_df[table_df["Name"] == selected_name].iloc[0]
            add_to_portfolio(row)
            st.success(f"{selected_name} wurde ins Portfolio gespeichert.")
            st.rerun()

with st.expander("Positionsgrößen-Rechner", expanded=False):
    st.caption("Berechnung auf Basis von Kontogröße, Risiko je Trade und Abstand zwischen Einstieg und Stop.")
    if all_df.empty:
        st.info("Keine Signale verfügbar.")
    else:
        calc_name = st.selectbox("Wert für Positionsgröße", all_df["Name"].tolist(), key="possize_name")
        calc_row = all_df[all_df["Name"] == calc_name].iloc[0]
        risk_amount, units, position_value = calculate_position_size(st.session_state.account_size_value, st.session_state.risk_pct_value, safe_float(calc_row["Preis €"]), safe_float(calc_row["Stop €"]))
        x1, x2, x3 = st.columns(3)
        with x1:
            st.metric("Risiko je Trade", fmt_eur(risk_amount))
        with x2:
            st.metric("Stückzahl", fmt_num(units))
        with x3:
            st.metric("Positionswert", fmt_eur(position_value))
        st.write(f"Preis: {fmt_dual_price(calc_row['Preis €'], calc_row['Symbol'])}")
        st.write(f"Stop: {fmt_dual_price(calc_row['Stop €'], calc_row['Symbol'])}")
        st.write(f"CRV: {fmt_num(calc_row['CRV'])}")

with st.expander("Portfolio Manager", expanded=False):
    st.caption("Positionen bleiben in data/scanner_7_4_final_portfolio.csv gespeichert.")
    portfolio_df = load_portfolio()
    with st.form("portfolio_add_form", clear_on_submit=False):
        a,b,c,d,e,f = st.columns([1.1,1.2,1.0,0.9,1.0,1.1])
        sym = a.text_input("Symbol", value="")
        name = b.text_input("Name", value="")
        buy_price = c.number_input("Kaufkurs €", min_value=0.0, value=0.0, step=0.1)
        shares = d.number_input("Stück", min_value=0.0, value=1.0, step=1.0)
        stop_input = e.number_input("Stop €", min_value=0.0, value=0.0, step=0.1)
        target_input = f.number_input("Ziel €", min_value=0.0, value=0.0, step=0.1)
        note = st.text_input("Notiz", value="")
        submitted = st.form_submit_button("Position speichern")
        if submitted and sym.strip():
            sym = sym.strip().upper()
            meta = assets.get(sym, {"name":name or sym,"wkn":"-","type":""})
            new_row = {"Symbol":sym,"Name":name.strip() or meta.get("name",sym),"WKN":meta.get("wkn","-"),"Typ":meta.get("type",""),"Kaufdatum":str(date.today()),"Kaufkurs €":buy_price,"Stück":shares,"Stop €":stop_input if stop_input > 0 else None,"Ziel €":target_input if target_input > 0 else None,"Notiz":note}
            save_portfolio(pd.concat([portfolio_df,pd.DataFrame([new_row])], ignore_index=True))
            st.success(f"{sym} wurde gespeichert.")
            st.rerun()
    portfolio_df = load_portfolio()
    if portfolio_df.empty:
        st.info("Noch keine Positionen gespeichert.")
    else:
        show_pf = portfolio_df.copy()
        show_pf["Kaufkurs Anzeige"] = show_pf.apply(lambda r: fmt_dual_price(r["Kaufkurs €"], r["Symbol"]), axis=1)
        show_pf["Stop Anzeige"] = show_pf.apply(lambda r: fmt_dual_price(r["Stop €"], r["Symbol"]), axis=1)
        show_pf["Ziel Anzeige"] = show_pf.apply(lambda r: fmt_dual_price(r["Ziel €"], r["Symbol"]), axis=1)
        st.dataframe(show_pf[["Symbol","Name","Typ","Kaufdatum","Kaufkurs Anzeige","Stück","Stop Anzeige","Ziel Anzeige","Notiz"]], use_container_width=True, hide_index=True)
        delete_options = [f"{idx}: {row['Name']} | Kaufkurs {row['Kaufkurs €']} € | Stück {row['Stück']}" for idx, row in portfolio_df.iterrows()]
        selected = st.selectbox("Position löschen", delete_options)
        if st.button("Ausgewählte Position löschen"):
            idx = int(str(selected).split(":")[0])
            save_portfolio(portfolio_df.drop(index=idx).reset_index(drop=True))
            st.success("Position gelöscht.")
            st.rerun()


# ==============================
# WATCHLIST VERGLEICH
# ==============================
@st.cache_data(show_spinner=False, ttl=1800)
def get_price_on_or_after_date(symbol: str, target_date):
    try:
        start = pd.to_datetime(target_date)
        end = start + pd.Timedelta(days=7)
        hist = yf.Ticker(symbol).history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
        if hist is None or hist.empty:
            return None
        close = hist["Close"].dropna()
        if close.empty:
            return None
        return float(close.iloc[0])
    except Exception:
        return None

@st.cache_data(show_spinner=False, ttl=600)
def get_current_native_price(symbol: str):
    try:
        hist = yf.Ticker(symbol).history(period="5d")
        if hist is None or hist.empty:
            return None
        close = hist["Close"].dropna()
        if close.empty:
            return None
        return float(close.iloc[-1])
    except Exception:
        return None

st.markdown("---")
st.subheader("⭐ Watchlist Vergleich")
st.caption("Vergleich deiner Watchlist zwischen einem frei wählbaren Datum und dem aktuellen Kurs inklusive Performance in Prozent.")

watch_col1, watch_col2 = st.columns([1.2, 5])
with watch_col1:
    compare_date = st.date_input("Vergleichsdatum", value=date.today() - timedelta(days=30), key="watchlist_compare_date")
with watch_col2:
    st.write("")

watchlist_df = load_watchlist()

if watchlist_df.empty:
    st.info("Deine Watchlist ist aktuell leer.")
else:
    compare_rows = []
    for _, row in watchlist_df.iterrows():
        symbol = str(row.get("Symbol", "")).strip()
        name = str(row.get("Name", "")).strip()
        typ = str(row.get("Typ", "")).strip()
        if not symbol:
            continue

        old_native = get_price_on_or_after_date(symbol, compare_date)
        current_native = get_current_native_price(symbol)

        old_eur = to_eur(old_native, symbol) if old_native is not None else None
        current_eur = to_eur(current_native, symbol) if current_native is not None else None

        pnl_pct = None
        if old_eur not in (None, 0) and current_eur is not None:
            pnl_pct = ((current_eur / old_eur) - 1.0) * 100.0

        compare_rows.append({
            "Symbol": symbol,
            "Name": name,
            "Typ": typ,
            f"Kurs am {compare_date.strftime('%d.%m.%Y')}": fmt_dual_price(old_eur, symbol) if old_eur is not None else "-",
            "Aktueller Kurs": fmt_dual_price(current_eur, symbol) if current_eur is not None else "-",
            "P&L %": round(pnl_pct, 2) if pnl_pct is not None else None,
        })

    compare_df = pd.DataFrame(compare_rows)

    if not compare_df.empty:
        if "P&L %" in compare_df.columns:
            compare_df = compare_df.sort_values(by="P&L %", ascending=False, na_position="last").reset_index(drop=True)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Für deine Watchlist konnten aktuell keine Vergleichsdaten geladen werden.")
