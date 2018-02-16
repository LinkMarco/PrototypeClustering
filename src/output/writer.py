from abc import ABCMeta, abstractmethod
import csv
import os
from scipy.spatial.distance import euclidean

"""
Marco Link
"""

class WriterBase(metaclass=ABCMeta):
    """Base class for the output writer objects."""
    def __init__(self, path):
        """:param path: the path to the output folder"""
        # http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
        if not os.path.exists(path):
            os.makedirs(path)
        self._path = path

    @abstractmethod
    def save(self, vectorizer, term_document_matrix, clusterer, complete_dataset=None):
        """
        Writes the specific clustering information.
        :param vectorizer: the vectorizer
        :param term_document_matrix: the term documet matrix created from the vectorizer
        :param clusterer: the clusterer which result should be saved.
        :param complete_dataset: the complete dataset
        """
        pass


class ClusterCSVWriter(WriterBase):
    """
    Saves the clustering result as csv file.
    Additionally to the original dataset informatioen, the cluster center, the distance
    to the cluster center, the main feature identifying the cluster center and some of the features identifying
    the cluster center will be stored.
    """

    # should the distance be written with a comma
    _float_with_comma = False

    def save(self, vectorizer, term_document_matrix, clusterer, complete_dataset=None):

        order_centroids = clusterer.cluster_centers_.argsort()[:, ::-1]
        cluster_centroids_terms = []

        terms = vectorizer.get_feature_names()

        # take the features from cluster centers in the order of their weighting. Minimum weight 0.08
        for k in range(clusterer.n_clusters):
            centroid_terms = []
            cluster_centroid = clusterer.cluster_centers_[k].reshape(1, term_document_matrix.shape[1])
            for ind in order_centroids[k, :30]:
                if cluster_centroid[0, ind] >= 0.1:
                    centroid_terms.append(terms[ind])
            cluster_centroids_terms.append(centroid_terms)

        # write the clustering results
        # https://docs.python.org/3/library/csv.html
        with open(os.path.join(self._path, 'Cluster.csv'), 'w', newline='', encoding='utf-8') as clustersCsv:
            # reader = csv.reader(clustersCsv, delimitter='\t')
            writer = csv.writer(clustersCsv, delimiter='\t')

            i = 0
            for entry in term_document_matrix:
                cluster_center = clusterer.labels_[i]
                cluster_centroid = clusterer.cluster_centers_[cluster_center].reshape(1, term_document_matrix.shape[1])

                main_term = terms[order_centroids[cluster_center, 0]]

                # compute the distance from the cluster center
                # http://stackoverflow.com/questions/29036561/how-to-get-meaningful-results-of-kmeans-in-scikit-learn
                distance = euclidean(entry.todense(), clusterer.cluster_centers_[cluster_center])
                row = complete_dataset[i].tolist()
                row.append(str(cluster_center))
                distance = "{0:.3f}".format(distance)
                cluster_main_term_weight = '%0.3f' % cluster_centroid[0, order_centroids[cluster_center, :1]]
                if self._float_with_comma:
                    distance = distance.replace('.', ',')
                    cluster_main_term_weight = cluster_main_term_weight.replace('.', ',')
                row.append(distance)
                row.append(main_term)
                row.append(cluster_main_term_weight)
                row.append(', '.join(cluster_centroids_terms[cluster_center]))
                writer.writerow(row)

                i += 1


class ClusterInformationWriter(WriterBase):
    """
    Saves the information from the clustering process.
    Dataset shape, features, information about the vectorizer and clusterer, the actual cluster centers with its
    features and the amount of documents within the cluster.
    """

    def save(self, vectorizer, term_document_matrix, clusterer, complete_dataset=None):

        # get amount of documents per cluster
        amount = {}
        for label in clusterer.labels_:
            if label in amount:
                amount[label] += 1
            else:
                amount.update({label: 1})

        f = open(os.path.join(self._path, 'Cluster_Information.txt'), 'w', encoding='utf-8')

        f.write('SHAPE: ')
        f.write(str(term_document_matrix.shape[0]))
        f.write(', ')
        f.write(str(term_document_matrix.shape[1]))
        f.write('\n')

        f.write('FEATURES:\n')
        for feature in vectorizer.get_feature_names():
            f.write(feature)
            f.write(', ')
        f.write('\n')
        f.write("vectorizer: %s" % vectorizer)
        f.write('\n\n')
        f.write("Clustering sparse data with %s" % clusterer)
        f.write('\n')
        f.write('\n\n')

        order_centroids = clusterer.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()

        for k in range(clusterer.n_clusters):
            cluster_centroid = clusterer.cluster_centers_[k].reshape(1, term_document_matrix.shape[1])
            if k in amount:
                f.write("Cluster %d" % k + " " + str(amount[k]) + " :")
            for ind in order_centroids[k, :30]:
                f.write(' %s' % terms[ind])
                f.write(' %0.3f,' % cluster_centroid[0, ind])
            f.write('\n')

        f.close()
