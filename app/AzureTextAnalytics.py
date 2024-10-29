from azure.ai.textanalytics import *
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from collections import namedtuple
from dotenv import load_dotenv
import os
from DTO import *

load_dotenv()

default_text_test = """
I have been in the beach this morning.
There were warm and comfortable, I love that place.
I took 2 balls to the beach and played with another unknown peoples that was there.
I've has just 2 dollar on my bucket to spent.

beach is good"""


Results = namedtuple('Results', ['sentiment', 'entities', 'linked_entities', 'key_phrases', 'language'])
textos = [
    "O aprendizado de máquina tem sido amplamente utilizado em várias áreas, incluindo saúde, finanças, e comércio eletrônico. Com o uso de modelos preditivos, é possível tomar decisões mais informadas e automatizar processos que antes dependiam exclusivamente da intervenção humana.",
    
    "A programação em Python oferece diversas bibliotecas para manipulação de dados e automação de tarefas repetitivas. Por meio de frameworks como Flask e Django, é possível criar aplicações web robustas e escaláveis de maneira relativamente simples, facilitando o desenvolvimento de novas funcionalidades.",
    
    "A análise de dados é uma etapa crucial no processo de tomada de decisões em muitas empresas. Ferramentas como o Pandas e o NumPy facilitam a manipulação e o tratamento de grandes volumes de dados, possibilitando a criação de relatórios e dashboards que ajudam a identificar tendências importantes.",
    
    "Com o avanço da tecnologia, o uso de inteligência artificial e aprendizado de máquina tem se tornado cada vez mais comum em várias indústrias. Estes sistemas ajudam a otimizar processos, reduzir custos operacionais, e aumentar a eficiência na execução de diversas tarefas rotineiras.",
    
    "O desenvolvimento ágil tem ganhado popularidade no mundo da tecnologia, especialmente devido à sua abordagem flexível e iterativa. Esse método permite que as equipes de desenvolvimento entreguem software de qualidade de forma rápida, respondendo de maneira eficaz às mudanças nos requisitos do projeto.",
    
    "A criação de APIs é uma prática essencial para integrar diferentes sistemas e compartilhar dados entre eles. Usando protocolos como REST e ferramentas como o Flask-RESTful, é possível estruturar a comunicação entre serviços e garantir a escalabilidade das soluções.",
    
    "As redes neurais artificiais são modelos computacionais inspirados no cérebro humano e têm sido aplicadas em diversas áreas, como reconhecimento de voz e imagem, tradução automática e detecção de fraudes. Esses modelos aprendem a partir de grandes conjuntos de dados, ajustando seus parâmetros de acordo com o feedback recebido.",
    
    "O desenvolvimento de software exige não apenas conhecimentos técnicos, mas também uma boa comunicação entre os membros da equipe. Métodos como Scrum e Kanban ajudam a organizar as tarefas e garantem que todos estejam alinhados com os objetivos do projeto, promovendo uma entrega mais eficiente.",
    
    "O uso de contêineres em ambientes de produção tem se tornado uma prática comum, principalmente com a popularização do Docker. Essa tecnologia permite o empacotamento de aplicações em um ambiente isolado, garantindo que todas as dependências estejam incluídas e facilitando o processo de deploy em diferentes servidores.",
    
    "O avanço da computação em nuvem tem possibilitado a criação de arquiteturas mais flexíveis e escaláveis. Serviços como o Azure e o AWS oferecem uma variedade de ferramentas que permitem a construção de soluções que se adaptam rapidamente às necessidades do mercado e à demanda dos usuários.",
    
    "A segurança da informação é um aspecto crucial no desenvolvimento de sistemas, especialmente quando lidamos com dados sensíveis. Práticas como criptografia, autenticação multifator e controle de acesso são fundamentais para garantir que informações confidenciais sejam protegidas contra acessos não autorizados.",
    
    "O uso de bancos de dados relacionais é amplamente difundido, mas com o aumento do volume de dados, os bancos NoSQL têm ganhado destaque. Eles oferecem uma maior flexibilidade na modelagem dos dados e são capazes de lidar melhor com grandes quantidades de informações em tempo real.",
    
    "A otimização de código é uma prática essencial para garantir o bom desempenho de sistemas de grande escala. Técnicas como cacheamento, paralelismo e algoritmos eficientes são usadas para reduzir o tempo de processamento e o consumo de recursos computacionais, melhorando a experiência do usuário final.",
    
    "A interface do usuário desempenha um papel crucial na experiência do usuário em qualquer aplicativo. Ferramentas como o Tailwind CSS ajudam os desenvolvedores a criar interfaces modernas e responsivas, garantindo que as aplicações sejam acessíveis em diferentes dispositivos e resoluções de tela.",
    
    "Os testes automatizados são uma etapa importante no desenvolvimento de software, pois garantem que as funcionalidades criadas funcionem conforme o esperado. O uso de frameworks como PyTest e unittest facilita a criação de testes unitários e de integração, reduzindo o risco de bugs em produção."
]


class AzureTextAnalyticsApi:
    def __init__(self, document  : str = None ) -> None:
        self.__credential = os.getenv('KEY')
        self.endpoint = os.getenv('ENDPOINT')

        self.client : TextAnalyticsClient = self.__create_authenticated_client()

        self.document = document
        self.all_analyses = (AnalyzeSentimentAction(),
                             RecognizeEntitiesAction(),
                             RecognizeLinkedEntitiesAction(),
                             ExtractKeyPhrasesAction())
        
    def __create_authenticated_client(self) -> TextAnalyticsClient:
        """
        Create a TextAnalyticsClient
        """
        ta_credential = AzureKeyCredential(self.__credential)
        text_analytics_client = TextAnalyticsClient(
                    endpoint=self.endpoint,
                    credential=ta_credential)

        return text_analytics_client

    def GetSentiment(self, data = None) -> SentencesResponseDTO:
        response = self.client.analyze_sentiment(documents = self.document)
        import time
        time.sleep(10)
        sentiments = [doc for doc in  response if not doc.is_error]

        response = SentencesResponseDTO([Sentences(text=sentence.text,
                                              sentiment_name=sentence.sentiment,
                                              confidence=max(sentence.confidence_scores.positive, sentence.confidence_scores.neutral, sentence.confidence_scores.negative),
                                              offset=sentence.offset) for sentence in sentiments[0].sentences]) if len(sentiments) else None
        
        if response:
            response.sentiment_name = sentiments[0].sentiment

        return response

    def GetEntities(self, data = None) -> EntitiesResponseDTO:
        response = self.client.recognize_entities(documents=[self.document])
        entities =  [doc for doc in  response if not doc.is_error]

        response = EntitiesResponseDTO(EntityDTO(entity_name=entity.text,
                                             category=entity.category,
                                             subcategory=entity.subcategory,
                                             offset=entity.offset,
                                             confidence=entity.confidence_score) for entity in entities[0].entities) if len(entities) else []
        
        return response
    
    def GetLinkedEntities(self, data = None) -> RecognizeLinkedEntitiesResult:
        response = self.client.recognize_linked_entities([self.document])
        linked_entities = [doc for doc in  response if not doc.is_error]

        response = LinkedEntitiesResponseDTO(LinkedEntitiesDTO(name=entity.name,
                                                           url=entity.url,
                                                           data_source=entity.data_source,
                                                           matches=[MatchesDTO(text=entity.matches[0].text,
                                                                               confidence_score=entity.matches[0].confidence_score)])
                                                           for entity in linked_entities[0].entities) if len(linked_entities) else []
        
        return response
    
    def GetKeyPhrases(self, data = None) -> ExtractKeyPhrasesResult:
        response = self.client.extract_key_phrases([self.document])
        key_phrases = [doc for doc in  response if not doc.is_error]

        return TagsResponseDTO([Tags(name=tag) for tag in key_phrases[0].key_phrases]) if len(key_phrases) else []
    
    def GetLanguage(self, data = None) -> LanguageResponseDTO:
        response = self.client.detect_language([self.document])
        return [LanguageDTO(name=doc.primary_language.name) for doc in response if not doc.is_error][0] if len(response) else []
    
    def GetAllInformation(self) -> Results:
        poller = self.client.begin_analyze_actions(documents=[self.document],
                                                   actions=self.all_analyses)
        result = poller.result()

        sentiment = None
        entities = None
        linked_entities = None
        key_phrases = 0
        language = None

        for action_result in result:
            for doc in action_result:
                if isinstance(doc, AnalyzeSentimentResult):
                    sentiment = SentencesResponseDTO(sentences=[Sentences(text=sentence.text, sentiment_name=sentence.sentiment,
                                                                          confidence=max(sentence.confidence_scores.positive, sentence.confidence_scores.negative, sentence.confidence_scores.neutral),
                                                                          offset=sentence.offset) for sentence in doc.sentences],
                                                                          sentiment_name=doc.sentiment,
                                                                          sentiment_confidance=max(doc.confidence_scores.positive, doc.confidence_scores.negative, doc.confidence_scores.neutral))
                
                if isinstance(doc, ExtractKeyPhrasesResult):
                    key_phrases = TagsResponseDTO(tags=[Tags(name=tag) for tag in doc.key_phrases])

                
                if isinstance(doc, RecognizeEntitiesResult):
                    entities = EntitiesResponseDTO(entities=[EntityDTO(entity_name=entity.text,
                                                                       category=entity.category,
                                                                       subcategory=entity.subcategory,
                                                                       offset=entity.offset,
                                                                       confidence=entity.confidence_score) for entity in doc.entities])
                
                if isinstance(doc, RecognizeLinkedEntitiesResult):
                    linked_entities = LinkedEntitiesResponseDTO([LinkedEntitiesDTO(name=linked_entity.name,
                                                                                   data_source=linked_entity.data_source,
                                                                                   url=linked_entity.url,
                                                                                   matches=MatchesDTO(text=linked_entity.matches[0].text,
                                                                                                      confidence_score=linked_entity.matches[0].confidence_score)
                                                                                                      )
                                                                                                        for linked_entity in  doc.entities])


        return Results(sentiment=sentiment, entities=entities, linked_entities=linked_entities, key_phrases=key_phrases, language=language)
