
import re
import unicodedata
from utils.constants import space_demarker
import nltk
from nltk.stem import PorterStemmer, RSLPStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('rslp')

stop_words = set(stopwords.words('portuguese'))

def mark_word_spaces(words: list):
    for idx, word in enumerate(words):
        words[idx] = space_demarker.join(word.strip().split(" "))
    return words

def mark_compound_names(sentence: str, compound_names) -> str:
    sentence_lower = sentence.lower()
    for name in compound_names:
        name_lower = name.lower()
        if name_lower in sentence_lower:
            marked_name = space_demarker.join(name_lower.split()) + space_demarker
            sentence_lower = sentence_lower.replace(name_lower, marked_name)
    return sentence_lower



def normalize_spaces(text: str) -> str:
    """
    Normalize multiple spaces in the text to a single space.
    """
    # Strip leading/trailing spaces and replace multiple spaces with a single space
    return re.sub(r'\s+', ' ', text.strip())


def normalize_word(input_data):
    def normalize(text):        
        if(isinstance(text, int)): return text

        nfkd_form = unicodedata.normalize('NFKD', text)
        without_accents = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
        return without_accents.lower()
    
    if isinstance(input_data, str):
        return normalize(input_data)
    elif isinstance(input_data, list):
        return [normalize(word) for word in input_data]
    elif isinstance(input_data, int):
        return input_data
    else:
        raise TypeError("A função aceita apenas string ou lista de strings.")

def is_stop_word(word:str):
    return word in stop_words

def is_word_present(word:str, comp):
    if(isinstance(comp, str)):
        return word in comp and len(word) == len(comp)
    
    if(isinstance(comp, list)):
        return word in "".join(comp)

    return False
    
    

def remove_space_demarker(word, demarker):
    if(isinstance(word, str)):
        if demarker not in word:
            return word
        
        word = word.replace(demarker, ' ')
        return word.strip()
    elif(isinstance(word, list)):
        for idx, w in enumerate(word):
            word[idx] = w.replace(demarker, ' ').strip()

def extract_compound_names(file_path, output_py_path):
    compound_names = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line.startswith('- '):
                continue

            name = line[2:].split(' - [')[0].strip()
            if ' ' in name:
                compound_names.append(normalize_word(name))

    with open(output_py_path, 'w', encoding='utf-8') as py_file:
        py_file.write(f"cidades_nome_composto = {compound_names}\n")


def perform_stemming(word: str, language: str = "english") -> str:
    """
    Reduces the given word to its stem based on the specified language.
    
    Parameters:
    - word (str): The word to be stemmed.
    - language (str): The language of the word ('english' or 'portuguese').

    Returns:
    - str: The stemmed form of the word.
    """

    if(len(word) == 0):
        return word

    if language == "english":
        stemmer = PorterStemmer()
    elif language == "portuguese":
        stemmer = RSLPStemmer()
    else:
        raise ValueError("Unsupported language. Use 'english' or 'portuguese'.")

    return stemmer.stem(word)

def get_setor_from_word(word: str, sentence: str) -> str:
    stop_words = set(stopwords.words('portuguese'))
    
    words = sentence.lower().split()
    word = word.lower()
    
    if word != "industria" and word != "comercio" and word not in stop_words:
        return word
    
    try:
        index = words.index(word)
    except ValueError:
        return word  
    
    for next_word in words[index + 1:]:
        if next_word not in stop_words:
            return next_word
    
    return word  

def remove_stopwords(sentence, language='portuguese'):
    '''
    Removes stopwords from a given sentence.
    '''
    stop_words = set(stopwords.words(language))
    words = word_tokenize(sentence)
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def is_valid_setor(sentence, ground_truth):
    words_sentence = sentence.split(" ")
    words_ground_truth = []
    for setor in ground_truth:
        setor = remove_stopwords(setor)
        words_setor = setor.split(" ")
        words_ground_truth.extend(words_setor)

    count = 0
    min_similarity = 2 if len(words_ground_truth) >= 2 else 1

    for word in words_ground_truth:
        if word in words_sentence:
            count += 1

    return count >= min_similarity
    