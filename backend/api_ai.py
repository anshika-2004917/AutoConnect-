
import os
from flask import Blueprint, request, jsonify
from groq import Groq

from db import get_db

ai_bp = Blueprint("ai", __name__)

SYSTEM_PROMPT = """
You are AutoConnect AI Assistant, a helpful assistant for a campus
auto-rickshaw application.

Answer questions using only the AutoConnect information provided
in the context.

You can explain:
- Existing routes and stops
- Existing fares
- Available autos and available seats

Do not invent routes, fares, autos, seats, or bookings.
If information is missing, clearly say that it is not available
in the current AutoConnect database.

Do not claim to create, cancel, or modify bookings.
Keep answers simple and concise.
"""


@ai_bp.route("/ai/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    if len(message) > 1000:
        return jsonify({"error": "Message is too long."}), 400

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "AI service is not configured."}), 503

    try:
        db = get_db()

        routes = db.execute("""
            SELECT route_id, route_name, start_location, end_location,
                   fare, distance_km, travel_minutes, route_status
            FROM routes
        """).fetchall()

        autos = db.execute("""
            SELECT a.auto_number, a.route_id, a.total_seats,
                   a.available_seats, a.availability,
                   r.route_name
            FROM autos a
            JOIN users u ON u.user_id = a.driver_id
            LEFT JOIN routes r ON r.route_id = a.route_id
            WHERE u.is_approved = 1
              AND u.is_active = 1
        """).fetchall()

        stops = db.execute("""
            SELECT route_id, stop_order, stop_name
            FROM stops
            ORDER BY route_id, stop_order
        """).fetchall()

        context = {
            "routes": [dict(row) for row in routes],
            "stops": [dict(row) for row in stops],
            "autos": [dict(row) for row in autos],
            "bookings": (
                "Booking records are not present in the current database."
            ),
        }

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"AutoConnect database information:\n{context}\n\n"
                        f"Student question: {message}"
                    ),
                },
            ],
            temperature=0.2,
            max_completion_tokens=500,
        )

        answer = response.choices[0].message.content

        return jsonify({"answer": answer or "I could not generate an answer."})

    except Exception:
        return jsonify({
            "error": "The AI assistant is temporarily unavailable."
        }), 500
