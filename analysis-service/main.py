from textblob import TextBlob
import json


def analyze_text(text: str) -> dict:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
    }


if __name__ == "__main__":
    ejemplo = "Las noticias falsas tienen un impacto muy negativo en la sociedad."
    result = analyze_text(ejemplo)
    print("[analysis] Ejemplo de análisis:", json.dumps(result, indent=2))
