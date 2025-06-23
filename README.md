# Requisitos
- poetry instalado na máquina local
- Recomendação de OS Linux Ubuntu 22.04

# Diretórios
|- datasets
    |- flair ( Datasets que efetivamente serão utilizados no train, dev e test do modelo.)
    |- processed ( Datasets que constituirão o dataset final .txt do flair - já pre-processados.)
    |- raw  ( Datasets  vindos do banco de dados da Econodata estão no .gitignore por privacidade )
    |- old  ( Datasets utilizados em treinamentos anteriors)
        |- __timestamp__  (dia/hora do último treinamento utilizando o dataset)
        ...
|- resources ( Modelos utilizados para o finetuning ) 
    |- taggers
    |- __modelo__
|- src
    |- b2ner ( Onde é chamado a função de treinamento do flair e o "chat" para tagging de frases pós treino)
    |- dataset_converter ( Pré-processamento do dataset, incrementação do dataset e criação dos arquivos do flair)
    |- utils ( Constantes, services de auxílio a classificação do dataset )