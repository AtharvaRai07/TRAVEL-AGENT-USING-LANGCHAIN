import os
import json
from typing import Any

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class TravelChatbot:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", "")

        if not self.groq_key:
            raise ValueError("GROQ_API_KEY must be set in environment variables")

        # Use Groq API
        self.model = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=self.groq_key,
            temperature=0.7
        )

        # Session storage for chat history - using email_id as key
        self.sessions: dict[str, list[dict]] = {}

    def _build_system_prompt(self, travel_details: dict) -> str:
        """Build system prompt with travel details context."""
        destination = travel_details.get("destination", "Unknown")
        weather = travel_details.get("weather", "")
        hotels = travel_details.get("hotels", "")
        restaurants = travel_details.get("restaurants", "")
        attractions = travel_details.get("attractions", "")
        currency = travel_details.get("currency", "")

        return f"""You are a helpful travel assistant for the user's trip to {destination}.
You have access to the following travel plan details and can answer any questions about their trip.

TRAVEL PLAN CONTEXT:
---
Weather Information:
{weather}

Hotels:
{hotels}

Restaurants:
{restaurants}

Attractions:
{attractions}

Currency & Budget:
{currency}
---

Based on this information, answer the user's travel questions helpfully and conversationally.
You can also help them with:
- Creating detailed day-by-day itineraries
- Optimizing their budget across different spending levels
- Practical travel tips and recommendations

Be friendly, concise, and practical. When they ask for itinerary or budget planning, provide detailed recommendations."""

    async def chat(self, email_id: str, message: str, travel_details: dict) -> str:
        """Send a message and get response. Maintains session history."""
        try:
            # Initialize session if new user
            if email_id not in self.sessions:
                self.sessions[email_id] = []

            # Build conversation with context
            system_prompt = self._build_system_prompt(travel_details)

            # Build message list with proper LangChain message objects
            messages = [
                SystemMessage(content=system_prompt),
            ]

            # Add previous conversation history
            for msg in self.sessions[email_id]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

            # Add current user message
            messages.append(HumanMessage(content=message))

            # Call LLM with proper message objects
            print(f"[DEBUG] Sending {len(messages)} messages to LLM")
            response = self.model.invoke(messages)
            bot_response = str(response.content)
            print(f"[DEBUG] Got response: {bot_response[:100]}...")

            # Store conversation in session history
            self.sessions[email_id].append({"role": "user", "content": message})
            self.sessions[email_id].append({"role": "assistant", "content": bot_response})

            return bot_response
        except Exception as e:
            print(f"[ERROR] Chat failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def clear_session(self, email_id: str):
        """Clear chat history for a user."""
        if email_id in self.sessions:
            self.sessions[email_id] = []

    def get_session_history(self, email_id: str) -> list[dict]:
        """Get chat history for a user."""
        return self.sessions.get(email_id, [])
