"""Itinerary planning agent using LangChain and LLM."""

import os
from datetime import date

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.schemas.travel import PlanRequest


class ItineraryAgent:
    """Agent for generating personalized travel itineraries."""

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
                "check_in",
                "check_out",
                "style",
                "adults",
                "weather",
                "hotels",
                "restaurants",
                "attractions",
            ],
            template="""You are an expert travel planner. Create a detailed day-by-day itinerary for a trip.

Destination: {city}
Check-in: {check_in}
Check-out: {check_out}
Travel Style: {style}
Number of Adults: {adults}

Weather forecast:
{weather}

Available hotels:
{hotels}

Popular restaurants:
{restaurants}

Top attractions:
{attractions}

Please create a detailed, practical itinerary that:
1. Optimizes for the travel style ({style})
2. Takes into account weather conditions
3. Includes realistic timing and transit between locations
4. Recommends specific restaurants from the provided list
5. Highlights must-see attractions
6. Includes rest/buffer time
7. Is organized day-by-day with morning, afternoon, and evening activities

Format the response as markdown tables only, with one table per day.
Use these columns for each table: Time, Activity, Place, Notes.

Time column rules (strict):
- Use a single 12-hour clock label per row only, e.g. "9 am", "12:30 pm", "7 pm".
- Do not use 24-hour times, do not use ranges (no "9:00–10:00"), and do not put two times in one cell.
- One activity = one row with one time when it starts.

Day titles and any headings: use Title Case (e.g. "Day 1 — City center"), never ALL CAPS.

Put a short 1-line intro before the tables and a short 1-line practical tip after the last table.
Keep the writing concise and legible. Do not use long paragraphs or bullet lists.""",
        )

        self.chain = self.prompt_template | self.llm | StrOutputParser()

    async def generate(
        self,
        req: PlanRequest,
        weather: str,
        hotels: str,
        restaurants: str,
        attractions: str,
    ) -> str:
        """Generate an itinerary based on travel request and gathered information."""
        try:
            result = await self.chain.ainvoke({
                "city": req.city,
                "check_in": req.check_in.isoformat(),
                "check_out": req.check_out.isoformat(),
                "style": req.style,
                "adults": req.adults,
                "weather": weather,
                "hotels": hotels,
                "restaurants": restaurants,
                "attractions": attractions,
            })
            return result.strip() if isinstance(result, str) else str(result).strip()
        except Exception as e:
            print(f"[ERROR] Itinerary generation failed: {str(e)}")
            return "Could not generate itinerary. Please try again later."
