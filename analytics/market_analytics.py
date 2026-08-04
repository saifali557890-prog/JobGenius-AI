import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from database.models import Job, Skill
from utils.logger import get_logger

logger = get_logger("MarketAnalytics")

class AnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_top_skills_chart(self, top_n: int = 10):
        """Generates Plotly Bar Chart for most demanded skills across database jobs."""
        skills_query = (
            self.db.query(Skill.name)
            .join(Job.skills)
            .all()
        )
        
        if not skills_query:
            return None

        skill_names = [s[0] for s in skills_query]
        df = pd.DataFrame(skill_names, columns=["Skill"])
        top_skills = df["Skill"].value_counts().reset_index()
        top_skills.columns = ["Skill", "Count"]
        top_skills = top_skills.head(top_n)

        fig = px.bar(
            top_skills,
            x="Count",
            y="Skill",
            orientation="h",
            title=f"🔥 Top {top_n} In-Demand Skills",
            color="Count",
            color_continuous_scale="Viridis",
            text="Count"
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#FFFFFF"},
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

    def get_top_locations_chart(self, top_n: int = 7):
        """Generates Donut Chart for Top Job Locations."""
        jobs = self.db.query(Job.location).all()
        if not jobs:
            return None

        locations = [j[0] if j[0] else "Remote / Unspecified" for j in jobs]
        df = pd.DataFrame(locations, columns=["Location"])
        top_locs = df["Location"].value_counts().reset_index()
        top_locs.columns = ["Location", "Count"]
        top_locs = top_locs.head(top_n)

        fig = px.pie(
            top_locs,
            values="Count",
            names="Location",
            title="📍 Job Distribution by Location",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#FFFFFF"},
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

    @staticmethod
    def create_skill_gap_radar(candidate_skills: list, target_job_skills: list):
        """
        Generates Radar Chart comparing Candidate Skill Vector vs Target Job Skills.
        """
        all_skills = list(set(candidate_skills + target_job_skills))
        if not all_skills:
            return None

        cand_vector = [1 if s in candidate_skills else 0 for s in all_skills]
        job_vector = [1 if s in target_job_skills else 0 for s in all_skills]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=cand_vector,
            theta=all_skills,
            fill='toself',
            name='Your Profile',
            line_color='#6366F1'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=job_vector,
            theta=all_skills,
            fill='toself',
            name='Job Requirement',
            line_color='#EC4899'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1])
            ),
            title="🎯 Skill Alignment Radar",
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#FFFFFF"},
            showlegend=True,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        return fig