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
        
        lean_response = markdown(self._lean_startup_assessment(idea))
        scrum_response = markdown(self._scrum_agile_plan(idea))
        web_context = markdown(search_web(idea))
        
        # Add a new response suggestions section
        suggestions_response = markdown(self._response_suggestions(idea))
        
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
        You are an innovative and practical assistant for Leanchems, providing actionable insights for project ideas. For the idea '{idea}', deliver a concise and engaging response that includes:

        - **Creative Insights**: Offer unique perspectives or approaches related to the idea.
        - **Practical Suggestions**: Provide actionable steps or considerations to advance the project.
        - **Potential Outcomes**: Briefly outline the expected benefits or impact of implementing the idea.
        Generate:
           - Top 5 Most Practical Actions the user can take right now.
           - Specific Tools, Platforms, or Resources to use.
           - Smart Shortcuts or Automation Ideas.
           - Relevant Business Models or Case Studies (if applicable).
           - Advanced Strategies or Next-Level Tips.

         Be creative, proactive, actionable, and detailed.
        Format the response using Markdown for clarity and emphasis. Aim for a balance between brevity and depth to ensure the suggestions are both informative and to the point.
        """
        return self._get_openai_response(prompt)

    def _lean_startup_assessment(self, idea):
        prompt = f"""
        Act as a world-class Lean Startup and Business Validation expert.
        Give a structured assessment covering:
            1. Core Problem Identification
            2. Target Customer Segment
            3. Unique Value Proposition
            4. Suggested Minimum Viable Product (MVP) Features
            5. Lean Business Hypotheses to Test
            6. Customer Acquisition Strategy
            7. Key Risks and How to Validate or Reduce Them
            8. Recommendations for Fastest Path to Market
            9. Suggested Tools, Frameworks or Resources

        And also as a Lean Startup expert for Leanchems, a chemical import/export company revolutionizing operations with technology. For the idea '{idea}', provide a detailed, flexible, and structured assessment:

        ### 🌱 Minimum Viable Product (MVP)  
        - Propose a detailed MVP tailored to the idea.  
        - Include a robust set of **key features** with descriptions (e.g., *real-time tracking* - Monitor shipments live).  
        - Use bullet points for clarity and allow for as many features as relevant.

        ### 🎯 Customer Segments  
        - Identify the primary **customer groups** (e.g., importers, suppliers, compliance teams).  
        - For each, describe:  
          - *Pain Points*: Their key challenges.  
          - *Solution*: How the MVP addresses them.  
        - Use bullet points and include as many segments as applicable.

        ### 📊 Hypotheses  
        - List **measurable hypotheses** with specific metrics (e.g., "Reduce delays by 25%").  
        - Provide a comprehensive set, formatted as a numbered list, without limiting the number.

        ### 🧪 Validation Plan  
        - Outline **actionable steps** to test hypotheses.  
        - Use a table for structure, including as many steps as needed:  
          | **Step** | **Description** | **Timeline** | **Method** |  
          |----------|-----------------|--------------|------------|  
          | Pilot    | Test with clients | 2 weeks     | Pilot run  |

        ### ⚠️ Risks  
        - Highlight **risks** (e.g., regulatory shifts).  
        - For each, add: *Mitigation* in italics (e.g., *Monitor updates*).  
        - Use bullet points and include all relevant risks.

        ### 🏭 Industry Fit  
        - Explain how this aligns with chemical import/export needs in a concise paragraph.  
        - Emphasize benefits like efficiency, safety, or scalability.

        ### 💻 Technology Stack  
        - Recommend a detailed stack, covering all necessary components:  
          - **Frontend**: Tools + rationale (e.g., *React* - Dynamic UI).  
          - **Backend**: Frameworks + databases (e.g., *Flask* - APIs).  
          - **APIs**: External services (e.g., *Customs API*).  
          - **DevOps**: Deployment tools (e.g., *Docker* - Consistency).  
        - Use subheadings and bullet points, adding as many tools as relevant.

        ### 💰 Cost Structure  
        - Outline initial costs and lean strategies in a table:  
        - Include a full range of cost items without restriction.

        ### 📅 Project Management  
        - Suggest a lightweight plan:  
          - **Tool**: Recommended tool (e.g., *Trello* - Task tracking).  
          - **Milestones**: Key milestones (e.g., "MVP prototype - Week 4").  
          - **Cadence**: Meeting schedule (e.g., "Weekly reviews").  
        - Use bullet points and include all relevant milestones.

        Format in Markdown with:  
        - **Subheadings** (`###`) with emojis (e.g., `### 🌱 MVP`).  
        - **Bold** for emphasis (e.g., **MVP**).  
        - *Italics* for secondary details (e.g., *mitigation*).  
        - Tables and bullet points for structure.  
        - A beautiful, organized, and flexible layout without strict limits on items.
        """
        return self._get_openai_response(prompt)

    def _scrum_agile_plan(self, idea):
        prompt = f"""
        You are a Scrum Master for Leanchems, a chemical import/export company blending Lean Startup principles with Agile development. For the idea '{idea}', provide a comprehensive, flexible Scrum plan:

        ### 📝 User Stories  
        - Write **detailed user stories** (e.g., "As a logistics manager, I want...").  
        - For each, include:  
          - *Goal*: Why they need it.  
          - *Acceptance Criteria*: "Given X, when Y, then Z".  
        - Use bullet points and include as many stories as relevant.

        ### ⏳ Sprint Plan  
        - Detail a **2-week sprint** with a full set of **tasks**.  
        - Add all necessary tasks without restriction.

        ### 🎁 Deliverables  
        - List **specific deliverables** (e.g., "Shipment dashboard").  
        - Add a *Purpose* sentence for each.  
        - Use bullet points and include all relevant deliverables.

        ### 👥 Team Roles  
        - Define **roles** with responsibilities (e.g., "Developer: Build APIs").  
        - Format as a numbered list, adding as many roles as needed.

        ### 🔗 Dependencies  
        - Note **dependencies** (e.g., "Customs API").  
        - Add *Contingency* in italics (e.g., *Mock API if delayed*).  
        - Use bullet points and include all relevant dependencies.

        ### 📈 Success Metrics  
        - Define **measurable metrics** (e.g., "95% uptime").  
        - Include *Tracking Method* (e.g., "CloudWatch").  
        - Use bullet points and list all applicable metrics.

        ### 🛡️ Risk Mitigation  
        - Identify **Scrum risks** (e.g., "Scope creep").  
        - Provide *Mitigation* steps (e.g., "Daily standups").  
        - Use bullet points and cover all key risks.

        ### 🚀 Deployment and End-to-End Strategy  
        - Outline a detailed plan:  
          - **CI/CD**: Pipeline setup (e.g., *GitHub Actions*).  
          - **Hosting**: Platform + scaling (e.g., *AWS EC2*).  
          - **Testing**: Types + tools (e.g., *pytest*).  
          - **Monitoring**: Tools + metrics (e.g., *CloudWatch*).  
          - **Workflow**: Steps (e.g., "Code -> Test -> Deploy").  
        - Use subheadings and bullet points, adding all relevant details.

        ### 📅 Project Management  
        - Suggest an Agile plan:  
          - **Tool**: Recommended tool (e.g., *Jira* - Sprint tracking).  
          - **Milestones**: Key milestones (e.g., "Sprint 1 end - Week 2").  
          - **Cadence**: Meeting schedule (e.g., "Daily standups").  
        - Use bullet points and include all necessary milestones.

        Format in Markdown with:  
        - **Subheadings** (`###`) with emojis (e.g., `### 📝 User Stories`).  
        - **Bold** for emphasis (e.g., **User Stories**).  
        - *Italics* for secondary details (e.g., *contingency*).  
        - Tables and bullet points for structure.  
        - A beautiful, organized, and flexible layout without strict limits on items.
        """
        return self._get_openai_response(prompt)

    def _get_openai_response(self, prompt):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a detailed assistant for Leanchems, providing structured Markdown responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.6
            )
            content = response.choices[0].message.content
            logger.debug(f"OpenAI response: {content}")
            return content
        except Exception as e:
            logger.error(f"OpenAI failed: {str(e)}")
            return "Response generation failed due to OpenAI error."