from flask import Blueprint, request, jsonify, render_template
from .chatbot_logic import LeanchemsChatbot

bp = Blueprint('main', __name__)
chatbot = LeanchemsChatbot()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    session_id, response = chatbot.chat(message, session_id)
    return jsonify({
        "response": response,
        "session_id": session_id
    })

@bp.route('/cleanup', methods=['POST'])
def cleanup():
    """Endpoint to manually trigger session cleanup."""
    try:
        chatbot.cleanup_expired_sessions()
        return jsonify({"status": "success", "message": "Expired sessions cleaned up"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500