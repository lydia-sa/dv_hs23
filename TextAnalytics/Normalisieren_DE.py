from contractions import CONTRACTION_MAP
import re
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
import spacy
import unicodedata
import re
from bs4 import BeautifulSoup

def normalize_corpus(corpus, html_stripping=True, contraction_expansion=True,
                     accented_char_removal=True, text_lower_case=True,
                     text_lemmatization=True, special_char_removal=True,
                     stopword_removal=True, remove_digits=True):

    # Corpus = Liste von Listen
    normalized_corpus = []
    # normalize each document in the corpus
    for doc in corpus:
        # strip HTML macht immer Sinn, da dies den Text massiv verkürzt
        if html_stripping:
            doc = strip_html_tags(doc)
        # remove accented characters
        if accented_char_removal:
            doc = remove_accented_chars(doc)

        # lowercase the text
        if text_lower_case:
            doc = doc.lower()
        # remove extra newlines
        doc = re.sub(r'[\r|\n|\r\n]+', ' ',doc)
        # lemmatize text
        if text_lemmatization:
            doc = lemmatize_text(doc)
        # remove special characters and\or digits
        if special_char_removal:
            # insert spaces between special characters to isolate them
            special_char_pattern = re.compile(r'([{.(-)!}])')
            doc = special_char_pattern.sub(" \\1 ", doc)
            doc = remove_special_characters(doc, remove_digits=remove_digits)
        # remove extra whitespace
        doc = re.sub(' +', ' ', doc)
        # remove stopwords
        if stopword_removal:
            doc = remove_stopwords(doc, is_lower_case=text_lower_case)

        normalized_corpus.append(doc)

    return normalized_corpus


tokenizer = ToktokTokenizer()
stopword_list = nltk.corpus.stopwords.words('german')
def remove_stopwords(text, is_lower_case=False, stopwords=stopword_list):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]        #Leerzeichen entfernen
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopwords]     #wenn nicht in der Stoppwortliste, dann übernehmen wir das Wort
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopwords]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
    text = re.sub(pattern, '', text)
    return text


nlp = spacy.load('de_dep_news_trf')
def lemmatize_text(text):
    text = nlp(text)
    text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in text])
    return text


def remove_accented_chars(text):
    translation_table = str.maketrans({'ä': 'ae', 'ü': 'ue', 'ö':'oe', 'Ä': 'Ae', 'Ü': 'Ue', 'Ö':'Oe'})
    text = text.translate(translation_table)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text


def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")                       # wir wollen alles html mässige rausschmeissen
    [s.extract() for s in soup(['iframe', 'script'])]               #iframe und scripte wollen wir extrahieren
    stripped_text = soup.get_text()
    stripped_text = re.sub(r'[\r|\n|\r\n]+', '\n', stripped_text)   #wollen bei mehreren Umbrüchen hintereinander alle durch einen ersetzen
    return stripped_text