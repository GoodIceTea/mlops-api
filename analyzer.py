from transformers import pipeline
from langdetect import detect

class JobAnalyzer:
    def __init__(self):
        print("Loading AI model...")
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
            )
            print("AI model loaded.")
        except Exception as e:
            print(f"Error loading AI model: {e}")
            exit(1)

    def extract_key_info(self, text:str) -> dict:
        short_text = text[:1500]

        try:
            detected_lang = detect(short_text)
        except:
            detected_lang = "pl"

        print(f"Detected language: {detected_lang.upper()}")

        exp_labels = ["Junior", "Mid", "Regular", "Senior", "Lead"]

        if detected_lang == "en":
            print("Using ENGLISH labels")
            exp_template = "Required experience level in this offer is {}"
            work_labels = ["fully remote", "hybrid", "on-site office work"]
            work_template = "If it's about locations, it's {}"
        else:
            print("Using POLISH labels")
            exp_template = "Wymagany poziom doświadczenia w tej ofercie to {}"
            work_labels = ["praca w pełni zdalna", "praca hybrydowa", "praca stacjonarna w biurze"]
            work_template = "Jeśli chodzi o lokalizacje jest to {}"

        exp_results = self.classifier(
            short_text,
            candidate_labels = exp_labels,
            hypothesis_template = exp_template
        )

        work_results = self.classifier(
            short_text,
            candidate_labels = work_labels,
            hypothesis_template = work_template
        )

        return {
            "language": detected_lang,
            "predicted_experience": exp_results["labels"][0],
            "experience_confidence": round(exp_results["scores"][0]*100,2),
            "predicted_work_mode": work_results["labels"][0],
            "work_mode_confidence": round(work_results["scores"][0]*100,2)
        }

#test
if __name__ == "__main__":
    sample_english_job = """
    We are looking for a data enthusiast to join our team in Lodz!
    You will be responsible for creating Python scripts and SQL analysis.
    We offer flexible hours and 100% remote work.
    We require about 1 year of commercial experience.
    """

    analyzer = JobAnalyzer()
    wyniki = analyzer.extract_key_info(sample_english_job)

    print("\n================ WNIOSKI AI ================")
    print(f"Wykryty język: {wyniki['language']}")
    print(f"Poziom: {wyniki['predicted_experience']} (Pewność: {wyniki['experience_confidence']}%)")
    print(f"Tryb: {wyniki['predicted_work_mode']} (Pewność: {wyniki['work_mode_confidence']}%)")