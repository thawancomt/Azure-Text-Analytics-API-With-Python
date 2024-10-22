from app.models.Model import cur, conn, sqlite3

from collections import namedtuple



SentenceObject = namedtuple('Sentence', ['text', 'sentiment_id', 'compliance', 'offset'])

class RetriveAnalysis:
    def __init__(self, UserInput):
        self.UserInput = UserInput
        self.InputId = self.__GetUserInput()
        self.SentenceObject = SentenceObject

    def __GetUserInput(self) -> int | None:
        try:
            RetriviedInput = cur.execute("SELECT * FROM Inputs WHERE input == (?)", (self.UserInput,)).fetchone()
        except sqlite3.OperationalError:
            return None

        if not RetriviedInput:
            return None
        
        InputId = RetriviedInput[0]
        return InputId

    def GetSentences(self) -> list[SentenceObject]:
        RetriviedSentences : tuple[int, int, int]= cur.execute("""SELECT input_id, sentence_id, offset, Sentences.sentiment_id FROM Sentences_inputs
                                                                  JOIN Inputs
                                                                  ON Inputs.id = input_id
                                                                  JOIN Sentences
                                                                  ON Sentences.id = sentence_id
                                                                  WHERE input_id == (?)
                                                                  ORDER BY offset ASC""",(self.InputId,)).fetchall()
        
        if not RetriviedSentences:
            return None
        
        Sentences : list = []

        for InputId_, SentenceId, OffSet, SentimentId  in RetriviedSentences:
            SentenceText, SentenceSentiment, Compliance = cur.execute("SELECT text, sentiment_id, compliance FROM Sentences WHERE id == (?)", (SentenceId, )).fetchone()
            SentenceObject = self.SentenceObject(text=SentenceText, sentiment_id=SentenceSentiment, compliance=Compliance, offset=OffSet)

            Sentences.append(SentenceObject)

        self.sentences = Sentences
        return Sentences

    def GetEntitiesInputs(self):
        # RetriviedEntities = cur.execute("""SELECT input_id, Categories.name, Subcategories.name, entity_id, offset
        #                                 FROM Entities_inputs
        #                                 JOIN Categories ON category_id = Categories.id
        #                                 JOIN Subcategories ON subcategory_id = Subcategories.id """).fetchall()
        pass
        

    def f(self):
        return cur.execute("SELECT id FROM Sub_Categories WHERE name IS NULL").fetchone()

