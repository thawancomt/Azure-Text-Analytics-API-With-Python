from azure.ai.textanalytics import *
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from collections import namedtuple
from dotenv import load_dotenv, find_dotenv
import os

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
        try:
            text_analytics_client = TextAnalyticsClient(
                    endpoint=self.endpoint, 
                    credential=ta_credential)
            
        except:
            pass
        
        return text_analytics_client

    def __create_response(response):
        return [doc for doc in response if not doc.is_error]

    def GetSentiment(self) -> AnalyzeSentimentResult:
        response = self.client.analyze_sentiment(documents = [self.document])
        return [doc for doc in response if not doc.is_error]

    def GetEntities(self) -> RecognizeEntitiesResult:
        response = self.client.recognize_entities(documents=[self.document]) 
        return [doc for doc in response if not doc.is_error]
    
    def GetLinkedEntities(self) -> RecognizeLinkedEntitiesResult:
        response = self.client.recognize_linked_entities([self.document])
        return [doc for doc in response if not doc.is_error]
    
    def GetKeyPhrases(self) -> ExtractKeyPhrasesResult:
        response = self.client.extract_key_phrases([self.document])
        return [doc for doc in response if not doc.is_error]
    
    def GetLanguage(self) -> DetectLanguageResult:
        response = self.client.detect_language([self.document])
        return [doc for doc in response if not doc.is_error]
    
    def GetAllInformation(self) -> None:
        poller = self.client.begin_analyze_actions(documents=[self.document],
                                                   actions=self.all_analyses)
        result = poller.result()

        sentiment = []
        entities = []
        linked_entities = []
        key_phrases = []
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
                    key_phrases.append(doc)

        return Results(sentiment=sentiment, entities=entities, linked_entities=linked_entities, key_phrases=key_phrases, language=language)