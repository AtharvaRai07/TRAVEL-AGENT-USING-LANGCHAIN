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
            temperature=0.7,
            max_tokens=2000,
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
            template="""You are an expert travel budget consultant. Create a comprehensive budget breakdown and optimization strategy for a trip.

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

Please create a detailed budget plan that includes:

1. BUDGET BREAKDOWN by category:
   - Accommodation (total & per night)
   - Food & Dining (breakfast, lunch, dinner breakdown)
   - Activities & Attractions
   - Transportation (local transit, taxis, etc.)
   - Contingency/Emergency fund (10-15%)

2. BUDGET TIERS (create 3 options):
   - Budget-Conscious: ~35% of total
   - Moderate/Balanced: ~60% of total
   - Comfort/Premium: ~100% of total

3. For each tier, provide:
   - Specific accommodation recommendations from the provided list
   - Restaurant recommendations (mix of street food, casual, upscale)
   - Which attractions to prioritize
   - Money-saving tips

4. DAILY BREAKDOWN:
   - Show how to distribute budget across {check_in} to {check_out}
   - Include tips for cutting costs without sacrificing experience

5. MONEY-SAVING STRATEGIES:
   - Local deals and discounts
   - Free activities in {city}
   - Best times to visit specific venues
   - Transportation optimization

Format the response as markdown tables only, with clear section headings.
Section headings must be short Title Case (e.g. "Budget breakdown", "Recommendations by tier") — never ALL CAPS blocks.

Use these tables:
1. Budget breakdown table with columns: Category, Suggested Spend, Notes.
2. Budget tier table with columns: Tier, Estimated Total, Best For.
3. Daily spend table with columns: Date/Day, Planned Spend, Notes.

Keep the text short, direct, and easy to scan. Avoid long paragraphs and avoid bullet lists.""",
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
