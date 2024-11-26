from matplotlib.path import Path
from matplotlib.pylab import ArrayLike
import matplotlib.pyplot as plt


def create_grapics(
    y_data: ArrayLike, x_data: ArrayLike, path_to_png: Path
):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.hist(x=x_data, y=y_data)
    fig.savefig(path_to_png)
    plt.close(fig)
