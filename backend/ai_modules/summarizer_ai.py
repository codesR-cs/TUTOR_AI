from backend.utils import call_gemini
from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no URL pattern matches, assume it's just the ID
    return url.strip()

async def summarize_youtube(message: str) -> str:
    """
    Fetch YouTube transcript and provide a simple explanation
    """
    # Extract video ID from message
    video_id = None
    words = message.split()
    
    for word in words:
        if 'youtu' in word.lower() or len(word) == 11:
            try:
                potential_id = extract_video_id(word)
                if potential_id:
                    video_id = potential_id
                    break
            except:
                continue
    
    if not video_id:
        return """I need a YouTube video URL or ID to summarize. 
        
Please provide a link like:
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- Or just the 11-character VIDEO_ID

Example: "Summarize https://www.youtube.com/watch?v=dQw4w9WgXcQ" """
    
    try:
        # Fetch transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine transcript
        full_transcript = " ".join([item['text'] for item in transcript_list])
        
        # Limit transcript length for API
        if len(full_transcript) > 8000:
            full_transcript = full_transcript[:8000] + "..."
        
        # Generate simple explanation using Gemini
        prompt = f"""Here's a transcript from a YouTube video:

{full_transcript}

Provide a comprehensive yet simple summary that:
1. Explains the main topic clearly
2. Lists key points (3-5 bullet points)
3. Highlights important takeaways
4. Uses simple language accessible to learners

Keep it concise but informative."""
        
        system_instruction = """You are SummarizerAI, an expert at distilling complex 
        content into clear, simple explanations. Focus on educational value."""
        
        summary = await call_gemini(prompt, system_instruction)
        
        return f"📺 **YouTube Video Summary**\n\n{summary}\n\n🔗 Video ID: {video_id}"
        
    except Exception as e:
        error_msg = str(e)
        
        if "TranscriptsDisabled" in error_msg:
            return f"""❌ Transcripts are disabled for this video (ID: {video_id}).
            
Unfortunately, the video creator has disabled captions/transcripts, so I can't summarize it. 
Try another video that has captions enabled!"""
        
        elif "VideoUnavailable" in error_msg:
            return f"""❌ Video not found (ID: {video_id}).
            
The video might be private, deleted, or the ID is incorrect. 
Please check the URL and try again!"""
        
        else:
            return f"""❌ Error fetching transcript: {error_msg}
            
Possible reasons:
- Video ID might be incorrect
- Video might not have captions
- API might be temporarily unavailable

Please try:
1. Double-check the video URL
2. Make sure the video has captions enabled
3. Try another video"""