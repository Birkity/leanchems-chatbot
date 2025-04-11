import openai
import os
import json
from .web_search import search_web
from dotenv import load_dotenv
import logging
from markdown2 import markdown

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

class LeanchemsChatbot:
    def __init__(self):
        self.memory_file = "memory.json"
        self.history = self._load_history()

    def _load_history(self):
        """Load chat history from memory.json, or initiate a new list if absent."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load history: {str(e)}")
            return []

    def _save_history(self):
        """Save chat history to memory.json."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {str(e)}")

    def assess_project_idea(self, idea):
        logger.info(f"Assessing project idea: {idea}")
        self.history.append({"role": "user", "content": idea})
        
        suggestions_response = markdown(self._response_suggestions(idea))
        lean_response = markdown(self._lean_startup_assessment(idea))
        scrum_response = markdown(self._scrum_agile_plan(idea))
        web_context = markdown(search_web(idea))
        
        response = f"""
<div class="assessment-container">
    <div class="assessment-section suggestions">
        <h3><i class="fas fa-star"></i> Response Suggestions</h3>
        {suggestions_response}
    </div>

    <div class="assessment-section lean-startup">
        <h3><i class="fas fa-lightbulb"></i> Lean Startup Assessment</h3>
        {lean_response}
    </div>

    <div class="assessment-section scrum">
        <h3><i class="fas fa-tasks"></i> Scrum Agile Plan</h3>
        {scrum_response}
    </div>

    <div class="assessment-section insights">
        <h3><i class="fas fa-globe"></i> Web Insights & Examples</h3>
        {web_context}
    </div>
</div>
"""
        logger.debug(f"Generated response: {response}")
        self.history.append({"role": "assistant", "content": response})
        self._save_history()
        return response

    def _response_suggestions(self, idea):
        prompt = f"""
        As my esteemed advisor at Leanchems—experts in technology-enhanced chemical import/export—provide a good and well written, actionable response to '{idea}', adapting as needed. Focus on delivering clear, practical steps and impactful outcomes tailored to my query. Use bullet points (- or *) where they enhance clarity. Format elegantly with Markdown: **bold** with emojis (e.g., 🌟, 🚀), *italics* for emphasis, in 1-2 paragraphs.
        """
        return self._get_openai_response(prompt)

    def _lean_startup_assessment(self, idea):
        prompt = f"""
        As my distinguished Lean Startup consultant at Leanchems, assess '{idea}'—align with our tech-driven chemical import/export focus if relevant, or adjust to my intent. Offer a good, action-oriented response rooted in Lean principles (problem-solving, value creation, rapid testing), tailored to my query. Integrate bullet points (- or *) where they sharpen the plan. Present it professionally with Markdown: **bold** with emojis (e.g., 🌱, ✨), *italics* for nuance, in 1-2 paragraphs.
        """
        return self._get_openai_response(prompt)

    def _scrum_agile_plan(self, idea):
        prompt = f"""
        As my proficient Scrum advisor at Leanchems, integrating technology into chemical import/export, devise an actionable plan for '{idea}', adapting to my input. Prioritise swift, practical steps within an Agile framework, directly addressing my query. Use bullet points (- or *) where they strengthen execution. Format with refined Markdown: **bold** with emojis (e.g., 📝, ⏳), *italics* for detail, in 1-2 paragraphs.
        """
        return self._get_openai_response(prompt)

    def _get_openai_response(self, prompt):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are my astute assistant at Leanchems, delivering concise, actionable, and professionally formatted Markdown responses—tailored to my input with a formal tone, using bullet points where effective."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            content = response.choices[0].message.content
            logger.debug(f"OpenAI response: {content}")
            return content
        except Exception as e:
            logger.error(f"OpenAI failed: {str(e)}")
            return "Apologies, an error occurred—please allow me to rectify it shortly."