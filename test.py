from threading import Thread

from matplotlib.axis import Axis
from matplotlib.figure import Figure


def make_plot():
    import matplotlib.pyplot as plt
    figure, axis = plt.subplots() # type: Figure, Axis
    figure.savefig('./test.png')


if __name__ == '__main__':
    thread = Thread(target=make_plot, daemon=True)
    thread.start()
