import json
import os
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for Flask apps
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

def generate_visuals(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    book_title = os.path.basename(json_path).replace("_bias.json", "")

    os.makedirs("data/plots", exist_ok=True)

    # Bar Chart
    plt.figure(figsize=(6, 4))
    plt.bar([book_title], [data["bias_score"]], color="#b26700")
    plt.title("Bias Intensity per Book")
    plt.ylabel("Number of Glorifying Terms")
    plt.tight_layout()
    plt.savefig("data/plots/bias_bar_chart.png")
    plt.close()

    # Pie Chart
    entity_labels = data.get("entity_labels", {})
    if entity_labels:
        labels = list(entity_labels.keys())
        sizes = list(entity_labels.values())
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.axis("equal")
        plt.title("Bias Mentions by Entity Type")
        plt.savefig("data/plots/entity_type_pie_chart.png")
        plt.close()

    bias_terms = data.get("bias_terms", [])
    if bias_terms:
        text = " ".join(bias_terms)
        wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="plasma").generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Most Common Glorifying Terms")
        plt.tight_layout()
        plt.savefig("data/plots/glorifying_wordcloud.png")
        plt.close()
    else:
        print("[INFO] No bias terms found — skipping word cloud.")

