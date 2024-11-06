from dataclasses import dataclass
from typing import List


@dataclass
class EntityDTO():
    """Data Transfer Object for Entities"""
    entity_name: str
    category: str
    subcategory: str
    offset: int
    confidence: float = None
@dataclass
class EntitiesResponseDTO:
    """Data Transfer Object for Entities Response"""
    entities : list[EntityDTO]

@dataclass
class Sentences:
    """Data Transfer Object for Sentences"""
    text : str
    sentiment_name : str
    confidence : float
    offset : int | str

@dataclass
class SentencesResponseDTO():
    """Data Transfer Object for Sentences response
    content : [SentenceDTO]"""
    sentences : list[Sentences]
    sentiment_name : str  = None
    sentiment_confidance : float = None


@dataclass
class Tags:
    """Data Transfer Object for Tags"""
    name : str

@dataclass
class TagsResponseDTO:
    """Data Transfer Object for Tags Response"""
    tags : list[Tags]


@dataclass
class ResponseAzure:
    """Data Transfer Object for Azure Response"""
    sentiment : SentencesResponseDTO = None
    entities : EntitiesResponseDTO = None
    # linked_entities : list[RecognizeLinkedEntitiesResult] = None
    # key_phrases : list[ExtractKeyPhrasesResult] = None
    # language : list[DetectLanguageResult] = None

@dataclass
class MatchesDTO:
    """Data Transfer Object for Matches"""
    text : str
    confidence_score : float

@dataclass
class LinkedEntitiesDTO:
    """Data Transfer Object for Linked Entities"""
    name : str
    url : str
    data_source : str
    matches : MatchesDTO

@dataclass
class LinkedEntitiesResponseDTO:
    """Data Transfer Object for Linked Entities Response"""
    linked_entities : list[LinkedEntitiesDTO]

@dataclass
class LanguageDTO:
    """Data Transfer Object for Language"""
    name : str

@dataclass
class LanguageResponseDTO:
    """Data Transfer Object for Language Response"""
    language : list[LanguageDTO]

@dataclass
class TextAnalyzedDTO:
    """Data Transfer Object for Azure Response"""
    sentiment : SentencesResponseDTO = None
    entities : EntitiesResponseDTO = None
    linked_entities : LinkedEntitiesResponseDTO = None
    key_phrases : TagsResponseDTO = None
    language : LanguageResponseDTO = None
