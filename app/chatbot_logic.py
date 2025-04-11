import openai
import os
from .web_search import search_web
from dotenv import load_dotenv
import logging
from markdown2 import markdown

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

class LeanchemsChatbot:
    def __init__(self):
        self.history = []

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
        return response

    def _response_suggestions(self, idea):
        prompt = f"""
        You’re my creative partner at Leanchems, brainstorming '{idea}'—a company blending tech into chemical import/export, but flex if the idea shifts. Craft a concise, stunning response that inspires me. Use bullet points for key ideas under these headings where they fit:

        - **Creative Angles** 🌟: Fresh spins or clever twists—list them as bullets.
        - **Next Steps** 🚀: Practical moves to start—bullet points for clarity.
        - **Impact** 🎉: What this could lead to—bullets for punchy outcomes.

        Make it gorgeous with Markdown: **bold** headings with emojis, *italics* for flair, and bullet points (- or *) for crisp lists. Keep it 1-3 paragraphs with bullets woven in, flowing naturally—like a beautifully sketched plan!
        """
        return self._get_openai_response(prompt)

    def _lean_startup_assessment(self, idea):
        prompt = f"""
        You’re my Lean Startup guide, exploring '{idea}'—think Leanchems, techifying chemical import/export, but adapt as needed. Give me a clear, beautiful assessment with bullet points under headings that suit the idea, like:

        - **Problem** 🔍: What’s this solving?—bullet what stands out.
        - **Who’s It For** 👥: Key people or groups—list them with details.
        - **Value** ✨: Why it’s worth it—bullets for impact.
        - **MVP** 🌱: A simple start—bullet features if they fit.
        - **Tests** 🧪: Ways to check it—list quick experiments.
        - **Risks** ⚠️: Hurdles and fixes—bullets with *mitigations* in italics.

        Use Markdown to shine: **bold** headings with emojis, *italics* for nuance, and bullet points (- or *) for tidy lists. Skip what doesn’t click, keep it natural, and nod to chemical import/export where it works—otherwise, just flow with the idea!
        """
        return self._get_openai_response(prompt)

    def _scrum_agile_plan(self, idea):
        prompt = f"""
        You’re my Scrum coach, planning '{idea}' with Agile flair—imagine Leanchems, mixing tech into chemical import/export, but pivot if the idea pulls elsewhere. Build a practical, pretty plan with bullet points under headings that work, like:

        - **Stories** 📝: Who needs what—list a few as bullets.
        - **Sprint** ⏳: What I’d tackle short-term—bullet the focus.
        - **Wins** 🎁: What I’d show off—list deliverables.
        - **Team** 👥: Rough roles—bullets for who does what.
        - **Risks** 🛡️: Things to watch—list with *fixes* in italics.

        Format it with Markdown magic: **bold** headings with emojis, *italics* for extras, and bullet points (- or *) for sharp lists. Don’t force anything—pick what’s useful, tying to chemical import/export if it fits, or just roll with the idea!
        """
        return self._get_openai_response(prompt)

    def _get_openai_response(self, prompt):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You’re my adaptable, style-savvy assistant at Leanchems, crafting Markdown responses that are clear, creative, and visually delightful—packed with bullet points and tailored to my idea!"},
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
            return "Oops, something hiccupped—let’s try again later!"