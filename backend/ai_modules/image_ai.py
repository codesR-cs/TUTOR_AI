from backend.utils import call_gemini, format_memory_context
import google.generativeai as genai
import os

async def generate_image(message: str, memory: list = None) -> str:
    """
    Generate educational images using Gemini's image generation
    Note: Gemini 2.5 Flash doesn't have native image generation,
    so we'll use Imagen API if available, or return a placeholder
    """
    context = format_memory_context(memory) if memory else ""
    
    # Enhance prompt for educational context
    enhanced_prompt = f"""Create an educational, clear, and informative image that illustrates: {message}
    
    Style: Clean, professional, educational diagram or illustration
    Focus: Clarity and learning value
    Avoid: Complex backgrounds, distracting elements"""
    
    try:
        # In production, you would use Google's Imagen API here
        # For now, we'll use a placeholder approach
        
        # Generate a descriptive alt text using Gemini
        alt_text_prompt = f"Describe what an educational image about '{message}' should look like in detail."
        system_instruction = "You create detailed image descriptions for educational purposes."
        
        description = await call_gemini(alt_text_prompt, system_instruction)
        
        # Return a data URL with SVG placeholder
        # In production, replace this with actual Imagen API call
        svg_placeholder = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
            <rect width="400" height="300" fill="#f0f4ff"/>
            <rect x="20" y="20" width="360" height="260" rx="10" fill="white" stroke="#3b82f6" stroke-width="2"/>
            <text x="200" y="140" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#3b82f6">
                Educational Image
            </text>
            <text x="200" y="165" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#6b7280">
                {message[:50]}
            </text>
        </svg>"""
        
        # Return as data URL
        import base64
        encoded = base64.b64encode(svg_placeholder.encode()).decode()
        return f"data:image/svg+xml;base64,{encoded}"
        
    except Exception as e:
        # Return a simple placeholder on error
        return None