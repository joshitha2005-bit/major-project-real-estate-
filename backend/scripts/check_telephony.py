#!/usr/bin/env python3
"""
Diagnostic utility to check the readiness of the Real AI Telephone Conversation system.
Never displays raw secrets.
"""
import os
import sys
import re
from pathlib import Path

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Load .env
backend_dir = Path(__file__).resolve().parent.parent
env_path = backend_dir / ".env"

if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
twilio_from = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
base_url = os.getenv("VOICE_PUBLIC_BASE_URL", "").strip().rstrip('/')
gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

print("=" * 70)
print("REAL AI TELEPHONY READINESS & DIAGNOSTIC AUDIT")
print("=" * 70)
print(f"Target Environment File: {env_path}")
print("-" * 70)

# 1. Twilio Account SID Check
sid_ok = bool(twilio_sid and twilio_sid.startswith("AC") and len(twilio_sid) == 34)
sid_display = f"{twilio_sid[:6]}...{twilio_sid[-4:]}" if len(twilio_sid) >= 10 else "(empty / invalid)"
print(f"1. TWILIO_ACCOUNT_SID:       [{'OK' if sid_ok else 'MISSING'}] {sid_display}")
if not sid_ok:
    print("   -> Must be 34 characters starting with 'AC', found in Twilio Console Dashboard.")

# 2. Twilio Auth Token Check
token_ok = bool(twilio_token and len(twilio_token) >= 30)
token_display = f"{twilio_token[:4]}...{twilio_token[-4:]}" if len(twilio_token) >= 8 else "(empty / invalid)"
print(f"2. TWILIO_AUTH_TOKEN:        [{'OK' if token_ok else 'MISSING'}] {token_display}")
if not token_ok:
    print("   -> Found directly below Account SID in Twilio Console Dashboard.")

# 3. Twilio Phone Number Check
phone_ok = bool(twilio_from and re.match(r"^\+[1-9]\d{6,14}$", twilio_from.replace(" ", "")))
print(f"3. TWILIO_PHONE_NUMBER:      [{'OK' if phone_ok else 'MISSING'}] {twilio_from or '(empty)'}")
if not phone_ok:
    print("   -> Must be E.164 format (e.g. +12025550199 or +91...). Must be an active Twilio number.")

# 4. Public Webhook Base URL Check
url_ok = bool(base_url.startswith("https://") and not ("localhost" in base_url or "127.0.0.1" in base_url))
print(f"4. VOICE_PUBLIC_BASE_URL:    [{'OK' if url_ok else 'ACTION REQUIRED'}] {base_url or '(empty)'}")
if not url_ok:
    print("   -> Twilio webhooks require public HTTPS. Use 'npx localtunnel --port 8000' or 'ngrok http 8000'.")

# 5. Gemini API Key Check
gemini_ok = bool(gemini_key and len(gemini_key) >= 20)
gemini_display = f"{gemini_key[:4]}...{gemini_key[-4:]}" if len(gemini_key) >= 8 else "(empty / invalid)"
print(f"5. GEMINI_API_KEY:           [{'OK' if gemini_ok else 'MISSING'}] {gemini_display}")

print("-" * 70)

# Final Readiness Verdict
ready_for_real_calls = sid_ok and token_ok and phone_ok and url_ok
print(f"TELEPHONY READY_FOR_REAL_CALLS: {ready_for_real_calls}")

if ready_for_real_calls:
    print("SUCCESS: All telephony prerequisites are met. Outbound telephone calls can be placed.")
else:
    print("STATUS: NOT READY FOR REAL CALLS. Complete the marked missing steps above.")
print("=" * 70)