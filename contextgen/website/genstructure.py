from google import genai

# Create client
client = genai.Client(api_key="AIzaSyDX7J86tZEneD8R4G5Pe6juL0unexF8EZ0")

def generate_structure(data):
    prompt = f"""
You are a UI/UX expert.

Analyze this website data and infer the structure.

DATA:
{data}

Return:
- Navbar
- Hero section
- Sections
- Footer
- Layout style
- Color/theme
- UX flow
"""

    response = client.models.generate_content(
        model="gemini-1.0-pro",   # ✅ correct for new SDK
        contents=prompt
    )

    return response.text