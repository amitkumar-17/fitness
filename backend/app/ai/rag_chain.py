"""
RAG Chain — The Brain of the App
----------------------------------
This module:
1. Takes user's query + their profile (goal, diet pref, location)
2. Searches the vector DB for relevant PDF chunks
3. Builds a prompt with context + user info
4. Sends to LLM and returns a personalized plan 

The LLM doesn't hallucinate random plans — it uses YOUR PDF content
as the knowledge base and personalizes based on user preferences.
"""

from langchain_openai import ChatOpenAI
from openai import OpenAIError
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.ai.ingestion import get_vector_store, search_local_knowledge
from app.core.config import settings


SYSTEM_PROMPT = """You are FitAI, an expert fitness coach and nutritionist.
You help users create personalized workout and diet plans.

RULES:
- Use the provided context from fitness documents to give accurate advice
- Always consider the user's profile: goal, diet preference, workout location, experience level
- Provide structured, day-by-day plans when asked for workout or diet plans
- Include sets, reps, rest times for workouts
- Include portion sizes, macros, and meal timing for diet plans
- If the context doesn't have enough info, use your general fitness knowledge but mention it
- Be encouraging and motivational
- Always warn about consulting a doctor before starting any new fitness program

USER PROFILE:
- Goal: {goal}
- Diet Preference: {diet_preference}
- Workout Location: {workout_location}
- Experience Level: {experience_level}
- Weight: {weight_kg} kg
- Height: {height_cm} cm
- Age: {age}

CONTEXT FROM FITNESS DOCUMENTS:
{context}
"""


def get_llm():
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0.3,
        openai_api_key=settings.OPENAI_API_KEY,
    )


def format_docs(docs):
    formatted = []
    for doc in docs:
        meta = doc.metadata
        header = f"[Category: {meta.get('category', 'unknown')}]"
        if meta.get("subcategory"):
            header += f" [Plan: {meta['subcategory']}]"
        if meta.get("calories"):
            header += f" [Calories: {meta['calories']}]"
        header += f" [Source: {meta.get('filename', meta.get('source', 'unknown'))}]"
        formatted.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def get_rag_chain(user_profile: dict | None = None):
    """
    Build a RAG chain that searches PDFs and generates personalized plans.

    Args:
        user_profile: Dict with user's fitness profile info.
    """
    profile = user_profile or {}
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance for diverse results
        search_kwargs={"k": 6},
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{question}"),
    ])

    llm = get_llm()

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "goal": lambda _: profile.get("fitness_goal", "general fitness"),
            "diet_preference": lambda _: profile.get("diet_preference", "not specified"),
            "workout_location": lambda _: profile.get("workout_location", "gym"),
            "experience_level": lambda _: profile.get("experience_level", "beginner"),
            "weight_kg": lambda _: str(profile.get("weight_kg", "not specified")),
            "height_cm": lambda _: str(profile.get("height_cm", "not specified")),
            "age": lambda _: str(profile.get("age", "not specified")),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def get_direct_chain(user_profile: dict | None = None):
    """Build a non-RAG chain used when vector search is unavailable."""
    profile = user_profile or {}
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{question}"),
    ])

    chain = (
        {
            "context": lambda _: "No fitness document context is available.",
            "question": RunnablePassthrough(),
            "goal": lambda _: profile.get("fitness_goal", "general fitness"),
            "diet_preference": lambda _: profile.get("diet_preference", "not specified"),
            "workout_location": lambda _: profile.get("workout_location", "gym"),
            "experience_level": lambda _: profile.get("experience_level", "beginner"),
            "weight_kg": lambda _: str(profile.get("weight_kg", "not specified")),
            "height_cm": lambda _: str(profile.get("height_cm", "not specified")),
            "age": lambda _: str(profile.get("age", "not specified")),
        }
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    return chain


async def generate_response(query: str, user_profile: dict | None = None) -> dict:
    """
    Generate an AI response for the user's fitness query.

    Returns dict with 'answer' and 'sources'.
    """
    if not settings.EMBEDDING_MODEL:
        relevant_docs = search_local_knowledge(query)
        if relevant_docs:
            sources = list({
                doc.metadata.get("filename", doc.metadata.get("source", "unknown"))
                for doc in relevant_docs
            })
            profile = user_profile or {}
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
                HumanMessagePromptTemplate.from_template("{question}"),
            ])
            chain = (
                {
                    "context": lambda _: format_docs(relevant_docs),
                    "question": RunnablePassthrough(),
                    "goal": lambda _: profile.get("fitness_goal", "general fitness"),
                    "diet_preference": lambda _: profile.get("diet_preference", "not specified"),
                    "workout_location": lambda _: profile.get("workout_location", "gym"),
                    "experience_level": lambda _: profile.get("experience_level", "beginner"),
                    "weight_kg": lambda _: str(profile.get("weight_kg", "not specified")),
                    "height_cm": lambda _: str(profile.get("height_cm", "not specified")),
                    "age": lambda _: str(profile.get("age", "not specified")),
                }
                | prompt
                | get_llm()
                | StrOutputParser()
            )
        else:
            sources = []
            chain = get_direct_chain(user_profile)

        answer = await chain.ainvoke(query)
        return {"answer": answer, "sources": sources}

    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 6})

    try:
        # Get relevant documents for source tracking
        relevant_docs = await retriever.ainvoke(query)
    except OpenAIError:
        # The current OpenAI project may not have an embeddings model enabled.
        chain = get_direct_chain(user_profile)
        answer = await chain.ainvoke(query)
        return {"answer": answer, "sources": []}

    sources = list({doc.metadata.get("source", "unknown") for doc in relevant_docs})

    chain = get_rag_chain(user_profile)
    answer = await chain.ainvoke(query)

    return {
        "answer": answer,
        "sources": sources,
    }


async def generate_workout_plan(
    goal: str,
    location: str,
    experience_level: str = "beginner",
    days_per_week: int = 5,
    duration_minutes: int = 60,
    specific_requirements: str | None = None,
    user_profile: dict | None = None,
) -> dict:
    """Generate a structured workout plan."""
    query = f"""Create a detailed {days_per_week}-day {goal} workout plan for {location}.
Experience level: {experience_level}
Each session should be about {duration_minutes} minutes.
{"Additional requirements: " + specific_requirements if specific_requirements else ""}

Please include:
- Day-by-day breakdown with specific exercises
- Sets, reps, and rest times
- Warm-up and cool-down recommendations
- Progressive overload suggestions
- Tips for {goal} specifically"""

    return await generate_response(query, user_profile)


async def generate_diet_plan(
    goal: str,
    diet_type: str,
    meals_per_day: int = 4,
    calories_target: int | None = None,
    allergies: list[str] | None = None,
    specific_requirements: str | None = None,
    user_profile: dict | None = None,
) -> dict:
    """Generate a structured diet plan."""
    query = f"""Create a detailed {diet_type} diet plan for {goal}.
Meals per day: {meals_per_day}
{"Target calories: " + str(calories_target) if calories_target else "Suggest appropriate calorie intake"}
{"Allergies to avoid: " + ", ".join(allergies) if allergies else ""}
{"Additional requirements: " + specific_requirements if specific_requirements else ""}

Please include:
- Meal-by-meal breakdown with specific foods and portions
- Macronutrient breakdown (protein, carbs, fats)
- Meal timing recommendations
- Grocery list for the week
- Supplement recommendations if needed
- Hydration guidelines"""

    return await generate_response(query, user_profile)
