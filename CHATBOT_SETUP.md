# Travel Chatbot Setup Guide

## Overview
This guide walks you through setting up the new Travel Chatbot feature that works alongside the Travel Planner.

## Architecture
- **Travel Planner**: Creates personalized travel plans (existing feature)
- **Travel Chatbot**: New feature that lets users ask questions about their saved travel plans using LangChain + Groq LLM
- **Storage**: All user travel plans are saved to Supabase
- **Chat History**: Session-based (in-memory) - cleared when user closes the session

---

## Step 1: Supabase Setup

### 1.1 Create Supabase Account & Project
1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Save your `Project URL` and `Anon Key` from the project settings

### 1.2 Create the Table
In Supabase SQL Editor, run:

```sql
CREATE TABLE travel_plans (
  id BIGSERIAL PRIMARY KEY,
  email_id VARCHAR(255) NOT NULL UNIQUE,
  travel_details JSONB NOT NULL
);

CREATE INDEX idx_email ON travel_plans(email_id);
```

---

## Step 2: Environment Variables

Update your `.env` file with:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Groq (already needed for travel planner)
GROQ_API_KEY=your_groq_api_key

# Other existing keys
RAPIDAPI_KEY=your_rapidapi_key
FOURSQUARE_API_KEY=your_foursquare_api_key
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Key new packages:
- `supabase`: PostgreSQL database client
- `pydantic[email]`: Email validation for schemas
- `langchain-postgres`: Optional for advanced persistence (not used yet)

---

## Step 4: Run the Application

```bash
python run.py
```

The app runs at `http://127.0.0.1:8000`

---

## How It Works

### User Flow

1. **Create Travel Plan** (Travel Planner tab)
   - User enters email_id (mandatory)
   - Fills travel details
   - Clicks "Generate Plan"
   - Plan is generated AND saved to Supabase with email_id as key

2. **Chat with Chatbot** (Travel Chatbot tab)
   - User enters email_id
   - Clicks "Load My Travel Plan"
   - Plan is fetched from Supabase
   - User can ask questions like:
     - "What's the weather forecast for my trip?"
     - "Can you suggest a good restaurant from my plan?"
     - "How much should I budget for hotels?"
   - LLM responds based on their specific travel plan data
   - Chat history is maintained in-memory during the session

### Backend Architecture

**New Files Created:**
- `app/services/supabase_service.py`: Handles database operations
- `app/services/chatbot.py`: LangChain chatbot with Groq + in-memory history

**New API Endpoints:**
- `POST /api/v1/plan` - Creates plan + stores to Supabase (updated)
- `POST /api/v1/chat` - Chat with bot (new)
- `GET /api/v1/chat/history/{email_id}` - Get chat history (new)
- `POST /api/v1/chat/clear/{email_id}` - Clear chat history (new)

**Updated Files:**
- `app/schemas/travel.py`: Added `email_id` to PlanRequest, ChatRequest, ChatResponse
- `app/api/routes.py`: New chat endpoints with lazy service initialization
- `app/templates/index.html`: Tabs UI + chatbot interface
- `app/static/css/styles.css`: Chat styling

---

## API Usage Examples

### 1. Create & Store Travel Plan

```bash
curl -X POST http://127.0.0.1:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "user@example.com",
    "city": "Paris",
    "check_in": "2026-06-01",
    "check_out": "2026-06-05",
    "adults": 2,
    "budget_amount": 50000,
    "budget_currency": "INR",
    "style": "balanced"
  }'
```

### 2. Chat with Chatbot

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "user@example.com",
    "message": "What are the best restaurants in my itinerary?"
  }'
```

### 3. Get Chat History

```bash
curl http://127.0.0.1:8000/api/v1/chat/history/user@example.com
```

### 4. Clear Chat History

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/clear/user@example.com
```

---

## Important Notes

### Email is Mandatory
- Every travel plan MUST have an associated email_id
- Email_id is used as the unique key in Supabase
- Users enter email when creating their first plan
- Same email retrieves the plan for chatting

### Session-Based Chat History
- Chat history is NOT persisted to database
- Stored in-memory during user session
- Cleared when:
  - User clicks "Clear History" button
  - User closes browser/refreshes page
  - Server restarts
- This is by design (lightweight, no database queries for chat history)

### Error Handling
- If Supabase is not configured, plan generation still works but storage fails with a warning
- If Groq API key is missing, chat endpoints will fail
- All errors are returned with detailed messages

---

## Troubleshooting

### Chatbot says "No travel plan found"
- Make sure you created a plan with the same email_id
- Check that the email exists in Supabase `travel_plans` table

### Chat responses are slow
- First message might be slower (model initialization)
- Groq API has rate limits - wait a moment between messages

### Can't load chat history
- Session history only works during same browser session
- Refresh page = history cleared (by design)

---

## Future Enhancements

Potential improvements:
1. Persistent chat history to database
2. Multi-turn conversation memory with RAG
3. Voice/image uploads to chat
4. Chat export as PDF
5. User authentication & multi-user support
6. Analytics on common travel questions

---

## Support
For issues, check:
1. Environment variables are set correctly
2. Supabase table exists and has correct schema
3. Network connectivity to Supabase
4. Groq API key is valid
