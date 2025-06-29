# convert from an df in a specific struct to .txt usable by flair
import pandas as pd
import random
import utils.constants as cts
from tqdm import tqdm
from collections import defaultdict
from dataset_converter.dataset_preprocessing import get_df_from_dataset
from dataset_converter.increment_dataset import increment_dataset
from difflib import SequenceMatcher
import re
import pickle

import re


random.seed(cts.seed)
def matcher(text, annotations):
    '''
    Retorna os spans (start, end, tipo) das anotações no texto.
    '''
    match_list = []
    for pattern, label in annotations:
        pattern = pattern.strip()
        for match in re.finditer(re.escape(pattern), text, flags=re.IGNORECASE):
            match_list.append((match.start(), match.end(), label))
    return match_list


def tokenize_with_positions(text):
    '''
    Tokeniza o texto e retorna lista de (token, start_idx, end_idx)
    '''
    tokens = []
    for match in re.finditer(r'\S+', text):  # Match palavras não separadas por espaço
        token = match.group()
        start = match.start()
        end = match.end()
        tokens.append((token, start, end))
    return tokens


def bio_tagging(text, annotations):
    '''
    Gera a marcação BIO por palavra, com base nos spans das entidades.
    '''
    entity_spans = matcher(text, annotations)
    tokens = tokenize_with_positions(text)

    tagged = []
    for token, start, end in tokens:
        tag = 'O'
        for ent_start, ent_end, label in entity_spans:
            if start == ent_start:
                tag = f'B-{label}'
                break
            elif ent_start < start < ent_end:
                tag = f'I-{label}'
                break
        tagged.append((token, tag))
    return tagged


def create_data(df, filepath):
    with open(filepath , 'w', encoding='utf-8') as f:
        for text, annotation in zip(df.text, df.annotation):
            tagged = bio_tagging(text, annotation)
            for token, tag in tagged:
                f.write(f"{token} {tag}\n")
            f.write("\n")

def get_label_from_example(example_text):
    """
    Exemplo simples: extrair o label principal do exemplo.
    Como seu dado parece estar em BIO com tokens, talvez pegar a primeira entidade B-XXX?
    Ajuste essa função conforme seu formato.
    """
    lines = example_text.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            tag = parts[-1]
            if tag.startswith('B-'):
                return tag[2:]
    return 'NO_LABEL'  # fallback para casos sem entidades

def split_train_file_stratified(file_path, dev_ratio=0.1, test_ratio=0.1, seed=42):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().strip().split('\n\n')

    # Agrupar exemplos pela label principal para estratificação
    label_to_examples = defaultdict(list)
    for example in data:
        label = get_label_from_example(example)
        label_to_examples[label].append(example)

    random.seed(seed)

    train_data, dev_data, test_data = [], [], []

    for label, examples in label_to_examples.items():
        random.shuffle(examples)
        n = len(examples)
        n_dev = int(n * dev_ratio)
        n_test = int(n * test_ratio)
        n_train = n - n_dev - n_test

        train_data.extend(examples[:n_train])
        dev_data.extend(examples[n_train:n_train + n_dev])
        test_data.extend(examples[n_train + n_dev:])

    # Shuffle para garantir mistura final
    random.shuffle(train_data)
    random.shuffle(dev_data)
    random.shuffle(test_data)

    # Salvar arquivos
    with open(file_path.replace('train.txt', 'train.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(train_data))

    with open(file_path.replace('train.txt', 'dev.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(dev_data))

    with open(file_path.replace('train.txt', 'test.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(test_data))

    total = len(data)
    print(f"Total de exemplos: {total}")
    print(f"Tamanho treino: {len(train_data)}")
    print(f"Tamanho dev: {len(dev_data)}")
    print(f"Tamanho teste: {len(test_data)}")
    print("Divisão estratificada concluída!")

def remove_void_entities(file_path):
    correted_lines = []
    with open(file=file_path, mode='r', encoding='utf-8') as f:
        lines = f.readlines()

        for line in lines:
            line_stripped = line.strip()

            if(line_stripped == ""):
                correted_lines.append(line)


            line_splited = line_stripped.split()
            if(len(line_splited) >= 2):
                correted_lines.append(line)

    with open(file=file_path, mode='w', encoding='utf-8') as f2:
        f2.writelines(correted_lines)

def count_entities(file_path):

    # Entidades esperadas
    entidades = ["NOME_EMPRESA", "PORTE", "SETOR", "FATURAMENTO", "LOCALIZACAO", "QTD_FUNCIONARIOS"]
    
    # Inicializa o dicionário com zero
    contagem = defaultdict(int)

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # ignora linhas vazias
            parts = line.split()
            if len(parts) >= 2:
                tag = parts[-1]  # última coluna é a tag (supondo token[TAB]tag ou token [espaço] tag)
                if tag.startswith("B-"):
                    entidade = tag[2:]
                    if entidade in entidades:
                        contagem[entidade] += 1

    return dict(contagem)


def main():
    # Se quiser obter todos os dados -> fine_tuning do modelo do 0
    data = pd.concat([get_df_from_dataset(), increment_dataset()])
    ## path to save the txt file.
    filepath = 'datasets/flair/train.txt'
    ## creating the file.
    create_data(data, filepath)
    remove_void_entities('datasets/flair/train.txt')
    split_train_file_stratified('datasets/flair/train.txt')
    entities_train = count_entities('datasets/flair/train.txt')
    entities_test = count_entities('datasets/flair/test.txt')
    entities_dev = count_entities('datasets/flair/dev.txt')

    print('======================================')
    print(f'Entidades treino {entities_train}')
    print(f'Entidades test {entities_test}')
    print(f'Entidades dev {entities_dev}')
    print('======================================')



if __name__ == '__main__':
    main()