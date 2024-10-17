import sqlite3
from typing import Any, Generator, Tuple, List

from azure.ai.textanalytics import (RecognizeEntitiesResult, CategorizedEntity, RecognizeLinkedEntitiesResult, LinkedEntity, LinkedEntityMatch,
                                    DetectLanguageResult,
                                    ExtractKeyPhrasesResult, 
                                    AnalyzeSentimentResult)

conn = sqlite3.connect('interections.sqlite', check_same_thread=False)
cur = conn.cursor()

class SqlitDatabase:
    def __init__(self):
        pass
    
    def CreateTables(self):
        cur.executescript("""
                            CREATE TABLE IF NOT EXISTS Inputs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                            input TEXT UNIQUE,
                            sentiment_id TEXT
                            );
                          
                            CREATE TABLE IF NOT EXISTS Sentences (
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
                            entity TEXT UNIQUE,
                            category_id INTEGER,
                            sub_category_id INTEGER,
                            compliance REAL
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

                          """)
    # HELPERS
    def __InsertCategory(self, Category) -> None:
        cur.execute("INSERT OR IGNORE INTO Categories (name) values (?)", (Category, ))
        conn.commit()

    def __InsertSubCategory(self, SubCategory) -> None:
        cur.execute("INSERT OR IGNORE INTO Sub_Categories (name) values (?)", (SubCategory, ))
        conn.commit()

    def __ExtractSentiments(self, sentiment: list) -> Generator[str, Any]:
        overral_sentiment = str(sentiment[0].sentiment) 
        
        sentences = []
        for sentence in sentiment[0].sentences:
                self.InsertSentiment(sentence.sentiment)
                sentences.append(
                                    (str(sentence.text),
                                    int(self.GetSentimentByName(str(sentence.sentiment))[0]),
                                    float(sentence.confidence_scores[sentence.sentiment]) * 100)
                                )
        yield overral_sentiment        
        yield sentences

    def Insert(self, UserInput : str, sentiment : list[AnalyzeSentimentResult],
               entities : list[RecognizeEntitiesResult],
               linked_entities : list[RecognizeLinkedEntitiesResult],
               key_phrases : list[ExtractKeyPhrasesResult]):
        
        sentiments = self.__ExtractSentiments(sentiment)
        OverallSentiment : str = next(sentiments)
        sentences = [sentence for sentence in next(sentiments)]

        self.InsertInput(UserInput, OverallSentiment)

        self.InsertSentences(sentences)

        self.InsertEntity(entities)

        self.InsertLinkedEntities(linked_entities)

        self.InsertTags(key_phrases)

    def InsertEntity(self, entity ) -> None:
        entities : list[CategorizedEntity] = entity[0].entities

        for entity in entities:
            self.__InsertCategory(entity.category)

            if entity.subcategory:
                SubCategoryId = entity.subcategory
                self.__InsertSubCategory(entity.subcategory)
            else:
                SubCategoryId = 'None'
                self.__InsertSubCategory('None')
            
            
            Text, CategoryId= entity.text, self.GetCategoryByName(entity.category)[0]
            SubCategoryId = self.GetSubCategoryByName(SubCategoryId)[0]

            Compliance = entity.confidence_score
            cur.execute("INSERT OR IGNORE INTO Entities (entity, category_id, sub_category_id, compliance) values (?, ?, ?, ?)", (Text, CategoryId, SubCategoryId, Compliance))
            conn.commit()

    def InsertInput(self, UserInput : str, Sentiment : str) -> None:
        SentimentId = self.GetSentimentByName(Sentiment)[0]
        cur.execute("INSERT OR IGNORE INTO Inputs (input, sentiment_id) values (?, ?)", (UserInput, SentimentId))
        conn.commit()
        

    def GetCategoryByName(self, Category) -> tuple[int]:
        return cur.execute("SELECT id FROM Categories WHERE name == (?)", (Category,)).fetchone()

    def GetSubCategoryByName(self, SubCategory) -> tuple[int]:
        return cur.execute("SELECT id FROM Sub_Categories WHERE name == (?)", (SubCategory,)).fetchone()

    def InsertTags(self, Tags) -> None:
        Tags : list[str] = Tags[0].key_phrases
        
        cur.executemany("INSERT OR IGNORE INTO Tags (name) values (?)", [(Tag, ) for Tag in Tags])
        conn.commit()
        

    
    
    
    def InsertSentiment(self, sentiment : str) -> int:
        cur.execute("INSERT OR IGNORE INTO Sentiments (name) values (?) ", (sentiment,))
        conn.commit()
        sentiment_id = cur.lastrowid
        return sentiment_id
    
    def GetSentimentByName(self, name : str) -> list[Tuple]:
        return cur.execute("SELECT id FROM Sentiments WHERE name == (?)", (str(name), )).fetchone()
    
    def InsertSentences(self, senteces : list) -> Any:
        cur.executemany("INSERT OR IGNORE INTO Sentences (text, sentiment_id, compliance) values (?, ?, ?)", [(name, sentiment_id, compliance) for name, sentiment_id, compliance in senteces])
        conn.commit()

    def InsertSource(self, source : str) -> None:
        cur.execute("INSERT OR IGNORE INTO Sources (name) values (?)", (source, ))
        conn.commit()
    
    def GetSourceByName(self, source : str) -> list[tuple[int]]:
        return cur.execute("SELECT id FROM Sources WHERE name == (?)", (source, )).fetchone()

    def InsertLinkedEntities(self, linked_entities) -> None:
        LinkedEntities : list[LinkedEntity] = linked_entities[0].entities
        for entity in LinkedEntities:
            Text = entity.name
            Matches : list[LinkedEntityMatch] = entity.matches
            Compliance = Matches[0].confidence_score
            Url = entity.url
            Source = entity.data_source


            self.InsertSource(Source)
            SourceId = self.GetSourceByName(Source)[0]

            cur.execute("INSERT OR IGNORE INTO Linked_entities (entity, url, source_id, compliance) values (?, ?, ?, ?)",
                        (Text, Url, SourceId, Compliance))
            conn.commit()
