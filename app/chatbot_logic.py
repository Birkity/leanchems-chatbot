import openai
import os
import json
import time
from dotenv import load_dotenv
import logging
from markdown2 import markdown
import uuid
from datetime import datetime, timedelta

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

class LeanchemsChatbot:
    def __init__(self):
        self.tmp_dir = "/tmp/chatbot_sessions"
        self.session_timeout = timedelta(hours=24)
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.sessions = self._load_sessions()

    def _get_session_file(self, session_id):
        return os.path.join(self.tmp_dir, f"{session_id}.json")

    def _load_sessions(self):
        sessions = {}
        try:
            for filename in os.listdir(self.tmp_dir):
                if filename.endswith('.json'):
                    session_id = filename[:-5]
                    filepath = os.path.join(self.tmp_dir, filename)
                    with open(filepath, 'r') as f:
                        session_data = json.load(f)
                        if self._is_session_valid(session_data):
                            sessions[session_id] = session_data
                        else:
                            os.remove(filepath)
        except Exception as e:
            logger.error(f"Failed to load sessions: {str(e)}")
        return sessions

    def _is_session_valid(self, session_data):
        last_activity = datetime.fromisoformat(session_data.get('last_activity', ''))
        return datetime.now() - last_activity < self.session_timeout

    def _save_session(self, session_id, session_data):
        try:
            session_data['last_activity'] = datetime.now().isoformat()
            filepath = self._get_session_file(session_id)
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")

    def get_or_create_session(self, session_id=None):
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if self._is_session_valid(session):
                return session_id, session

        new_session_id = str(uuid.uuid4())
        new_session = {
            'history': [],
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        self.sessions[new_session_id] = new_session
        self._save_session(new_session_id, new_session)
        return new_session_id, new_session

    def chat(self, message, session_id=None):
        session_id, session = self.get_or_create_session(session_id)

        session['history'].append({"role": "user", "content": message})

        response = self._generate_response(message, session['history'])

        session['history'].append({"role": "assistant", "content": response})
        self._save_session(session_id, session)

        return session_id, response

    def _generate_response(self, message, history):
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a world-class Lean Startup strategist and product advisor for early-stage founders. "
                        "Your job is to help the user validate ideas, build MVPs, and launch real businesses using Lean Startup, Design Thinking, and fast customer feedback.\n\n"
                        "Break answers into markdown sections with headings and bullet points. "
                        "Be specific, technical, and actionable. If the user asks how to do something, walk them through it step-by-step. "
                        "Keep responses clear and realistic for a founder launching now.\n\n"
                        "Your response should include:\n"
                        "- **Problem/Solution fit**: Identify the real user pain and whether the idea solves it.\n"
                        "- **Customer validation**: How to talk to real users to validate assumptions fast.\n"
                        "- **MVP design**: What’s the smallest product they can build to test the idea.\n"
                        "- **Experiments**: Lean tests, landing pages, waitlists, emails, interviews.\n"
                        "- **Metrics to track**: AARRR metrics (acquisition, activation, retention, etc.)\n"
                        "- **Real startup examples** if relevant\n"
                        "- **Go-to-market** tactics: how to get first users or sales fast\n\n"
                        "Always use this format:\n"
                        "## 🔍 Problem & Insight\n"
                        "## 🧪 Validation Strategy\n"
                        "## 🛠️ MVP Plan\n"
                        "## 📊 Key Metrics\n"
                        "## 🚀 Go-to-Market\n"
                        "## 💡 Final Thoughts\n\n"
                        "Tone: Direct, supportive, and practical — like a YC advisor. Challenge weak assumptions. Be honest and founder-focused."
                    )
                }
            ]

            messages.extend(history[-6:])

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1200,
                temperature=0.7
            )
            return markdown(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"OpenAI failed: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now."

    def cleanup_expired_sessions(self):
        try:
            for session_id, session in list(self.sessions.items()):
                if not self._is_session_valid(session):
                    filepath = self._get_session_file(session_id)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    del self.sessions[session_id]
        except Exception as e:
            logger.error(f"Failed to clean up sessions: {str(e)}")
