import asyncio
from crewai import Agent, Task, Crew, Process, LLM
from backend.agents.tools import WeatherTool, TranslateTool, PesticidePriceTool, normalize_disease_name
from backend.config import get_settings

settings = get_settings()

# ─── LLM SETUP ────────────────────────────────────────────────
llm_small = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,
    max_tokens=1024,
    max_retries=2,
)

llm_large = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,
    max_tokens=2048,
    max_retries=2,
)

# ─── PRE-FETCH TOOL (no LLM loop needed) ──────────────────────
_pesticide_tool = PesticidePriceTool()


# ─── STATIC AGENTS (created once at startup) ──────────────────

disease_analyst = Agent(
    role="Plant Disease Specialist",
    goal="Analyze the detected plant disease and identify key risk factors.",
    backstory=(
        "You are a PhD plant pathologist with 15 years of field experience. "
        "You have deep expert knowledge of all plant diseases. "
        "Answer directly from your expertise. Do not use any tools."
    ),
    tools=[],
    llm=llm_small,
    verbose=True,
    max_iter=1,
    max_rpm=2,
)

weather_agent = Agent(
    role="Weather & Spray Schedule Optimizer",
    goal="Get weather forecast and create an optimal spray schedule.",
    backstory=(
        "Agrometeorologist with 10,000+ farm optimizations. "
        "Call get_weather_forecast ONCE then immediately write the schedule. "
        "Never call it twice."
    ),
    tools=[WeatherTool()],
    llm=llm_large,
    verbose=True,
    max_iter=2,
)

treatment_advisor = Agent(
    role="Agricultural Treatment Expert",
    goal="Recommend effective and affordable treatment plans.",
    backstory=(
        "Senior agricultural scientist at ICAR. "
        "Use the pesticide data provided to write a clear treatment plan."
    ),
    tools=[],
    llm=llm_large,
    verbose=True,
    max_iter=1,
)


# ─── MAIN CREW FUNCTION ───────────────────────────────────────

async def run_agriguard_crew(
    disease: str,
    plant: str,
    confidence: float,
    lat: float = None,
    lng: float = None,
    lang: str = "en",
) -> str:

    # Use shared normalizer from tools.py (handles all dataset label formats)
    clean_disease = normalize_disease_name(disease)
    context = f"{clean_disease} on {plant} (confidence: {confidence:.0%})"
    location_str = f"{lat},{lng}" if lat else "20.5937,78.9629"

    # ─── Pre-fetch pesticide data (no ReAct loop) ──────────────
    try:
        pesticide_info = _pesticide_tool._run(clean_disease)
    except Exception:
        pesticide_info = "Apply Copper Oxychloride 3 g/L every 7–10 days as fallback."

    # ─── Dynamic agent: report_writer depends on lang ──────────
    report_writer = Agent(
        role="Farmer Communication Specialist",
        goal="Compile findings into a clear, actionable farmer report.",
        backstory=(
            "Rural extension worker. Use simple language and bullet points. "
            "For English: write directly, NO tools. "
            "For other languages: call translate_report ONCE with the full report."
        ),
        tools=[] if lang == "en" else [TranslateTool()],
        llm=llm_large,
        verbose=True,
        max_iter=2,
        allow_delegation=False,
    )

    # ─── TASK 1: Disease Analysis ──────────────────────────────
    task1 = Task(
        description=(
            f"Disease detected: {context}. "
            "Using your expert plant pathology knowledge, answer in 4-5 sentences: "
            "1) Stage (early/mid/late based on typical progression)? "
            "2) How fast does it spread? "
            "3) Crop loss % if untreated? "
            "4) What conditions make it worse (humidity, temperature, rainfall)?"
        ),
        expected_output=(
            f"4-5 sentence expert analysis of {clean_disease}: "
            "stage, spread speed, crop loss %, worsening conditions."
        ),
        agent=disease_analyst,
    )

    # ─── TASK 2: Treatment Plan (data pre-fetched, no tool loop)
    task2 = Task(
        description=(
            f"Disease: {clean_disease} on {plant}.\n"
            f"Pesticide data (already fetched):\n{pesticide_info}\n\n"
            "Using this data, write a treatment plan covering: "
            "chemical name, dose, frequency, cost (₹), and organic alternative."
        ),
        expected_output=(
            "Treatment plan with: "
            "1) Chemical: name, dose, frequency, cost. "
            "2) Organic alternative."
        ),
        agent=treatment_advisor,
        context=[task1],
    )

    # ─── TASK 3: Weather & Spray Schedule ─────────────────────
    task3 = Task(
        description=(
            f"Call get_weather_forecast ONCE with location '{location_str}'. "
            "Then immediately write a 7-day spray schedule. "
            "Mark ✅ safe and ❌ unsafe spray days. "
            "Add 1-2 sentences on why weather matters for this pesticide."
        ),
        expected_output=(
            "7-day spray schedule with date, weather summary, safe/unsafe status. "
            "1-2 sentences on weather impact on pesticide effectiveness."
        ),
        agent=weather_agent,
        context=[task2],
    )

    # ─── TASK 4: Final Report ──────────────────────────────────
    task4 = Task(
        description=(
            f"Write a final farmer report in language: {lang}. "
            "Rules: "
            "- English: write directly, NO tools needed. "
            "- Other language: call translate_report ONCE with the full report. "
            "Format: bullet points, simple words. "
            "Start with: 'Most Important Action Today:'"
        ),
        expected_output="Complete farmer-friendly bullet point report.",
        agent=report_writer,
        context=[task1, task2, task3],
    )

    # ─── CREW ─────────────────────────────────────────────────
    crew = Crew(
        agents=[disease_analyst, treatment_advisor, weather_agent, report_writer],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

    # ─── RUN WITH RETRY ───────────────────────────────────────
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            result = await asyncio.to_thread(crew.kickoff)
            return str(result)

        except Exception as e:
            error_str = str(e).lower()

            if "rate_limit" in error_str or "429" in error_str:
                wait_seconds = 60 * (attempt + 1)
                print(f"⏳ Rate limit hit (attempt {attempt + 1}/{max_attempts}). Waiting {wait_seconds}s...")
                await asyncio.sleep(wait_seconds)
                if attempt == max_attempts - 1:
                    return (
                        f"⚠️ AI analysis temporarily unavailable due to high demand.\n\n"
                        f"**Disease detected:** {clean_disease} on {plant} ({confidence:.0%} confidence)\n\n"
                        f"**Quick action:** Apply Copper Oxychloride 3 g/L as a general fungicide while waiting.\n\n"
                        f"Please try again in 2-3 minutes.\n"
                        f"Kisan Call Center: 1800-180-1551 (free)"
                    )

            elif "invalid response from llm" in error_str or "none or empty" in error_str:
                print(f"⚠️ LLM loop failed on attempt {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(10)
                    continue
                else:
                    return (
                        f"**Disease:** {clean_disease} on {plant} ({confidence:.0%} confidence)\n\n"
                        f"**Treatment (standard protocol):** {pesticide_info}\n\n"
                        f"⚠️ Full AI report unavailable. Please retry in a moment.\n"
                        f"Kisan Call Center: 1800-180-1551 (free)"
                    )

            else:
                raise e