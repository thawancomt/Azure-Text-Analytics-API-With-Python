from app.models.Model import cur, conn

from collections import namedtuple



SentenceObject = namedtuple('Sentence', ['text', 'sentiment_id', 'compliance', 'offset'])

class RetriveAnalysis:
    def __init__(self, UserInput):
        self.UserInput = UserInput
        self.InputId = self.__GetUserInput()
        self.SentenceObject = SentenceObject

    def __GetUserInput(self) -> int | None:
        RetriviedInput = cur.execute("SELECT * FROM Inputs WHERE input == (?)", (self.UserInput,)).fetchone()

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
        
        return Sentences

    def GetEntities(self):
        pass


userInput = 'The style of a narrative text is distinctive. It employs a chronological sequencing of events. Coherent, right-branching sentences, varying in length, create rhythm and draw the reader into the unfolding story. Active voice is favored to maintain directness and immediacy, bringing scenes alive.'
a = RetriveAnalysis(userInput)
print(a.GetSentences())
        
        
    