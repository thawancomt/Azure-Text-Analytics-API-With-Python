# Standart import
import os

# Third parties imports
from azure.ai.textanalytics import *
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from dotenv import load_dotenv

# Local imports
from DTO import *

# load the environment variables
# Make sure you have a .env file in the root directory of your project with all the necessary variables
# Documented on docs.md in the project root directory
load_dotenv()

# This class is a wrapper for the Azure Text Analytics API
class AzureTextAnalyticsApi:
    """
    A low level class to interact with Azure Text Analytics API through the Azure SDK
    
    Parameters:
        - document : str : The text to be analyzed

    All we need to use this class is the text to be analyzed, the class will take care of the rest.~
    Make sure you have the necessary environment variables set in your .env file

    Methods:
        - get_setiment : Get the sentiment of the text and it respective sentences
        - get_entities : Get the entities of the text
        - get_linked_entities : Get the linked entities of the text
        - get_key_phrases : Get the key phrases of the text
        - get_language : Get the language of the text
    """
    def __init__(self, document  : str = None ) -> None:
        self.__credential = os.getenv('KEY')
        self.__endpoint = os.getenv('ENDPOINT')

        self.client : TextAnalyticsClient = self.__create_authenticated_client()

        self.document = document
        self.all_analyses = (AnalyzeSentimentAction(),
                             RecognizeEntitiesAction(),
                             RecognizeLinkedEntitiesAction(),
                             ExtractKeyPhrasesAction())
        
    def __create_authenticated_client(self) -> TextAnalyticsClient:
        """
        Create a TextAnalyticsClient from Azure SDK
        """
        azure_credential = AzureKeyCredential(self.__credential)
        text_analytics_client = TextAnalyticsClient(endpoint=self.__endpoint,
                                                    credential=azure_credential)

        return text_analytics_client

    def get_sentiment(self) -> SentencesResponseDTO:
        """
        Get the sentiment of the text and it respective sentences
        Don't forget to set the document attribute in yout implemantation before running this method 
        """
        response : list[AnalyzeSentimentResult] = self.client.analyze_sentiment(documents = [self.document])

        sentiments = [doc for doc in response if not doc.is_error]

        return SentencesResponseDTO(
            sentences = [
                Sentences(
                    text=sentence.text,
                    sentiment_name=sentence.sentiment,
                    confidence=max(sentence.confidence_scores.positive, sentence.confidence_scores.neutral, sentence.confidence_scores.negative),
                    offset=sentence.offset
                ) for sentence in sentiments[0].sentences
            ],
            sentiment_name=sentiments[0].sentiment,
            sentiment_confidance=max(sentiments[0].confidence_scores.positive, sentiments[0].confidence_scores.neutral, sentiments[0].confidence_scores.negative)
        ) if len(sentiments) else []

    def get_entities(self) -> EntitiesResponseDTO:
        response = self.client.recognize_entities(documents=[self.document])
        entities =  [doc for doc in  response if not doc.is_error]
        return EntitiesResponseDTO(
            entities=[
                EntityDTO(
                    entity_name=entity.text,
                    category=entity.category,
                    subcategory=entity.subcategory,
                    offset=entity.offset,
                    confidence=entity.confidence_score
                ) for entity in entities[0].entities
            ]
        ) if len(entities) else []
    
    def get_linked_entities(self) -> LinkedEntitiesResponseDTO:
        response = self.client.recognize_linked_entities([self.document])
        linked_entities = [doc for doc in  response if not doc.is_error]

        return LinkedEntitiesResponseDTO(
            linked_entities = [
                LinkedEntitiesDTO(
                    name=entity.name,
                    url=entity.url,
                    data_source=entity.data_source,
                    matches = [
                        MatchesDTO(
                            text=entity.matches[0].text,
                            confidence_score=entity.matches[0].confidence_score)
                    ] if len(entity.matches) else []
                ) for entity in linked_entities[0].entities
            ]
        ) if len(linked_entities) else []
        
        
    
    def get_tags(self) -> TagsResponseDTO:
        response = self.client.extract_key_phrases([self.document])
        tags = [doc for doc in  response if not doc.is_error]

        return TagsResponseDTO(
                tags = [
                    Tags(
                        name=tag
                    ) for tag in tags[0].key_phrases
                ]
        ) if len(tags) else []
    
    def get_language(self, data = None) -> LanguageResponseDTO:
        response = self.client.detect_language([self.document])
        return [
            LanguageDTO(
                name=doc.primary_language.name
            ) for doc in response if not doc.is_error
        ] if len(response) else []
    
    def get_all_analysis(self) -> TextAnalyzedDTO:
        poller = self.client.begin_analyze_actions(documents=[self.document],
                                                   actions=self.all_analyses)
        analysis_results = poller.result()

        sentiment = None
        entities = None
        linked_entities = None
        key_phrases = None
        language = None

        for action_result in analysis_results:
            for azure_result_object in action_result:

                if isinstance(azure_result_object, AnalyzeSentimentResult):
                    sentences = azure_result_object

                    sentiment = SentencesResponseDTO(
                        sentences = [
                            Sentences(
                                text = sentence.text,
                                sentiment_name = sentences.sentiment,
                                confidence = max(sentence.confidence_scores.positive, sentence.confidence_scores.negative, sentence.confidence_scores.neutral),
                                offset = sentence.offset
                            ) for sentence in sentences.sentences
                        ],
                        sentiment_name=sentences.sentiment,
                        sentiment_confidance=max(sentences.confidence_scores.positive, sentences.confidence_scores.negative, sentences.confidence_scores.neutral)
                    )
                
                if isinstance(azure_result_object, ExtractKeyPhrasesResult):
                    tags = azure_result_object
                    key_phrases = TagsResponseDTO(
                        tags = [
                                Tags(
                                    name=tag
                                ) for tag in tags.key_phrases
                        ]
                    )

                
                if isinstance(azure_result_object, RecognizeEntitiesResult):
                    entities_obj = azure_result_object
                    entities = EntitiesResponseDTO(
                        entities = [
                            EntityDTO(
                                entity_name = entity.text,
                                category = entity.category,
                                subcategory = entity.subcategory,
                                offset = entity.offset,
                                confidence = entity.confidence_score
                            ) for entity in entities_obj.entities
                        ]
                    )
                
                if isinstance(azure_result_object, RecognizeLinkedEntitiesResult):
                    doc = azure_result_object
                    linked_entities = LinkedEntitiesResponseDTO(
                        linked_entities = [
                            LinkedEntitiesDTO(
                                name = linked_entity.name,
                                data_source = linked_entity.data_source,
                                url = linked_entity.url,
                                matches = MatchesDTO(
                                    text = linked_entity.matches[0].text,
                                    confidence_score = linked_entity.matches[0].confidence_score
                                )
                            ) for linked_entity in  doc.entities])


        return TextAnalyzedDTO(
            sentiment = sentiment,
            entities = entities,
            linked_entities = linked_entities,
            key_phrases = key_phrases
        )
