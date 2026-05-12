import os
import json
from typing import Optional
import sys

from supabase import create_client, Client


class SupabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
        self.table_name = "travel_plans"

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def store_travel_plan(self, email_id: str, travel_details: dict) -> dict:
        """Store travel plan for user. Returns the stored record. Creates new record each time (not upsert)."""
        try:
            print(f"[DEBUG] Storing plan for email: {email_id}", file=sys.stderr)
            print(f"[DEBUG] Supabase URL: {self.supabase_url}", file=sys.stderr)

            # Use insert() instead of upsert() so each plan is a new row, not an update
            response = self.client.table(self.table_name).insert({
                "email_id": email_id,
                "travel_details": travel_details
            }).execute()

            print(f"[DEBUG] Insert response: {response}", file=sys.stderr)
            print(f"[DEBUG] Response data: {response.data}", file=sys.stderr)

            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"[ERROR] Failed to store travel plan: {str(e)}", file=sys.stderr)
            print(f"[ERROR] Exception type: {type(e)}", file=sys.stderr)
            raise Exception(f"Failed to store travel plan: {str(e)}")

    def fetch_travel_plan(self, email_id: str) -> Optional[dict]:
        """Fetch the most recent travel plan for user by email_id."""
        try:
            print(f"[DEBUG] Fetching plan for email: {email_id}", file=sys.stderr)

            # Order by id DESC to get the most recent plan (id increases with each insert)
            response = self.client.table(self.table_name).select("*").eq("email_id", email_id).order("id", desc=True).limit(1).execute()

            print(f"[DEBUG] Fetch response: {response}", file=sys.stderr)

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch travel plan: {str(e)}", file=sys.stderr)
            raise Exception(f"Failed to fetch travel plan: {str(e)}")

    def plan_exists(self, email_id: str) -> bool:
        """Check if travel plan exists for user."""
        plan = self.fetch_travel_plan(email_id)
        return plan is not None

    def fetch_all_plans(self, email_id: str) -> list[dict]:
        """Fetch all travel plans for a user. Orders by most recent first."""
        try:
            print(f"[DEBUG] Fetching all plans for email: {email_id}", file=sys.stderr)

            response = self.client.table(self.table_name).select("*").eq("email_id", email_id).order("id", desc=True).execute()

            if response.data:
                # Extract destination and dates from travel_details for each plan
                plans = []
                for record in response.data:
                    details = record.get("travel_details", {})
                    plans.append({
                        "id": record.get("id"),
                        "destination": details.get("destination", "Unknown"),
                        "check_in": details.get("check_in", ""),
                        "check_out": details.get("check_out", "")
                    })
                return plans
            return []
        except Exception as e:
            print(f"[ERROR] Failed to fetch all plans: {str(e)}", file=sys.stderr)
            raise Exception(f"Failed to fetch all plans: {str(e)}")
