"""
Prompt Templates for different fitness goals.
These are pre-built prompt enhancers that make user queries more specific.
"""

GOAL_PROMPTS = {
    "bulking": {
        "workout_focus": "Focus on compound movements, progressive overload, heavy weights with 6-12 rep ranges. Include exercises like squats, deadlifts, bench press, overhead press, rows.",
        "diet_focus": "Caloric surplus of 300-500 calories. High protein (1.6-2.2g/kg body weight). Complex carbs for energy. Healthy fats.",
    },
    "shredding": {
        "workout_focus": "High intensity training, supersets, drop sets, HIIT cardio. Maintain heavy compounds but add volume with isolation exercises. Include 3-4 cardio sessions.",
        "diet_focus": "Caloric deficit of 300-500 calories. Very high protein (2.0-2.4g/kg) to preserve muscle. Moderate carbs timed around workouts. Low-moderate fats.",
    },
    "leaning": {
        "workout_focus": "Balanced approach with moderate weights, 8-15 rep range. Mix of strength and endurance. Include 2-3 cardio sessions with steady state and HIIT.",
        "diet_focus": "Slight caloric deficit of 200-300 calories. High protein (1.8-2.0g/kg). Balanced macros. Focus on whole foods and micronutrients.",
    },
    "general_fitness": {
        "workout_focus": "Well-rounded program covering strength, cardio, flexibility. Functional movements. 3-5 sessions per week. Mix of compound and bodyweight exercises.",
        "diet_focus": "Maintenance calories. Balanced macros (30% protein, 40% carbs, 30% fats). Focus on whole foods, variety, and sustainability.",
    },
    "weight_loss": {
        "workout_focus": "Circuit training, HIIT, compound movements. High calorie burn sessions. Include daily movement goals (10k steps). Resistance training to preserve muscle.",
        "diet_focus": "Caloric deficit of 400-600 calories. High protein (2.0g/kg). High fiber foods for satiety. Reduce processed foods and sugars.",
    },
    "muscle_gain": {
        "workout_focus": "Hypertrophy-focused training. 8-12 rep range. Progressive overload. Split routine targeting each muscle group 2x/week. Adequate rest between sessions.",
        "diet_focus": "Caloric surplus of 200-400 calories. Very high protein (2.0-2.4g/kg). Carb-heavy around workouts. Track macros closely.",
    },
}


def enhance_query(query: str, goal: str, location: str, diet_preference: str) -> str:
    """Enhance a user query with goal-specific context."""
    goal_info = GOAL_PROMPTS.get(goal, GOAL_PROMPTS["general_fitness"])

    enhanced = f"""{query}

Context for this user's goal ({goal}):
- Workout approach: {goal_info['workout_focus']}
- Nutrition approach: {goal_info['diet_focus']}
- Workout location: {location}
- Diet preference: {diet_preference}"""

    return enhanced
