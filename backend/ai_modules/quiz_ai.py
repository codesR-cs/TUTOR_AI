from backend.utils import call_gemini, format_memory_context
import json

async def generate_quiz(message: str, memory: list) -> dict:
    """
    Generate an educational quiz with multiple choice questions
    """
    context = format_memory_context(memory)
    
    prompt = f"""{context}

Create a quiz about: {message}

Generate 5 multiple choice questions with 4 options each.
Return ONLY valid JSON in this exact format:
{{
  "title": "Quiz Title",
  "questions": [
    {{
      "question": "Question text?",
      "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
      "correct": 0,
      "explanation": "Why this is correct"
    }}
  ]
}}

The "correct" field should be the index (0-3) of the correct answer.
Return ONLY the JSON, no other text."""
    
    system_instruction = """You are QuizAI, an expert at creating educational quizzes. 
    Return only valid JSON, no other text or formatting."""
    
    try:
        response = await call_gemini(prompt, system_instruction)
        
        # Clean response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        quiz_data = json.loads(response)
        return quiz_data
        
    except Exception as e:
        # Return a fallback quiz
        return {
            "title": f"Quiz: {message}",
            "questions": [
                {
                    "question": "What would you like to learn about this topic?",
                    "options": ["A) Basics", "B) Advanced concepts", "C) Applications", "D) All of the above"],
                    "correct": 3,
                    "explanation": "Learning all aspects gives you a complete understanding!"
                }
            ]
        }

async def evaluate_quiz(quiz_data: dict, user_answers: list) -> dict:
    """
    Evaluate user's quiz answers
    """
    score = 0
    total = len(quiz_data.get("questions", []))
    
    feedback = []
    for i, question in enumerate(quiz_data.get("questions", [])):
        correct_idx = question.get("correct", 0)
        user_answer = user_answers[i] if i < len(user_answers) else -1
        
        is_correct = user_answer == correct_idx
        if is_correct:
            score += 1
        
        feedback.append({
            "question": question.get("question", ""),
            "correct": is_correct,
            "explanation": question.get("explanation", "")
        })
    
    percentage = (score / total * 100) if total > 0 else 0
    
    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "feedback": feedback
    }