from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from app.chatbot_logic import LeanchemsChatbot
from dotenv import load_dotenv
import logging

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    CORS(app)
    load_dotenv()

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    chatbot = LeanchemsChatbot()

    @app.route('/')
    def index():
        logger.info("Serving index.html")
        return render_template('index.html')

    @app.route('/chat', methods=['POST'])
    def chat():
        try:
            data = request.json
            logger.debug(f"Received data: {data}")
            message = data.get('message')
            if not message:
                logger.warning("No message provided")
                return jsonify({"error": "No message provided"}), 400
                
            logger.info(f"Processing idea: {message}")
            response = chatbot.assess_project_idea(message)
            logger.debug(f"Response generated: {response}")
            return jsonify({"response": response})
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)