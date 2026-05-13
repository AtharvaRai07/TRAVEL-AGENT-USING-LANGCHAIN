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

    def store_travel_plan(self, email_id: str, city: str, travel_details: dict) -> dict:
        try:
            print(f"[DEBUG] Storing plan for email: {email_id}, city: {city}", file=sys.stderr)

            response = self.client.table(self.table_name).insert({
                "email_id": email_id,
                "city": city,
                "travel_details": travel_details
            }).execute()

            print(f"[DEBUG] Insert response: {response}", file=sys.stderr)

            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"[ERROR] Failed to store travel plan: {str(e)}", file=sys.stderr)
            raise Exception(f"Failed to store travel plan: {str(e)}")

    def fetch_travel_plan(self, email_id: str, city: str = None) -> Optional[dict]:
        try:
            print(f"[DEBUG] Fetching plan for email: {email_id}, city: {city}", file=sys.stderr)

            query = self.client.table(self.table_name).select("*").eq("email_id", email_id)

            if city:
                query = query.eq("city", city)

            response = query.order("id", desc=True).limit(1).execute()

            print(f"[DEBUG] Fetch response: {response}", file=sys.stderr)

            if response.data and len(response.data) > 0:
                record = response.data[0]
                travel_details = record.get("travel_details", {})
                return {
                    **record,
                    **travel_details
                }
            return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch travel plan: {str(e)}", file=sys.stderr)
            raise Exception(f"Failed to fetch travel plan: {str(e)}")

    def plan_exists(self, email_id: str, city: str = None) -> bool:
        plan = self.fetch_travel_plan(email_id, city)
        return plan is not None

    def fetch_all_plans(self, email_id: str) -> list[dict]:
        try:
            print(f"[DEBUG] Fetching all plans for email: {email_id}", file=sys.stderr)

            response = self.client.table(self.table_name).select("*").eq("email_id", email_id).order("id", desc=True).execute()

            if response.data:
                plans = []
                for record in response.data:
                    details = record.get("travel_details", {})
                    plans.append({
                        "id": record.get("id"),
                        "city": record.get("city", details.get("destination", "Unknown")),
                        "destination": details.get("destination", "Unknown"),
                        "check_in": details.get("check_in", ""),
                        "check_out": details.get("check_out", "")
                    })
                return plans
            return []
        except Exception as e:
            print(f"[ERROR] Failed to fetch all plans: {str(e)}", file=sys.stderr)
            raise Exception(f"Failed to fetch all plans: {str(e)}")

    def fetch_plan_by_id(self, email_id: str, plan_id: int) -> Optional[dict]:
        try:
            print(f"[DEBUG] Fetching plan by id: email={email_id}, plan_id={plan_id}", file=sys.stderr)

            response = (
                self.client
                .table(self.table_name)
                .select("*")
                .eq("email_id", email_id)
                .eq("id", plan_id)
                .limit(1)
                .execute()
            )

            if response.data and len(response.data) > 0:
                record = response.data[0]
                travel_details = record.get("travel_details", {})
                return {
                    **record,
                    **travel_details,
                }
            return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch plan by id: {str(e)}", file=sys.stderr)
            raise Exception(f"Failed to fetch plan by id: {str(e)}")
