from backend.utils import call_gemini, format_memory_context

async def handle_code_request(message: str, memory: list) -> str:
    """
    Handle code generation and explanation requests
    """
    context = format_memory_context(memory)
    
    # Determine if it's a generation or explanation request
    is_explanation = any(word in message.lower() for word in ["explain", "what does", "how does", "understand"])
    
    if is_explanation:
        prompt = f"""{context}

User wants you to explain code or a coding concept: {message}

Provide a clear, educational explanation:
1. Start with what the code/concept does
2. Break down each part step by step
3. Use simple language and analogies
4. Include examples if helpful
5. Mention common use cases or pitfalls

Make it easy to understand for learners."""
        
        system_instruction = """You are CodeAI, an expert programming tutor who explains 
        code and concepts clearly. Use simple language and helpful examples."""
        
    else:
        prompt = f"""{context}

User wants you to generate code: {message}

Provide:
1. Clean, well-commented code
2. Brief explanation of how it works
3. Example usage if applicable
4. Any important notes or best practices

Format with proper code blocks and clear explanations."""
        
        system_instruction = """You are CodeAI, an expert programmer who writes clean, 
        efficient code with helpful comments and explanations."""
    
    response = await call_gemini(prompt, system_instruction)
    return response