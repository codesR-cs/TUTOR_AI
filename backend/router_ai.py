import os
from backend.ai_modules.advisor_ai import detect_emotion_and_intent, generate_advice
from backend.ai_modules.enhancer_ai import enhance_prompt
from backend.ai_modules.router_logic import determine_route
from backend.ai_modules.tutor_ai import teach_topic
from backend.ai_modules.quiz_ai import generate_quiz
from backend.ai_modules.code_ai import handle_code_request
from backend.ai_modules.image_ai import generate_image
from backend.ai_modules.summarizer_ai import summarize_youtube
from backend.utils import humanize_response

async def route_and_respond(message: str, mode: str, session_memory: list):
    """
    Main routing logic for TutorAI+
    Pipeline: AdvisorAI → Enhancer → Router → Module → Humanizer
    """
    
    # Step 1: AdvisorAI - Detect emotion and intent
    emotion_data = await detect_emotion_and_intent(message)
    emotion = emotion_data.get("emotion", "neutral")
    intent = emotion_data.get("intent", "general")
    empathy_line = emotion_data.get("empathy_line", "")
    
    # Step 2: Enhancer - Expand short prompts if needed
    enhanced_message = message
    if len(message.split()) < 5:
        enhanced_message = await enhance_prompt(message, session_memory)
    
    # Step 3: Router - Determine which AI module to use
    if mode == "auto":
        route = await determine_route(enhanced_message, intent)
    else:
        route = mode.lower()
    
    # Step 4: Execute appropriate AI module
    response = {
        "empathy_line": empathy_line,
        "main_content": "",
        "suggested_questions": [],
        "image_url": None,
        "quiz": None,
        "route": route,
        "emotion": emotion
    }
    
    try:
        if route == "advisor":
            advice = await generate_advice(enhanced_message, emotion, session_memory)
            response["main_content"] = advice
            
        elif route == "tutor":
            tutor_response = await teach_topic(enhanced_message, session_memory)
            response["main_content"] = tutor_response.get("explanation", "")
            response["suggested_questions"] = tutor_response.get("questions", [])
            response["image_url"] = tutor_response.get("image_url")
            # Include quiz if available
            if tutor_response.get("quiz"):
                response["quiz"] = tutor_response["quiz"]
                response["main_content"] += "\n\nI've included a quick quiz to help you test your understanding!"
            
        elif route == "quiz":
            quiz_data = await generate_quiz(enhanced_message, session_memory)
            response["main_content"] = "I've created a quiz for you!"
            response["quiz"] = quiz_data
            
        elif route == "code":
            code_response = await handle_code_request(enhanced_message, session_memory)
            response["main_content"] = code_response
            
        elif route == "image":
            image_url = await generate_image(enhanced_message, session_memory)
            response["main_content"] = "I've generated an educational image for you!"
            response["image_url"] = image_url
            
        elif route == "summarizer":
            summary = await summarize_youtube(enhanced_message)
            response["main_content"] = summary
            
        else:
            # Default to tutor
            tutor_response = await teach_topic(enhanced_message, session_memory)
            response["main_content"] = tutor_response.get("explanation", "")
            response["suggested_questions"] = tutor_response.get("questions", [])
    
    except Exception as e:
        response["main_content"] = f"I encountered an error: {str(e)}. Let me try to help you differently."
    
    # Step 5: Humanizer - Make response more empathetic
    if response["main_content"]:
        response["main_content"] = await humanize_response(response["main_content"], emotion)
    
    return response