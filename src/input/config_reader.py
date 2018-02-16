from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.cluster import KMeans

from configobj import ConfigObj, flatten_errors
from validate import Validator

from input.database_reader import MSAccessDatabaseReader
from input.reader import CSVReader
from output.writer import ClusterInformationWriter, ClusterCSVWriter
from output.category_creation import NHTSADatabaseCategoryCreation
from preprocessing import *
from clustering_process import ClusteringProcess
from output.visualization import ClusterPlot, SilhouettePlot

"""
Marco Link
"""

class ConfigReader:
    """Class for reading in specific clustering config files."""

    def __init__(self, path_out):
        """:param path_out: the default outhput path for the clustering process"""
        self._path_out = path_out

    def read_config(self, path_conf, path_spec):
        """
        Reads in a config file.
        :param path_conf: the path to the config file
        :param path_spec: the path to the config specification which defines the structure of a valid config file
        :return: Returns a clustering_process
        """
        # validate the config file
        validator = Validator()
        config = ConfigObj(path_conf, configspec=path_spec)
        validation_result = config.validate(validator, preserve_errors=True)
        self.print_errors(config, validation_result)

        preprocessing_pipeline, tokenizer_added = self.handle_preprocessing(config['PREPROCESSING'])
        category_creator, reader = self.handle_input(config['INPUT'])
        writers, visualizations = self.handle_output(config['OUTPUT'])
        vectorizer = self.handle_vectorizing(config['VECTORIZING'], tokenizer_added)
        clusterer = self.handle_clustering(config['CLUSTERING'])

        # creates the clustering process
        clustering_process = ClusteringProcess()
        ClusteringProcess.clusterer = clusterer
        ClusteringProcess.preprocessing_pipeline = preprocessing_pipeline
        clustering_process.vectorizer = vectorizer
        clustering_process.reader = reader
        clustering_process.category_creator = category_creator
        clustering_process.writers = writers
        clustering_process.viusalizers = visualizations

        return clustering_process

    def print_errors(self, config, validation_result):
        """
        Prints the errors of the config file.
        :param config: the config file which errors should be printed
        :param validation_result: the result of the config checking
        http://configobj.readthedocs.io/en/latest/configobj.html#flatten-errors
        """
        for entry in flatten_errors(config, validation_result):
            # each entry is a tuple
            section_list, key, error = entry
            if key is not None:
                section_list.append(key)
            else:
                section_list.append('[missing section]')
            section_string = ', '.join(section_list)
            if error == False:
                error = 'Missing value or section.'
            print(section_string, ' = ', error)

    def handle_preprocessing(self, preprocessing_dict):
        """
        Creates the preprocessing pipeline on the basis of the config file.
        :param preprocessing_dict: the preprocessing entry of the config file
        :return: the created preprocessing pipeline and whether a tokenizer was added to the pipeline
        """
        # whether a tokenizer was added to the pipeline
        tokenizer_added = False

        pipeline = preprocessing_pipeline.PreprocessingPipeline()

        # iterates over all preprocessing steps in the preprocessing entry in the config file and all sub steps
        # the order remains preserved
        for entry in preprocessing_dict:
            preprocessingStep = preprocessing_dict[entry]
            for entry in preprocessingStep:
                # tokenizer
                if entry == 'tokenizer':
                    preprocessing_tokenizer = preprocessingStep[entry]
                    if preprocessing_tokenizer is not None:
                        if preprocessing_tokenizer == 'PTBTokenizer':
                            pipeline.add_preprocessig_step(tokenizer.PennTreebankWordTokenizer())
                            tokenizer_added = True
                        elif preprocessing_tokenizer == 'WhitespaceTokenizer':
                            pipeline.add_preprocessig_step(tokenizer.Whitespace_Tokenizer())
                            tokenizer_added = True

                # lowercase
                elif entry == 'lowercase':
                    has_lowercase = preprocessingStep[entry]
                    if has_lowercase:
                        pipeline.add_preprocessig_step(preprocess.ToLowercase())

                # textacy
                elif entry == 'remove_punctuation':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.RemovePunct())

                elif entry == 'unpack_contractions':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.UnpackContractions())

                elif entry == 'normalize_whitespace':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.NormalizeWhitespace())

                elif entry == 'remove_urls':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.ReplaceUrls())

                elif entry == 'remove_emails':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.ReplaceEMails())

                elif entry == 'remove_phone_numbers':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.ReplacePhoneNumbers())

                elif entry == 'remove_numbers':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.ReplaceNumbers())

                elif entry == 'remove_currency_symbols':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.ReplaceCurrencySymbols())

                elif entry == 'remove_accents':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.RemoveAccents())

                elif entry == 'fix_bad_unicode':
                    if preprocessingStep[entry]:
                        pipeline.add_preprocessig_step(preprocessing_with_textacy.FixBadUnicode())
                # ----------------

                # spelling correction
                elif entry == 'correct_english_spelling_errors':
                    is_spelling_correction = preprocessingStep[entry]
                    if is_spelling_correction:
                        pipeline.add_preprocessig_step(spelling_correction.CorrectEnglishSpelling())

                elif entry == 'stemmer':
                    stem = preprocessingStep[entry]
                    if stem == 'PorterStemmer':
                        pipeline.add_preprocessig_step(stemmer.PorterStemmer())
                    elif stem == 'GermanStemmer':
                        pipeline.add_preprocessig_step(stemmer.GermanStemmer())

                # englisch stopwords
                elif entry == 'remove_english_stopwords':
                    english_stopwords = preprocessingStep[entry]
                    if english_stopwords:
                        pipeline.add_preprocessig_step(remove_stopwords.EnglishStopwords())

                # custom stopwords
                elif entry == 'CUSTOMSTOPWORDS':
                    custom_stopwords = preprocessingStep[entry]
                    for stop in custom_stopwords:
                        path = custom_stopwords[stop]
                        if path is not None:
                            pipeline.add_preprocessig_step(remove_stopwords.CustomStopwords(path))

                # synonyms
                elif entry == 'SYNONYMS':
                    for path in preprocessingStep[entry]:
                        synonyms_path = preprocessingStep[entry][path]
                        if synonyms_path is not None:
                            pipeline.add_preprocessig_step(synonyms.SimpleSynonyms(synonyms_path))

                # collocations
                elif entry == 'COLLOCATIONS':
                    for path in preprocessingStep[entry]:
                        collocation_path = preprocessingStep[entry][path]
                        if collocation_path is not None:
                            pipeline.add_preprocessig_step(tokenizer.MultiWordTokenizer(collocation_path))

                # ngram synonyms
                elif entry == 'CONTEXT-SYNONYMS':
                    for context_synonym in preprocessingStep[entry]:
                        context_synonym = preprocessingStep[entry][context_synonym]
                        pipeline.add_preprocessig_step(synonyms.ContextSynonyms(context_synonym['main_words'],
                                                                                context_synonym['context_words'],
                                                                                context_synonym['before'],
                                                                                context_synonym['after'],
                                                                                context_synonym['substitution']))

                # regex subs
                elif entry == 'REGEX-SUBSTITUTIONS':
                    for regex in preprocessingStep[entry]:
                        regex = preprocessingStep[entry][regex]
                        if (regex['regex_pattern'] is not None) and (regex['substitution'] is not None):
                            regex_pattern = regex['regex_pattern'].replace('\\\\', '\\')
                            substitution = regex['substitution'].replace('\\\\', '\\')
                            pipeline.add_preprocessig_step(regex_substitution.RegexSubstitution(regex_pattern,
                                                                                                substitution))

        pipeline._has_tokenizer = tokenizer_added
        return pipeline, tokenizer_added

    def handle_input(self, input_dict):
        """
        Creates the category creator and the input reader on the basis of the config file
        :param input_dict: the input entry of the config file
        :return: the category creator if specified and the created input reader.
        """
        category_creator = None
        reader = None
        input_type = input_dict['input_type']
        input_path = input_dict['input_path']
        category_field = input_dict['CATEGORY']['column_with_category']
        categories = input_dict['CATEGORY']['categories_to_choose']
        text_fields = input_dict['CATEGORY']['columns_with_text_fields']

        if input_type == 'CSV':
            # remove escaping because of parsing with ConfigObj
            # http://stackoverflow.com/questions/5186839/python-replace-with
            delimiter = bytes(input_dict['delimiter'], 'utf-8').decode("unicode_escape")
            reader = CSVReader(input_path, category_field, categories, text_fields, input_dict['encoding'],
                               delimiter, input_dict['has_header'])

        elif input_type == 'MSACCESS':
            reader = MSAccessDatabaseReader(input_path, category_field, categories, text_fields,
                                            input_dict['table_name'], input_dict['username'], input_dict['password'])

            if input_dict['CATEGORY']['create_categories'] == 'NHTSA':
                category_creator = NHTSADatabaseCategoryCreation(input_path, input_dict['table_name'],
                                                                 input_dict['username'], input_dict['password'],
                                                                 input_dict['CATEGORY']['column_with_primary_key'])

        return category_creator, reader

    def handle_output(self, output_dict):
        """
        Creates the output writers and the visualizers  on the basis of the config file
        :param output_dict: the output entry of the config file
        :return: a list with the output writers and a list with the visualizers.
        """
        path = output_dict['output_path']
        if path is None:
            path = self._path_out
        visualizations = []
        output_writers = []
        if output_dict['save_plot']:
            visualizations.append(ClusterPlot(path))
        if output_dict['save_silhouette_score_plot']:
            visualizations.append(SilhouettePlot(path))
        output_writers.append(ClusterCSVWriter(path))
        output_writers.append(ClusterInformationWriter(path))
        return output_writers, visualizations

    def handle_vectorizing(self, vectorizing_dict, tokenizer_added=False):
        """
        Creates the vectorizer on the basis of the config file
        :param vectorizing_dict: the vectorizing entry of the config file
        :param tokenizer_added: whether a tokenizer was added to the preprocessing pipeline
        :return: the vectorizer
        """
        # In case of a tokenizer was added to the preprocessing pipeline, the default behaviour of using
        # whitespaces to split a document into tokens has to be changed.
        if tokenizer_added:
            # https://github.com/scikit-learn/scikit-learn/issues/5482
            analyzer = lambda x: x.split('\t')
        else:
            analyzer = 'word'

        vectorizer = None

        max_df = vectorizing_dict['max_df']
        min_df = vectorizing_dict['min_df']
        try:
            min_df = int(min_df)
        except ValueError:
            min_df = float(min_df)
        try:
            max_df = int(max_df)
        except ValueError:
            max_df = float(max_df)

        binary = vectorizing_dict['binary']
        max_features = vectorizing_dict['max_features']
        use_idf = vectorizing_dict['use_idf']
        smooth_idf = vectorizing_dict['smooth_idf']
        sublinear_tf = vectorizing_dict['sublinear_tf']

        if vectorizing_dict['vectorizer'] == 'CountVectorizer':
            print(analyzer)
            vectorizer = CountVectorizer(lowercase=False, max_df=max_df, min_df=min_df,
                                         max_features=max_features, binary=binary, analyzer=analyzer)
        elif vectorizing_dict['vectorizer'] == 'TF-IDF':
            vectorizer = TfidfVectorizer(lowercase=False, max_df=max_df, min_df=min_df, max_features=max_features,
                                         binary=binary, use_idf=use_idf, smooth_idf=smooth_idf,
                                         sublinear_tf=sublinear_tf, analyzer=analyzer)

        return vectorizer

    def handle_clustering(self, clustering_dict):
        """
        Creates the clusterer on the basis of the config file
        :param clustering_dict: the clustering entry of the config file
        :return: Returns the clusterer.
        """
        clusterer = None
        n_clusters = clustering_dict['n_clusters']
        max_iter = clustering_dict['max_iter']
        init = clustering_dict['init']
        n_init = clustering_dict['n_init']

        if clustering_dict['algorithm'] == 'kmeans':
            clusterer = KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter, init=init)

        return clusterer
