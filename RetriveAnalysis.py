from typing import List

from app.models.Model import cur, SqliteDatabase

from DTO import *


class RetriveAnalysis:
    """
    Class to retrieve analysis from the database based on the user input
    """
    def __init__(self, user_input : str):
        self.user_input : str = str(user_input)
        self.input_id = None
        self.__get_input_id()

        self.sentiment_name : str = cur.execute("SELECT name FROM Sentiments \
                                                JOIN Inputs \
                                                    ON Inputs.sentiment_id = Sentiments.id \
                                                WHERE Inputs.id = ?", (self.input_id,)).fetchone()
        if self.sentiment_name:
            self.sentiment_name = self.sentiment_name[0]


    def __get_input_id(self) ->  None:
        input_id = cur.execute("SELECT id FROM Inputs WHERE input = ?", (self.user_input,)).fetchone()
        if input_id:
            self.input_id = input_id[0]

        return self.input_id

    def get_sentences(self) -> SentencesResponseDTO:
        """
        Get the sentences from the database
        """
        return SentencesResponseDTO(
            [
                Sentences(*sentence) for sentence in cur.execute("""SELECT
                                                                        Sentences.text,
                                                                        Sentiments.name,
                                                                        Sentences.compliance,
                                                                        offset
                                                                    FROM Sentences_inputs
                                                                    JOIN Inputs
                                                                        ON Inputs.id = input_id
                                                                    JOIN Sentences
                                                                        ON Sentences.id = sentence_id
                                                                    JOIN Sentiments
                                                                        ON Sentiments.id = Sentences.sentiment_id
                                                                    WHERE input_id == (?)
                                                                    ORDER BY offset ASC""", (self.input_id,)).fetchall()
            ], sentiment_name = self.sentiment_name)

    def get_entities_inputs(self) -> EntitiesResponseDTO:
        """
        Get the entities from database
        """
        return EntitiesResponseDTO(
            [
                EntityDTO(*entity) for entity in cur.execute("""SELECT
                                                    Entities.entity AS EntityName, 
                                                    Categories.name AS category,
                                                    Sub_Categories.name AS SubCategory, 
                                                    Entities_Inputs.offset,
                                                    Entities.compliance
                                                FROM Categories
                                                JOIN Entities_Inputs 
                                                    ON Entities_Inputs.category_id = Categories.id
                                                JOIN Sub_Categories 
                                                    ON Entities_Inputs.subcategory_id = Sub_categories.id
                                                JOIN Entities 
                                                    ON Entities_Inputs.entity_id = Entities.id
                                                WHERE input_id = ?""", (self.input_id,)).fetchall()
            ]
        )
    def get_tags(self) -> TagsResponseDTO:
        """
        Get the key_phrases (tags) from the database
        """
        return TagsResponseDTO(
            [
                Tags(name=tag[0]) for tag in cur.execute("""SELECT name FROM Text_tags
                                                JOIN Tags
                                                ON tag_id = Tags.id
                                                WHERE input_id = ? """, (self.input_id,) ).fetchall()
            ]
        )
    def get_linked_entities(self, sentences) -> LinkedEntitiesResponseDTO:
        """
        Get the linked entities from the database
        """

        for sentence in sentences.sentences:
            sentence_id = SqliteDatabase().get_sentence_id_by_text(sentence.text)
            print(sentence_id)
            sentences_tags = cur.execute("""SELECT name FROM Sentences_tags
                                            JOIN Tags
                                                ON tag_id = Tags.id
                                            WHERE sentence_id = ? """, (sentence_id,)).fetchall()
            print(type(sentences_tags))
            

        # TODO: Implement this method
        q = """SELECT
                    Linked_Entities.entity,
                    Linked_Entities.category,
                    Linked_Entities.subcategory,
                    Linked_Entities.offset,
                    Linked_Entities.compliance
                FROM Linked_Entities"""
        return []
        return LinkedEntitiesResponseDTO(
            linked_entities = [
                LinkedEntitiesDTO(*linked_entity) for linked_entity in cur.execute(q).fetchall()
            ]
        )
    
    def get_language(self):
        return cur.execute("SELECT language FROM Inputs WHERE id = ?", (self.input_id,)).fetchone()[0]

