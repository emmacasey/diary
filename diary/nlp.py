import nltk

nltk.download("punkt")
nltk.download("stopwords")

stemmer = nltk.PorterStemmer()
stopwords = nltk.corpus.stopwords.words("english")


def tokenize(sent: str) -> list[str]:
    """Given some prose produe lematised tokens with stopwords stripped."""
    tokens = nltk.tokenize.word_tokenize(
        sent.replace("-", " ").replace("—", " ").lower()
    )
    content_words = [
        word for word in tokens if word not in stopwords and word.isalpha()
    ]
    return [stemmer.stem(word, to_lowercase=True) for word in content_words]
