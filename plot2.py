import os
import pandas as pd
import matplotlib.pyplot as plt

base_dir = "analysis_outputs"

folders = [os.path.join(base_dir, d) for d in os.listdir(base_dir)]
latest_folder = max(folders, key=os.path.getctime)

csv_path = os.path.join(latest_folder, "results_summary.csv")

print("Loading:", csv_path)

df = pd.read_csv(csv_path)

# 畫圖
pivot = df.pivot(index="template", columns="method", values="filtered_count")

pivot.plot(kind="bar")
plt.title("Filtered Count")
plt.tight_layout()
plt.show()