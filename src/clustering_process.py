from time import time
import numpy

"""
Marco Link
"""

class ClusteringProcess:
    """
    the actual clustering process
    """

    complete_dataset = None
    text_fields = None

    reader = None
    category_creator = None
    writers = None
    viusalizers = None

    preprocessing_pipeline = None
    vectorizer = None
    clusterer = None

    distance_metrics = None

    def start(self):
        """
        Starts the clustering process.
        """

        # create categories if specified
        if self.category_creator is not None:
            t0 = time()
            self.category_creator.create_categories()
            print("Finished category creation in %fs" % (time() - t0))

        # read the dataset
        t0 = time()
        self.complete_dataset, self.text_fields = self.reader.read()
        print("Finished input reading in %fs" % (time() - t0))

        # transform the text fields with the preprocessing pipeline
        preprocessed_freeformed_texts = self.text_fields
        if self.preprocessing_pipeline is not None:
            if not self.preprocessing_pipeline.is_empty():
                t0 = time()
                preprocessed_freeformed_texts = self.preprocessing_pipeline.transform(preprocessed_freeformed_texts)

        # if the pipeline has a tokenizer, the tokens will be joined with tabspace character
        # it is needed for the vectorizer for not destroying the created tokens
        if self.preprocessing_pipeline.has_tokenizer():
            joined_tokens_text_fields = []
            for document in preprocessed_freeformed_texts:
                joined_tokens = "\t".join(token for token in document)
                joined_tokens_text_fields.append(joined_tokens)
            preprocessed_freeformed_texts = numpy.array(joined_tokens_text_fields)
        print("Finished preprocessing pipeline in %fs" % (time() - t0))

        # vectorizing the preprocessed text fields
        t0 = time()
        term_document_matrix = self.vectorizer.fit_transform(preprocessed_freeformed_texts)
        print("Finished vectorizing in %fs" % (time() - t0))

        # clustering
        t0 = time()
        self.clusterer.fit(term_document_matrix)
        print("Finished clustering in %fs" % (time() - t0))

        # saving the clustering results
        t0 = time()
        for writer in self.writers:
            writer.save(term_document_matrix=term_document_matrix, vectorizer=self.vectorizer,
                        clusterer=self.clusterer, complete_dataset=self.complete_dataset)

        # create the diagrams
        if self.viusalizers is not None:
            if len(self.viusalizers) > 0:
                for visualization in self.viusalizers:
                    visualization.save(self.clusterer, term_document_matrix)
        print("Finished results saving in %fs" % (time() - t0))
