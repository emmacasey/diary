import nltk
import string
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("vader_lexicon")

stemmer = nltk.PorterStemmer()
stopwords = nltk.corpus.stopwords.words("english")
sentiment_analyser = SentimentIntensityAnalyzer()
word_characters = string.ascii_letters + string.whitespace + string.digits


def strip_punc(sent: str) -> str:
    return "".join(c for c in sent if c in word_characters)


def tokenize(sent: str) -> list[str]:
    """Given some prose produe lematised tokens with stopwords stripped."""
    tokens = word_tokenize(strip_punc(sent).lower())
    return [stemmer.stem(word) for word in tokens if word not in stopwords]


def stats(para: str) -> dict[str, float]:
    sents = sent_tokenize(para)
    tokens = word_tokenize(para)
    content_lemmas = tokenize(para)
    return sentiment(para) | {
        "sent_count": len(sents),
        "token_count": len(tokens),
        "content_words": len(content_lemmas),
        "letters_per_word": sum(len(word) for word in tokens) / len(tokens),
        "words_per_sent": len(tokens) / len(sents),
        "content_per_sent": len(content_lemmas) / len(sents),
    }


def sentiment(sent: str) -> dict[str, float]:
    return sentiment_analyser.polarity_scores(sent)
