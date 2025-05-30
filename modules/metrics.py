import os
from pymorphy2 import MorphAnalyzer
from fuzzywuzzy import fuzz

morph = MorphAnalyzer()

def lemmatize_term(term):
    return ' '.join([morph.parse(word)[0].normal_form for word in term.lower().split()])

def load_reference_terms(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    ref_file = os.path.join('reference_terms', f'{base}.txt')
    if not os.path.exists(ref_file):
        print(f"[!] Эталонный файл не найден: {ref_file}")
        return set()
    with open(ref_file, 'r', encoding='utf-8') as f:
        terms = set(lemmatize_term(line.strip()) for line in f if line.strip())
    return terms

def normalize_term(term):
    return lemmatize_term(term.strip())

def evaluate_terms(predicted_terms, reference_terms, fuzzy_threshold=90):
    predicted_set = set(map(normalize_term, predicted_terms))
    reference_set = set(reference_terms)  # уже лемматизированы

    true_positives = 0
    matched_pred = set()
    matched_ref = set()
    for pred in predicted_set:
        for ref in reference_set:
            if fuzz.ratio(pred, ref) >= fuzzy_threshold:
                true_positives += 1
                matched_pred.add(pred)
                matched_ref.add(ref)
                break

    precision = true_positives / len(predicted_set) if predicted_set else 0
    recall = true_positives / len(reference_set) if reference_set else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    return precision, recall, f1
