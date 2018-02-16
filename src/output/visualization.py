from abc import ABCMeta, abstractmethod
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.metrics import silhouette_score, silhouette_samples
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy
import os

"""
Marco Link
"""

class VisualizationBase(metaclass=ABCMeta):
    """Visualization base class from which all visualization classes should be inherited."""

    def __init__(self, path):
        """:param path: the folder in which the visualization should be saved."""

        # http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
        if not os.path.exists(path):
            os.makedirs(path)

        # http://stackoverflow.com/questions/510972/getting-the-class-name-of-an-instance-in-python
        self._path = os.path.join(path, self.__class__.__name__ + '.png')

    @abstractmethod
    def save(self, clusterer, term_document_matrix):
        """
        Creates and saves the visualization.
        :param clusterer: the clusterer which results should be visualized
        :param term_document_matrix: the term document matrix which was used by the clusterer
        """
        pass


class ClusterPlot(VisualizationBase):
    """
    Visualize the cluster centers with its members.
    Used sk-learn example: http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
    """
    def __init__(self, path):
        super().__init__(path)

    def save(self, clusterer, term_document_matrix):
        plt.close('all')
        try:
            # does automatic analysis for pca work
            matrix_minimizer = PCA(n_components='mle', svd_solver='full').fit(term_document_matrix.todense())
        except:
            try:
                # does pca in general work
                matrix_minimizer = PCA(n_components=2).fit(term_document_matrix.todense())
            except:
                # use lsa if pca does not work because of a too big term document matrix
                matrix_minimizer = TruncatedSVD(n_components=2, n_iter=10, random_state=42).fit(term_document_matrix)

        data_2d = matrix_minimizer.transform(term_document_matrix.todense())
        # 2nd Plot showing the actual clusters formed
        colors = cm.spectral(clusterer.labels_.astype(float) / clusterer.n_clusters)
        plt.scatter(data_2d[:, 0], data_2d[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                    c=colors)

        # Labeling the clusters
        centers = matrix_minimizer.transform(clusterer.cluster_centers_)
        # Draw white circles at cluster centers
        plt.scatter(centers[:, 0], centers[:, 1],
                    marker='o', c="white", alpha=1, s=200)

        for i, c in enumerate(centers):
            plt.scatter(c[0], c[1], marker='$%d$' % i, alpha=1, s=50)

        plt.savefig(self._path, bbox_inches='tight')
        plt.close()


class SilhouettePlot(VisualizationBase):
    """
    Visualize the silhouette score from the clustering result.
    Used sk-learn example: http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
    """
    def __init__(self, path):
        super().__init__(path)

    def save(self, clusterer, term_document_matrix):
        plt.close('all')
        # Create a subplot with 1 row and 1 column
        fig, (ax1) = plt.subplots(1, 1)
        fig.set_size_inches(9, 7)

        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        ax1.set_xlim([-1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax1.set_ylim([0, term_document_matrix.shape[0] + (clusterer.n_clusters + 1) * 10])

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(term_document_matrix, clusterer.labels_)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(term_document_matrix, clusterer.labels_)

        y_lower = 10
        for i in range(clusterer.n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[clusterer.labels_ == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.spectral(float(i) / clusterer.n_clusters)
            ax1.fill_betweenx(numpy.arange(y_lower, y_upper),
                              0, ith_cluster_silhouette_values,
                              facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])

        plt.savefig(self._path, bbox_inches='tight')
        plt.close()
