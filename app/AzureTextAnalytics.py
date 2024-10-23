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


class AzureTextAnalyticsApi:
    def __init__(self, document  : str = default_text_test) -> None:
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
        response = self.client.analyze_sentiment(documents = [self.document])
        sentiments = [doc for doc in  response if not doc.is_error]

        response = SentencesResponseDTO(Sentences(text=sentence.text,
                                              sentiment_name=sentence.sentiment,
                                              confidence=max(sentence.confidence_scores.positive, sentence.confidence_scores.neutral, sentence.confidence_scores.negative),
                                              offset=sentence.offset) for sentence in sentiments[0].sentences) if len(sentiments) else None
        
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
        key_phrases = [doc for doc in  data]

        return TagsResponseDTO([Tags(name=tag) for tag in key_phrases.key_phrases]) if len(key_phrases) else []
    
    def GetLanguage(self, data = None) -> LanguageResponseDTO:
        response = self.client.detect_language([self.document])
        return [LanguageDTO(name=doc.primary_language.name) for doc in response if not doc.is_error][0] if len(response) else []
    
    def GetAllInformation(self) -> Results:
        poller = self.client.begin_analyze_actions(documents=[self.document],
                                                   actions=self.all_analyses)
        result = poller.result()

        sentiment = []
        entities = []
        linked_entities = []
        key_phrases = 0
        language = self.GetLanguage()

        for action_result in result:
            for doc in action_result:
                if isinstance(doc, AnalyzeSentimentResult):
                    sentiment.append(doc)
                elif isinstance(doc, RecognizeEntitiesResult):
                    entities.append(doc)
                elif isinstance(doc, RecognizeLinkedEntitiesResult):
                    linked_entities.append(doc)
                elif isinstance(doc, ExtractKeyPhrasesResult):
                    key_phrases = self.GetKeyPhrases(doc)

        return Results(sentiment=sentiment, entities=entities, linked_entities=linked_entities, key_phrases=key_phrases, language=language)