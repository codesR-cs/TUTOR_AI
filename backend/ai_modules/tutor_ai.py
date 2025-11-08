from backend.utils import call_gemini, format_memory_context
from backend.ai_modules.image_ai import generate_image
import json
import re

async def teach_topic(message: str, memory: list) -> dict:
    """
    Teach a topic comprehensively with explanations, questions, and optional image
    """
    context = format_memory_context(memory)
    
    prompt = f"""{context}

User wants to learn: {message}

Provide a comprehensive, engaging explanation:
1. Start with a clear introduction
2. Break down complex concepts into simple terms
3. Use examples and analogies
4. Include practical applications
5. End with encouragement

Then suggest 3 follow-up questions the user might ask.

Format your response as:
EXPLANATION:
[your detailed explanation here]

QUESTIONS:
1. [question 1]
2. [question 2]
3. [question 3]"""
    
    system_instruction = """You are TutorAI, an expert educator who makes complex topics 
    accessible and engaging. You use clear explanations, examples, and encouragement."""
    
    response = await call_gemini(prompt, system_instruction)
    
    # Parse response
    parts = response.split("QUESTIONS:")
    explanation = parts[0].replace("EXPLANATION:", "").strip()
    
    questions = []
    if len(parts) > 1:
        question_text = parts[1].strip()
        # Extract questions
        for line in question_text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                q = re.sub(r'^[\d\-\.\)]+\s*', '', line).strip()
                if q:
                    questions.append(q)
    
    # Generate image for visual topics
    image_url = None
    visual_keywords = ["diagram", "structure", "process", "anatomy", "system", "cycle", "chart"]
    if any(keyword in message.lower() for keyword in visual_keywords):
        try:
            image_url = await generate_image(f"Educational diagram of {message}")
        except:
            pass
    
    # Generate a quick quiz for learning reinforcement based on the explanation
    try:
        from backend.ai_modules.quiz_ai import generate_quiz
        quiz_prompt = f"Create a quiz about this topic:\n\n{explanation}"
        quiz_data = await generate_quiz(quiz_prompt, memory)
    except:
        quiz_data = None

    return {
        "explanation": explanation,
        "questions": questions[:3],
        "image_url": image_url,
        "quiz": quiz_data  # Include the quiz data in the response
    }