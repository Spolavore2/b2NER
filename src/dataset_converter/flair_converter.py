# convert from an df in a specific struct to .txt usable by flair
import pandas as pd
from tqdm import tqdm
from dataset_converter.dataset_preprocessing import get_df_from_dataset
from dataset_converter.increment_dataset import increment_dataset
from dataset_converter.increment_dataset import increment_funcionarios_entity
from difflib import SequenceMatcher
import re
import pickle

def matcher(string, pattern):
    '''
    Return the start and end index of any pattern present in the text.
    '''
    match_list = []
    pattern = pattern.strip()
    seqMatch = SequenceMatcher(None, string, pattern, autojunk=False)
    match = seqMatch.find_longest_match(0, len(string), 0, len(pattern))
    if (match.size == len(pattern)):
        start = match.a
        end = match.a + match.size
        match_tup = (start, end)
        string = string.replace(pattern, "X" * len(pattern), 1)
        match_list.append(match_tup)
        
    return match_list, string

def mark_sentence(s, match_list):
    '''
    Marks all the entities in the sentence as per the BIO scheme. 
    '''
    word_dict = {}
    for word in s.split():
        word_dict[word] = 'O'
        
    for start, end, e_type in match_list:
        temp_str = s[start:end]
        tmp_list = temp_str.split()
        if len(tmp_list) > 1:
            word_dict[tmp_list[0]] = 'B-' + e_type
            for w in tmp_list[1:]:
                word_dict[w] = 'I-' + e_type
        else:
            word_dict[temp_str] = 'B-' + e_type
    return word_dict


def clean(text):
    '''
    Removes only the dot (.) and normalizes multiple spaces.
    '''
    # Remove all dots
    text_no_dot = text.replace('.', '')
    
    # Normalize multiple spaces to a single space
    return re.sub(r'\s+', ' ', text_no_dot.strip())

def create_data(df, filepath):
    '''
    The function responsible for the creation of data in the said format.
    '''
    with open(filepath , 'w') as f:
        for text, annotation in zip(df.text, df.annotation):
            text_ = text        
            match_list = []
            for i in annotation:
                a, text_ = matcher(text, i[0])
                if(len(a) == 0):
                    continue
                match_list.append((a[0][0], a[0][1], i[1]))

            d = mark_sentence(text, match_list)

            for i in d.keys():
                f.writelines(i + ' ' + d[i] +'\n')
            f.writelines('\n')

import random

def split_train_file(file_path, dev_ratio=0.1, test_ratio=0.1):
    # Lê todo o conteúdo do train.txt
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().strip().split('\n\n')

    # Shuffle data to get randow data for each set
    random.shuffle(data)

    # Calculate the lenght of each set
    total = len(data)
    dev_size = int(total * dev_ratio)
    test_size = int(total * test_ratio)

    # Create Splits
    dev_data = data[:dev_size]
    test_data = data[dev_size:dev_size + test_size]
    train_data = data[dev_size + test_size:]

    # Write news files
    with open(file_path.replace('train.txt', 'train.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(train_data))

    with open(file_path.replace('train.txt', 'dev.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(dev_data))

    with open(file_path.replace('train.txt', 'test.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(test_data))

    print(f"Total de exemplos: {total}")
    print(f"Tamanho treino: {len(train_data)}")
    print(f"Tamanho dev: {len(dev_data)}")
    print(f"Tamanho teste: {len(test_data)}")
    print("Divisão concluída!")


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


def main():
    # Se quiser obter todos os dados -> fine_tuning do modelo do 0
    # data = pd.concat([get_df_from_dataset(), increment_dataset()])

    # Se quiser aumentar a quantidade de dado da entidade funcionarios
    data = increment_funcionarios_entity()
    ## path to save the txt file.
    filepath = 'datasets/flair/train.txt'
    ## creating the file.
    create_data(data, filepath)
    remove_void_entities('datasets/flair/train.txt')
    split_train_file('datasets/flair/train.txt')

if __name__ == '__main__':
    main()