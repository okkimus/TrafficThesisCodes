import matplotlib.pyplot as plt

def visualise_model(model, preds, dataset, scaled, include_small, color="r"):
  class_c = model.n_clusters
  for yi in range(class_c):
    plt.subplot(int(class_c / 3), 3, 1 + yi)
    # for xx in dataset[preds == yi]:
    #     plt.plot(xx.ravel(), "k-", alpha=.2)
    plt.plot(model.cluster_centers_[yi].ravel(), color)
    plt.xlim(0, 336)
    plt.ylim(-2, 4)
    plt.text(0.55, 0.85,'Cluster %d' % (yi + 1),
            transform=plt.gca().transAxes)
    if yi == 1:
        plt.title("DTW $k$-means")

  plt.tight_layout()
  plt.show()