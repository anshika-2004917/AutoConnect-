
import os
import json
import logging

from flask import Blueprint, request, jsonify
from groq import Groq

from db import get_db

ai_bp = Blueprint("ai", __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are AutoConnect AI, a friendly and intelligent assistant.

Your responsibilities:

1. AUTOCONNECT PROJECT QUESTIONS
Answer questions about AutoConnect, including:
- What AutoConnect is
- Student login and registration
- Driver registration
- Admin functionality
- Finding autos and routes
- Available seats
- Stops and fares
- How the application works
- Technology stack
- Project features and benefits

2. GENERAL KNOWLEDGE
You can also answer general questions about:
- Artificial Intelligence
- Machine Learning
- Python programming
- Flask and SQLite
- Computer science
- Engineering subjects
- Education and technology
- Everyday general knowledge

3. DATABASE INFORMATION
You will receive actual AutoConnect database information.
Use it when answering questions about routes, stops, autos,
fares and seat availability.

IMPORTANT:
- Never invent routes, fares, auto numbers or seat availability.
- If database information is unavailable, explain that clearly.
- Do not claim that a booking was created or cancelled.
- Do not claim that you performed an operation in the application.
- Never ask users to share passwords or API keys.
- Explain login and registration procedures in simple language.
- Do not expose private user information.
- Clearly distinguish existing features from future enhancements.

4. RESPONSE STYLE
- Be friendly and professional.
- Use simple English.
- Give clear and useful explanations.
- Use numbered steps when explaining procedures.
- Avoid unnecessary technical language.
- Answer general questions normally instead of refusing them.
- Keep answers concise but informative.

You are the official AI assistant of AutoConnect.
"""


@ai_bp.route("/ai/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({
            "error": "Please enter a message."
        }), 400

    if len(message) > 1000:
        return jsonify({
            "error": "Message is too long."
        }), 400

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        logger.error("GROQ_API_KEY is not configured.")

        return jsonify({
            "error": "AI service is not configured."
        }), 503

    try:

        db = get_db()

        # Fetch route information
        routes = db.execute("""
            SELECT route_id, route_name, start_location,
                   end_location, fare, distance_km,
                   travel_minutes, route_status
            FROM routes
        """).fetchall()

        # Fetch approved and active auto information
        autos = db.execute("""
            SELECT a.auto_number, a.route_id,
                   a.total_seats, a.available_seats,
                   a.availability, r.route_name
            FROM autos a
            JOIN users u ON u.user_id = a.driver_id
            LEFT JOIN routes r ON r.route_id = a.route_id
            WHERE u.is_approved = 1
              AND u.is_active = 1
        """).fetchall()

        # Fetch stop information
        stops = db.execute("""
            SELECT route_id, stop_order, stop_name
            FROM stops
            ORDER BY route_id, stop_order
        """).fetchall()

        # Convert database records into JSON-friendly data
        context = {
            "routes": [dict(row) for row in routes],
            "stops": [dict(row) for row in stops],
            "autos": [dict(row) for row in autos]
        }

        database_context = json.dumps(
            context,
            indent=2,
            ensure_ascii=False
        )

        # Connect to Groq AI
        client = Groq(api_key=api_key)

        # Generate AI response
        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": (
                        "Here is the current AutoConnect database "
                        "information:\n\n"
                        + database_context
                        + "\n\nStudent question:\n"
                        + message
                    )
                }
            ],

            temperature=0.5,
            max_completion_tokens=700
        )

        answer = response.choices[0].message.content

        if not answer:
            answer = "Sorry, I could not generate a response."

        return jsonify({
            "answer": answer
        }), 200

    except Exception as e:

        logger.exception("AutoConnect AI chatbot error: %s", str(e))

        return jsonify({
            "error": "The AI assistant is temporarily unavailable. Please try again."
        }), 500
