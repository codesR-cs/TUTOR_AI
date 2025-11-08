from backend.utils import call_gemini, format_memory_context

async def enhance_prompt(short_message: str, memory: list = None) -> str:
    """
    Enhance short prompts to be more detailed and specific
    Uses conversation memory if available for better context
    """
    if len(short_message.split()) >= 5:
        return short_message
        
    context = format_memory_context(memory) if memory else ""
    
    prompt = f"""The user sent this short message: "{short_message}"

Expand this into a more detailed, specific request that captures what they likely want to learn or do.
Keep it under 3 sentences. Be specific and educational.

Enhanced request:"""
    
    system_instruction = """You are an AI that enhances short user prompts into detailed, 
    specific requests while preserving the original intent."""
    
    try:
        enhanced = await call_gemini(prompt, system_instruction)
        return enhanced.strip()
    except:
        return short_message  # Return original if enhancement fails