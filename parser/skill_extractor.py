import re
from typing import List, Set
from utils.logger import get_logger

logger = get_logger("SkillExtractor")

# Core Technical & Soft Skill Taxonomy Database
TAXONOMY_SKILLS = {
    # Tech / Software / Data Science
    "python", "java", "c++", "c#", "javascript", "typescript", "html", "css", "sql", "nosql",
    "postgresql", "mysql", "mongodb", "redis", "fastapi", "django", "flask", "streamlit",
    "react", "angular", "vue.js", "node.js", "express", "next.js", "docker", "kubernetes",
    "aws", "azure", "gcp", "git", "github", "gitlab", "ci/cd", "linux", "bash",
    
    # AI / Machine Learning / Data Science
    "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spacy", "nltk", "opencv",
    "faiss", "transformers", "huggingface", "bert", "langchain", "llm", "generative ai",
    
    # Software Engineering & Analytics
    "data analysis", "data engineering", "power bi", "tableau", "excel", "spark", "hadoop",
    "rest api", "graphql", "microservices", "agile", "scrum", "jira", "unit testing"
}

class SkillExtractor:
    def __init__(self, skill_set: Set[str] = None):
        self.skills_db = skill_set if skill_set else TAXONOMY_SKILLS

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts verified tech skills using normalized word boundary Regex matching.
        """
        if not text:
            return []
        
        normalized_text = f" {text.lower()} "
        # Replace non-alphanumeric boundaries while retaining key tech symbols (+, #, .)
        clean_text = re.sub(r'[^a-z0-9\+#\.]', ' ', normalized_text)
        
        found_skills = set()
        
        for skill in self.skills_db:
            # Escape symbols like c++, c#
            pattern = r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)'
            if re.search(pattern, clean_text):
                found_skills.add(skill.strip())

        logger.info(f"Extracted {len(found_skills)} distinct skills.")
        return sorted(list(found_skills))