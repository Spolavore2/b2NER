from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from transformers import AutoTokenizer  # necessário para contar subtokens

def main(model_to_train="neuralmind/bert-base-portuguese-cased", name_model="ner-bertimbau"):
    columns = {0: 'text', 1: 'ner'}
    data_folder = 'datasets/flair/'

    corpus: Corpus = ColumnCorpus(data_folder, columns,
                                   train_file='train.txt',
                                   test_file='test.txt',
                                   dev_file='dev.txt')

    # Usa o tokenizer do modelo BERTimbau
    tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")
    MAX_SUBTOKENS = 512

    def filter_sentences(sentences):
       filtered = []
       for sentence in sentences:
           text = sentence.to_tokenized_string()
           subtoken_ids = tokenizer.encode(text, add_special_tokens=True)
           if len(subtoken_ids) <= MAX_SUBTOKENS:
               filtered.append(sentence)
       return filtered

    # Aplica o filtro nas três divisões
    corpus._train = filter_sentences(corpus.train)
    corpus._dev = filter_sentences(corpus.dev)
    corpus._test = filter_sentences(corpus.test)

    tag_dictionary = corpus.make_label_dictionary(label_type='ner')

    embeddings = TransformerWordEmbeddings(
        model=model_to_train,
        layers="-1",
        subtoken_pooling="first",
        fine_tune=True,
        use_context=False,
    )

    tagger = SequenceTagger(hidden_size=128,
                            embeddings=embeddings,
                            tag_dictionary=tag_dictionary,
                            tag_type='ner',
                            use_crf=True)

    trainer = ModelTrainer(tagger, corpus)

    trainer.train(f'resources/taggers/{name_model}',
                  learning_rate=2e-4,
                  mini_batch_size=16,
                  max_epochs=10)

if __name__ == '__main__':
    main()
