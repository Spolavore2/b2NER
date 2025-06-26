from flair.data import Sentence
from flair.models import SequenceTagger
import utils.word_service as ws



model = SequenceTagger.load('resources/taggers/ner-bertimbau/final-model.pt')
print('Busque uma empresa: Exemplo -> Empresas em santa catarina com porte X no setor Y que se chamam Z')
while True:
    inputado = input('> ')
    if(inputado == 'exit'):
      break
    
    inputado = ' '.join(ws.normalize_spaces(p) for p in inputado.split())

    sentence = Sentence(inputado)
    model.predict(sentence)
    print(sentence.to_tagged_string())