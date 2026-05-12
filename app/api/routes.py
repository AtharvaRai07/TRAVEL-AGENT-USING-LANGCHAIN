from fastapi import APIRouter, HTTPException

from app.schemas.travel import PlanRequest, PlanResponse, ChatRequest, ChatResponse
from app.services.planner import PlannerService


router = APIRouter(prefix="/api/v1", tags=["travel"])
planner_service = PlannerService()

# Lazy initialization for services that need env vars
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

    # Add check_in and check_out to the response
    plan.check_in = str(payload.check_in)
    plan.check_out = str(payload.check_out)

    # Store in Supabase
    try:
        supabase = get_supabase_service()
        # Add check_in and check_out to the plan data before storing
        plan_data = plan.model_dump()
        result = supabase.store_travel_plan(
            payload.email_id,
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
    """Get all travel plans for a user."""
    try:
        supabase = get_supabase_service()
        plans = supabase.fetch_all_plans(email_id)
        return {"plans": plans}
    except Exception as e:
        print(f"[ERROR] Failed to fetch plans: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch plans: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Chat endpoint for travel questions."""
    try:
        supabase = get_supabase_service()
        chatbot = get_chatbot_service()
    except Exception as e:
        print(f"[ERROR] Service init failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")

    # Fetch user's travel plan
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

    # Get bot response
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
    """Get chat history for a user."""
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
    """Clear chat history for a user."""
    try:
        chatbot = get_chatbot_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")

    chatbot.clear_session(email_id)
    return {"message": "Chat history cleared"}
