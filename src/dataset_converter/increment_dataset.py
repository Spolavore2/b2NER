import pandas as pd
import utils.word_service as ws
import csv;
import random
import utils.word_service as ws
import itertools
from utils.constants import estados_to_ufs, setores, sinonimos_empresa, sinonimos_setor, sinonimos_porte, sinonimos_funcionarios
from utils.cidades_nome_composto import cidades_nome_composto

portes = ["grande", "medio", "pequeno", "micro"]
portes_plural = {
    'grande': 'grandes',
    'medio': 'medias',
    'pequeno': 'pequenas',
    'micro': 'micro'
}

MAX_FUNCIONARIOS = 9999
setores_utilizados = setores
nms_empresa = []
df_scheme = []

def import_incremented_data():
    setores_utilizados = set()

    with open('./datasets/processed/incremented_data.csv', mode='r', encoding='utf-8') as processed_dataset:
        csv_reader = csv.reader(processed_dataset, delimiter=';', quotechar='"')
        next(csv_reader)  # pula o cabeçalho

        for row in csv_reader:
            razao_social  = ws.normalize_word(row[0])
            nm_empresa    = ws.normalize_word(row[1])
            setor         = ws.normalize_word(row[-1])  # última coluna
            setores_utilizados.add(setor)

            if not razao_social:
                nms_empresa.append(nm_empresa)
            else:
                nms_empresa.append(razao_social)

def permutate_estado_setor_porte(estados_list: list):
    for estado in estados_list:
        for porte in portes:
            for setor in setores:
                default_sentence = f'{sinonimos_empresa[random.randint(0, len(sinonimos_empresa)-1)]} '
                add_setor_word = random.random() > 0.7
                add_port_word = random.random() > 0.7
                add_setor_first = random.random() > 0.5
                add_nm_empresa = random.random() > 0.6
                sinonimo_porte = sinonimos_porte[random.randint(0, len(sinonimos_porte) - 1)]
                sinonimo_setor = sinonimos_setor[random.randint(0, len(sinonimos_setor) - 1)]
                porte_formated = porte if add_port_word else portes_plural[porte]
                sentenceAux = ' '

                if add_setor_first:
                    sentenceAux += f'{sinonimo_setor} de {setor}' if add_setor_word else f'de {setor}'
                    sentenceAux += f' de {sinonimo_porte} {porte_formated}' if add_port_word else f' {porte_formated}'
                else:
                    sentenceAux += f'de {sinonimo_porte} {porte_formated}' if add_port_word else f'{porte_formated}'
                    sentenceAux += f' {sinonimo_setor} de {setor}' if add_setor_word else f' de {setor}'

                add_em_in_beggining = random.random() > 0.5
                sentence = '' + default_sentence
                
                # Adiciona o nome de um empresa aleatoriamente
                if add_nm_empresa:
                    nm_empresa = nms_empresa[random.randint(0, len(nms_empresa) - 1)]
                    add_nm_empresa_beggining =  random.random() > 0.5
                    add_chamada_word = random.random() > 0.5
                    if add_chamada_word:
                        if(add_nm_empresa_beggining):
                            sentence += f' chamada {nm_empresa} '
                            sentence += f'em {estado} {sentenceAux}' if add_em_in_beggining else f'{sentenceAux} em {estado}'
                        else:
                            sentence += f'em {estado} {sentenceAux}' if add_em_in_beggining else f'{sentenceAux} em {estado}'
                            sentence += f' chamada {nm_empresa}'
                    else:
                        sentence += f'{nm_empresa} '
                        sentence += f'em {estado} {sentenceAux}' if add_em_in_beggining else f'{sentenceAux} em {estado}'

                    df_scheme.append([sentence.lower(), [(estado.lower(), 'LOCALIZACAO'), (porte_formated, 'PORTE'), (setor.lower(), 'SETOR'), (nm_empresa, 'NOME_EMPRESA')]])
                else:
                    sentence += f'em {estado} {sentenceAux}' if add_em_in_beggining else f'{sentenceAux} em {estado}'
                    df_scheme.append([sentence.lower(), [(estado.lower(), 'LOCALIZACAO'), (porte_formated, 'PORTE'), (setor.lower(), 'SETOR')]])

def increment_funcionarios_entity(estados_nome=None):
    if(not estados_nome):
        estados_nome = list(estados_to_ufs.keys())

    for estado in estados_nome:
        for porte in portes:
            for setor in setores_utilizados:
                default_sentence = f'{sinonimos_empresa[random.randint(0, len(sinonimos_empresa)-1)]}'
                add_setor = random.random() > 0.5
                add_porte = random.random() > 0.5
                sinonimo_porte = sinonimos_porte[random.randint(0, len(sinonimos_porte) - 1)]
                sinonimo_setor = sinonimos_setor[random.randint(0, len(sinonimos_setor) - 1)]
                add_estado = random.random() > 0.5
                add_faixa = random.random() > 0.5
                sentence = '' + default_sentence
                sentenceWithSetor = ''
                sentenceWithPorte = ''
                sentenceWithEstado = ''
                sentenceWithFuncionarios = ''
                mapping = ['', []] # 0 - sentence 1 - Mapping

                if(add_setor):
                    possible_sentences = [f'{sinonimo_setor} {setor}', f'de {setor}']
                    sentenceWithSetor += possible_sentences[random.randint(0,1)]
                    mapping[1].append((setor.lower(), 'SETOR'))

                if(add_porte):
                    possible_sentences = [f'de {sinonimo_porte} {porte}', f'{porte}']
                    sentenceWithPorte += possible_sentences[random.randint(0,1)]
                    mapping[1].append((porte.lower(), 'PORTE'))

                if(add_estado):
                    possible_sentences = [f'em {estado}', f'{estado}']
                    sentenceWithEstado += possible_sentences[random.randint(0,1)]
                    mapping[1].append((estado.lower(), 'LOCALIZACAO'))

                if(add_faixa):
                    faixa_de = random.randint(1, int(MAX_FUNCIONARIOS/2))
                    faixa_ate = random.randint((faixa_de + 1), MAX_FUNCIONARIOS)
                    sentenceWithFuncionarios += f'{faixa_de} ate {faixa_ate}'
                    mapping[1].append((str(faixa_de), 'QTD_FUNCIONARIOS'))
                    mapping[1].append((str(faixa_ate), 'QTD_FUNCIONARIOS'))
                else:
                    qtd_funcionarios = random.randint(1, MAX_FUNCIONARIOS)
                    sentenceWithFuncionarios += f'{qtd_funcionarios}'
                    mapping[1].append((str(qtd_funcionarios), 'QTD_FUNCIONARIOS'))

                sentenceWithFuncionarios = f'com {sentenceWithFuncionarios} {sinonimos_funcionarios[random.randint(0, len(sinonimos_funcionarios) -1)]}'
                partes = [sentenceWithEstado, sentenceWithSetor, sentenceWithPorte, sentenceWithFuncionarios]

                # Gera todas as permutações possíveis das partes
                permutacoes = list(itertools.permutations(partes))

                # Monta as frases finais com sentence no início
                possible_final_sentences = [f"{sentence} {' '.join(p)}" for p in permutacoes]
                index_sentence_chosen = random.randint(0, len(possible_final_sentences) - 1)
                mapping[0] = possible_final_sentences[index_sentence_chosen].lower()
                df_scheme.append(mapping)

def increment_dataset():
    import_incremented_data()
    estados_nome = list(estados_to_ufs.keys())
    estados_uf = list(estados_to_ufs.values())

    default_sentence = f'{sinonimos_empresa[random.randint(0, len(sinonimos_empresa)-1)]} '

    # Empresas + porte
    for porte in portes:
        sentence1 = default_sentence + "de porte "  + porte
        sentence2 = default_sentence + "com porte "  + porte

        df_scheme.append([sentence1.lower(), [(porte.lower(), 'PORTE')]])
        df_scheme.append([sentence2.lower(), [(porte.lower(), 'PORTE')]])
        
    # Empresa + estado nome + porte + setor
    permutate_estado_setor_porte(estados_nome)    
    # Empresa + estado uf + porte + setor
    permutate_estado_setor_porte(estados_uf)    
    # Empresa + nome cidade composto + porte + setor
    permutate_estado_setor_porte(cidades_nome_composto[0:150])

    increment_funcionarios_entity(estados_nome)

    # Empresa + setor
    for setor in setores:
        add_setor_word = random.random() > 0.5
        sentence = default_sentence 
        sentence += "no setor de " if add_setor_word else "de "
        sentence += setor
        df_scheme.append([sentence.lower(), [(setor.lower(), 'SETOR')]])

        
    incremented_df = pd.DataFrame(df_scheme, columns=['text', 'annotation'])
    return incremented_df
