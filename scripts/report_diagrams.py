"""Generate PNG diagrams for the Capstone report."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ASSETS = Path(__file__).resolve().parent / "report_assets"
NAVY = "#1A365D"
TEAL = "#0D5C63"
SAFFRON = "#E86C00"
LIGHT = "#F0F4F8"
GREEN = "#2A9D8F"
RED = "#C0392B"


def _save(fig, name: str) -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def draw_architecture() -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Go Bharat — System Architecture", fontsize=14, fontweight="bold", color=NAVY, pad=12)

    boxes = [
        (0.5, 4.2, 2.2, 1.0, "User\n(Web Browser)", LIGHT, NAVY),
        (3.2, 4.2, 2.4, 1.0, "FastAPI\n+ Jinja2 UI", TEAL, "white"),
        (6.2, 4.2, 3.0, 1.0, "LangGraph\nParser → Parallel → Merge", SAFFRON, "white"),
        (0.6, 2.5, 1.7, 0.75, "Weather", GREEN, "white"),
        (2.4, 2.5, 1.7, 0.75, "Hotel", GREEN, "white"),
        (4.2, 2.5, 1.7, 0.75, "Food", GREEN, "white"),
        (6.0, 2.5, 1.7, 0.75, "POI", GREEN, "white"),
        (7.8, 2.5, 1.7, 0.75, "Itinerary", GREEN, "white"),
        (0.6, 1.5, 1.7, 0.75, "Budget", GREEN, "white"),
        (2.4, 1.5, 1.7, 0.75, "Pack", GREEN, "white"),
        (4.5, 1.5, 2.2, 0.75, "Summary Plan", "#27AE60", "white"),
        (7.2, 1.5, 2.3, 0.75, "Travel Chatbot", "#6C3483", "white"),
        (3.5, 0.45, 3.0, 0.75, "Supabase", NAVY, "white"),
    ]
    for x, y, w, h, text, bg, fg in boxes:
        patch = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08",
            linewidth=1.2, edgecolor=NAVY, facecolor=bg, alpha=0.95,
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, color=fg, fontweight="bold")

    arrows = [
        ((2.7, 4.7), (3.2, 4.7)),
        ((5.6, 4.7), (6.2, 4.7)),
        ((7.7, 4.2), (7.7, 3.3)),
        ((5.6, 1.9), (5.0, 0.9)),
    ]
    for (x1, y1), (x2, y2) in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5))
    return _save(fig, "fig1_system_architecture.png")


def draw_single_vs_multi() -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle("Single Monolithic Agent vs Multi-Agent Design (Go Bharat)", fontsize=13, fontweight="bold", color=NAVY)

    # Left — bad single agent
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Single Agent (Not Used)", fontsize=11, color=RED, fontweight="bold")
    big = FancyBboxPatch((1.5, 2), 7, 6, boxstyle="round,pad=0.05", facecolor="#FDEDEC", edgecolor=RED, lw=2)
    ax.add_patch(big)
    ax.text(5, 7.8, "ONE LLM does everything", ha="center", fontsize=10, fontweight="bold", color=RED)
    tasks = ["Weather prose", "Hotels", "Budget tables", "Itinerary", "Chat", "API parsing"]
    for i, t in enumerate(tasks):
        ax.text(5, 6.8 - i * 0.85, f"• {t}", ha="center", fontsize=9, color="#922B21")
    ax.text(5, 1.2, "Long prompts, errors compound,\nhigh cost, slow responses", ha="center", fontsize=8, style="italic", color=RED)

    # Right — multi agent
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Multi-Agent (Our Approach)", fontsize=11, color=GREEN, fontweight="bold")
    ax.text(2.0, 7.5, "Parser Agent", ha="center", fontsize=9, fontweight="bold", color="#6C3483")
    ax.annotate("", xy=(2.0, 7.2), xytext=(2.0, 8.0), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2))
    parallel = ["Weather", "Hotel", "Food", "POI", "Itinerary", "Budget", "Pack"]
    xs = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
    for x, label in zip(xs, parallel):
        p = FancyBboxPatch((x, 5.5), 0.85, 0.9, boxstyle="round,pad=0.02", facecolor="#E8F8F5", edgecolor=GREEN, lw=1.2)
        ax.add_patch(p)
        ax.text(x + 0.42, 5.95, label, ha="center", va="center", fontsize=6.5, fontweight="bold", color=TEAL)
        ax.annotate("", xy=(x + 0.42, 5.5), xytext=(2.0, 7.2), arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.8))
    ax.text(3.5, 4.8, "PARALLEL", ha="center", fontsize=8, fontweight="bold", color=SAFFRON)
    orch = FancyBboxPatch((2.5, 2.8), 5.0, 1.4, boxstyle="round,pad=0.04", facecolor=LIGHT, edgecolor=NAVY, lw=1.5)
    ax.add_patch(orch)
    ax.text(5.0, 3.5, "LangGraph: Merge → Summary Plan", ha="center", fontsize=9, fontweight="bold", color=NAVY)
    ax.text(5.0, 1.2, "7 parallel specialists + Parser\n(fast, focused, maintainable)", ha="center", fontsize=8, style="italic", color=GREEN)

    plt.tight_layout()
    return _save(fig, "fig2_single_vs_multi_agent.png")


def draw_agent_flow() -> Path:
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Agentic Workflow — Trip Planning Session", fontsize=14, fontweight="bold", color=NAVY, pad=10)

    steps = [
        (5, 9.0, "1. User submits destination,\ndates, budget, style"),
        (5, 7.5, "2. PlannerService fetches\nlive API data"),
        (5, 6.0, "3. WeatherAgent writes\nfriendly weather brief"),
        (5, 4.5, "4. Plan saved to Supabase"),
        (2.5, 3.0, "5a. ItineraryAgent\n(on demand)"),
        (5.0, 3.0, "5b. BudgetAgent\n(on demand)"),
        (7.5, 3.0, "5c. TravelChatbot\n(Q&A)"),
        (5, 1.2, "6. User refines trip via dashboard & chat"),
    ]
    colors = [NAVY, TEAL, GREEN, SAFFRON, GREEN, GREEN, GREEN, NAVY]
    for (x, y, text), col in zip(steps, colors):
        p = FancyBboxPatch((x - 1.6, y - 0.55), 3.2, 1.1, boxstyle="round,pad=0.03", facecolor=LIGHT, edgecolor=col, lw=2)
        ax.add_patch(p)
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5, fontweight="bold", color=NAVY)

    for y1, y2 in [(8.45, 8.05), (6.95, 6.55), (5.45, 4.95), (4.0, 3.55)]:
        ax.annotate("", xy=(5, y2), xytext=(5, y1), arrowprops=dict(arrowstyle="->", color=NAVY, lw=2))
    ax.annotate("", xy=(2.5, 3.55), xytext=(4.2, 3.95), arrowprops=dict(arrowstyle="->", color=SAFFRON, lw=1.5))
    ax.annotate("", xy=(5.0, 3.55), xytext=(5.0, 3.95), arrowprops=dict(arrowstyle="->", color=SAFFRON, lw=1.5))
    ax.annotate("", xy=(7.5, 3.55), xytext=(5.8, 3.95), arrowprops=dict(arrowstyle="->", color=SAFFRON, lw=1.5))
    ax.annotate("", xy=(5, 1.75), xytext=(5, 2.45), arrowprops=dict(arrowstyle="->", color=NAVY, lw=2))
    return _save(fig, "fig3_agent_workflow.png")


def draw_ui_mockup() -> Path:
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    ax.set_title("Go Bharat — Dashboard (UI Concept)", fontsize=13, fontweight="bold", color=NAVY)

    # browser frame
    frame = FancyBboxPatch((0.3, 0.3), 8.4, 4.8, boxstyle="round,pad=0.02", facecolor="white", edgecolor=NAVY, lw=2)
    ax.add_patch(frame)
    ax.add_patch(FancyBboxPatch((0.3, 4.6), 8.4, 0.5, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    ax.text(4.5, 4.85, "Go Bharat — Travel Dashboard", ha="center", va="center", color="white", fontsize=10, fontweight="bold")

    fields = ["Destination: Jaipur", "Check-in: 2026-03-23", "Budget: ₹50,000 INR", "Style: Balanced"]
    for i, f in enumerate(fields):
        ax.add_patch(FancyBboxPatch((0.7, 3.8 - i * 0.55), 3.5, 0.4, boxstyle="round,pad=0.01", facecolor=LIGHT, edgecolor="#CCC"))
        ax.text(0.9, 4.0 - i * 0.55, f, fontsize=8, color=NAVY, va="center")

    ax.add_patch(FancyBboxPatch((4.5, 3.5), 3.8, 0.55, boxstyle="round,pad=0.02", facecolor=SAFFRON, edgecolor=SAFFRON))
    ax.text(6.4, 3.78, "Generate Plan", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

    cards = [("Weather", TEAL), ("Hotels", SAFFRON), ("Food", GREEN)]
    for i, (label, col) in enumerate(cards):
        ax.add_patch(FancyBboxPatch((0.7 + i * 2.7, 0.7), 2.4, 2.0, boxstyle="round,pad=0.02", facecolor=LIGHT, edgecolor=col, lw=1.5))
        ax.text(0.7 + i * 2.7 + 1.2, 2.5, label, ha="center", fontsize=9, fontweight="bold", color=col)
        ax.text(0.7 + i * 2.7 + 1.2, 1.5, "Live results\nfrom APIs", ha="center", fontsize=7, color="#555")

    return _save(fig, "fig4_ui_mockup.png")


def draw_database_er() -> Path:
    """Entity-relationship style diagram for Supabase travel_plans."""
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("Database Layout — Supabase (PostgreSQL)", fontsize=14, fontweight="bold", color=NAVY, pad=14)

    # Cloud / platform
    cloud = FancyBboxPatch((0.4, 6.5), 10.2, 1.1, boxstyle="round,pad=0.03", facecolor=LIGHT, edgecolor=TEAL, lw=2)
    ax.add_patch(cloud)
    ax.text(5.5, 7.05, "Supabase Project  →  PostgreSQL  (public schema)", ha="center", fontsize=11, fontweight="bold", color=TEAL)

    # Main table
    tbl = FancyBboxPatch((1.0, 2.8), 4.2, 3.2, boxstyle="round,pad=0.02", facecolor="white", edgecolor=NAVY, lw=2.5)
    ax.add_patch(tbl)
    ax.text(3.1, 5.7, "TABLE: travel_plans", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    cols = [
        ("id", "BIGINT", "PK, identity"),
        ("email_id", "TEXT", "NOT NULL"),
        ("city", "TEXT", "NOT NULL"),
        ("travel_details", "JSONB", "NOT NULL"),
        ("created_at", "TIMESTAMPTZ", "default now()"),
    ]
    y = 5.15
    for name, typ, note in cols:
        ax.text(1.25, y, name, fontsize=9, fontweight="bold", color=NAVY, family="monospace")
        ax.text(2.55, y, typ, fontsize=8, color=SAFFRON, family="monospace")
        ax.text(1.25, y - 0.22, note, fontsize=7, color="#666")
        y -= 0.55

    # JSONB expansion
    json_box = FancyBboxPatch((5.8, 1.2), 4.8, 5.5, boxstyle="round,pad=0.02", facecolor="#FFF8F0", edgecolor=SAFFRON, lw=2)
    ax.add_patch(json_box)
    ax.text(8.2, 6.45, "travel_details (JSONB)", ha="center", fontsize=10, fontweight="bold", color=SAFFRON)
    keys = [
        "destination, city, check_in, check_out",
        "adults, budget_amount, budget_currency, style",
        "weather, hotels, restaurants, attractions",
        "currency, final_response, generated_at",
        "warning (optional)",
    ]
    jy = 5.9
    for k in keys:
        ax.text(6.0, jy, "• " + k, fontsize=8, color=NAVY)
        jy -= 0.45

    ax.annotate("", xy=(5.8, 4.5), xytext=(5.2, 4.5),
                arrowprops=dict(arrowstyle="->", color=SAFFRON, lw=2))
    ax.text(5.5, 4.75, "stores", fontsize=8, color=SAFFRON, ha="center")

    # Indexes note
    idx = FancyBboxPatch((1.0, 0.5), 4.2, 1.6, boxstyle="round,pad=0.02", facecolor=LIGHT, edgecolor=GREEN, lw=1.5)
    ax.add_patch(idx)
    ax.text(3.1, 1.65, "Indexes (recommended)", ha="center", fontsize=9, fontweight="bold", color=GREEN)
    ax.text(3.1, 1.25, "idx_travel_plans_email_id", ha="center", fontsize=7.5, family="monospace", color=NAVY)
    ax.text(3.1, 0.95, "idx_travel_plans_email_id_city", ha="center", fontsize=7.5, family="monospace", color=NAVY)
    ax.text(3.1, 0.65, "GIN on travel_details (optional)", ha="center", fontsize=7.5, family="monospace", color=NAVY)

    return _save(fig, "fig5_database_er.png")


def draw_database_crud() -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Database Operations — How the App Uses travel_plans", fontsize=13, fontweight="bold", color=NAVY, pad=12)

    app = FancyBboxPatch((0.5, 5.5), 2.5, 1.0, boxstyle="round,pad=0.03", facecolor=TEAL, edgecolor=TEAL)
    ax.add_patch(app)
    ax.text(1.75, 6.0, "FastAPI\nSupabaseService", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

    db = FancyBboxPatch((6.5, 4.8), 2.8, 1.8, boxstyle="round,pad=0.03", facecolor=NAVY, edgecolor=NAVY)
    ax.add_patch(db)
    ax.text(7.9, 5.7, "travel_plans", ha="center", va="center", color="white", fontsize=10, fontweight="bold")

    ops = [
        (0.3, 3.8, "INSERT", "POST /plan\nstore_travel_plan()", SAFFRON),
        (0.3, 2.5, "SELECT latest", "fetch_travel_plan()\nchat, itinerary, budget", GREEN),
        (0.3, 1.2, "SELECT list", "fetch_all_plans()\nGET /plans/{email}", GREEN),
        (5.0, 3.8, "SELECT by id", "fetch_plan_by_id()\nGET /plans/.../id", GREEN),
    ]
    for x, y, op, desc, col in ops:
        b = FancyBboxPatch((x, y), 4.2, 1.0, boxstyle="round,pad=0.02", facecolor=LIGHT, edgecolor=col, lw=1.8)
        ax.add_patch(b)
        ax.text(x + 0.5, y + 0.65, op, fontsize=9, fontweight="bold", color=col)
        ax.text(x + 0.5, y + 0.28, desc, fontsize=7.5, color=NAVY)
        ax.annotate("", xy=(6.5, 5.5), xytext=(x + 4.2, y + 0.5),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.3))

    ax.annotate("", xy=(3.0, 6.0), xytext=(6.5, 5.8),
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.5))
    return _save(fig, "fig6_database_crud.png")


def draw_sample_record() -> Path:
    """Table-style sample row — renders reliably in Word."""
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.axis("off")
    fig.subplots_adjust(top=0.88, bottom=0.05, left=0.06, right=0.94)
    ax.set_title(
        "Sample travel_plans Row (Illustrative)",
        fontsize=14,
        fontweight="bold",
        color=NAVY,
        pad=16,
    )

    headers = ["Column / JSON key", "Example value"]
    rows = [
        ["id", "42"],
        ["email_id", "student@iitp.ac.in"],
        ["city", "Jaipur"],
        ["created_at", "2026-03-30T10:15:00Z"],
        ["travel_details → destination", "Jaipur"],
        ["travel_details → check_in / check_out", "2026-04-10 / 2026-04-14"],
        ["travel_details → adults", "2"],
        ["travel_details → budget_amount / currency", "50000 / INR"],
        ["travel_details → style", "balanced"],
        ["travel_details → weather", "Prose from WeatherAgent (2 paragraphs)"],
        ["travel_details → hotels", "HTML cards from TripAdvisor API"],
        ["travel_details → restaurants", "HTML cards from TripAdvisor API"],
        ["travel_details → attractions", "HTML cards from OpenTripMap"],
        ["travel_details → currency", "FX conversion summary text"],
        ["travel_details → final_response", "Composed HTML trip brief"],
        ["travel_details → generated_at", "ISO timestamp string"],
    ]

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        loc="center",
        cellLoc="left",
        colWidths=[0.38, 0.55],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.45)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(NAVY)
        cell.set_linewidth(0.8)
        if row == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor(LIGHT)
        else:
            cell.set_facecolor("white")
        if col == 0 and row > 0:
            cell.set_text_props(fontfamily="monospace", fontsize=8)

    return _save(fig, "fig7_sample_record.png")


def draw_api_sequence() -> Path:
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("Sequence: Creating a Travel Plan (POST /api/v1/plan)", fontsize=13, fontweight="bold", color=NAVY)

    lanes = [("User", 1.2), ("Browser", 3.0), ("FastAPI", 5.0), ("APIs+Agents", 7.0), ("Supabase", 9.0)]
    for label, x in lanes:
        ax.plot([x, x], [0.5, 7.5], "--", color="#CCC", lw=1)
        ax.text(x, 7.7, label, ha="center", fontsize=9, fontweight="bold", color=NAVY)

    messages = [
        (1.2, 3.0, 7.0, "Submit form"),
        (3.0, 5.0, 6.5, "POST /plan JSON"),
        (5.0, 7.0, 6.0, "Fetch weather, hotels, food, POIs"),
        (7.0, 5.0, 5.0, "WeatherAgent + compose HTML"),
        (5.0, 9.0, 4.2, "INSERT travel_plans"),
        (9.0, 5.0, 3.4, "Row id + JSON"),
        (5.0, 3.0, 2.6, "PlanResponse"),
        (3.0, 1.2, 1.8, "Render dashboard"),
    ]
    y = 7.0
    for x1, x2, ypos, msg in messages:
        ax.annotate("", xy=(x2, ypos), xytext=(x1, ypos),
                    arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.2))
        ax.text((x1 + x2) / 2, ypos + 0.12, msg, ha="center", fontsize=7, color=NAVY)
    return _save(fig, "fig8_api_sequence.png")


def draw_deployment() -> Path:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Deployment Architecture (Render + Supabase + Groq)", fontsize=13, fontweight="bold", color=NAVY)

    boxes = [
        (0.5, 4.0, 2.2, 1.2, "End User", LIGHT, NAVY),
        (3.2, 4.0, 2.6, 1.2, "Render Web Service\nPython 3.12 + Uvicorn", TEAL, "white"),
        (6.5, 4.5, 2.8, 0.9, "Groq API\n(LLM)", "#6C3483", "white"),
        (6.5, 3.0, 2.8, 0.9, "RapidAPI / Open-Meteo\nOpenTripMap / FX API", SAFFRON, "white"),
        (3.2, 1.5, 2.6, 1.2, "Supabase\nPostgreSQL", NAVY, "white"),
        (0.5, 1.5, 2.2, 1.2, ".env secrets\n(keys on Render)", LIGHT, NAVY),
    ]
    for x, y, w, h, text, bg, fg in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", facecolor=bg, edgecolor=NAVY, lw=1.5))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.5, color=fg, fontweight="bold")

    for (x1, y1), (x2, y2) in [((2.7, 4.6), (3.2, 4.6)), ((5.8, 4.6), (6.5, 4.9)), ((5.8, 4.3), (6.5, 3.4)), ((4.5, 4.0), (4.5, 2.7)), ((2.7, 2.1), (3.2, 2.1))]:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2))
    return _save(fig, "fig9_deployment.png")


def draw_layered_architecture() -> Path:
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Layered Application Architecture", fontsize=13, fontweight="bold", color=NAVY)

    layers = [
        ("Presentation", "Jinja2 templates, HTML, CSS, static files", LIGHT, NAVY),
        ("API / Routing", "app/api/routes.py — REST endpoints", TEAL, "white"),
        ("Business Logic", "PlannerService, SupabaseService, Agents", SAFFRON, "white"),
        ("Schemas", "Pydantic models — PlanRequest, PlanResponse", GREEN, "white"),
        ("External I/O", "httpx → third-party APIs; Supabase client", "#6C3483", "white"),
    ]
    y = 5.8
    for title, desc, bg, fg in layers:
        ax.add_patch(FancyBboxPatch((0.8, y - 0.9), 6.4, 1.0, boxstyle="round,pad=0.02", facecolor=bg, edgecolor=NAVY, lw=1.5))
        ax.text(1.1, y - 0.25, title, fontsize=10, fontweight="bold", color=fg)
        ax.text(1.1, y - 0.55, desc, fontsize=8, color=fg if fg != NAVY else "#333")
        y -= 1.15
    return _save(fig, "fig10_layered_architecture.png")


def generate_all() -> list[Path]:
    return [
        draw_architecture(),
        draw_single_vs_multi(),
        draw_agent_flow(),
        draw_ui_mockup(),
        draw_database_er(),
        draw_database_crud(),
        draw_sample_record(),
        draw_api_sequence(),
        draw_deployment(),
        draw_layered_architecture(),
    ]


if __name__ == "__main__":
    for p in generate_all():
        print(p)
