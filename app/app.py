# Standart import
import os
import sys
import logging

# Third parties imports
from flask import Flask, request, render_template, jsonify
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

# Local imports
from RetriveAnalysis import RetriveAnalysis
from .azure_services.azure_text_analytics import AzureTextAnalyticsApi
from app.database_services.database_controller import SqliteDatabase
from DTO import *

class App:
    def __init__(self):
        self.app : Flask = Flask(__name__)
        self.app.secret_key = os.getenv('SECRET_KEY')
        self.database = SqliteDatabase()

        # Logger configs
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('log.txt', encoding='utf-8')
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)


        # Verbose logging
        self.verbose = False


        try:
            self.logger.info('Initialiazing the Azure Text Analytics SDK')
            self.text_analyzer : AzureTextAnalyticsApi = AzureTextAnalyticsApi()
            # TODO : Implement the test user credentials [fixme]
            # self.TextAnalizer.client.analyze_sentiment(['s'])

        except ResourceNotFoundError as err:
            self.logger.critical(f'Check your endpoint {err.message}')
            sys.exit()
        except ClientAuthenticationError as err:
            self.logger.critical(f'Check your Api Key {err.message}')
            sys.exit()

        self.register_routes()

    def register_routes(self):
        self.logger.info('Routes %s registered' % '/')
        self.app.add_url_rule('/', 'index', methods=['GET', 'POST'], view_func=self.analyse_user_input)
        self.app.add_url_rule('/get', 'get', methods=['GET', 'POST'], view_func=self.get)
        self.app.add_url_rule('/get_historic', 'get_historic', methods=['GET'], view_func=self.get_inputs_hitoric)

        # self.App.add_url_rule('/<input_id>', 'get_tags', methods=['GET'], view_func=self.get_tags)

    def analyse_user_input(self):
        """
        The homepage of our application:
        Make sure, in the HTML the attributte name of the text input is 'document',
        The following checkboxes need to be in the form if you want to run it respectivily analyze:
            - sentiment to execute sentiment and sentences extraction
            - entities to extract the entities from the user input
            - linked_entities to extract the linked entities from the user input
            - key_phrases to extract the key phrases from the user input
            - all_actions to execute all the actions above
        
        This endpoint use the TextAnalizer class to get the information from the user input, so before running
        any analysis, the user input need to be passed to the TextAnalizer.document attributte. e.g. TextAnalizer.document = 'user_input_variable'

        Always the response will be an object with the following keys:
            - sentiment : SentencesResponseDTO
            - entities : EntitiesResponseDTO
            - linked_entities : LinkedEntitiesResponseDTO
            - key_phrases : TagsResponseDTO
            - language : LanguageResponseDTO

        Behavior:
            - All these keys will be None if the user doesn't check the respective checkbox.
            - All the keys will be filled with the information if the user check the 'all_actions' checkbox or if the user doesn't check any checkbox.
            - If more than 3 checkboxes are checked the system will execute all the actions.
            - If the user check only one checkbox, the system will execute only the action of the checkbox checked.
            - Only the all_actions performed will be saved in the database.

        Logging:
            - All call will be saved on log.txt file    
        """


        context : TextAnalyzedDTO = {}


        if request.method == 'POST':
            self.logger.info('POST > registered')

            resquest_form : dict = request.form.to_dict()
            self.logger.debug('POST > Form loaded')

            user_input = resquest_form.get('text')
            self.logger.info(f'POST > User input lenght = {len(user_input)}')

            if not user_input:
                self.logger.info('No input registered, going back to home...')
                return render_template('index.html', **context)

            self.text_analyzer.document = user_input
            self.logger.info('User input loaded into Text Analytics')

            marked_checkboxes_on_form = resquest_form.keys()
            self.logger.info(f'Form checkboxes loaded : {str([key for key in marked_checkboxes_on_form])} ')


            if 'all_actions' in marked_checkboxes_on_form or len(marked_checkboxes_on_form) > 3:
                self.logger.info('All actions were selected...')
                # Verify if the user input exists in the database.
                # If found: Retrieve existing analysis from database
                # If not found: Perform new analysis and store in database
                # This caching mechanism helps avoid redundant API calls and improves performance
                # by reusing previously analyzed content.

                self.logger.info('Trying retrieve the analysis from the database')
                retrieved_analysis_data = RetriveAnalysis(user_input=user_input)

                

                if retrieved_analysis_data.input_id:
                    self.logger.info('Analysis already in the databases, retriving the data input_id in database: %d' % retrieved_analysis_data.input_id)

                    context['sentiment'] = retrieved_analysis_data.get_sentences()

                    # logging
                    self.logger.info('Number of Sentences loaded to context: %d' % len(context['sentiment'].sentences))
                    for sentence in context['sentiment'].sentences:
                        self.logger.info('Sentence text %s ' % sentence)

                    context['entities'] = retrieved_analysis_data.get_entities_inputs()

                    # Logging
                    self.logger.info('Number of Entities loaded to context: %d' % len(context['entities'].entities))
                    for entity in context['entities'].entities:
                        self.logger.info('Entity text %s ' % entity)

                    context['linked_entities'] = retrieved_analysis_data.get_linked_entities()

                    # Logging
                    self.logger.info('Number of Linked Entities loaded to context: %d' % len(context['linked_entities'].linked_entities))
                    for entity in context['linked_entities'].linked_entities:
                        self.logger.info('Linked Entity text %s ' % entity)

                    context['key_phrases'] = retrieved_analysis_data.get_tags()

                    # Logging
                    self.logger.info('Number of Key Phrases loaded to context: %d' % len(context['key_phrases'].tags))
                    for tag in context['key_phrases'].tags:
                        self.logger.info('Key Phrase text %s ' % tag)

                    context['language'] = retrieved_analysis_data.get_language()


                else:
                    self.logger.info('Analysis not found in the database, performing new analysis...')
                    analysis_result = self.text_analyzer.get_all_analysis()


                    context['sentiment'] = analysis_result.sentiment
                    
                    # Logging
                    self.logger.info('Sentiment analysis performed')
                    self.logger.info('Number of Sentences loaded to context: %d' % len(context['sentiment'].sentences))
                    for sentence in context['sentiment'].sentences:
                        self.logger.info('Sentence text %s ' % sentence)

                    context['entities'] = analysis_result.entities

                    # Logging
                    self.logger.info('Entities analysis performed')
                    self.logger.info('Number of Entities loaded to context: %d' % len(context['entities'].entities))
                    for entity in context['entities'].entities:
                        self.logger.info('Entity text %s ' % entity)

                    context['linked_entities'] = analysis_result.linked_entities
                    
                    # Logging
                    self.logger.info('Linked entities analysis performed')
                    self.logger.info('Number of Linked Entities loaded to context: %d' % len(context['linked_entities'].linked_entities))
                    for entity in context['linked_entities'].linked_entities:
                        self.logger.info('Linked Entity text %s ' % entity)

                    context['key_phrases'] = analysis_result.key_phrases
                    
                    # logging
                    self.logger.info('Key phrases analysis performed')
                    self.logger.info('Number of Key Phrases loaded to context: %d' % len(context['key_phrases'].tags))
                    for tag in context['key_phrases'].tags:
                        self.logger.info('Key Phrase text %s ' % tag)

                    context['language'] = analysis_result.language

                    self.logger.info('Setting the context into database controller')
                    # Save the analysis in the database
                    self.database.user_input = user_input
                    self.database.language = context['language']
                    self.database.sentiment = context['sentiment']
                    self.database.entities = context['entities']
                    self.database.linked_entities = context['linked_entities']
                    self.database.key_phrases = context['key_phrases']
                    
                    
                    try:
                        self.logger.info('Inserting the analysis into the database')
                        self.database.insert()
                    except Exception as err:
                        self.logger.error(f'Error inserting the analysis into the database {err}')

            else:
                self.logger.info('Less than 3 actions, getting individuals analysis from Azure...')
                context = self.perform_individual_analysis(context, marked_checkboxes_on_form)

            # TODO: Fix the language detection
            context['language'] = 'English'

        return render_template('index.html', **context)

    def perform_individual_analysis(self, context, marked_checkboxes_on_form):
        if 'sentiment' in marked_checkboxes_on_form:
            self.logger.info('Sentiment analysis selected...')
            self.logger.info('Performing sentiment analysis...')

            context['sentiment'] = self.text_analyzer.get_sentiment()

            self.logger.info('Sentiment analysis performed')
            self.logger.info('Number of Sentences loaded to context: %d' % len(context['sentiment'].sentences))
            for sentence in context['sentiment'].sentences:
                self.logger.info('Sentence text %s ' % sentence)

        if 'entities' in marked_checkboxes_on_form:
            self.logger.info('Entities analysis selected...')
            self.logger.info('Performing entities analysis...')

            context['entities'] = self.text_analyzer.get_entities()

            self.logger.info('Entities analysis performed')
            self.logger.info('Number of Entities loaded to context: %d' % len(context['entities'].entities))
            for entity in context['entities'].entities:
                self.logger.info('Entity text %s ' % entity)

        if 'linked_entities' in marked_checkboxes_on_form:
            self.logger.info('Linked entities analysis selected...')
            self.logger.info('Performing linked entities analysis...')

            context['linked_entities'] = self.text_analyzer.get_linked_entities()

            self.logger.info('Linked entities analysis performed')
            self.logger.info('Number of Linked Entities loaded to context: %d' % len(context['linked_entities'].linked_entities))
            for entity in context['linked_entities'].linked_entities:
                self.logger.info('Linked Entity text %s ' % entity)

        if 'key_phrases' in marked_checkboxes_on_form:
            self.logger.info('Key phrases analysis selected...')
            self.logger.info('Performing key phrases analysis...')

            context['key_phrases'] = self.text_analyzer.get_tags()

            self.logger.info('Key phrases analysis performed')
            self.logger.info('Number of Key Phrases loaded to context: %d' % len(context['key_phrases'].tags))
            for tag in context['key_phrases'].tags:
                self.logger.info('Key Phrase text %s ' % tag)
        
        return context
    
    def get(self):
        getter = RetriveAnalysis(user_input=request.form.get('text'))
    
        response : TextAnalyzedDTO = {
            "sentiment" : getter.get_sentences(),
            "entities" : getter.get_entities_inputs(),
            "linked_entities" : getter.get_linked_entities(),
            "key_phrases" : getter.get_tags(),
        }

        print(response)

        return jsonify(response)
    def get_inputs_hitoric(self):
        inputs = RetriveAnalysis.get_inputs()
        

        return jsonify(inputs)
    
app = App().app
