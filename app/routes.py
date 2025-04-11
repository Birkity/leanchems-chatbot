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
    project_idea = data.get('message', '')
    
    if not project_idea:
        return jsonify({"error": "No project idea provided"}), 400
    
    response = chatbot.assess_project_idea(project_idea)
    return jsonify({"response": response})