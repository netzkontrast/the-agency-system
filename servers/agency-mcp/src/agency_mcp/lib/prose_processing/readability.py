import textstat
def analyze_readability(text: str) -> dict:
    return {
        "flesch": textstat.flesch_reading_ease(text),
        "fog": textstat.gunning_fog(text),
        "smog": textstat.smog_index(text),
        "grade_level": textstat.text_standard(text, float_output=True),
        "avg_sentence_length": textstat.avg_sentence_length(text)
    }
