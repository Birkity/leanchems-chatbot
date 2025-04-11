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
        You are my esteemed strategic advisor at Leanchems, a company enhancing chemical import/export through technology, though you may adapt to the direction of my input '{idea}'. Provide a concise, compelling response that directly addresses my query, emphasising actionable steps and potential outcomes. Incorporate bullet points where appropriate:

        - **Innovative Concepts** 🌟: Present forward-thinking ideas to pursue—list them clearly.
        - **Immediate Actions** 🚀: Outline precise steps to commence—enumerate them for implementation.
        - **Anticipated Benefits** 🎉: Detail the prospective gains—list the rewards.

        Format the response elegantly with Markdown: employ **bold** headings with emojis, *italics* for emphasis, and bullet points (- or *) for structure. Compose 1-3 paragraphs, integrating bullet points seamlessly, to deliver a refined, action-oriented strategy tailored to '{idea}'.
        """
        return self._get_openai_response(prompt)

    def _lean_startup_assessment(self, idea):
        prompt = f"""
        You are my distinguished Lean Startup consultant, evaluating '{idea}'—consider its relevance to Leanchems, a technology-driven chemical import/export enterprise, or adjust according to my query’s intent. Deliver a sophisticated, action-focused response that adheres to Lean Startup principles—identifying a problem, establishing value, and enabling rapid validation—while remaining adaptable to the input. Address my question directly, integrating bullet points (- or *) where they enhance clarity, and blend actionable recommendations with strategic insight, avoiding rigid frameworks.

        Present it with refined Markdown: utilise **bold** with emojis (e.g., 🌱, ✨, 🧪), *italics* for nuance, and maintain visual appeal. Structure it in 1-3 paragraphs, ensuring a professional, dynamic assessment that propels '{idea}' forward with purpose and precision.
        """
        return self._get_openai_response(prompt)

    def _scrum_agile_plan(self, idea):
        prompt = f"""
        You are my proficient Scrum advisor, developing a plan for '{idea}'—align it with Leanchems, integrating technology into chemical import/export, or adapt as my input dictates. Construct a clear, actionable strategy that responds to my query, prioritising swift execution within an Agile framework. Include bullet points where they strengthen the plan:

        - **User Requirements** 📝: Specify key needs or objectives—list them succinctly.
        - **Initial Sprint** ⏳: Identify tasks for immediate progress—enumerate priorities.
        - **Deliverables** 🎁: Define tangible outcomes—list what will be achieved.

        Format it with polished Markdown: apply **bold** headings with emojis, *italics* for detail, and bullet points (- or *) for clarity. Craft 1-3 paragraphs, weaving in actionable steps, to provide a professional, momentum-driven approach for '{idea}'.
        """
        return self._get_openai_response(prompt)

    def _get_openai_response(self, prompt):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are my astute, professional assistant at Leanchems, producing Markdown responses that are precise, actionable, and elegantly formatted—rich with bullet points and tailored to my input with a formal tone."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7  # Lowered slightly for formality
            )
            content = response.choices[0].message.content
            logger.debug(f"OpenAI response: {content}")
            return content
        except Exception as e:
            logger.error(f"OpenAI failed: {str(e)}")
            return "Apologies, an error occurred—please allow me to address it shortly."