import matplotlib.pyplot as plt

l1 = [10, 10, 10, 10]
l2 = [9, 10, 11, 9]
l3 = [9.5, 10.5, 11.5, 9.6]

bplot1 = plt.boxplot([l1, l2, l3], widths=0.05,
                     showmeans=True, patch_artist=True)
plt.plot([1, 2, 3], [10, 9.75, 10.275])

l4 = [1, 2, 3, 4]
l5 = [2, 3, 3, 2]
l6 = [7, 0, 0, 1]

bplot2 = plt.boxplot([l4, l5, l6], widths=0.05,
                     showmeans=True, patch_artist=True)
plt.plot([1, 2, 3], [2.5, 2.5, 2])

colors = ["pink", "lightblue", "lightgreen"]

for patch, color in zip(bplot1['boxes'], colors):
    patch.set_facecolor(color)

plt.axis((0, 4, 0, 12))
plt.savefig("1.png")
