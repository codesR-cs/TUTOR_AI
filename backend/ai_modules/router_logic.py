from backend.utils import call_gemini
import json

async def determine_route(message: str, intent: str) -> str:
    """
    Use Gemini to intelligently determine which AI module to route to
    """
    
    # Quick keyword-based routing for obvious cases
    message_lower = message.lower()
    
    if "youtube" in message_lower or "video" in message_lower and ("summarize" in message_lower or "transcript" in message_lower):
        return "summarizer"
    
    if any(word in message_lower for word in ["code", "program", "function", "class", "algorithm"]):
        return "code"
    
    if any(word in message_lower for word in ["quiz", "test", "questions", "assess"]):
        return "quiz"
    
    if any(word in message_lower for word in ["image", "picture", "diagram", "illustration", "draw"]) and "generate" in message_lower:
        return "image"
    
    if any(word in message_lower for word in ["feeling", "stressed", "anxious", "worried", "advice", "help me"]):
        return "advisor"
    
    # Use Gemini for ambiguous cases
    prompt = f"""Analyze this user message and determine which AI module should handle it.

User message: "{message}"
Detected intent: {intent}

Available modules:
- tutor: teaching concepts, explaining topics, learning
- code: generating or explaining code
- quiz: creating or taking quizzes
- image: generating educational images
- summarizer: summarizing YouTube videos
- advisor: emotional support and advice

Return ONLY ONE WORD - the module name, nothing else."""
    
    system_instruction = "You are a routing AI that returns only a single module name."
    
    try:
        response = await call_gemini(prompt, system_instruction)
        route = response.strip().lower()
        
        # Validate route
        valid_routes = ["tutor", "code", "quiz", "image", "summarizer", "advisor"]
        if route in valid_routes:
            return route
        
    except:
        pass
    
    # Default to tutor
    return "tutor"