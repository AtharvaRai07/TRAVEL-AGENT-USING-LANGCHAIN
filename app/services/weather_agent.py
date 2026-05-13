"""Weather narration agent using Groq + LangChain."""

import os

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class WeatherAgent:
    """Turn structured weather facts into a human-sounding trip brief."""

    def __init__(self) -> None:
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY", ""),
            temperature=0.6,
            max_tokens=700,
        )

        self.prompt = PromptTemplate(
            input_variables=["city", "date", "resolved_name", "current_snapshot", "seasonal_snapshot"],
            template=(
                "You are a warm, conversational travel buddy. Write a natural weather note that sounds like one human talking to another.\n"
                "Do not sound robotic, scripted, or overly formal. Do not use headings. Avoid bullet points unless they genuinely improve readability.\n"
                "Do not repeat the raw data line by line. Turn it into a friendly, easy-to-read explanation.\n\n"
                "City requested: {city}\n"
                "Resolved city name: {resolved_name}\n"
                "Travel date: {date}\n\n"
                "Current weather facts:\n{current_snapshot}\n\n"
                "Seasonal/weather history facts:\n{seasonal_snapshot}\n\n"
                "Write exactly 2 short paragraphs.\n"
                "The first paragraph should describe what the weather is likely to feel like in a natural way.\n"
                "The second paragraph should say what the traveler should expect during the day and at night, plus practical packing advice.\n"
                "If the data is limited, mention that casually and honestly.\n"
                "Use plain language like 'it should feel', 'you can expect', and 'you’ll probably want'."
            ),
        )

        self.chain = self.prompt | self.llm | StrOutputParser()

    async def generate(
        self,
        city: str,
        target_date: str,
        resolved_name: str,
        current_snapshot: str,
        seasonal_snapshot: str,
    ) -> str:
        try:
            result = await self.chain.ainvoke(
                {
                    "city": city,
                    "date": target_date,
                    "resolved_name": resolved_name,
                    "current_snapshot": current_snapshot,
                    "seasonal_snapshot": seasonal_snapshot,
                }
            )
            return result.strip() if isinstance(result, str) else str(result).strip()
        except Exception as e:
            print(f"[ERROR] Weather generation failed: {str(e)}")
            return "Weather details are available, but I could not generate a friendly summary right now."
