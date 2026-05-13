"""Budget optimization agent using LangChain and LLM."""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.schemas.travel import PlanRequest


class BudgetAgent:
    """Agent for generating budget-conscious travel plans."""

    def __init__(self) -> None:
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY", ""),
            temperature=0.55,
            max_tokens=8192,
        )

        self.prompt_template = PromptTemplate(
            input_variables=[
                "city",
                "budget_amount",
                "budget_currency",
                "check_in",
                "check_out",
                "adults",
                "hotels",
                "restaurants",
                "attractions",
            ],
            template="""You are an expert travel budget consultant. Produce a thorough, actionable budget plan for this trip. Use only markdown (section headings + tables). Do not reply with only one or two sentences—fill every table with real numbers and multiple rows.

Destination: {city}
Total Budget: {budget_amount} {budget_currency}
Check-in: {check_in}
Check-out: {check_out}
Number of Adults: {adults}

Available hotels:
{hotels}

Popular restaurants:
{restaurants}

Top attractions:
{attractions}

Rules:
- Express every amount in {budget_currency} (use integers or simple decimals). Show both trip totals and per-night or per-day figures where useful.
- Three tiers: Budget-conscious (~35% of total), Moderate (~60%), Comfort/Premium (~100%). Derive numeric caps from {budget_amount}.
- Name specific hotels, restaurants, and attractions drawn from the lists above when you recommend them (if a list is thin, say so in Notes and still give realistic placeholders).
- Section headings: short Title Case only (e.g. "Lodging by tier") — never ALL CAPS blocks.
- No long prose paragraphs outside tables; one optional 1–2 sentence intro after each heading is allowed, then the table must carry the detail.

Required structure (in this order):

1) **Overview**
   - One line stating trip length (nights between check-in and check-out) and adults.

2) **Master allocation** — table columns: Category | Trip total ({budget_currency}) | Per night or per day | Notes
   - Minimum rows: Accommodation, Food & dining, Activities & tickets, Local transport, Contingency (10–15%), **Total** (should reconcile with tier caps).

3) **Tier summary** — table columns: Tier | % of full budget | Max spend ({budget_currency}) | Best for | Tradeoffs

4) **Lodging by tier** — table columns: Tier | Property or area | Est. nightly rate | Est. trip lodging total | Why it fits
   - At least **3 rows** (one per tier), more if you suggest alternates.

5) **Dining by tier** — table columns: Tier | Meal focus | Est. daily food | Est. trip food total | Example venues from list

6) **Activities by tier** — table columns: Tier | Must-do priorities | Est. spend | Booking or timing tip

7) **Daily cash plan** — table columns: Date or Day label | Planned spend ({budget_currency}) | Focus (e.g. transit day, big museum) | Cost-saving tip
   - Include **one row per calendar day** from check-in through check-out (inclusive).

8) **Savings and upgrades** — table columns: Idea | Saves or costs ({budget_currency}) | How to apply

If you run out of space, prioritize completing tables 2–7 with full rows over optional intro text.""",
        )

        self.chain = self.prompt_template | self.llm | StrOutputParser()

    async def generate(
        self,
        req: PlanRequest,
        hotels: str,
        restaurants: str,
        attractions: str,
    ) -> str:
        """Generate a budget plan based on travel request and gathered information."""
        try:
            result = await self.chain.ainvoke({
                "city": req.city,
                "budget_amount": req.budget_amount,
                "budget_currency": req.budget_currency,
                "check_in": req.check_in.isoformat(),
                "check_out": req.check_out.isoformat(),
                "adults": req.adults,
                "hotels": hotels,
                "restaurants": restaurants,
                "attractions": attractions,
            })
            return result.strip() if isinstance(result, str) else str(result).strip()
        except Exception as e:
            print(f"[ERROR] Budget generation failed: {str(e)}")
            return "Could not generate budget plan. Please try again later."
