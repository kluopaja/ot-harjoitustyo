import logging
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

logging.getLogger('matplotlib').setLevel(logging.WARNING)

class Plotter:
    def __init__(self):
        self.figure = plt.figure(frameon = False)

    def plot_histogram_to_image(self, data, x, hue, bin_range,
                                bins=10, title="", width=100, height=100):
        """

        Args:
            `data`: a dataframe
            `x`: a string
                The name of the column to be plotted
            `hue`: a string
                The name of the column specifying the groups
            `bin_range`: a tuple of scalars
                The range of the histogram
            `bins`: an integer
                The number of bins in the histogram
            `title`: a string
                The title of the plot
            `width`: an integer
                The width of the plot in pixels
            `height`: an integer
                The height of the plot in pixels

        Returns:
            `image`: a (width, height, 4) numpy array
                The image of the plot
        """
        try:
            plt.ioff()
            ax = self.figure.gca()
            ax.patch.set_visible(False)
            self.figure.patch.set_visible(False)

            sns.histplot(data, x=x, hue=hue, binrange = bin_range,
                         bins=bins, element="poly", fill=False, ax=ax)

            ax.set_title(title)

            dpi = self.figure.get_dpi()

            # add small value for numerical errors
            self.figure.set_size_inches(width/float(dpi) + 1e-5, height/float(dpi) + 1e-5)

            self.figure.canvas.draw()

            image = np.fromstring(self.figure.canvas.tostring_argb(), dtype=np.uint8, sep='')
            image = image.reshape(height, width, 4)
            image = np.swapaxes(image, 0, 1)
            self.figure.clf()
            return image
        except Exception:
            # the plotting seemed to fail on some macOS versions.
            return np.zeros(shape=(width, height, 4))
