from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from backend.database.vector_store import get_vector_store
from backend.config import get_settings
import asyncio
from operator import itemgetter
from langchain_core.runnables import RunnableLambda

# FIX: read from settings so .env changes take effect (was hardcoded "llama3" / "http://localhost:11434")
settings = get_settings()

TREATMENT_PROMPT = PromptTemplate.from_template("""
You are AgriGuard, an expert agricultural AI assistant for Indian farmers.
Use ONLY the context below from research papers to give treatment advice.
If context doesn't cover the disease, say so clearly.

Disease Detected: {disease}
Plant: {plant}
Confidence: {confidence}
Farmer Location: {location}

Research Context:
{context}

Provide a structured treatment plan with these sections:
1. IMMEDIATE ACTION (what to do in next 24 hours)
2. CHEMICAL TREATMENT (ICAR-approved pesticide name, exact dosage, frequency)
3. ORGANIC ALTERNATIVE (neem oil, copper sulfate, etc. if applicable)
4. PREVENTIVE MEASURES (to avoid recurrence)
5. ESTIMATED RECOVERY TIME

Use simple language suitable for small-scale farmers. Avoid jargon.
""")

async def get_treatment_advice(
    disease: str, plant: str,
    confidence: float, location: str = "India"
) -> str:
    vectorstore = get_vector_store()

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    # FIX: LLM now reads model and base_url from settings
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.3
    )

    def format_docs(docs):
        return "\n\n---\n\n".join(d.page_content for d in docs)

    chain = (
        {
            "context": (
                RunnableLambda(lambda x: f"{x['disease']} {x['plant']} treatment")
                | retriever
                | format_docs
            ),
            "disease": itemgetter("disease"),
            "plant": itemgetter("plant"),
            "confidence": itemgetter("confidence"),
            "location": itemgetter("location"),
        }
        | TREATMENT_PROMPT
        | llm
        | StrOutputParser()
    )

    return await chain.ainvoke({
        "disease": disease,
        "plant": plant,
        "confidence": f"{confidence:.0%}",
        "location": location
    })

async def stream_treatment_advice(disease: str, plant: str):
    """
    Generator for Server-Sent Events.
    Frontend receives chunks like: data: The disease...\n\n
    """
    # FIX: LLM now reads model and base_url from settings
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.3
    )
    vectorstore = get_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    docs = retriever.invoke(f"{disease} {plant} treatment")
    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"Based on this research:\n{context}\n\nGive treatment advice for {disease} on {plant}."

    async for chunk in llm.astream(prompt):
        yield f"data: {chunk.content}\n\n"
        await asyncio.sleep(0)
