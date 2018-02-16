from .preprocess import PreprocessBase

"""
Marco Link
"""

class PreprocessingPipeline:
    """Pipeline for preprocessing tasks."""

    def __init__(self, preprocessing_steps=None, has_tokenizer=False):
        """
        Initializes the pipeline with the given preprocessing steps.
        :param preprocessing_steps: the preprocessing steps to add
        :param has_tokenizer: whether the preprocessing_steps contain a tokenizer.
        """
        self._preprocessing_steps = []
        self._has_tokenizer = has_tokenizer
        if preprocessing_steps is not None:
            if isinstance(preprocessing_steps, PreprocessBase):
                self._preprocessing_steps.append(preprocessing_steps)
            elif isinstance(preprocessing_steps, list):
                for preprocessing_step in preprocessing_steps:
                    if isinstance(preprocessing_step, PreprocessBase):
                        self._preprocessing_steps.append(preprocessing_step)

    def transform(self, documents):
        """
        Starts the preprocessing pipeline and transforms the given documents.
        :param documents: the documents to preprocess
        :return: the preprocessed documents
        """
        if len(self._preprocessing_steps) > 0:
            transformed_documents = documents
            for preprocessing_step in self._preprocessing_steps:
                transformed_documents = preprocessing_step.transform(transformed_documents)
            return transformed_documents

    def add_preprocessig_step(self, preprocessing_step):
        """
        Adds a preprocessing step to the preprocessing pipeline.
        :param preprocessing_step: The preprocessing step to add
        """
        if isinstance(preprocessing_step, PreprocessBase):
            self._preprocessing_steps.append(preprocessing_step)

    def is_empty(self):
        """:return: True if the pipeline contains no prerprocessing steps, else False"""
        if len(self._preprocessing_steps) == 0:
            return True
        else:
            return False

    def has_tokenizer(self):
        """:return: True if a tokenizer was added to the pipeline, else False"""
        return self._has_tokenizer
