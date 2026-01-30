from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


# -----------------------
# Stock Data (same as React)
# -----------------------
stock_data = [
    {"symbol":"DOCN","name":"DigitalOcean Holdings","high":59.42,"low":53.15,"gain_pct":12.23,"cap":"Mid","buyout_trap":False,"rsi_14d":78,"strategy":"Momentum / 52-Week High","worth_investing":"Yes","recommendation":"Strong Buy","analyst_insights_strategy":"Hit 52-week high after appointing Vinay Kumar as CPTO and receiving a price target upgrade to $63 from Barclays."},
    {"symbol":"ZM","name":"Zoom Video Communications","high":95.83,"low":85.5,"gain_pct":11.22,"cap":"Large","buyout_trap":False,"rsi_14d":75,"strategy":"Options Volatility / Swing","worth_investing":"Yes","recommendation":"Buy","analyst_insights_strategy":"High call option volume (up 154%) driven by enterprise segment re-acceleration and strong free cash flow."},
    {"symbol":"NET","name":"Cloudflare Inc.","high":191.79,"low":173.44,"gain_pct":10.79,"cap":"Large","buyout_trap":False,"rsi_14d":72,"strategy":"Growth Momentum","worth_investing":"Yes","recommendation":"Buy","analyst_insights_strategy":"Benefitting from strong growth momentum in the cloud sector and general AI expansion tailwinds."},
    {"symbol":"ORCL","name":"Oracle Corporation","high":185.28,"low":177.15,"gain_pct":4.11,"cap":"Mega","buyout_trap":False,"rsi_14d":65,"strategy":"Cloud Infrastructure Play","worth_investing":"Yes","recommendation":"Hold","analyst_insights_strategy":"Significant movement driven by leadership in cloud infrastructure and expanding AI capabilities."},
    {"symbol":"MSFT","name":"Microsoft Corporation","high":472.58,"low":450.53,"gain_pct":3.28,"cap":"Mega","buyout_trap":False,"rsi_14d":68,"strategy":"Pre-Earnings Accumulation","worth_investing":"Yes","recommendation":"Buy","analyst_insights_strategy":"Buying momentum ahead of Q2 fiscal 2026 earnings with focus on AI Copilot and Azure growth."},
    {"symbol":"AAPL","name":"Apple Inc.","high":256.12,"low":248.04,"gain_pct":3.0,"cap":"Mega","buyout_trap":False,"rsi_14d":66,"strategy":"Defensive Growth","worth_investing":"Yes","recommendation":"Hold","analyst_insights_strategy":"Steady movement as a defensive growth play within the mega-cap tech sector's AI-driven rally."},
    {"symbol":"CSCO","name":"Cisco Systems","high":56.1,"low":54.3,"gain_pct":3.17,"cap":"Large","buyout_trap":False,"rsi_14d":62,"strategy":"AI Infrastructure Pivot","worth_investing":"Yes","recommendation":"Buy","analyst_insights_strategy":"Transitioning to a core AI infrastructure provider with a new partner program for enterprise AI readiness."},
    {"symbol":"LKQ","name":"LKQ Corporation","high":49.5,"low":48.1,"gain_pct":1.0,"cap":"Large","buyout_trap":True,"rsi_14d":55,"strategy":"Strategic Review / Sale","worth_investing":"Maybe","recommendation":"Watch","analyst_insights_strategy":"Price increase linked to a strategic review including potential sale of business units."},
    {"symbol":"NVDA","name":"NVIDIA Corporation","high":148.5,"low":144.2,"gain_pct":1.53,"cap":"Mega","buyout_trap":False,"rsi_14d":64,"strategy":"AI Sector Leader","worth_investing":"Yes","recommendation":"Buy","analyst_insights_strategy":"Maintaining position as AI sector leader despite broader intraday volatility in the semiconductor industry."}
]


# -----------------------
# PDF Generation
# -----------------------
def generate_pdf(filename="stock_analysis_dashboard.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleStyle",
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=16,
        textColor=colors.darkblue
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=14,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.darkred
    ))

    styles.add(ParagraphStyle(
        name="NormalSmall",
        fontSize=10,
        leading=14
    ))

    story = []

    # Title
    story.append(Paragraph("Stock Analysis Dashboard", styles["TitleStyle"]))
    story.append(Paragraph("Market insights and analyst-driven recommendations", styles["Italic"]))
    story.append(Spacer(1, 12))

    # Summary calculations
    strong_buy = sum(1 for s in stock_data if s["recommendation"] in ("Strong Buy", "Buy"))
    hold = sum(1 for s in stock_data if s["recommendation"] == "Hold")
    avg_gain = sum(s["gain_pct"] for s in stock_data) / len(stock_data)
    buyout_traps = sum(1 for s in stock_data if s["buyout_trap"])

    summary_table = Table([
        ["Strong Buy / Buy", "Hold", "Avg Gain %", "Buyout Traps"],
        [strong_buy, hold, f"{avg_gain:.2f}%", buyout_traps]
    ], colWidths=[120]*4)

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold")
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 16))

    # Per-stock sections
    for stock in stock_data:
        story.append(Paragraph(
            f"{stock['symbol']} – {stock['name']} ({stock['recommendation']})",
            styles["SectionHeader"]
        ))

        info_table = Table([
            ["High", "Low", "Gain %", "Market Cap", "RSI (14d)", "Worth Investing"],
            [
                f"${stock['high']}",
                f"${stock['low']}",
                f"+{stock['gain_pct']}%",
                stock["cap"],
                stock["rsi_14d"],
                stock["worth_investing"]
            ]
        ], colWidths=[70]*6)

        info_table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
            ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (0,0), (-1,-1), "CENTER")
        ]))

        story.append(info_table)
        story.append(Spacer(1, 6))

        story.append(Paragraph(
            f"<b>Strategy:</b> {stock['strategy']}",
            styles["NormalSmall"]
        ))

        story.append(Paragraph(
            f"<b>Analyst Insights:</b> {stock['analyst_insights_strategy']}",
            styles["NormalSmall"]
        ))

        if stock["buyout_trap"]:
            story.append(Paragraph(
                "<b>Warning:</b> Potential Buyout Trap",
                ParagraphStyle(
                    "Warning",
                    textColor=colors.orange,
                    fontSize=10,
                    spaceBefore=4
                )
            ))

        story.append(Spacer(1, 12))

    doc.build(story)
    print(f"PDF generated: {filename}")


if __name__ == "__main__":
    generate_pdf()

