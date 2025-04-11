import openai
import os
import json
import time
from .web_search import search_web
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
        self.session_timeout = timedelta(hours=24)  # 24 hours session timeout
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.sessions = self._load_sessions()

    def _get_session_file(self, session_id):
        return os.path.join(self.tmp_dir, f"{session_id}.json")

    def _load_sessions(self):
        """Load all session files from /tmp directory."""
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
                            os.remove(filepath)  # Clean up expired sessions
        except Exception as e:
            logger.error(f"Failed to load sessions: {str(e)}")
        return sessions

    def _is_session_valid(self, session_data):
        """Check if session is still valid based on last activity."""
        last_activity = datetime.fromisoformat(session_data.get('last_activity', ''))
        return datetime.now() - last_activity < self.session_timeout

    def _save_session(self, session_id, session_data):
        """Save session data to file."""
        try:
            session_data['last_activity'] = datetime.now().isoformat()
            filepath = self._get_session_file(session_id)
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")

    def get_or_create_session(self, session_id=None):
        """Get existing session or create a new one."""
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if self._is_session_valid(session):
                return session_id, session
        
        # Create new session
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
        """Handle chat message with session management."""
        session_id, session = self.get_or_create_session(session_id)
        
        # Add user message to history
        session['history'].append({"role": "user", "content": message})
        
        # Check if user explicitly requested Lean/Scrum analysis
        is_lean_requested = any(keyword in message.lower() for keyword in ['lean', 'startup', 'mvp'])
        is_scrum_requested = any(keyword in message.lower() for keyword in ['scrum', 'agile', 'sprint'])
        
        # Generate response based on context
        if is_lean_requested or is_scrum_requested:
            response = self._generate_specialized_response(message, is_lean_requested, is_scrum_requested)
        else:
            response = self._generate_natural_response(message, session['history'])
        
        # Add assistant response to history
        session['history'].append({"role": "assistant", "content": response})
        
        # Save updated session
        self._save_session(session_id, session)
        
        return session_id, response

    def _generate_natural_response(self, message, history):
        """Generate a natural, context-aware response."""
        try:
            messages = [
                {"role": "system", "content": """You are a helpful assistant at Leanchems, a technology-enhanced chemical import/export company. 
                Maintain a professional yet conversational tone. Use markdown formatting for clarity. 
                Only provide specialized analysis when explicitly requested."""}
            ]
            
            # Add conversation history
            messages.extend(history[-5:])  # Keep last 5 messages for context
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return markdown(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI failed: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now."

    def _generate_specialized_response(self, message, is_lean_requested, is_scrum_requested):
        """Generate specialized response when Lean/Scrum is requested."""
        try:
            specialized_prompts = []
            
            if is_lean_requested:
                specialized_prompts.append(f"""
                As a Lean Startup consultant at Leanchems, analyze '{message}' focusing on:
                - Problem-solution fit
                - Minimum Viable Product (MVP) approach
                - Customer validation
                - Iterative development
                Format with clear markdown structure and bullet points.
                """)
            
            if is_scrum_requested:
                specialized_prompts.append(f"""
                As a Scrum expert at Leanchems, provide an Agile plan for '{message}' covering:
                - Sprint planning
                - Backlog management
                - Iterative delivery
                - Team collaboration
                Format with clear markdown structure and bullet points.
                """)
            
            responses = []
            for prompt in specialized_prompts:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a specialized consultant at Leanchems, providing detailed analysis with clear markdown formatting."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                responses.append(markdown(response.choices[0].message.content))
            
            return "\n\n".join(responses)
        except Exception as e:
            logger.error(f"OpenAI failed: {str(e)}")
            return "I apologize, but I'm having trouble processing your specialized request right now."

    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            current_time = datetime.now()
            for session_id, session in list(self.sessions.items()):
                if not self._is_session_valid(session):
                    filepath = self._get_session_file(session_id)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    del self.sessions[session_id]
        except Exception as e:
            logger.error(f"Failed to clean up sessions: {str(e)}")