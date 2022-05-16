import matplotlib.pyplot as plt
from tslearn.metrics import dtw

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

def visualise_models(models, colors):
  cluster_count = models[0].n_clusters

  mapping = []

  for i in range(cluster_count):
    mapping.append(find_closest_clusters(models, i, cluster_count))
  
  for i in range(len(mapping)):
    m = mapping[i]
    plt.subplot(int(cluster_count / 3), 3, 1 + i)
    for i in range(len(m)):
      plt.plot(models[i].cluster_centers_[m[i]].ravel(), colors[i])
      plt.xlim(0, 336)
      plt.ylim(-2, 4)
      plt.text(0.55, 0.85,'Cluster %d' % (i + 1),
              transform=plt.gca().transAxes)
      if i == 1:
          plt.title("DTW $k$-means")

  plt.tight_layout()
  plt.show()

def find_closest_clusters(models, i, cluster_count):
  cluster = models[0].cluster_centers_[i]
  closest_clusters = [i]

  for i in range(1, len(models)):
    next_model_clusters = models[i]
    closest = -1
    closest_value = 999999

    for j in range(cluster_count):
      distance = dtw(cluster, next_model_clusters.cluster_centers_[j], global_constraint="sakoe_chiba", sakoe_chiba_radius=10)
      if distance < closest_value:
        closest = j
        closest_value = distance
    
    closest_clusters.append(closest)

  return closest_clusters
