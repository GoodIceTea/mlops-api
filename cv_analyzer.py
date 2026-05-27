import pypdf
from sentence_transformers import SentenceTransformer, util
import time
import os

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


#test
if __name__ == "__main__":
    analyzer = CV_Analyzer()

    my_pdf_file = "Michal_Galezowski_ENG_CV.pdf"
    print(f"\n Trying to read {my_pdf_file}...")
    cv_content = analyzer.extract_text_from_pdf(my_pdf_file)

    if cv_content:
        print(f"Success, extracted {len(cv_content.split())} words from PDF.")
        print(f"First 100 words: {cv_content[:100]}")

        test_stack = "Python, PyTorch, Machine Learning, Data Analysis, SQL"
        print(f"Test stack: {test_stack}")

        start_time = time.time()
        score = analyzer.calculate_match(cv_content, test_stack)
        calc_time = time.time() - start_time

        print(f"\nCV match score: {score}% (calculated in {calc_time:.4f} seconds)")
    else:
        print("Failed to extract text from PDF.")
