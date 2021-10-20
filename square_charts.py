import numpy as np
import matplotlib.pyplot as plt


def square_chart(fractions, defaultcolor='lightgrey'):

	if sum([f[0] for f in fractions]) > 1 or not all([f[0] >= 0 for f in fractions]):
		raise ValueError('Fractions must be positive and in sum between 0 and 1.')

	fractions, colors = zip(*fractions)
	percentages = [int(round(fraction * 100, 0)) for fraction in fractions]
	percentages = np.cumsum(percentages)
	percentages = np.append([0], percentages)
	color_counter = len(colors) - 1

	matrix = np.full((10, 10), len(fractions), dtype=int)

	while True:
		square_counter = percentages[-1] - 1
		if square_counter == -1:
			break
		percentages = percentages[:-1]
		while (square_counter >= percentages[-1]):
			matrix[9 - square_counter % 10][9 - square_counter // 10] = color_counter
			square_counter -= 1
		color_counter -= 1

	ax = plt.gca()
	ax.patch.set_facecolor(defaultcolor)
	ax.set_aspect('equal', 'box')
	ax.xaxis.set_major_locator(plt.NullLocator())
	ax.yaxis.set_major_locator(plt.NullLocator())

	for (x, y), color_index in np.ndenumerate(matrix):
		try:
			color = colors[color_index]
		except IndexError:
			color = defaultcolor
		size = 1
		rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,
							 facecolor=color, edgecolor='white')
		ax.add_patch(rect)

	ax.autoscale_view()
	ax.invert_yaxis()


if __name__ == '__main__':

	square_chart([(0.2, 'firebrick'), (0., 'blue'), (0.2, 'green')], 'lightgray')
	plt.show()