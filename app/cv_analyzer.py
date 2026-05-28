import pypdf
from sentence_transformers import SentenceTransformer, util
import time
import os
import re

class CV_Analyzer:
    def __init__(self):
        print("Loading AI model...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("AI model loaded.")
        except Exception as e:
            print(f"Error loading AI model: {e}")
            exit(1)

    def extract_text_from_pdf(self, pdf_path:str) -> str:
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return ""

        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + " "
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def calculate_match(self, cv_text: str, job_requirements: str) -> float:
        if not job_requirements or job_requirements == "Not found" or not cv_text:
            return 0.0

        cv_words = cv_text.split()[:400]
        truncated_cv = " ".join(cv_words)

        embeddings = self.model.encode([truncated_cv, job_requirements])
        cosine_score = util.cos_sim(embeddings[0], embeddings[1])

        raw_score = cosine_score.item()

        ux_score = (raw_score * 1.3) * 100

        return max(0.0, min(100.0, round(ux_score, 1)))

    def get_missing_skills(self, cv_text: str, job_requirements: str) -> list[str]:
        if not job_requirements or job_requirements == "Not found" or not cv_text:
            return []

        missing =[]

        cv_lower = cv_text.lower()
        required_skills = [skill.strip() for skill in job_requirements.split(',')]

        for skill in required_skills:
            clean_skill = skill.lower()
            escaped = re.escape(clean_skill)
            pattern = rf"(^|\W){escaped}($|\W)"

            if not re.search(pattern, cv_lower):
                missing.append(skill)

        return missing
