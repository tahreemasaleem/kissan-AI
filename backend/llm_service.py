import os
import json
import csv
import urllib.request
import urllib.error
import ssl
from pydantic import BaseModel
from typing import List, Optional

# Manually load .env
def load_env_file():
    # Try multiple locations for .env
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    for env_path in possible_paths:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = parts[1].strip()
                            os.environ[key] = val
                            print(f"[OK] Loaded env: {key}=***{val[-4:]}")
            return
    print("[WARN] No .env file found")

load_env_file()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Load crop knowledge base for context injection
CROP_KB_TEXT = ""
try:
    csv_path = os.path.join(os.path.dirname(__file__), "..", "crop fertilizers ds", "updated_dataset.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        crop_entries = []
        for row in reader:
            entry = (
                f"Crop: {row.get('Crop_Name','')}\n"
                f"Duration: {row.get('Growing_Duration','')}\n"
                f"Season: {row.get('Season','')}\n"
                f"Fertilizer: {row.get('Fertilizer_Application','')}\n"
                f"Pesticides: {row.get('Pesticides_Used','')}\n"
                f"Guide: {row.get('Cultivation_Guide','')}"
            )
            crop_entries.append(entry)
        CROP_KB_TEXT = "\n---\n".join(crop_entries)
    print(f"[OK] Botanist knowledge base loaded: {len(crop_entries)} crops")
except Exception as e:
    print(f"[WARN] Could not load crop KB: {e}")

SYSTEM_PROMPT = (
    "You are 'Kissan AI Virtual Botanist', an expert agronomist, botanist, and plant pathologist built for Pakistani farmers. "
    "You help farmers diagnose plant diseases, recommend treatments (both organic and chemical), suggest fertilizers, "
    "and give advice on crops, soil, irrigation, and farming practices. "
    "You speak in a friendly, practical tone. Keep answers concise but thorough. "
    "When asked about specific crops, use the knowledge base provided. "
    "You can respond in English or Urdu depending on the user's language. "
    "If the user asks something outside agriculture, politely redirect them to farming topics.\n\n"
)

if CROP_KB_TEXT:
    # Only include a summary to keep context manageable
    SYSTEM_PROMPT += "You have access to a comprehensive crop database with 52+ crops including their fertilizer schedules, pesticide recommendations, and cultivation guides for Pakistani agriculture.\n\n"

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_disease: Optional[str] = None


def _make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _find_relevant_crop_info(query):
    """Find relevant crop info from the KB to inject as context."""
    if not CROP_KB_TEXT:
        return ""
    
    query_lower = query.lower()
    csv_path = os.path.join(os.path.dirname(__file__), "..", "crop fertilizers ds", "updated_dataset.csv")
    relevant = []
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                crop_name = row.get("Crop_Name", "").lower()
                name_parts = crop_name.replace("(", " ").replace(")", " ").replace("/", " ").split()
                
                for part in name_parts:
                    if len(part) > 2 and part in query_lower:
                        entry = (
                            f"Crop: {row.get('Crop_Name','')}\n"
                            f"Duration: {row.get('Growing_Duration','')}\n"
                            f"Season: {row.get('Season','')}\n"
                            f"Fertilizer: {row.get('Fertilizer_Application','')}\n"
                            f"Pesticides: {row.get('Pesticides_Used','')}\n"
                            f"Guide: {row.get('Cultivation_Guide','')}"
                        )
                        relevant.append(entry)
                        break
    except Exception:
        pass
    
    if relevant:
        return "\n\nRelevant crop data from your database:\n" + "\n---\n".join(relevant[:3])
    return ""


def _try_groq_api(request: ChatRequest) -> str:
    """Use Groq's free API with Llama 3.3 70B."""
    if not GROQ_API_KEY:
        return None
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        system = SYSTEM_PROMPT
        if request.context_disease:
            system += f"\nIMPORTANT CONTEXT: The user recently scanned a plant image and the AI detected: '{request.context_disease}'. Reference this when relevant.\n"
        
        # Find relevant crop info from last user message
        if request.messages:
            last_msg = request.messages[-1].text
            crop_context = _find_relevant_crop_info(last_msg)
            if crop_context:
                system += crop_context
        
        messages = [{"role": "system", "content": system}]
        for msg in request.messages:
            role = "user" if msg.role == "user" else "assistant"
            messages.append({"role": role, "content": msg.text})
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "User-Agent": "KissanAI/1.0"
        })
        
        with urllib.request.urlopen(req, context=_make_ssl_context(), timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    
    except Exception as e:
        print(f"[GROQ ERROR] {e}")
        return None


def _try_gemini_api(request: ChatRequest) -> str:
    """Try Gemini API as secondary option."""
    if not GEMINI_API_KEY:
        return None
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        system = SYSTEM_PROMPT
        if request.context_disease:
            system += f"\nIMPORTANT CONTEXT: The user recently scanned a plant and detected: '{request.context_disease}'.\n"
        
        if request.messages:
            crop_context = _find_relevant_crop_info(request.messages[-1].text)
            if crop_context:
                system += crop_context
        
        contents = []
        for msg in request.messages:
            role = "user" if msg.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.text}]})
        
        payload = {
            "system_instruction": {"parts": {"text": system}},
            "contents": contents
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "User-Agent": "KissanAI/1.0"
        })
        
        with urllib.request.urlopen(req, context=_make_ssl_context(), timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
    
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        return None


def _offline_fallback(request: ChatRequest) -> str:
    """Last resort offline response."""
    return (
        "I'm currently running in offline mode. To get intelligent AI-powered responses, "
        "please add a free Groq API key to your backend/.env file:\n\n"
        "1. Go to https://console.groq.com/keys\n"
        "2. Sign up (free) and create an API key\n"
        "3. Add GROQ_API_KEY=your_key_here to backend/.env\n"
        "4. Restart the backend server\n\n"
        "In the meantime, you can use the Crop Guide tab to browse crop information, "
        "or the Disease Scan tab to analyze plant images!"
    )


def get_botanist_response(request: ChatRequest) -> str:
    """
    Returns a response from the Virtual Botanist.
    Priority: Groq (Llama 3.3) -> Gemini -> Offline fallback
    """
    # Try Groq first (free, fast, reliable)
    response = _try_groq_api(request)
    if response:
        return response
    
    # Try Gemini as backup
    response = _try_gemini_api(request)
    if response:
        return response
    
    # Offline fallback
    return _offline_fallback(request)
