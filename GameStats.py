from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes, np
from numpy import ndarray


class GameStatistics:
    def __init__(self):
        self._fitness_samples = []
        self._blue_production_samples = []
        self._red_production_samples = []
        self._blue_attack_samples = []
        self._red_attack_samples = []
        self._blue_transport_samples = []
        self._red_transport_samples = []
        self.figure = None
        self.ax_list = None

    def add_fitness(self, sample: int) -> None:
        self._fitness_samples.append(sample)

    def add_blue_production(self, sample: int) -> None:
        self._blue_production_samples.append(sample)

    def add_red_production(self, sample: int) -> None:
        self._red_production_samples.append(sample)

    def add_blue_attack(self, sample: int) -> None:
        self._blue_attack_samples.append(sample)

    def add_red_attack(self, sample: int) -> None:
        self._red_attack_samples.append(sample)

    def add_blue_transport(self, sample: int) -> None:
        self._blue_transport_samples.append(sample)

    def add_red_transport(self, sample: int) -> None:
        self._red_transport_samples.append(sample)

    def render_plot(self) -> None:
        if self.figure is None:
            self.figure, self.ax_list = plt.subplots(2, 2)

        self.figure.suptitle('Game Statistics')
        plt.ion()
        plt.show()

        fitness_axis = self.ax_list[0, 0]  # type: Axes
        production_axis = self.ax_list[0, 1]  # type: Axes
        attack_axis = self.ax_list[1, 0]  # type: Axes
        transport_axis = self.ax_list[1, 1]  # type: Axes

        fitness_axis.cla()
        production_axis.cla()
        attack_axis.cla()
        transport_axis.cla()

        fitness_axis.set_title('Fitness')

        if len(self._fitness_samples):
            x, y, mean_y = self.get_graph_data(self._fitness_samples)
            fitness_axis.plot(x, y, color='green', alpha=0.6)
            fitness_axis.plot(x, mean_y, color='gray')

        production_axis.set_title('Production')

        if len(self._blue_production_samples) > 0:
            x, y, mean_y = self.get_graph_data(self._blue_production_samples)
            production_axis.plot(x, y, color='blue', alpha=0.6)
            production_axis.plot(x, mean_y, color='blue')

        if len(self._red_production_samples) > 0:
            x, y, mean_y = self.get_graph_data(self._red_production_samples)
            production_axis.plot(x, y, color='red', alpha=0.6)
            production_axis.plot(x, mean_y, color='red')

        attack_axis.set_title('Attacks')

        if len(self._blue_attack_samples) > 0:
            x, y, mean_y = self.get_graph_data(self._blue_attack_samples)
            attack_axis.plot(x, y, color='blue', alpha=0.6)
            attack_axis.plot(x, mean_y, color='blue')

        if len(self._red_attack_samples) > 0:
            x, y, mean_y = self.get_graph_data(self._red_attack_samples)
            attack_axis.plot(x, y, color='red', alpha=0.6)
            attack_axis.plot(x, mean_y, color='red')

        transport_axis.set_title('Transports')

        if len(self._blue_transport_samples) > 0:
            x, y, mean_y = self.get_graph_data(self._blue_transport_samples)
            transport_axis.plot(x, y, color='blue', alpha=0.6)
            transport_axis.plot(x, mean_y, color='blue')

        if len(self._red_transport_samples) > 0:
            x, y, mean_y = self.get_graph_data(self._red_transport_samples)
            transport_axis.plot(x, y, color='red', alpha=0.6)
            transport_axis.plot(x, mean_y, color='red')

        plt.pause(0.001)

    def get_graph_data(self, sample_array: List[int]) -> Tuple[List[int], List[int], List[ndarray]]:
        sample_array = sample_array[-5000:]
        x = [i for i in range(len(sample_array))]
        y = sample_array
        mean = np.mean(sample_array)
        mean_y = [mean for i in range(len(sample_array))]

        return x, y, mean_y
