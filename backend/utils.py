import re
import os
import google.generativeai as genai
from typing import List, Dict

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Chat memory placeholder
chat_memory = []

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>{}]', '', text)
    
    # Limit length
    text = text[:2000]
    
    # Strip whitespace
    text = text.strip()
    
    return text

async def call_gemini(prompt: str, system_instruction: str = None, history: List[Dict] = None) -> str:
    """
    Call Gemini 2.5 API
    """
    try:
        # Configure API key for each call to ensure it's set
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error calling Gemini API: API key not found in environment variables"
        genai.configure(api_key=api_key)
        
        # Initialize model with the correct model name
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Combine system instruction with prompt if provided
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # Build chat history if provided
        if history:
            chat = model.start_chat(history=[
                {"role": h["role"], "parts": [h["content"]]} 
                for h in history
            ])
            response = chat.send_message(full_prompt)
        else:
            response = model.generate_content(full_prompt)
        
        return response.text
        
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

async def humanize_response(content: str, emotion: str) -> str:
    """
    Use Gemini to humanize AI responses with empathy
    """
    prompt = f"""Rewrite the following response to be more empathetic and human-like, 
    considering the user's emotional state is: {emotion}.
    
    Keep the core information intact, but make it warmer and more conversational.
    
    Original response:
    {content}
    
    Humanized response:"""
    
    system_instruction = "You are a compassionate tutor who rewrites AI responses to be more empathetic and natural."
    
    try:
        humanized = await call_gemini(prompt, system_instruction)
        return humanized
    except:
        return content  # Return original if humanization fails

def format_memory_context(memory: List[Dict]) -> str:
    """Format chat memory for context"""
    if not memory:
        return ""
    
    context = "Previous conversation:\n"
    for msg in memory[-14:]:  # Last 7 exchanges
        role = "User" if msg["role"] == "user" else "Assistant"
        context += f"{role}: {msg['content'][:200]}...\n"
    
    return context