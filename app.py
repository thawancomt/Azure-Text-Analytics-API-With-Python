import os
from typing import TypedDict
from flask import Flask, request, render_template, flash, g
from AzureTextAnalytics import *
from azure.core.exceptions import ResourceNotFoundError
import os
import sys
class ResponseAzure(TypedDict):
        sentiment : list[AnalyzeSentimentResult | DocumentError]
        entities : list[RecognizeEntitiesResult | DocumentError]
        linked_entities : list[RecognizeLinkedEntitiesResult | DocumentError]
        key_phrases : list[ExtractKeyPhrasesResult | DocumentError]
        language : list[DetectLanguageResult | DocumentError]

class TextApp:
    def __init__(self):
        self.App : Flask = Flask(__name__)
        self.App.secret_key = os.getenv('SECRET_KEY')

        try:
            self.TextAnalizer : AzureTextAnalyticsApi = AzureTextAnalyticsApi()
            self.TextAnalizer.client.analyze_sentiment(['s'])

        except ResourceNotFoundError as err:
             print(f'Check your endpoint', err.message)
             sys.exit()
        except ClientAuthenticationError as err:
             print(f'Check your Api Key', err.message)
             sys.exit()

        self.register_routes()

    def register_routes(self):
         self.App.add_url_rule('/', 'index', methods=['GET', 'POST'], view_func=self.analyze)

    def analyze(self):
        Context: ResponseAzure  = dict()

        if request.method == 'POST':
            Data : dict = request.form.to_dict()

            Document = Data.get('text')
            Actions = Data.keys()

            self.TextAnalizer.document = Document

            if 'all_actions' in Actions:
                All : namedtuple = self.TextAnalizer.GetAllInformation()
                Context['sentiment'] = All.sentiment
                Context['entities'] = All.entities
                Context['linked_entities'] = All.linked_entities
                Context['key_phrases'] = All.key_phrases
                Context['language'] = All.language
            else:
                # Analyzers
                SentimentResponse : AnalyzeSentimentResult = self.TextAnalizer.GetSentiment() if 'sentiment' in Actions else []
                EntitiesResponse : RecognizeEntitiesResult = self.TextAnalizer.GetEntities() if 'entities' in Actions else []
                LinkedEntities : RecognizeLinkedEntitiesResult = self.TextAnalizer.GetLinkedEntities() if 'linked_entities' in Actions else []
                KeyPhrases : ExtractKeyPhrasesResult = self.TextAnalizer.GetKeyPhrases() if 'key_phrases' in Actions else []
                Language : DetectLanguageResult = self.TextAnalizer.GetLanguage() if 'language' in Actions else []

                Context['sentiment'] = SentimentResponse
                Context['entities'] = EntitiesResponse
                Context['linked_entities'] = LinkedEntities
                Context['key_phrases'] = KeyPhrases
                Context['language'] = Language
        else:
            pass
        return render_template('index.html', **Context)

app = TextApp().App