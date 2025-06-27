import pandas as pd
import utils.word_service as ws
import csv;
import random
import utils.word_service as ws
import itertools
import utils.constants as cts
from utils.constants import estados_to_ufs, setores, sinonimos_empresa, sinonimos_setor, sinonimos_porte, sinonimos_funcionarios
from utils.cidades_nome_composto import cidades_nome_composto

# Seta seed para ter sempre a mesma saida no incremento, mudar a seed pode gerar novas frases
random.seed(cts.seed)

portes = ["grande", "medio", "pequeno", "micro"]
portes_plural = {
    'grande': 'grandes',
    'medio': 'medias',
    'pequeno': 'pequenas',
    'micro': 'micro'
}

MAX_FUNCIONARIOS = 9999
setores_utilizados = set(cts.setores)
nms_empresa = []
df_scheme = []



def carregar_setores_utilizados():    
    with open('./datasets/processed/setores_amigaveis.csv', 'r', encoding='utf-8') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            for celula in linha:
                setores = celula.split(",")
                for setor in setores:
                    setor = setor.strip()
                    if setor:
                        setores_utilizados.add(setor.lower()) 

def import_incremented_data():
    
    with open('./datasets/processed/incremented_data.csv', mode='r', encoding='utf-8') as processed_dataset:
        csv_reader = csv.reader(processed_dataset, delimiter=';', quotechar='"')
        next(csv_reader)  # pula o cabeçalho

        for row in csv_reader:
            razao_social  = ws.normalize_word(row[0])
            nm_empresa    = ws.normalize_word(row[1])
            setor         = ws.normalize_word(row[-1])  # última coluna
            setores_utilizados.add(setor.lower())

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

def increment_all_entities_randomly(estados_nome=None, p_setor=0, p_porte=0, p_estado=0, 
                                    p_funcionarios=0, p_faturamento=0, p_faixa_funcionarios=0.5,
                                    p_faixa_faturamento=0.5, p_abreviacao_faturamento=0.5, p_hifen_faixa=0.3):
    'Increment entities base on a percentace'
    
    for estado in estados_nome:
        for porte in portes:
            for setor in setores_utilizados:
                default_sentence = f'{sinonimos_empresa[random.randint(0, len(sinonimos_empresa)-1)]}'
                add_setor = 1 - random.random() <= p_setor
                add_porte = 1 - random.random() <= p_porte
                add_estado = 1 - random.random() <= p_estado
                add_funcionarios = 1 - random.random() <= p_funcionarios
                add_faturamento =  1- random.random() <= p_faturamento

                sentence = '' + default_sentence
                sentence_with_setor = ''
                sentence_with_porte = ''
                sentence_with_estado = ''
                sentence_with_funcionarios = ''
                sentence_with_faturamento = ''

                mapping = ['', []] # 0 - sentence 1 - Mapping

                if(add_setor):
                    sinonimo_setor = sinonimos_setor[random.randint(0, len(sinonimos_setor) - 1)]
                    possible_sentences = [f'{sinonimo_setor} {setor}', f'de {setor}']
                    sentence_with_setor += possible_sentences[random.randint(0,1)]
                    mapping[1].append((setor.lower(), 'SETOR'))

                if(add_porte):
                    sinonimo_porte = sinonimos_porte[random.randint(0, len(sinonimos_porte) - 1)]
                    possible_sentences = [f'de {sinonimo_porte} {porte}', f'{porte}']
                    sentence_with_porte += possible_sentences[random.randint(0,1)]
                    mapping[1].append((porte.lower(), 'PORTE'))

                if(add_estado):
                    possible_sentences = [f'em {estado}', f'{estado}']
                    sentence_with_estado += possible_sentences[random.randint(0,1)]
                    mapping[1].append((estado.lower(), 'LOCALIZACAO'))

                if(add_funcionarios):
                    add_faixa_funcionarios = 1 - random.random() <= p_faixa_funcionarios
                    add_hyphen = 1 - random.random() <= p_hifen_faixa
                    if(add_faixa_funcionarios):
                        faixa_de = random.randint(1, int(MAX_FUNCIONARIOS/2))
                        faixa_ate = random.randint((faixa_de + 1), MAX_FUNCIONARIOS)
                        sentence_with_funcionarios += f'{faixa_de}-{faixa_ate}' if add_hyphen else f'{faixa_de} ate {faixa_ate}'
                        mapping[1].append((sentence_with_funcionarios, 'QTD_FUNCIONARIOS'))
                    else:
                        qtd_funcionarios = random.randint(1, MAX_FUNCIONARIOS)
                        sentence_with_funcionarios += f'{qtd_funcionarios}'
                        mapping[1].append((str(qtd_funcionarios), 'QTD_FUNCIONARIOS'))

                    sentence_with_funcionarios = f'com {sentence_with_funcionarios} {sinonimos_funcionarios[random.randint(0, len(sinonimos_funcionarios) -1)]}'
                
                if(add_faturamento):
                    add_faixa_faturamento = 1 - random.random() <= p_faixa_faturamento
                    add_faturamento_abreviation = 1 - random.random() <= p_abreviacao_faturamento
                    abreviations = list(cts.faturamento_faixa.keys())
                    sinonimo_faturamento = cts.sinonimos_faturamento[random.randint(0, len(cts.sinonimos_faturamento) - 1)]
                    if(add_faixa_faturamento):
                        add_hyphen = 1 - random.random() <= p_hifen_faixa
                        faturamento_de = random.randint(1, 500)
                        faturamento_ate = random.randint(faturamento_de, 999)
                        if(add_faturamento_abreviation):
                            abreviation = abreviations[random.randint(0, len(abreviations) - 1)]
                            sentence_with_faturamento_aux = f'{faturamento_de}-{faturamento_ate} {abreviation}' if add_hyphen else f'{faturamento_de} ate {faturamento_ate} {abreviation}'
                            sentence_with_faturamento = f'com {sinonimo_faturamento} de {sentence_with_faturamento_aux}'    
                            mapping[1].append((sentence_with_faturamento_aux, 'FATURAMENTO'))
                        else:
                            faturamento_adjust1 = cts.faturamento_faixa[abreviations[random.randint(0, len(abreviations) -1)]]
                            faturamento_adjust2 = cts.faturamento_faixa[abreviations[random.randint(0, len(abreviations) -1)]]
                            faturamento_de *= faturamento_adjust2 if faturamento_adjust2 < faturamento_adjust1 else faturamento_adjust1
                            faturamento_ate *= faturamento_adjust2 if faturamento_adjust2 > faturamento_adjust1 else faturamento_adjust1
                            sentence_with_faturamento_aux = f'{faturamento_de}-{faturamento_ate}' if add_hyphen else f'{faturamento_de} ate {faturamento_ate}'
                            sentenceWithFaturamento = f'com {sinonimo_faturamento} de {sentence_with_faturamento_aux}'
                            mapping[1].append((sentence_with_faturamento_aux, 'FATURAMENTO'))

                    else:
                        random_number = random.randint(1,999)
                        abreviation = abreviations[random.randint(0, len(abreviations) - 1)]
                        faturamento = f'{random_number} {abreviation}' if add_faturamento_abreviation else random_number * cts.faturamento_faixa[abreviation]
                        sentence_with_faturamento = f'com {sinonimo_faturamento} de {faturamento}'
                        mapping[1].append((str(faturamento), 'FATURAMENTO'))
                                            
                parts = [sentence_with_estado, sentence_with_setor, sentence_with_porte, sentence_with_funcionarios, sentence_with_faturamento]

                # Gera todas as permutações possíveis das partes
                permutations = list(itertools.permutations(parts))

                # Monta as frases finais com sentence no início
                possible_final_sentences = [f"{sentence} {' '.join(p)}" for p in permutations]
                index_sentence_chosen = random.randint(0, len(possible_final_sentences) - 1)
                mapping[0] = possible_final_sentences[index_sentence_chosen].lower()
                df_scheme.append(mapping)

def increment_dataset():
    import_incremented_data()
    carregar_setores_utilizados()
    estados_nome = list(cts.estados_to_ufs.keys())
    estados_uf = list(cts.estados_to_ufs.values())
        
    # Empresa + estado nome + porte + setor
    permutate_estado_setor_porte(estados_nome)    
    # Empresa + estado uf + porte + setor
    permutate_estado_setor_porte(estados_uf)    
    # Empresa + nome cidade composto + porte + setor

    # Funcionarios
    increment_all_entities_randomly(cidades_nome_composto[151:200], p_funcionarios=1, p_faturamento=0.5, p_setor=0.5, p_porte=0.5, p_estado=0.5)
    increment_all_entities_randomly(estados_uf, p_funcionarios=1, p_faturamento=0.5, p_setor=0.5, p_porte=0.5, p_estado=0.5)

    # Faturamento
    increment_all_entities_randomly(cidades_nome_composto[201:350], p_faturamento=1, p_funcionarios=0.5, p_setor=0.5, p_porte=0.5, p_estado=0.5)
    increment_all_entities_randomly(estados_nome, p_faturamento=1, p_funcionarios=0.5, p_setor=0.5, p_porte=0.5, p_estado=0.5)

    incremented_df = pd.DataFrame(df_scheme, columns=['text', 'annotation'])
    return incremented_df
