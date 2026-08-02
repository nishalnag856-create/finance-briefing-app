import os
import json
import requests
from datetime import datetime
import streamlit as st
import yfinance as yf
from weasyprint import HTML

st.set_page_config(page_title="Finance Intelligence Engine", page_icon="📈", layout="centered")

st.title("📈 Daily Finance Intelligence Engine")
st.caption("Real-Time Macro Tracking • FP&A Variance Models • C-Suite Simulation")

# Sidebar Configuration
st.sidebar.header("🔑 Configuration")
api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password", help="If left empty or invalid, built-in C-Suite engine will be used automatically.")

if not api_key:
    api_key = st.secrets.get("GEMINI_API_KEY", "")

api_key = api_key.strip().strip("'").strip('"')

def get_ai_content(key, prompt_text, nifty, spx, crude, us10y, usdinr):
    # Try Gemini API via REST (Supports both AIzaSy keys and AQ Bearer tokens!)
    if key:
        try:
            if key.startswith("AQ"):
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                payload = {"contents": [{"parts": [{"text": prompt_text}]}], "generationConfig": {"response_mime_type": "application/json"}}
                res = requests.post(url, headers=headers, json=payload, timeout=8)
                if res.status_code == 200:
                    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
            else:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                headers = {"Content-Type": "application/json"}
                payload = {"contents": [{"parts": [{"text": prompt_text}]}], "generationConfig": {"response_mime_type": "application/json"}}
                res = requests.post(url, headers=headers, json=payload, timeout=8)
                if res.status_code == 200:
                    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
        except Exception:
            pass  # Fallback gracefully to built-in CFO engine

    # Built-in High-Caliber Executive Intelligence Engine (Guarantees PDF Output 100%)
    return {
        "exec_summary": f"Global markets are exhibiting active volatility across core asset classes. NIFTY 50 stands at {nifty.get('price')} ({nifty.get('change_str')}) with Brent Crude trading at ${crude.get('price')} ({crude.get('change_str')}). USD/INR trades at {usdinr.get('price')}, directly impacting landed import costs. Executive teams must balance raw material inflation against pricing power elasticity across operating units.",
        "cfo_dilemma": "<strong>The CFO Trade-Off:</strong> Absorbing a 12–15% increase in input energy and import costs versus passing price hikes to price-sensitive retail customers. <em>Strategic Action:</em> Execute selective forward hedging on foreign currency exposures while renegotiating key supplier SLA terms.",
        "board_pitch": "<strong>Boardroom Takeaway:</strong> We recommend maintaining current OPEX discipline while accelerating automated route optimization to defend EBITDA margins. Revenue growth remains steady, but margin preservation is our primary quarter focus.",
        "fpna_drill": "<strong>FP&A Scenario Drill:</strong> Analyzing a 3-way variance (Price, Volume, FX). Volume variance (+20%) drove top-line expansion, but unhedged FX depreciation combined with Crude cost inflation eroded gross margin by 180 bps. Re-forecasting Q3 EPS model under $90+ crude baseline.",
        "csuite_treat": "<strong>C-Suite Wisdom:</strong> 'In finance, top-line is vanity, profit is sanity, but cash flow is reality.' Focus on compressing the Cash Conversion Cycle (CCC) during commodity volatility."
    }

if st.button("🚀 Generate Today's PDF Briefing", type="primary", use_container_width=True):
    with st.spinner("Fetching live market feeds & building executive briefing..."):
        
        # 1. Fetch Market Data
        TICKER_MAP = {
            "NIFTY 50": "^NSEI",
            "S&P 500 (SPX)": "^GSPC",
            "BRENT CRUDE (UKOIL)": "BZ=F",
            "US 10Y YIELD (US10Y)": "^TNX",
            "USD/INR": "INR=X",
            "INDIA VIX": "^INDIAVIX",
            "BAJAJ FINANCE": "BAJFINANCE.NS",
            "HYUNDAI MOTOR": "HYUNDAI.NS",
            "HINDUSTAN COPPER": "HINDCOPPER.NS",
            "JINDAL STEEL": "JINDALSTEL.NS",
            "TCS": "TCS.NS",
            "SWIGGY": "SWIGGY.NS",
            "RELIANCE": "RELIANCE.NS",
        }

        market_data = {}
        for label, symbol in TICKER_MAP.items():
            try:
                hist = yf.Ticker(symbol).history(period="5d")
                if len(hist) >= 2:
                    close = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = close - prev
                    pct = (change / prev) * 100
                    market_data[label] = {
                        "price": f"{close:,.2f}",
                        "change_str": f"{'+' if change >= 0 else ''}{change:,.2f} ({'+' if pct >= 0 else ''}{pct:.2f}%)",
                        "is_pos": change >= 0,
                        "raw_price": round(close, 2)
                    }
                else:
                    market_data[label] = {"price": "N/A", "change_str": "N/A", "is_pos": True, "raw_price": 0}
            except Exception:
                market_data[label] = {"price": "N/A", "change_str": "N/A", "is_pos": True, "raw_price": 0}

        today_str = datetime.now().strftime("%B %d, %Y")
        nifty = market_data.get("NIFTY 50", {})
        spx = market_data.get("S&P 500 (SPX)", {})
        crude = market_data.get("BRENT CRUDE (UKOIL)", {})
        us10y = market_data.get("US 10Y YIELD (US10Y)", {})
        usdinr = market_data.get("USD/INR", {})

        prompt = f"""
        You are a World-Class CFO and Senior FP&A Corporate Finance Advisor.
        Today's Date: {today_str}
        NIFTY 50: {nifty.get('price')} ({nifty.get('change_str')})
        S&P 500: {spx.get('price')} ({spx.get('change_str')})
        Brent Crude: ${crude.get('price')} ({crude.get('change_str')})
        US 10Y Yield: {us10y.get('price')}% ({us10y.get('change_str')})
        USD/INR: {usdinr.get('price')} ({usdinr.get('change_str')})
        Return a JSON object with keys: exec_summary, cfo_dilemma, board_pitch, fpna_drill, csuite_treat.
        """

        ai_content = get_ai_content(api_key, prompt, nifty, spx, crude, us10y, usdinr)

        # 3. Dynamic Worked Variance Calculations
        crude_price = crude.get('raw_price', 90.0) if crude.get('raw_price', 0) > 0 else 90.0
        usd_rate = usdinr.get('raw_price', 85.0) if usdinr.get('raw_price', 0) > 0 else 85.0

        price_var = round((crude_price - 75.0) * 1200 * 85.0)
        vol_var = round((1200 - 1000) * 75.0 * 85.0)
        fx_var = round((usd_rate - 85.0) * crude_price * 1200)
        total_var = price_var + vol_var + fx_var

        table_rows_html = ""
        for label, info in market_data.items():
            css = "pos" if info["is_pos"] else "neg"
            table_rows_html += f"<tr><td><strong>{label}</strong></td><td>Financial Asset</td><td>{info['price']}</td><td><span class='{css}'>{info['change_str']}</span></td></tr>"

        # 4. Compile HTML Template
        html_template = """<!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8">
        <style>
          *, *::before, *::after { box-sizing: border-box; }
          @page { size: A4; margin: 14mm 12mm; background-color: #ffffff;
            @bottom-left { content: "Daily Market Intelligence & Scenario Report | Finance Mastery Sprint"; font-family: 'DejaVu Sans', sans-serif; font-size: 8pt; color: #64748b; }
            @bottom-right { content: "Page " counter(page) " of " counter(pages); font-family: 'DejaVu Sans', sans-serif; font-size: 8pt; color: #64748b; }
          }
          body { font-family: 'DejaVu Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #111827; margin: 0; font-size: 8.5pt; line-height: 1.45; }
          .page-section { page-break-before: always; break-before: page; }
          .main-title { font-size: 18pt; font-weight: 700; color: #000000; margin: 0 0 3px 0; }
          .sub-title { font-size: 9.5pt; color: #111827; margin: 0 0 8px 0; }
          .meta-grid { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
          .meta-grid td { padding: 0; font-size: 8.5pt; color: #111827; }
          .indicators-table { width: 100%; border-collapse: collapse; margin-bottom: 16px; border: 1px solid #cbd5e1; }
          .indicators-table th { font-size: 7.5pt; font-weight: 700; text-align: center; padding: 6px 4px; border: 1px solid #cbd5e1; text-transform: uppercase; background-color: #ffffff; }
          .indicators-table td { padding: 8px 4px; text-align: center; border: 1px solid #cbd5e1; width: 20%; background-color: #ffffff; }
          .ind-val { font-size: 11pt; font-weight: 700; color: #000000; }
          .ind-change { font-size: 7.5pt; font-weight: 600; margin-top: 2px; }
          .pos { color: #16a34a; } .neg { color: #dc2626; }
          h2 { font-size: 11.5pt; font-weight: 700; color: #000000; margin: 0 0 10px 0; padding-bottom: 3px; border-bottom: 1px solid #cbd5e1; page-break-after: avoid; }
          p { margin: 0 0 8px 0; text-align: justify; }
          table.data-table { width: 100%; border-collapse: collapse; margin-bottom: 14px; font-size: 8pt; }
          table.data-table th { background-color: #1e293b; color: #ffffff; font-weight: 700; text-align: left; padding: 7px 8px; border: 1px solid #1e293b; }
          table.data-table td { padding: 6px 8px; border: 1px solid #cbd5e1; vertical-align: top; }
          table.data-table tr:nth-child(even) { background-color: #f8fafc; }
          .cfo-box { background-color: #f8fafc; border-left: 3px solid #2563eb; border: 1px solid #cbd5e1; border-left-width: 3px; border-radius: 4px; padding: 8px 10px; margin-bottom: 12px; }
          .pitch-box { background-color: #fffaf0; border-left: 3px solid #d97706; border: 1px solid #fed7aa; border-left-width: 3px; border-radius: 4px; padding: 8px 10px; margin-bottom: 12px; }
          .treat-box { background-color: #f0fdf4; border-left: 3px solid #16a34a; border: 1px solid #bbf7d0; border-left-width: 3px; border-radius: 4px; padding: 8px 10px; margin-bottom: 12px; }
        </style></head>
        <body>
          <div>
            <div class="main-title">Daily Market Intelligence Briefing</div>
            <div class="sub-title">Scenario & "What-If" Matrix, Plain-English Guide & Strategic FP&A Deep Dive</div>
            <table class="meta-grid">
              <tr><td style="width: 25%;"><strong>Date:</strong> __TODAY_STR__</td><td style="width: 40%;"><strong>Coverage:</strong> Equities, FX, Commodities & Yields</td><td style="width: 35%;"><strong>Focus:</strong> Live Macro Analysis & C-Suite Simulation</td></tr>
            </table>
            <table class="indicators-table">
              <thead><tr><th>NIFTY 50</th><th>S&P 500</th><th>BRENT CRUDE</th><th>US 10Y YIELD</th><th>USD/INR</th></tr></thead>
              <tbody><tr>
                <td><div class="ind-val">__NIFTY_VAL__</div><div class="ind-change __NIFTY_CLASS__">__NIFTY_CHG__</div></td>
                <td><div class="ind-val">__SPX_VAL__</div><div class="ind-change __SPX_CLASS__">__SPX_CHG__</div></td>
                <td><div class="ind-val">$__CRUDE_VAL__</div><div class="ind-change __CRUDE_CLASS__">__CRUDE_CHG__</div></td>
                <td><div class="ind-val">__US10Y_VAL__%</div><div class="ind-change __US10Y_CLASS__">__US10Y_CHG__</div></td>
                <td><div class="ind-val">__USDINR_VAL__</div><div class="ind-change __USDINR_CLASS__">__USDINR_CHG__</div></td>
              </tr></tbody>
            </table>
            <h2>Executive Summary (Live Market Commentary)</h2>
            <p>__EXEC_SUMMARY__</p>
          </div>

          <div class="page-section">
            <h2>1. "What-If" & Market Scenario Matrix</h2>
            <table class="data-table">
              <thead><tr><th style="width: 22%;">Scenario Trigger</th><th style="width: 23%;">Key Catalyst / Level</th><th style="width: 28%;">Ripple Effect Across Asset Classes</th><th style="width: 27%;">Strategy & Impact</th></tr></thead>
              <tbody>
                <tr><td><strong>1. Sustained Crude Spike Above $100/bbl</strong></td><td><strong>UKOIL &gt; $100–$105</strong><br>Supply bottlenecks & OPEC discipline.</td><td>Gross margin compression across manufacturing, paint, chemicals (+18% RM cost). Expands CAD & exerts USD/INR pressure.</td><td><strong>Tactical Pivot:</strong> Underweight energy-intensive industrials; overweight pricing-power leaders.</td></tr>
                <tr><td><strong>2. US 10Y Yield Breaches 5.00%</strong></td><td><strong>US10Y &gt; 5.00%</strong><br>Persistent inflation data.</td><td>Higher risk-free rates elevate WACC (+140 bps), compressing valuation multiples (-15% EV).</td><td><strong>Tactical Pivot:</strong> Rotate into high free-cash-flow corporates & defensive dividend blue-chips.</td></tr>
                <tr><td><strong>3. Last-Mile Delivery Fuel Surcharge Shock</strong></td><td><strong>Local Fuel &gt; ₹115/L</strong><br>Auto-indexing rider payouts (+10–12%).</td><td>Contribution margin per order drops from ₹25 to ₹15 (-40%). Passing fees creates negative volume variance (-12% to -15%).</td><td><strong>Tactical Pivot:</strong> Implement dynamic surge routing & multi-order batching.</td></tr>
              </tbody>
            </table>
          </div>

          <div class="page-section">
            <h2>3. Live Numerical Working Paper</h2>
            <h3>Raw Material & FX Variance Deconstruction</h3>
            <table class="data-table">
              <thead><tr><th>Component</th><th>Budget Baseline</th><th>Today's Live Value</th><th>Formula & Calculation</th><th>Variance Amount</th></tr></thead>
              <tbody>
                <tr><td><strong>Material Volume (Q)</strong></td><td>1,000 units</td><td>1,200 units</td><td>Lead/Volume expansion (+200 units)</td><td>—</td></tr>
                <tr><td><strong>Crude Price (P)</strong></td><td>$75.00/bbl</td><td>$__RAW_CRUDE__/bbl</td><td>Market Commodity Shift</td><td>—</td></tr>
                <tr><td><strong>Exchange Rate (FX)</strong></td><td>₹85.00/USD</td><td>₹__RAW_USD__/USD</td><td>FX Depreciation Shift</td><td>—</td></tr>
                <tr><td><strong>1. Price Variance</strong></td><td>—</td><td>—</td><td>(P_act - P_budg) × Q_act × FX_budg</td><td><span class="neg">+₹__PRICE_VAR__</span></td></tr>
                <tr><td><strong>2. Volume Variance</strong></td><td>—</td><td>—</td><td>(Q_act - Q_budg) × P_budg × FX_budg</td><td><span class="neg">+₹__VOL_VAR__</span></td></tr>
                <tr><td><strong>3. FX Variance</strong></td><td>—</td><td>—</td><td>(FX_act - FX_budg) × P_act × Q_act</td><td><span class="neg">+₹__FX_VAR__</span></td></tr>
                <tr><td><strong>Total Cost Variance</strong></td><td>₹63,75,000</td><td>₹__TOTAL_COST__</td><td><strong>Net Total Variance</strong></td><td><span class="neg">+₹__TOTAL_VAR__</span></td></tr>
              </tbody>
            </table>
          </div>

          <div class="page-section">
            <h2>4. Live Asset Summary Data</h2>
            <table class="data-table">
              <thead><tr><th>Asset / Symbol</th><th>Category</th><th>Latest Price</th><th>Day Net Change</th></tr></thead>
              <tbody>__TABLE_ROWS__</tbody>
            </table>
          </div>

          <div class="page-section">
            <h2>5. "In the CFO's Shoes": Decision Simulation</h2>
            <div class="cfo-box"><p>__CFO_DILEMMA__</p></div>
            <h2>6. Executive Boardroom Pitch</h2>
            <div class="pitch-box"><p>__BOARD_PITCH__</p></div>
          </div>

          <div class="page-section">
            <h2>9. FP&A Interview Case Study Drill</h2>
            <div class="cfo-box" style="border-left-color: #7c3aed;"><p>__FPNA_DRILL__</p></div>
            <h2>10. Daily C-Suite Treat 🎁</h2>
            <div class="treat-box"><p>__CSUITE_TREAT__</p></div>
          </div>
        </body></html>"""

        final_html = html_template \
            .replace("__TODAY_STR__", today_str) \
            .replace("__NIFTY_VAL__", nifty.get('price', 'N/A')) \
            .replace("__NIFTY_CHG__", nifty.get('change_str', 'N/A')) \
            .replace("__NIFTY_CLASS__", 'pos' if nifty.get('is_pos') else 'neg') \
            .replace("__SPX_VAL__", spx.get('price', 'N/A')) \
            .replace("__SPX_CHG__", spx.get('change_str', 'N/A')) \
            .replace("__SPX_CLASS__", 'pos' if spx.get('is_pos') else 'neg') \
            .replace("__CRUDE_VAL__", crude.get('price', 'N/A')) \
            .replace("__CRUDE_CHG__", crude.get('change_str', 'N/A')) \
            .replace("__CRUDE_CLASS__", 'neg' if crude.get('is_pos') else 'pos') \
            .replace("__US10Y_VAL__", us10y.get('price', 'N/A')) \
            .replace("__US10Y_CHG__", us10y.get('change_str', 'N/A')) \
            .replace("__US10Y_CLASS__", 'neg' if us10y.get('is_pos') else 'pos') \
            .replace("__USDINR_VAL__", usdinr.get('price', 'N/A')) \
            .replace("__USDINR_CHG__", usdinr.get('change_str', 'N/A')) \
            .replace("__USDINR_CLASS__", 'pos' if usdinr.get('is_pos') else 'neg') \
            .replace("__TABLE_ROWS__", table_rows_html) \
            .replace("__RAW_CRUDE__", f"{crude_price:,.2f}") \
            .replace("__RAW_USD__", f"{usd_rate:,.2f}") \
            .replace("__PRICE_VAR__", f"{price_var:,.0f}") \
            .replace("__VOL_VAR__", f"{vol_var:,.0f}") \
            .replace("__FX_VAR__", f"{fx_var:,.0f}") \
            .replace("__TOTAL_COST__", f"{6375000 + total_var:,.0f}") \
            .replace("__TOTAL_VAR__", f"{total_var:,.0f}") \
            .replace("__EXEC_SUMMARY__", ai_content.get('exec_summary', '')) \
            .replace("__CFO_DILEMMA__", ai_content.get('cfo_dilemma', '')) \
            .replace("__BOARD_PITCH__", ai_content.get('board_pitch', '')) \
            .replace("__FPNA_DRILL__", ai_content.get('fpna_drill', '')) \
            .replace("__CSUITE_TREAT__", ai_content.get('csuite_treat', ''))

        pdf_bytes = HTML(string=final_html).write_pdf()

        st.success("✅ PDF Successfully Compiled!")
        st.download_button(
            label="📥 Download Daily Briefing PDF",
            data=pdf_bytes,
            file_name=f"Daily_Market_Briefing_{datetime.now().strftime('%Y_%m_%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
