import csv;
import json;
import pandas as pd
import utils.word_service as ws
from utils.constants import estados_to_ufs, ufs_to_estados, estados_compostos, space_demarker
from utils.cidades_nome_composto import cidades_nome_composto

def filter_json_attributes(json):
    default_qtd_funcionarios_ate = 999999999 # default value when the filter is not mapped in the dataset
    default_faturamento_ate = 999999999999999 # default value when the filter is not mapped in the dataset
    new_json = {
        "ufs": ws.normalize_word(json["ufs"]),
        "cidades": ws.normalize_word(json["cidades"]),
        "portes": ws.normalize_word(json["portes"]),
        "qtd_funcionarios_de": ws.normalize_word(json["qtd_funcionarios_de"]) if json["qtd_funcionarios_de"] != 0 else None ,
        "qtd_funcionarios_ate": ws.normalize_word(json["qtd_funcionarios_ate"]) if json["qtd_funcionarios_ate"] != default_qtd_funcionarios_ate else None,
        "faturamento_de": ws.normalize_word(json["faturamento_de"]) if json["faturamento_de"] != 0 else None ,
        "faturamento_ate": ws.normalize_word(json["faturamento_ate"]) if json["faturamento_ate"] != default_faturamento_ate else None,
        "nome_empresa": [] if "palavraChave" not in json else ws.normalize_word(json["palavraChave"]),
        "setor": ws.normalize_word(json["setoresAmigaveis"]),
    }
    return new_json

# raw dataset -> normalized & reduced dataset
def pre_process_dataset():
    new_rows = [["prompt", "json"]]
    compound_names = estados_compostos + cidades_nome_composto
    with open('./datasets/raw/econodata_prompt_response_json.csv', mode='r', encoding='utf-8') as dataset :
        csv_reader = csv.reader(dataset)
        next(csv_reader)
        for row in csv_reader:
            prompt,json_mapping = row[0], json.loads(row[1])
            new_rows.append([ws.mark_compound_names(ws.normalize_word(prompt),compound_names), json.dumps(filter_json_attributes(json_mapping))])

    with open('./datasets/processed/econodata_prompt_response_json.csv',  mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(new_rows)



def is_location_present(word: str,comp: list):
    word_upper = word.upper()
    t1 = False if word_upper not in estados_to_ufs else ws.is_word_present(estados_to_ufs[word_upper].lower(), comp)
    t2 = False if word_upper not in ufs_to_estados else ws.is_word_present(ufs_to_estados[word_upper].lower(),comp)
    t3 = word in comp
    return t1 or t2 or t3

# processed dataset -> df specified by flair.doc
def get_df_from_dataset():
    entities = ['ufs', 'cidades', 'setor', 'nome_empresa',  'portes', 'faturamento_de', 
                'faturamento_ate', 'qtd_funcionarios_de', 'qtd_funcionarios_ate']
    # incrementing those var's to know how much data ( ground_truth ) we have in which of them
    r_ufs = r_cidades = r_nome_empresa = r_setor = r_portes  = r_funcionarios = r_faturamento = 0
    df_scheme = [] # index 0 - prompt ; index 1 - list of tuples with word and entity mapped (EX: ['i love horses', [(horses, Animal)]])

    with open('./datasets/processed/econodata_prompt_response_json.csv', mode='r', encoding='utf-8') as processed_dataset:
        csv_reader = csv.reader(processed_dataset)
        next(csv_reader)
        for idx_row, row  in enumerate(csv_reader):
            sentence_without_demarker = ws.normalize_spaces(ws.remove_space_demarker(row[0], space_demarker).strip())
            df_scheme.append([sentence_without_demarker]) # <- prompt
            df_scheme[idx_row].append([]) # <- (Word, Entity)

            nome_empresa_already_added = False # since we already add the full company name when a word has a match, we just need one insertion
            words_already_added = []

            words_from_prompt = row[0].split(" ")
            entities_mapped = json.loads(row[1])
            for entity in entities:
                for word in words_from_prompt:
                    ground_truth = entities_mapped[entity]
                    word = ws.remove_space_demarker(word, space_demarker)

                    if(ground_truth == None or (isinstance(ground_truth, list) and len(ground_truth) == 0) or word in words_already_added):
                        continue

                    if(entity == 'ufs'):
                        if is_location_present(word, ground_truth):
                            wg_tuple = (word, 'LOCALIZACAO')
                            r_ufs += 1
                            df_scheme[idx_row][1].append(wg_tuple)
                            words_already_added.append(word)
                    elif(entity == 'cidades'):
                        if is_location_present(word, ground_truth):
                            wg_tuple = (word, 'LOCALIZACAO')
                            r_cidades += 1
                            df_scheme[idx_row][1].append(wg_tuple)
                            words_already_added.append(word)
                    elif(entity == "nome_empresa"):
                        if(not ws.is_stop_word(word) and ws.is_word_present(word, ground_truth) and not nome_empresa_already_added):
                            # In this case we use de ground_truth instead of the word
                            # to get the full name of the enterprise
                            nome_empresa_already_added = True
                            wg_tuple = (ground_truth[0], entity.upper())
                            r_nome_empresa += 1
                            df_scheme[idx_row][1].append(wg_tuple)
                            words_already_added.append(word)
                    elif (entity == "setor"):
                        steamed_word = ws.perform_stemming(word, "portuguese")
                        if(not ws.is_stop_word(steamed_word) and  ws.is_word_present(steamed_word, ground_truth) and ws.is_valid_setor(sentence_without_demarker, ground_truth)):
                            setor = ws.get_setor_from_word(word, sentence_without_demarker)
                            wg_tuple = (setor, "SETOR")
                            r_setor += 1
                            df_scheme[idx_row][1].append(wg_tuple)
                            words_already_added.append(word)
                            # Todo , pensar em uma maneira para detectar mais de uma palavra como setor
                    elif (entity ==  "portes"):
                        if(not ws.is_stop_word(word) and  ws.is_word_present(word, ground_truth)):
                            wg_tuple = (word, 'PORTE')
                            r_portes += 1
                            df_scheme[idx_row][1].append(wg_tuple)
                            words_already_added.append(word)
                    elif (entity == "qtd_funcionarios_de" or entity == "qtd_funcionarios_ate"):
                        if(not ws.is_stop_word(word) and  ws.is_word_present(word, str(ground_truth))):
                            wg_tuple = (word, "QTD_FUNCIONARIOS")
                            r_funcionarios += 1
                            df_scheme[idx_row][1].append(wg_tuple)
                            words_already_added.append(word)
                    # Todo, verificar se faz sentido utilizar Entidade de qtd_funcionarios e faturamento                

    df = pd.DataFrame(df_scheme, columns=['text', 'annotation'])
    df_filtered = df[df['annotation'].apply(lambda x: len(x) > 0)]
    return df_filtered