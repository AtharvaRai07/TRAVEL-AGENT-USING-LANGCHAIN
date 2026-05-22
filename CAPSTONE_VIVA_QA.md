# Go Bharat — Capstone Viva Q&A (Group 138)

**Student:** Atharva Rai | **Roll:** UA2503CDH393  
**Project:** Go Bharat — Smart Travel Planning Website  
**Live URL:** https://travel-agent-using-langchain.onrender.com  
**Your role:** Backend — FastAPI, multi-agent pipeline, API integrations, deployment

Use this document to rehearse answers aloud. Speak in your own words; do not memorize every sentence.

---

## Table of Contents

1. [How to explain the workflow (SHORT)](#how-to-explain-the-workflow-short)
2. [How to explain the workflow (LONG)](#how-to-explain-the-workflow-long)
3. [Project overview & motivation](#1-project-overview--motivation)
4. [Your contribution & team](#2-your-contribution--team)
5. [Backend — FastAPI & architecture](#3-backend--fastapi--architecture)
6. [LangChain, LangGraph, Groq, Agentic AI](#4-langchain-langgraph-groq-agentic-ai)
7. [Agents (specialists)](#5-agents-specialists)
8. [External APIs & data grounding](#6-external-apis--data-grounding)
9. [Database — Supabase & JSONB](#7-database--supabase--jsonb)
10. [REST API endpoints](#8-rest-api-endpoints)
11. [Frontend integration](#9-frontend-integration)
12. [Deployment & environment](#10-deployment--environment)
13. [Testing, security, limitations](#11-testing-security-limitations)
14. [Single agent vs multi-agent (exam favourite)](#12-single-agent-vs-multi-agent-exam-favourite)
15. [Tough / follow-up questions](#13-tough--follow-up-questions)
16. [Demo script for the teacher](#14-demo-script-for-the-teacher)
17. [Quick glossary](#15-quick-glossary)

---

## How to explain the workflow (SHORT)

> **30–60 seconds — say this first if they ask “explain your project flow”:**

“Go Bharat is a travel planning web app. The user enters email, city, dates, budget, and travel style on the dashboard. FastAPI validates the request with Pydantic. Then **PlannerService** runs: it geocodes the city, fetches **live data** from Open-Meteo, TripAdvisor, OpenTripMap, and an exchange-rate API, builds HTML cards for hotels, restaurants, and attractions, and uses a **LangChain + Groq** Weather Agent to turn raw weather numbers into friendly prose. The full plan is returned to the UI and **saved in Supabase** as one JSON row. Later the user can call separate endpoints for a **day-wise itinerary** and **budget tiers**—those agents read the saved plan so we do not redo all API calls. A **Travel Chatbot** answers follow-up questions using the stored plan as context, with chat history kept in server memory per email.”

---

## How to explain the workflow (LONG)

> **2–4 minutes — use when they want depth:**

“**Problem:** Trip planning is fragmented—weather, hotels, food, places, and budget live on different sites, and generic chatbots can hallucinate without real data.

“**Solution:** Go Bharat unifies this in one FastAPI backend with a **layered architecture**: templates for the UI, `/api/v1` routes, service layer (`PlannerService`, specialist agents, `SupabaseService`), and external APIs plus Groq for language generation.

“**Step 1 — User input:** On POST `/api/v1/plan`, the client sends `PlanRequest`: email, city, check-in/out, adults, budget amount/currency, and style. We reject invalid dates—check-out must be after check-in—with HTTP 422.

“**Step 2 — Orchestration (conceptual multi-agent flow):** In our report we document a **LangGraph-style** pipeline: parse intent → run specialists → merge → summary. In code, **PlannerService** is the orchestrator for the main plan. It does not invent hotels; it calls TripAdvisor via RapidAPI, OpenTripMap for attractions, and Open-Meteo for geocoding, current forecast, and historical weather for the travel date.

“**Step 3 — Grounding + AI:** Raw API results become structured HTML snippets. For weather, we pass **factual snapshots** (temperature, humidity, seasonal highs/lows, rain) into the **Weather Agent**—a LangChain chain: `PromptTemplate | ChatGroq | StrOutputParser`—so the LLM only narrates what the APIs already proved.

“**Step 4 — Response & persistence:** `PlanResponse` includes weather text, hotel/restaurant/attraction HTML, currency sentence, and `final_response`—one composed HTML brief. `routes.py` merges metadata and calls `SupabaseService.store_travel_plan`. If Supabase fails, the user still gets the plan with a `warning` field.

“**Step 5 — On-demand agents:** Itinerary and budget are heavier LLM tasks with large prompts and high `max_tokens`. They run on POST `/itinerary/{email_id}` and `/budget/{email_id}` after loading the latest plan from Supabase—so we isolate failures and save Groq cost.

“**Step 6 — Chat:** POST `/chat` loads the same plan, builds a system prompt with weather/hotels/food/attractions/currency, and uses Groq with multi-turn history in a Python dict keyed by `email_id`.

“**Why this design:** Live APIs reduce hallucination; separate agents mean separate prompts and token limits; persistence means the chatbot is **plan-aware**, not a blank slate. We deploy on **Render** with secrets in environment variables, database on **Supabase PostgreSQL**.”

---

## 1. Project overview & motivation

### Q1. What is Go Bharat?

**A:** Go Bharat is a smart travel planning web application for “Digital Bharat.” It lets users enter trip details (destination, dates, party size, budget, style) and get a unified brief: weather narrative, hotel and restaurant suggestions, attractions, and currency context—backed by live APIs and AI agents, stored in a database, with optional itinerary, budget breakdown, and a plan-aware chatbot.

### Q2. What problem does it solve?

**A:** Travellers usually juggle many websites for weather, stays, food, sightseeing, and money. Information is fragmented, not personalized to their dates/budget, and often lost between sessions. Single generic chatbots may invent hotels or weather. Go Bharat aggregates real API data, structures it, persists it, and uses specialized AI only where narrative or planning is needed.

### Q3. Who is in your team and what did you do?

**A:** Group 138, IIT Patna Hybrid UG CS & Data Analytics. Nishant—concept and vision; **I (Atharva)—backend**: FastAPI, LangChain agents, external API integration, Supabase, Render deployment; Pranav—supporting full-stack learning; Avni—data/support; Ritika—frontend (HTML, CSS, Jinja2), UI, presentation. I own the server-side flow from HTTP request to stored plan.

### Q4. How is this related to tourism policy / Digital Bharat?

**A:** Government initiatives push digital access to tourism information. Our app lowers friction for first-pass planning—especially domestic trips—by combining discovery and AI-assisted narrative in one place. We position it as educational aggregation, not a replacement for licensed tour operators or OTAs for final booking.

### Q5. What is the live deployment URL?

**A:** https://travel-agent-using-langchain.onrender.com — hosted on Render; database on Supabase; LLM via Groq.

---

## 2. Your contribution & team

### Q6. What exactly did you implement in the backend?

**A:** FastAPI app and `/api/v1` routes; Pydantic schemas; `PlannerService` for async httpx calls to weather, TripAdvisor, OpenTripMap, exchange rates; `WeatherAgent`, `ItineraryAgent`, `BudgetAgent` using LangChain + Groq; `TravelChatbot`; `SupabaseService` for CRUD on `travel_plans`; environment-based config; deployment via `render.yaml`.

### Q7. Did you build the frontend?

**A:** Ritika led frontend. I integrated via REST—forms POST to `/api/v1/plan`, dashboard lists plans by email, chat/itinerary/budget hit my endpoints. I ensured response shapes match what templates expect (HTML fragments in `final_response`, etc.).

### Q8. Why FastAPI and not Flask/Django?

**A:** FastAPI gives automatic OpenAPI docs, native async support for parallel HTTP calls to external APIs, and Pydantic validation built in—important when we validate dates, email, and budget fields on every plan request.

---

## 3. Backend — FastAPI & architecture

### Q9. Explain your layered architecture.

**A:**  
- **Presentation:** Jinja2 templates (`login.html`, `dashboard.html`) + static CSS.  
- **API:** `app/api/routes.py` — REST under `/api/v1`.  
- **Services:** `planner.py`, `*_agent.py`, `supabase_service.py`, `chatbot.py`.  
- **Schemas:** `app/schemas/travel.py` — request/response models.  
- **Config:** `app/core/config.py`, `.env` for secrets.  
- **Data:** Supabase PostgreSQL.  
- **External:** Open-Meteo, RapidAPI TripAdvisor16, OpenTripMap, Exchange Rate API, Groq.

### Q10. What is `PlannerService`?

**A:** The main orchestrator for POST `/plan`. Its `generate()` method: geocodes city → fetches weather (API + Weather Agent) → hotels/restaurants (TripAdvisor) → attractions (OpenTripMap) → currency line → builds HTML cards → composes `final_response` → returns `PlanResponse`. It is the “merge + summary” for the base trip brief.

### Q11. Why async (`async def`, `httpx`)?

**A:** Plan generation waits on multiple network I/O calls. Async lets the server handle other requests while awaiting APIs. We use `httpx.AsyncClient` with timeouts (typically 20–25 seconds) per external call.

### Q12. What is Pydantic used for?

**A:** `PlanRequest` validates email (`EmailStr`), city length, adults 1–10, budget ≥ 0, ISO dates. `PlanResponse` defines the API contract. Invalid body → FastAPI returns 422 automatically; we add a custom check that `check_out > check_in`.

### Q13. Where is validation for dates?

**A:** In `routes.py` `create_plan`: if `check_out <= check_in`, HTTP 422 with detail `"check_out must be after check_in"`. Pydantic ensures types; business rule is in the route.

### Q14. What happens if Supabase insert fails?

**A:** Plan generation still succeeds. We catch the exception, log it, and set `plan.warning` so the client knows storage failed but data is still shown.

### Q15. What is CORS middleware for?

**A:** `CORSMiddleware` with `allow_origins=["*"]` so browser clients (or separate frontends) can call the API during development/demo. In strict production you would narrow origins.

### Q16. Difference between `main.py` at root and `app/main.py`?

**A:** `app/main.py` is the FastAPI application—routes, static files, template pages for `/` and `/dashboard`. Root `main.py` / `run.py` typically starts Uvicorn pointing at that app (check your `run.py` entry when demonstrating).

---

## 4. LangChain, LangGraph, Groq, Agentic AI

### Q17. What is LangChain?

**A:** A Python framework for building LLM applications. We use it for **prompt templates**, **chains** (`prompt | llm | parser`), and **message types** (System/Human/AI) in the chatbot. It standardizes how we connect Groq models to structured prompts.

### Q18. What is LangGraph?

**A:** A library to model agent workflows as a **directed graph**: nodes (agents/tools), edges (control flow), support for parallel branches and merge nodes. Our **report architecture** is Parser → 7 parallel specialists → Merge → Summary Plan. That is the design pattern we teach and diagram—even where the MVP orchestrates mainly through `PlannerService` and on-demand agent endpoints.

### Q19. Do you use LangGraph library in code today?

**A:** Be honest if asked deeply: `requirements.txt` lists LangChain packages, not `langgraph`. The **implemented** flow is orchestrated by `PlannerService` plus separate `ItineraryAgent` / `BudgetAgent` / `TravelChatbot`. The **conceptual** multi-agent graph matches our capstone diagrams and is the target architecture; LangGraph would formalize parallel Parser/fan-out/Merge in one graph object. Say: “We follow multi-agent **principles**; LangGraph is how we document and can refactor the orchestrator.”

### Q20. What is an AI “agent” in your project?

**A:** A module with a **narrow goal**, **fixed prompt**, **bounded inputs** (often API-sourced lists), and **structured output**—e.g. Weather Agent writes two paragraphs from weather snapshots; Budget Agent outputs markdown tables in eight sections. “Agentic” means goal-directed steps within guardrails, not a fully autonomous human travel agent.

### Q21. What is Groq and why use it?

**A:** Groq provides fast LLM inference APIs. We use `langchain_groq.ChatGroq` with model `openai/gpt-oss-120b` for interactive latency on plan/chat/itinerary/budget generation.

### Q22. What is `ChatGroq`?

**A:** LangChain’s wrapper around Groq’s chat completion API. Configured with `api_key`, `temperature`, and `max_tokens` per use case.

### Q23. What is a LangChain “chain” in your code?

**A:** Example in `WeatherAgent`:  
`self.chain = self.prompt | self.llm | StrOutputParser()`  
Then `await self.chain.ainvoke({...})`. This pipes template-filled prompt → LLM → string output.

### Q24. What is `StrOutputParser`?

**A:** Converts the LLM response object to a plain string we return to FastAPI and store in Supabase/UI.

### Q25. What is `PromptTemplate`?

**A:** A reusable string template with variables (`{city}`, `{hotels}`, etc.). Keeps prompts out of route handlers and lets each agent evolve independently.

### Q26. What is temperature? What values do you use?

**A:** Temperature controls randomness. Weather Agent ~0.6 (consistent prose); Itinerary ~0.7 (creative scheduling); Budget ~0.55 (more numeric discipline); Chatbot ~0.7 (conversational). Higher = more varied wording.

### Q27. What is `max_tokens` and why different per agent?

**A:** Caps output length and cost. Weather uses 700 tokens; Itinerary 2000; Budget up to 8192 for large tables. A single monolithic prompt would force one compromise for all tasks.

### Q28. What is Agentic AI vs a normal chatbot?

**A:** Normal chatbot: fixed FAQ, little tool use, no persistent structured plan. Agentic (our case): orchestrated specialists, live API context injected into prompts, inspectable modules, stored plan in DB, outputs as HTML/tables—not one short generic reply.

### Q29. Do you use RAG / vector database?

**A:** No vector DB. We do **RAG-like context injection**: the chatbot’s system prompt embeds the full saved plan text from Supabase. That is retrieval by primary key (email + latest plan), not semantic search.

### Q30. What is an LLM hallucination and how do you reduce it?

**A:** Model invents facts not in context. Mitigations: hotel/restaurant names come from TripAdvisor JSON; attractions from OpenTripMap; weather numbers from Open-Meteo before the LLM writes prose; prompts tell agents to use **provided lists only**; itinerary/budget prompts reference stored HTML lists.

### Q31. What model name do you use?

**A:** `openai/gpt-oss-120b` via Groq in Weather, Itinerary, Budget agents and Travel Chatbot.

### Q32. What if `GROQ_API_KEY` is missing?

**A:** Weather Agent catches errors and returns a fallback friendly message; chatbot **raises** on init if key missing; itinerary/budget return error strings. Demo requires key in Render env.

---

## 5. Agents (specialists)

### Q33. List all agents / specialist modules.

**A:**  
1. **Weather Agent** — LangChain chain; narrative from API snapshots.  
2. **Hotel/Restaurant/Attraction presentation** — `PlannerService` HTML builders (API-grounded, not LLM-invented).  
3. **Itinerary Agent** — day tables in markdown.  
4. **Budget Agent** — tiered budget tables.  
5. **Travel Chatbot** — multi-turn Q&A on saved plan.  
Report also describes Parser, Things to Carry, Merge, Summary as graph nodes—for full LangGraph target.

### Q34. How does the Weather Agent work step by step?

**A:** `PlannerService._weather_brief` geocodes city → current forecast + historical archive for same calendar day last year → builds `current_snapshot` and `seasonal_snapshot` strings → passes to `WeatherAgent.generate()` → LLM returns two short paragraphs → stored in `PlanResponse.weather`.

### Q35. Why LLM for weather if you already have API data?

**A:** APIs give numbers; users want readable, friendly guidance (packing, day vs night). The LLM **narrates** grounded facts; it should not invent temperatures we did not supply.

### Q36. How does Itinerary Agent get its inputs?

**A:** Route loads latest plan from Supabase (`weather`, `hotels`, `restaurants`, `attractions` strings), rebuilds `PlanRequest`, calls `ItineraryAgent.generate()`. Prompt demands markdown tables per day with 12-hour times, Title Case day labels.

### Q37. How does Budget Agent work?

**A:** Same pattern—loads stored listings and budget fields. Prompt requires eight sections: overview, master allocation, tier summary (~35%, ~60%, 100% of user budget), lodging/dining/activities by tier, daily cash plan per calendar day, savings table—all in markdown tables in `{budget_currency}`.

### Q38. What is the Travel Chatbot?

**A:** `TravelChatbot` class: builds system prompt from plan fields; keeps `sessions[email_id]` list of user/assistant messages; invokes `ChatGroq` with `SystemMessage`, history, new `HumanMessage`; appends to session. Not part of initial parallel fan-out—it runs after plan exists.

### Q39. Where is chat history stored?

**A:** In-memory Python dict on the server process. **Limitation:** lost on restart or second Render instance; report future work is persist chat in Supabase.

### Q40. Why are itinerary and budget separate endpoints, not in `/plan`?

**A:** They are token-heavy and slow; user may only want base plan first. Separating endpoints saves cost, allows retry on one agent, and matches “modular features” in the report.

### Q41. Is there a “Parser Agent” in code?

**A:** For structured form POST `/plan`, **Pydantic + the form fields** effectively parse entities (city, dates, budget, style)—no separate LLM parser node. A natural-language “Parser Agent” is in the **target LangGraph** design for free-text queries like “5-day trip to Jaipur.”

### Q42. Things to Carry agent?

**A:** Described in report as using weather output; **not a separate Python file** in current repo—mention as future graph node or extension using weather + destination metadata.

---

## 6. External APIs & data grounding

### Q43. Which external APIs do you use?

**A:**  
- **Open-Meteo Geocoding** — lat/lon from city name.  
- **Open-Meteo Forecast** — current temp/humidity.  
- **Open-Meteo Archive** — historical same-date-last-year for seasonal expectation.  
- **RapidAPI TripAdvisor16** — hotels and restaurants.  
- **OpenTripMap** — attractions radius + detail by xid.  
- **Exchange Rate API** (`exchangerate-api.com`) — budget conversion narrative.  
- **Groq** — LLM.

### Q44. How do you pick the right city from geocoding?

**A:** Open-Meteo returns multiple matches; `PlannerService._geocode` scores by exact name match, prefix, substring, `difflib` similarity, and admin/country token overlap—picks highest score.

### Q45. What if `RAPIDAPI_KEY` is missing?

**A:** `_fetch_hotels` / `_fetch_restaurants` return empty lists; UI shows “No live hotel/restaurant results”—graceful degradation, no crash.

### Q46. What if `OPENTRIP_API_KEY` is missing?

**A:** Attractions list empty; message in UI. Plan still returns.

### Q47. Why TripAdvisor via RapidAPI?

**A:** Structured hotel/restaurant search with ratings, price hints, and addresses suitable for cards—common choice for academic integration without scraping.

### Q48. How do attractions search work?

**A:** Geocode → radius search 15 km with kinds filter → for each `xid` fetch place details → keep up to 8 with names, categories, distance from center.

### Q49. Why historical weather one year back?

**A:** For future trip dates, long-range forecast may be limited; archive for the same calendar date last year estimates seasonal highs, lows, and rain—a practical heuristic for packing advice.

### Q50. What is `httpx`?

**A:** Modern async HTTP client used for all external API calls in `PlannerService`.

---

## 7. Database — Supabase & JSONB

### Q51. Why Supabase?

**A:** Managed PostgreSQL, quick setup, Python client, fits capstone timeline. Stores rich plan documents without designing many normalized tables upfront.

### Q52. Describe the `travel_plans` table.

**A:** Columns: `id` (bigint identity PK), `email_id` (text), `city` (text), `travel_details` (JSONB), `created_at` (timestamptz). Indexes on `email_id`, `(email_id, city)`, optional GIN on JSONB.

### Q53. Why JSONB instead of many tables?

**A:** UI and agents consume one blob (weather HTML, hotels, metadata). One round-trip per fetch; matches `PlanResponse.model_dump()`. Trade-off: cross-user analytics needs JSON operators; acceptable for Capstone-I.

### Q54. What CRUD operations does `SupabaseService` implement?

**A:**  
- **Create:** `store_travel_plan` — INSERT after plan.  
- **Read:** `fetch_travel_plan` (latest by email, optional city filter), `fetch_all_plans`, `fetch_plan_by_id`.  
- **Update/Delete:** Not implemented in MVP—new plan = new row.

### Q55. How does `fetch_travel_plan` merge data?

**A:** SELECT latest row; spreads `travel_details` JSON into top-level dict with record fields so routes/agents access `weather`, `hotels`, etc. directly.

### Q56. What is stored inside `travel_details`?

**A:** Full plan payload: `PlanResponse` fields plus `adults`, `budget_amount`, `budget_currency`, `style`, `city`, dates—everything chat and itinerary endpoints need.

### Q57. Is email authentication?

**A:** **No**—email is identifier only, not OAuth/password. Limitation: anyone knowing an email could request their plans; future work is proper auth + RLS.

### Q58. Service role vs anon key?

**A:** Backend should use Supabase key server-side only (Render env), never commit keys to Git. RLS can harden if anon key ever goes to browser.

---

## 8. REST API endpoints

### Q59. List all API endpoints.

**A:**  
- `GET /api/v1/health` — uptime.  
- `POST /api/v1/plan` — create plan + store.  
- `GET /api/v1/plans/{email_id}` — list plans.  
- `GET /api/v1/plans/{email_id}/{plan_id}` — one plan.  
- `POST /api/v1/chat` — chat with plan context.  
- `GET /api/v1/chat/history/{email_id}`  
- `POST /api/v1/chat/clear/{email_id}`  
- `POST /api/v1/itinerary/{email_id}` — optional `city` query.  
- `POST /api/v1/budget/{email_id}` — optional `city` query.

### Q60. Sample POST `/plan` body?

**A:**
```json
{
  "email_id": "student@example.com",
  "city": "Jaipur",
  "check_in": "2026-04-10",
  "check_out": "2026-04-14",
  "adults": 2,
  "budget_amount": 50000,
  "budget_currency": "INR",
  "style": "balanced"
}
```

### Q61. What does the plan response contain?

**A:** `email_id`, `destination`, `weather`, `hotels`, `restaurants`, `attractions`, `currency`, `final_response` (HTML article), `generated_at`, optional `warning`.

### Q62. What is `final_response`?

**A:** Single HTML document assembled in `_compose_final`—hero, weather section, stay/food/places cards, budget glance—for dashboard rendering.

---

## 9. Frontend integration

### Q63. How does the dashboard talk to your backend?

**A:** Browser JavaScript/fetch calls REST JSON endpoints; templates render returned HTML strings into the page. Login collects email used across requests.

### Q64. Jinja2 role?

**A:** Server-side HTML templates for login and dashboard shell; dynamic trip content often injected client-side from API JSON/HTML fields.

### Q65. Why server-rendered pages + API?

**A:** Simple capstone stack: FastAPI serves pages and JSON from one deploy; no separate React build required.

---

## 10. Deployment & environment

### Q66. Where is it deployed?

**A:** **Render** Python web service; `render.yaml` defines build/start; env vars injected at runtime.

### Q67. Required environment variables?

**A:** `SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY`, `RAPIDAPI_KEY`, `OPENTRIP_API_KEY`, plus app settings (`ENVIRONMENT`, `DEBUG` as applicable).

### Q68. What is Uvicorn / ASGI?

**A:** ASGI server running the FastAPI app—handles async routes. Production: Uvicorn workers behind Render’s HTTP router.

### Q69. How do you protect API keys?

**A:** Keys only in `.env` locally and Render dashboard—never in Git. `.gitignore` should exclude `.env`.

### Q70. What happens on Render free tier cold start?

**A:** First request after idle may be slow (spin-up). Mention during demo—hit health or load page early.

---

## 11. Testing, security, limitations

### Q71. How did you test?

**A:** Health check; 422 on bad dates; plan with/without optional keys; Supabase round-trip; itinerary/budget after plan; multi-turn chat; manual UI walkthrough (Jaipur, Paris, etc.).

### Q72. Main limitations?

**A:** Email-only identity; API keys needed for rich hotels/food/places; LLM outputs need human verification for bookings; chat not persisted; no LangGraph parallel fan-out in code yet; Things to Carry not implemented as separate agent file.

### Q73. Future work?

**A:** OAuth; persist chat; Hindi prompts; PDF/ICS export; more agents (AQI, transit); CI tests; rate limiting on Groq; curated Indian “hidden gems” dataset.

### Q74. Advantages of your approach?

**A:** Unified UX; live data trust; modular agents; on-demand heavy LLM; deployable full stack; clear architecture for viva diagrams.

---

## 12. Single agent vs multi-agent (exam favourite)

### Q75. Why not one LLM call for everything?

**A:** One prompt must handle weather prose, HTML lists, markdown itinerary tables, eight budget sections, and chat—high hallucination risk, conflicting format rules, huge latency/cost, hard to debug, cannot rerun only budget. We split concerns.

### Q76. Benefits of multi-agent / multi-module design?

**A:** Specialization, independent prompts/token limits, API grounding per domain, parallel **conceptual** execution, failure isolation (budget fails, weather still saved), easier testing and grading against diagrams.

### Q77. When is single agent OK?

**A:** Small FAQ bots or demos with narrow scope—not our combination of live APIs, long structured outputs, persistence, and multi-turn plan-aware chat.

### Q78. Compare single vs multi in one table?

**A:**

| Criterion | Single agent | Go Bharat (multi-module) |
|-----------|--------------|---------------------------|
| Prompt complexity | Very high | Moderate per agent |
| Hallucination control | Weak | Stronger (API lists in context) |
| Chat follow-up cost | Full replan | Chat only |
| Maintainability | Low | High |
| Explainability in viva | Hard | Clear diagram |

---

## 13. Tough / follow-up questions

### Q79. “Show me the code path for one plan request.”

**A:** `routes.create_plan` → validates dates → `PlannerService.generate()` → geocode/weather APIs → `WeatherAgent` → hotel/restaurant/attraction APIs → HTML builders → `_compose_final` → `PlanResponse` → `SupabaseService.store_travel_plan` → return JSON.

### Q80. “What if two cities have the same name?”

**A:** Geocoding scoring favors best name/admin match; user can type more specific query (“Jaipur, India”). Acknowledge ambiguity as edge case.

### Q81. “How do you handle API rate limits?”

**A:** Timeouts, try/except returning empty lists or fallback messages; on-demand itinerary/budget; no aggressive polling. Future: caching and rate-limit middleware.

### Q82. “Is this true multi-agent or just multiple prompts?”

**A:** Architecturally yes—separate classes, goals, prompts, and orchestration. LangGraph would add explicit graph state and parallel node execution; we already have the **separation of concerns** multi-agent systems aim for.

### Q83. “Difference between LangChain and LangGraph?”

**A:** LangChain = chains, prompts, tools, model wrappers. LangGraph = workflow graph on top (state, branches, cycles). We use LangChain heavily; LangGraph is our documented orchestration model.

### Q84. “Why PostgreSQL JSONB not MongoDB?”

**A:** Supabase is Postgres; JSONB gives document flexibility with SQL and indexes; team familiarity and single managed service.

### Q85. “How is budget ‘optimized’?”

**A:** Budget Agent prompt enforces three tiers (~35%, ~60%, 100% of user budget), category tables, daily spend rows—LLM plans allocation using real hotel/restaurant/attraction context, not a separate OR solver.

### Q86. “Do you fine-tune models?”

**A:** No—we use zero-shot / prompt engineering with Groq hosted model only.

### Q87. “Ethical concerns with AI travel advice?”

**A:** Users must verify prices, visas, safety; we aggregate public API data; disclaimers that we are not a booking agent; prompts discourage inventing venues.

### Q88. “What if LLM ignores instructions?”

**A:** Temperature and strict prompt rules; grounded lists; human review before booking; fallback error strings in agents.

### Q89. “Concurrency in `/plan`—parallel or sequential?”

**A:** Current `PlannerService` awaits weather, then hotels, restaurants, attractions largely **sequentially** in code; report’s LangGraph design targets **parallel** fan-out—honest answer: optimization opportunity with `asyncio.gather` or LangGraph.

### Q90. “Difference between agent and tool?”

**A:** **Tool** = deterministic function/API call (geocode, fetch hotels). **Agent** = LLM + prompt that reasons/narrates over tool outputs (weather prose, itinerary).

### Q91. “Why HTML in API response?”

**A:** Frontend can inject ready-made cards; Ritika’s styling expects structured snippets; reduces client templating work.

### Q92. “How would you scale to 10k users?”

**A:** Auth + RLS; Redis cache for API responses; queue for plan generation; persist chat; horizontal Render instances with sticky sessions or shared session store; monitor Groq spend.

### Q93. “What did you learn?”

**A:** Production-style layering, async API integration, prompt design per task, trade-offs of JSONB vs normalization, deploying secrets safely, explaining agentic systems clearly.

### Q94. “Biggest technical challenge?”

**A:** Pick one you lived: aligning API keys and TripAdvisor geoIds; geocoding ambiguity; long budget outputs needing high `max_tokens`; Supabase errors without blocking UX.

### Q95. “If teacher says report mentions 7 parallel agents but code differs?”

**A:** “Our **architecture and report** follow LangGraph multi-agent design—Parser, parallel specialists, merge, summary. **Implementation** centralizes API orchestration in `PlannerService` and uses LangChain agents where language generation is needed; itinerary, budget, and chat are separate modules. LangGraph is the next step to encode parallel edges explicitly. The **design rationale**—specialization, grounding, modular endpoints—is fully intentional.”

---

## 14. Demo script for the teacher

1. Open live URL → login with your email.  
2. Create plan: **Jaipur**, 4 nights, 2 adults, **₹50,000**, balanced style.  
3. Point out **weather prose** (API + LLM) and **hotel/restaurant/attraction cards** (API lists).  
4. Show plan on dashboard / list endpoint.  
5. Click **Generate itinerary** → markdown day tables.  
6. Click **Generate budget** → tier tables.  
7. Ask chatbot: *“Which hotel is better for families?”* — emphasize it uses **saved plan**.  
8. (Optional) Supabase Table Editor → one `travel_plans` row with JSONB.  
9. Mention **Render** + env vars + **FastAPI health** endpoint.

---

## 15. Quick glossary

| Term | Meaning |
|------|---------|
| **Agentic AI** | Goal-directed AI steps with context and tools, orchestrated by code |
| **LLM** | Large language model (here via Groq) |
| **LangChain** | Framework for prompts, chains, parsers |
| **LangGraph** | Graph-based multi-agent workflow orchestration |
| **JSONB** | PostgreSQL JSON binary type with indexing |
| **Orchestrator** | `PlannerService` + FastAPI routes |
| **Grounding** | Feeding real API data into prompts |
| **ASGI** | Async server interface (Uvicorn + FastAPI) |
| **Pydantic** | Data validation library for request/response models |
| **RAG-like** | Injecting stored plan into chat system prompt without vectors |

---

*Generated for capstone viva preparation — Go Bharat, Group 138, IIT Patna.*
