from backend.utils import call_gemini, format_memory_context
import json

async def detect_emotion_and_intent(message: str) -> dict:
    """
    Detect user emotion and intent using Gemini
    """
    prompt = f"""Analyze this message and return a JSON object with:
    1. emotion: the user's emotional state (happy, sad, frustrated, confused, anxious, neutral, excited)
    2. intent: what the user wants (learn, help, advice, quiz, code, summarize, clarify)
    3. empathy_line: a short empathetic response (1 sentence)
    
    Message: "{message}"
    
    Return ONLY valid JSON, no other text."""
    
    system_instruction = "You are an emotion detection AI that returns only JSON."
    
    try:
        response = await call_gemini(prompt, system_instruction)
        
        # Clean response and parse JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        data = json.loads(response)
        
        return {
            "emotion": data.get("emotion", "neutral"),
            "intent": data.get("intent", "general"),
            "empathy_line": data.get("empathy_line", "I'm here to help you!")
        }
    except:
        return {
            "emotion": "neutral",
            "intent": "general",
            "empathy_line": "I'm here to support your learning journey!"
        }

async def generate_advice(message: str, emotion: str, memory: list) -> str:
    """
    Generate empathetic advice using AdvisorAI
    """
    context = format_memory_context(memory)
    
    prompt = f"""{context}

User's emotional state: {emotion}
User's message: {message}

Provide empathetic, actionable advice. Be supportive and understanding. 
Include practical steps they can take."""
    
    system_instruction = """You are AdvisorAI, a compassionate advisor who provides 
    emotional support and practical guidance. Be warm, understanding, and helpful."""
    
    response = await call_gemini(prompt, system_instruction)
    return response