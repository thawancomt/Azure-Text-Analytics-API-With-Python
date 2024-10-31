import sqlite3
from typing import Generator, Tuple, Any

from azure.ai.textanalytics import (RecognizeEntitiesResult,
                                    RecognizeLinkedEntitiesResult)

from DTO import *


conn = sqlite3.connect('interections.sqlite', check_same_thread=False)
cur = conn.cursor()

class SqliteDatabase:
    """The interface to the sqlite databasea.
    (ATENTION) : 
        Some insert methods need parameters that need to be DTO object from DTO.py (root directory)
        but in some the insert methods will be passed the raw values and other methods will be used
        the DTO objects properly.
    """
    def __init__(self):
        self.user_input = None
        self.sentiment : SentencesResponseDTO = None
        self.entities : EntitiesResponseDTO = None
        self.linked_entities : LinkedEntitiesResponseDTO = None
        self.key_phrases : TagsResponseDTO = None
        self.language : LanguageDTO = None

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
                        CREATE TABLE IF NOT EXISTS linked_entities_inputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        input_id INTEGER,
                        linked_entity_id INTEGER
                        );
                          """)
        conn.commit()

    # HELPERS
    def __insert_category(self, category_name) -> None:
        cur.execute("INSERT OR IGNORE INTO Categories (name) values (?)", (category_name, ))
        conn.commit()

    def __insert_sub_category(self, sub_category) -> None:
        cur.execute("INSERT OR IGNORE INTO Sub_Categories (name) values (?)", (sub_category or 'None', ))
        conn.commit()

    def insert(self):
        """
        This method will insert the user input, sentiment, entities, linked entities and key phrases in the database.
        """

        self.insert_sentences()

        self.insert_entities()

        self.insert_user_input()

        self.insert_tags()

        self.insert_linked_entities()


        self.insert_text_tags()

        self.insert_sentence_tags()

        self.insert_sentence_inputs()

        self.insert_entities_inputs()

        self.insert_linked_entities_inputs()

        # TODO : Make commit here instead in each insert method
    
    def insert_entities_inputs(self):
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

        # Logic steps
        # 1. Get the input id by the user input
        # 2. Get the entity id by the entity name
        # 3. Get the category id by the category name
        # 4. Get the sub category id by the sub category name
        # 5. Insert the entities inputs in the database using the input id, entity id, category id, sub category id and the offset
        input_id = self.get_input_id_by_user_input(self.user_input)

        for entity in self.entities.entities:

            category_id = self.get_category_by_name(entity.category)
            sub_category_id = self.get_sub_category_by_name(entity.subcategory)

            entity_id = cur.execute("SELECT id FROM Entities WHERE entity = (?) AND category_id = (?) AND subcategory_id = (?)", (entity.entity_name, category_id, sub_category_id)).fetchone()[0]
            

            if cur.execute("SELECT 1 FROM Entities_inputs WHERE input_id = ? AND entity_id = ? AND category_id = ? AND subcategory_id = ? AND offset = ?", (input_id, entity_id, category_id, sub_category_id, entity.offset)).fetchone():
                continue

            cur.execute("INSERT OR IGNORE INTO Entities_inputs (input_id, entity_id, category_id, subcategory_id, offset) values (?, ?, ?, ?, ?)",
                            (input_id, entity_id, category_id, sub_category_id, entity.offset))
                
        conn.commit()

    def get_input_id_by_user_input(self, user_input : str) -> int:
        """
        Get the input id by the user input
        """
        return cur.execute("SELECT id FROM Inputs WHERE input = ?", (user_input,)).fetchone()[0]

    def get_tag_id_by_name(self, tag_name : str) -> int:
        """
        Get the tag id by the tag name
        """
        return cur.execute("SELECT id FROM Tags WHERE name = ?", (tag_name,)).fetchone()[0]

    def insert_text_tags(self) -> None:
        """
        Insert the text tags in the database
        """

        input_id = self.get_input_id_by_user_input(self.user_input)

        for tag in self.key_phrases.tags:
            tag_id = self.get_tag_id_by_name(tag.name)

            if cur.execute("SELECT 1 FROM Text_tags WHERE input_id = ? AND tag_id = ?", (input_id, tag_id)).fetchone():
                continue

            cur.execute("INSERT OR IGNORE INTO Text_tags (input_id, tag_id) values (?, ?)", (input_id, tag_id))
            conn.commit()

    def insert_sentence_tags(self) -> None:
        """
        insert the sentence tags in the database
        """
        # Logic steps
        # 1. Get the sentence id by the text
        # 2. Get the tag id by the tag name
        # 3. Insert the sentence tags in the database using the sentence id and the tag id

        for sentence in self.sentiment.sentences:
            sentence_id = self.get_sentence_id_by_text(sentence.text)

            for tag in self.key_phrases.tags:
                tag_id = self.get_tag_id_by_name(tag.name)

                if cur.execute("SELECT 1 FROM Sentences_tags WHERE sentence_id = ? AND tag_id = ?", (sentence_id, tag_id)).fetchone():
                    continue

                cur.execute("INSERT OR IGNORE INTO Sentences_tags (sentence_id, tag_id) values (?, ?)", (sentence_id, tag_id))
                conn.commit()
        
        
    
    def insert_sentence_inputs(self) -> None:
        """
        Insert the sentence inputs in the database
        """
        input_id = self.get_input_id_by_user_input(self.user_input)

        for sentence in self.sentiment.sentences:
            sentence_id = self.get_sentence_id_by_text(sentence.text)

            if cur.execute("SELECT 1 FROM Sentences_inputs WHERE input_id = ? AND sentence_id = ?", (input_id, sentence_id)).fetchone():
                continue

            cur.execute("INSERT OR IGNORE INTO Sentences_inputs (input_id, sentence_id) values (?, ?)", (input_id, sentence_id))
            conn.commit()

    def insert_entities(self) -> None:
        """
        Insert the entities in the database
        """

        for entity in self.entities.entities:
            self.__insert_category(entity.category)

            self.__insert_sub_category(entity.subcategory)
            
            category_id =  self.get_category_by_name(entity.category)
            sub_category_id = self.get_sub_category_by_name(entity.subcategory)
            confidence = entity.confidence

            if cur.execute("SELECT entity, category_id, subcategory_id FROM Entities WHERE entity = (?) AND category_id = (?) AND subcategory_id = (?)",
                                             (entity.entity_name, category_id, sub_category_id)).fetchone():
                continue
            
            cur.execute("INSERT OR IGNORE INTO Entities (entity, category_id, subcategory_id, compliance) values (?, ?, ?, ?)",
                        (entity.entity_name, category_id, sub_category_id, confidence)
            )

        conn.commit()

    def insert_user_input(self) -> None:

        """
        In this method I decided to pass the raw string of the user input and the sentiment of the user input, so make sure
        that the input, sentiment and language are strings.

        :param user_input: The user input ( a raw text) string object
        :param sentiment: The sentiment of the user input string object
        :param language: The language of the user input string object
        """
        # Logic steps
        # 1. get the sentiment id by the sentiment name ( This code supposes
        # that the sentiment name is already in the database )
        # 2. Insert the user input in the database
        # 3. Commit the changes

        sentiment_id = self.get_sentiment_id_by_name(self.sentiment.sentiment_name)

        cur.execute("INSERT OR IGNORE INTO Inputs (input, sentiment_id, language) values (?, ?, ?)", (self.user_input, sentiment_id, self.language))
        conn.commit()
        

    def get_category_by_name(self, category) -> tuple[int]:
        """
        Get the category ID from the Categories table by category name
        
        Args:
            category (str): The name of the category to look up
            
        Returns:
            int: The ID of the matching category
        """
        return cur.execute("SELECT id FROM Categories WHERE name == (?)", (category,)).fetchone()[0]

    def get_sub_category_by_name(self, sub_category) -> tuple[int]:
        """
        Get the subcategory ID from the Sub_Categories table by subcategory name
        
        Args:
            sub_category (str): The name of the subcategory to look up
            
        Returns:
            int: The ID of the matching subcategory
        """
        return cur.execute("SELECT id FROM Sub_Categories WHERE name == (?)", (sub_category or 'None',)).fetchone()[0]

    def insert_tags(self) -> None:
        """
        Insert tags from key_phrases into the Tags table
        
        Inserts each tag name from self.key_phrases.tags into the Tags table,
        ignoring any duplicates
        """
        cur.executemany("INSERT OR IGNORE INTO Tags (name) values (?)", [(tag.name, ) for tag in self.key_phrases.tags])
        conn.commit()

    def insert_sentiment(self) -> int:
        """
        Insert sentiment name into the Sentiments table
        
        Inserts the sentiment name from self.sentiment into the Sentiments table,
        ignoring duplicates
        """
        cur.execute("INSERT OR IGNORE INTO Sentiments (name) values (?) ", (self.sentiment.sentiment_name,))
        conn.commit()
    
    def get_sentiment_id_by_name(self, name : str) -> list[Tuple]:
        """
        Get the sentiment ID from the Sentiments table by sentiment name
        
        Args:
            name (str): The name of the sentiment to look up
            
        Returns:
            int: The ID of the matching sentiment
        """
        return cur.execute(
                "SELECT id FROM Sentiments WHERE name == (?)", (str(name),)
                ).fetchone()[0]
    
    def insert_sentences(self) -> None:
        """
        Insert sentences into the Sentences table
        
        For each sentence in self.sentiment.sentences:
        - Gets the sentiment ID for the sentence's sentiment
        - Inserts the sentence text, sentiment ID and confidence score into the Sentences table
        - Ignores duplicate entries
        """

        if self.sentiment is None:
            # TODO: We should fix this at some point  # [fixme]
            return None

        for sentence in self.sentiment.sentences:
            sentence_text = sentence.text
            sentence_sentiment_name = sentence.sentiment_name
            sentence_sentiment_confidence = sentence.confidence

            self.insert_sentiment()
            sentiment_id = self.get_sentiment_id_by_name(name = sentence_sentiment_name)

            cur.execute("INSERT OR IGNORE INTO Sentences (text, sentiment_id, compliance) values (?, ?, ?)",
                        (sentence_text, sentiment_id, sentence_sentiment_confidence))

        # TODO: remove the commit from here
        conn.commit()


    def insert_source(self, source : str) -> None:
        cur.execute("INSERT OR IGNORE INTO Sources (name) values (?)", (source, ))
        conn.commit()
    
    def get_data_source_id_by_name(self, source : str) -> list[tuple[int]]:
        """
        Get data source id by the name
        """
        return cur.execute("SELECT id FROM Sources WHERE name == (?)", (source, )).fetchone()

    def insert_linked_entities(self) -> None:
        """
        Insert the linked entities in the database
        """
        for entity in self.linked_entities.linked_entities:
            self.insert_source(entity.data_source)

            source_id = self.get_data_source_id_by_name(entity.data_source)[0]

            cur.execute("INSERT OR IGNORE INTO Linked_entities (entity, url, source_id, compliance) values (?, ?, ?, ?)",
                        (entity.name, entity.url, source_id, entity.matches.confidence_score))
            conn.commit()
            
    def insert_linked_entities_inputs(self) -> None:
        """
        Insert the linked entities inputs in the database
        """
        input_id = self.get_input_id_by_user_input(self.user_input)

        for entity in self.linked_entities.linked_entities:
            linked_entity_id = self.get_linked_entities_id_by_name(entity.name)

            if cur.execute("SELECT 1 FROM linked_entities_inputs WHERE input_id = ? AND linked_entity_id = ?", (input_id, linked_entity_id)).fetchone():
                continue

            cur.execute("INSERT OR IGNORE INTO linked_entities_inputs (input_id, linked_entity_id) values (?, ?)", (input_id, linked_entity_id))
            conn.commit()
    
    def get_linked_entities_id_by_name(self, name : str) -> int:
        """
        Get the linked entities id by the name
        """
        return cur.execute("SELECT id FROM Linked_Entities WHERE entity = ?", (name,)).fetchone()[0]

    def get_sentence_id_by_text(self, text : str) -> int:
        """
        Get the sentence id by the text
        """
        return cur.execute("SELECT id FROM Sentences WHERE text == (?)", (text,)).fetchone()[0]
    
    def get_tags_id_by_sentence_id(self, sentence_id : int) -> list[int]:
        """
        Get the tags id by the sentence id
        """
        return cur.execute("SELECT tag_id FROM Sentences_tags WHERE sentence_id == (?)", (sentence_id,)).fetchall()