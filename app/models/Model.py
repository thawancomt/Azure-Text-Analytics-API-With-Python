import sqlite3
from typing import Generator, Tuple, Any


from DTO import *

from azure.ai.textanalytics import (RecognizeEntitiesResult, CategorizedEntity, RecognizeLinkedEntitiesResult, LinkedEntity, LinkedEntityMatch,
                                    AnalyzeSentimentResult)

conn = sqlite3.connect('interections.sqlite', check_same_thread=False)
cur = conn.cursor()

class SqliteDatabase:
    """The interface to the sqlite database"""
    def __init__(self):
        self.CreateTables()
    
    def CreateTables(self):
        cur.executescript("""
                        CREATE TABLE IF NOT EXISTS Inputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        input TEXT UNIQUE,
                        sentiment_id INTEGER,
                        language VARCHAR(4)
                        );
                        
                        CREATE TABLE IF NOT EXISTS Sentences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        text TEXT UNIQUE,
                        sentiment_id INTEGER,
                        compliance REAL
                        );
                        
                        CREATE TABLE IF NOT EXISTS Sentiments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        name TEXT UNIQUE
                        );
                        
                        CREATE TABLE IF NOT EXISTS Entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        entity TEXT,
                        category_id INTEGER,
                        subcategory_id INTEGER,
                        compliance REAL
                        );
                          
                        CREATE TABLE IF NOT EXISTS Entities_Inputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        input_id INTERGER,
                        category_id INTEGER,
                        subcategory_id INTEGER,
                        entity_id INTEGER,
                        offset INTEGER
                        );
                        
                        CREATE TABLE IF NOT EXISTS Linked_Entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        entity TEXT UNIQUE,
                        url TEXT,
                        source_id INTEGER,
                        compliance REAL
                        );
                        
                        CREATE TABLE IF NOT EXISTS Categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        name TEXT UNIQUE
                        );
                        
                        CREATE TABLE IF NOT EXISTS Sub_Categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        name TEXT UNIQUE
                        );
                        
                        CREATE TABLE IF NOT EXISTS Tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        name TEXT UNIQUE
                        );
                        CREATE TABLE IF NOT EXISTS Sources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        name TEXT UNIQUE
                        );
                        
                        CREATE TABLE IF NOT EXISTS Text_tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        input_id INTEGER,
                        tag_id INTEGER
                        );
                        
                        CREATE TABLE IF NOT EXISTS Sentences_tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        sentence_id INTEGER,
                        tag_id INTEGER
                        );
                        
                        CREATE TABLE IF NOT EXISTS Sentences_inputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        input_id INTEGER,
                        sentence_id INTEGER,
                        offset INTEGER
                        );
                          """)
        conn.commit()

    # HELPERS
    def __InsertCategory(self, Category) -> None:
        cur.execute("INSERT OR IGNORE INTO Categories (name) values (?)", (Category, ))
        conn.commit()

    def __InsertSubCategory(self, SubCategory) -> None:
        cur.execute("INSERT OR IGNORE INTO Sub_Categories (name) values (?)", (SubCategory, ))
        conn.commit()

    def __ExtractSentiments(self, sentiment: SentencesResponseDTO) -> Generator[str, Any, None]:
        
        overral_sentiment = str(sentiment.sentiment_name)
        sentences = []
        for sentence in sentiment.sentences:
                
                
                self.InsertSentiment(sentence.sentiment_name)

                sentences.append(
                                    (str(sentence.text),
                                    int(self.GetSentimentByName(str(sentence.sentiment_name))),
                                    float(sentence.confidence) * 100,
                                    sentence.offset)
                                    
                                )
        yield overral_sentiment        
        yield sentences 

    def Insert(self, UserInput : str, language : str, sentiment : SentencesResponseDTO,
               entities : list[RecognizeEntitiesResult],
               linked_entities : list[RecognizeLinkedEntitiesResult],
               key_phrases : list[int]):
        
        sentiments = self.__ExtractSentiments(sentiment)

        OverallSentiment : str = next(sentiments)
        sentences = [sentence for sentence in next(sentiments)]

        self.InsertInput(UserInput, OverallSentiment, language)

        self.InsertSentences(sentences)

        self.InsertEntity(entities)

        self.InsertLinkedEntities(linked_entities)

        self.InsertTags(key_phrases)

        self.InsertTextTags(UserInput, key_phrases)

        self.InsertSentencesTags(sentences, key_phrases)

        self.InsertSentencesInputs(sentences, UserInput)

        self.InsertEntitiesInputs(UserInput, entities)
    
    def InsertEntitiesInputs(self, UserInput : str, Entities : EntitiesResponseDTO):
        """
        CREATE TABLE IF NOT EXISTS Entities_Inputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        input_id INTERGER,
                        cat
                        sub
                        entity_id INTEGER,
                        offset INTEGER
                        );
        """
        InputId = cur.execute("SELECT id FROM Inputs WHERE input = (?)", (UserInput,)).fetchone()[0]

        for Entity in Entities.entities:
            CategoryId = self.GetCategoryByName(Entity.category)
            SubCategoryId = self.GetSubCategoryByName(Entity.subcategory)

            if SubCategoryId is None:
                SubCategoryId = None
                EntityId = cur.execute("SELECT id FROM Entities WHERE entity = (?) AND category_id = (?) AND subcategory_id IS NULL", (Entity.entity_name, CategoryId)).fetchone()[0]
            else:
                SubCategoryId : int = SubCategoryId
                EntityId = cur.execute("SELECT id FROM Entities WHERE entity = (?) AND category_id = (?) AND subcategory_id = (?)", (Entity.entity_name, CategoryId, SubCategoryId)).fetchone()[0]
            

            ThisRelationExist = cur.execute("SELECT 1 FROM Entities_inputs WHERE input_id = ? AND entity_id = ? AND category_id = ? AND subcategory_id = ? AND offset = ?", (InputId, EntityId, CategoryId, SubCategoryId, Entity.offset)).fetchone()

            if not ThisRelationExist:

                cur.execute("INSERT OR IGNORE INTO Entities_inputs (input_id, entity_id, category_id, subcategory_id, offset) values (?, ?, ?, ?, ?)",
                            (InputId, EntityId, CategoryId, SubCategoryId, Entity.offset))
                
                conn.commit()

    def InsertTextTags(self, UserInput : str, Tags_ : TagsResponseDTO) -> None:

        
        tags = Tags_.tags
        InputId = cur.execute("SELECT id FROM Inputs WHERE input == (?)", (UserInput,)).fetchone()[0]

        for tag in tags:
            TagId = cur.execute("SELECT id FROM Tags WHERE name == (?)", (tag.name,)).fetchone()[0]

            ThisRelationExist = cur.execute("SELECT 1 FROM Text_tags WHERE input_id = ? AND tag_id = ?", (InputId, TagId)).fetchone()

            if not ThisRelationExist:
                cur.execute("INSERT OR IGNORE INTO Text_tags (input_id, tag_id) values (?, ?)", (InputId, TagId))
                conn.commit()

    def InsertSentencesTags(self, Sentences : SentencesResponseDTO, Tags_ : TagsResponseDTO) -> None:
        """
        CREATE TABLE IF NOT EXISTS Sentences_tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        sentence_id INTEGER,
                        tag_id INTEGER
                        );
        """
        for sentence, sentimentId, confidence, offset in Sentences:
            SentenceId = cur.execute("SELECT id FROM Sentences WHERE text == (?)", (sentence,)).fetchone()[0]
            for tag in Tags_.tags:
                TagId = cur.execute("SELECT id FROM Tags WHERE Tags.name == (?)", (tag.name,)).fetchone()[0]

                ThisRelationExist = cur.execute("SELECT 1 FROM Sentences_tags WHERE sentence_id == (?) AND tag_id == (?)", (SentenceId, TagId)).fetchone()
                if not ThisRelationExist:
                    cur.execute("INSERT OR IGNORE INTO Sentences_tags (sentence_id, tag_id) values (?, ?)", (SentenceId, TagId)) 
                    conn.commit()
    
    def InsertSentencesInputs(self, Sentences : list[str], UserInput : str) -> None:
        InputId = cur.execute("SELECT id FROM Inputs WHERE input == (?)", (UserInput,)).fetchone()[0]
        
        for sentence, sentimentId, confidence, offset in Sentences:
            sentence_Id = cur.execute("SELECT id FROM Sentences WHERE text == (?)", (sentence, )).fetchone()[0]

            ThisRelationExist = cur.execute("SELECT 1 FROM Sentences_inputs WHERE input_id == (?) AND sentence_id == (?) AND offset == (?)", (InputId, sentence_Id, offset)).fetchone()
            
            if not ThisRelationExist:
                cur.execute("INSERT OR IGNORE INTO Sentences_inputs (input_id, sentence_id, offset) values (?, ?, ?)", (InputId, sentence_Id, offset)) 
                conn.commit()

    def InsertEntity(self, entities : EntitiesResponseDTO) -> None:

        for entity in entities.entities:
            self.__InsertCategory(entity.category)

            if entity.subcategory:
                SubCategoryId = entity.subcategory
                self.__InsertSubCategory(entity.subcategory)
            else:
                SubCategoryId = None
                self.__InsertSubCategory(None)
            
            
            Text = entity.entity_name
            CategoryId=  self.GetCategoryByName(entity.category)
            SubCategoryId = self.GetSubCategoryByName(SubCategoryId)

            ThisRelationExists = cur.execute("SELECT entity, category_id, subcategory_id FROM Entities WHERE entity = (?) AND category_id = (?) AND subcategory_id = (?)", (entity.entity_name, CategoryId, SubCategoryId)).fetchone()
            
            if not ThisRelationExists:
                Compliance = entity.confidence
                cur.execute("INSERT OR IGNORE INTO Entities (entity, category_id, subcategory_id, compliance) values (?, ?, ?, ?)", (Text, CategoryId, SubCategoryId, Compliance))
                conn.commit()

    def InsertInput(self, UserInput : str, Sentiment : str, language : str) -> None:
        SentimentId = self.GetSentimentByName(Sentiment)
        cur.execute("INSERT OR IGNORE INTO Inputs (input, sentiment_id, language) values (?, ?, ?)", (UserInput, SentimentId, language))
        conn.commit()
        

    def GetCategoryByName(self, Category) -> tuple[int]:
        return cur.execute("SELECT id FROM Categories WHERE name == (?)", (Category,)).fetchone()[0]

    def GetSubCategoryByName(self, SubCategory) -> tuple[int]:
        if SubCategory is None:
            return cur.execute("SELECT id FROM Sub_Categories WHERE name IS NULL").fetchone()[0]
        
        return cur.execute("SELECT id FROM Sub_Categories WHERE name == (?)", (SubCategory,)).fetchone()[0]

    def InsertTags(self, tags : TagsResponseDTO) -> None:
        tags = [Tags(name = tag.name) for tag in tags.tags]
        
        cur.executemany("INSERT OR IGNORE INTO Tags (name) values (?)", [(Tag.name, ) for Tag in tags])
        conn.commit()

    def InsertSentiment(self, sentiment : str) -> int:
        cur.execute("INSERT OR IGNORE INTO Sentiments (name) values (?) ", (sentiment,))
        conn.commit()
        sentiment_id = cur.lastrowid
        return sentiment_id
    
    def GetSentimentByName(self, name : str) -> list[Tuple]:
        return cur.execute("SELECT id FROM Sentiments WHERE name == (?)", (str(name), )).fetchone()[0]
    
    def InsertSentences(self, senteces : list) -> None:
        cur.executemany("INSERT OR IGNORE INTO Sentences (text, sentiment_id, compliance) values (?, ?, ?)", [(name, sentiment_id, compliance) for name, sentiment_id, compliance, offset in senteces])
        conn.commit()

    def InsertSource(self, source : str) -> None:
        cur.execute("INSERT OR IGNORE INTO Sources (name) values (?)", (source, ))
        conn.commit()
    
    def GetSourceByName(self, source : str) -> list[tuple[int]]:
        return cur.execute("SELECT id FROM Sources WHERE name == (?)", (source, )).fetchone()

    def InsertLinkedEntities(self, linked_entities : LinkedEntitiesResponseDTO) -> None:
        for entity in linked_entities.linked_entities:

            Text = entity.name
            Matches = entity.matches
            Compliance = Matches.confidence_score
            Url = entity.url
            Source = entity.data_source


            self.InsertSource(Source)
            SourceId = self.GetSourceByName(Source)[0]

            cur.execute("INSERT OR IGNORE INTO Linked_entities (entity, url, source_id, compliance) values (?, ?, ?, ?)",
                        (Text, Url, SourceId, Compliance))
            conn.commit()
