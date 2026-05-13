from fastapi import APIRouter, HTTPException

from app.schemas.travel import PlanRequest, PlanResponse, ChatRequest, ChatResponse
from app.services.planner import PlannerService


router = APIRouter(prefix="/api/v1", tags=["travel"])
planner_service = PlannerService()

supabase_service = None
chatbot_service = None


def get_supabase_service():
    global supabase_service
    if supabase_service is None:
        from app.services.supabase_service import SupabaseService
        supabase_service = SupabaseService()
    return supabase_service


def get_chatbot_service():
    global chatbot_service
    if chatbot_service is None:
        from app.services.chatbot import TravelChatbot
        chatbot_service = TravelChatbot()
    return chatbot_service


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/plan", response_model=PlanResponse)
async def create_plan(payload: PlanRequest) -> PlanResponse:
    if payload.check_out <= payload.check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")

    plan = await planner_service.generate(payload)

    plan.check_in = str(payload.check_in)
    plan.check_out = str(payload.check_out)

    try:
        supabase = get_supabase_service()
        plan_data = plan.model_dump()
        plan_data.update(
            {
                "adults": payload.adults,
                "budget_amount": payload.budget_amount,
                "budget_currency": payload.budget_currency,
                "style": payload.style,
                "city": payload.city,
            }
        )
        result = supabase.store_travel_plan(
            payload.email_id,
            payload.city,
            plan_data
        )
        print(f"✅ Plan stored successfully: {result}")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Storage error: {error_msg}")
        plan.warning = f"⚠️ Plan generated but storage failed: {error_msg}"

    return plan


@router.get("/plans/{email_id}")
async def get_user_plans(email_id: str) -> dict:
    try:
        supabase = get_supabase_service()
        plans = supabase.fetch_all_plans(email_id)
        return {"plans": plans}
    except Exception as e:
        print(f"[ERROR] Failed to fetch plans: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch plans: {str(e)}")


@router.get("/plans/{email_id}/{plan_id}")
async def get_plan_details(email_id: str, plan_id: int) -> dict:
    try:
        supabase = get_supabase_service()
        plan = supabase.fetch_plan_by_id(email_id, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch plan details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch plan details: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    try:
        supabase = get_supabase_service()
        chatbot = get_chatbot_service()
    except Exception as e:
        print(f"[ERROR] Service init failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")

    try:
        travel_plan = supabase.fetch_travel_plan(payload.email_id)
    except Exception as e:
        print(f"[ERROR] Fetch plan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch plan: {str(e)}")

    if not travel_plan:
        raise HTTPException(
            status_code=404,
            detail="No travel plan found for this email. Please create a plan first."
        )

    try:
        print(f"[DEBUG] Calling chatbot for email: {payload.email_id}")
        bot_response = await chatbot.chat(
            payload.email_id,
            payload.message,
            travel_plan
        )
        print(f"[DEBUG] Chatbot response successful")
    except Exception as e:
        print(f"[ERROR] Chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

    return ChatResponse(
        email_id=payload.email_id,
        user_message=payload.message,
        bot_response=bot_response
    )


@router.get("/chat/history/{email_id}")
async def get_chat_history(email_id: str) -> dict:
    try:
        chatbot = get_chatbot_service()
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Chatbot service init failed: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")

    history = chatbot.get_session_history(email_id)
    return {"email_id": email_id, "history": history}


@router.post("/chat/clear/{email_id}")
async def clear_chat_history(email_id: str) -> dict:
    try:
        chatbot = get_chatbot_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")

    chatbot.clear_session(email_id)
    return {"message": "Chat history cleared"}


@router.post("/itinerary/{email_id}")
async def generate_itinerary(email_id: str, city: str = None) -> dict:
    try:
        supabase = get_supabase_service()
        from app.services.itinerary_agent import ItineraryAgent
        from app.schemas.travel import PlanRequest
        from datetime import datetime

        travel_plan = supabase.fetch_travel_plan(email_id, city)
        if not travel_plan:
            raise HTTPException(
                status_code=404,
                detail="No travel plan found. Please create a plan first."
            )

        check_in_str = travel_plan.get("check_in", "")
        check_out_str = travel_plan.get("check_out", "")

        try:
            check_in_date = datetime.fromisoformat(check_in_str).date() if check_in_str else datetime.utcnow().date()
            check_out_date = datetime.fromisoformat(check_out_str).date() if check_out_str else datetime.utcnow().date()
        except Exception:
            check_in_date = datetime.utcnow().date()
            check_out_date = datetime.utcnow().date()

        plan_req = PlanRequest(
            email_id=email_id,
            city=travel_plan.get("destination", travel_plan.get("city", "")),
            check_in=check_in_date,
            check_out=check_out_date,
            adults=int(travel_plan.get("adults", 2)),
            budget_amount=float(travel_plan.get("budget_amount", 0)),
            budget_currency=str(travel_plan.get("budget_currency", "USD")),
            style=str(travel_plan.get("style", "balanced")),
        )

        agent = ItineraryAgent()
        itinerary = await agent.generate(
            req=plan_req,
            weather=travel_plan.get("weather", ""),
            hotels=travel_plan.get("hotels", ""),
            restaurants=travel_plan.get("restaurants", ""),
            attractions=travel_plan.get("attractions", ""),
        )

        return {
            "email_id": email_id,
            "destination": travel_plan.get("destination"),
            "itinerary": itinerary
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Itinerary generation failed: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate itinerary: {str(e)}")


@router.post("/budget/{email_id}")
async def generate_budget(email_id: str, city: str = None) -> dict:
    try:
        supabase = get_supabase_service()
        from app.services.budget_agent import BudgetAgent
        from app.schemas.travel import PlanRequest
        from datetime import datetime

        travel_plan = supabase.fetch_travel_plan(email_id, city)
        if not travel_plan:
            raise HTTPException(
                status_code=404,
                detail="No travel plan found. Please create a plan first."
            )

        check_in_str = travel_plan.get("check_in", "")
        check_out_str = travel_plan.get("check_out", "")

        try:
            check_in_date = datetime.fromisoformat(check_in_str).date() if check_in_str else datetime.utcnow().date()
            check_out_date = datetime.fromisoformat(check_out_str).date() if check_out_str else datetime.utcnow().date()
        except Exception:
            check_in_date = datetime.utcnow().date()
            check_out_date = datetime.utcnow().date()

        plan_req = PlanRequest(
            email_id=email_id,
            city=travel_plan.get("destination", travel_plan.get("city", "")),
            check_in=check_in_date,
            check_out=check_out_date,
            adults=int(travel_plan.get("adults", 2)),
            budget_amount=float(travel_plan.get("budget_amount", 0)),
            budget_currency=str(travel_plan.get("budget_currency", "USD")),
            style=str(travel_plan.get("style", "balanced")),
        )

        agent = BudgetAgent()
        budget_plan = await agent.generate(
            req=plan_req,
            hotels=travel_plan.get("hotels", ""),
            restaurants=travel_plan.get("restaurants", ""),
            attractions=travel_plan.get("attractions", ""),
        )

        return {
            "email_id": email_id,
            "destination": travel_plan.get("destination"),
            "budget_plan": budget_plan
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Budget generation failed: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate budget: {str(e)}")
