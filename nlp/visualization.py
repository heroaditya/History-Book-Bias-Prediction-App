import json
import os
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for Flask apps
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

# Load and handle single or multi-book bias file
with open("data/bias_scores/.Futuhus-Salatin-Or-Shah-Namah-I-Hind-Of-Isami-Vol-i_text_bias.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

if isinstance(raw_data, dict) and "bias_count" in raw_data:
    bias_data = {"Futuhus Salatin (Vol I)": raw_data}
else:
    bias_data = raw_data

# --- BAR CHART: Bias Intensity per Book ---
def plot_bias_per_book(data):
    titles = list(data.keys())
    counts = [data[book]["bias_count"] for book in titles]

    plt.figure(figsize=(12, 6))
    sns.barplot(x=titles, y=counts, palette="viridis")
    plt.xticks(rotation=45, ha="right")
    plt.title("Bias Intensity per Book")
    plt.xlabel("Book Title")
    plt.ylabel("Number of Glorifying Terms")
    plt.tight_layout()
    plt.savefig("data/plots/bias_bar_chart.png")
    plt.close()


# --- PIE CHART: Entity Type Distribution ---
def plot_entity_distribution(data):
    entity_counter = {}
    for book_data in data.values():
        for ent_type, count in book_data.get("entity_labels", {}).items():
            entity_counter[ent_type] = entity_counter.get(ent_type, 0) + count

    labels = list(entity_counter.keys())
    sizes = list(entity_counter.values())

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, colors=sns.color_palette("pastel"))
    plt.axis("equal")
    plt.title("Bias Mentions by Entity Type")
    plt.tight_layout()
    plt.savefig("data/plots/entity_type_pie_chart.png")
    plt.close()


# --- WORD CLOUD: Glorifying Terms ---
def plot_word_cloud(data):
    all_terms = []
    for book_data in data.values():
        all_terms.extend(book_data.get("bias_terms", []))

    text = " ".join(all_terms)
    wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="plasma").generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Most Common Glorifying Terms")
    plt.tight_layout()
    plt.savefig("data/plots/glorifying_wordcloud.png")
    plt.close()


# --- MAIN ---
def visualize_all():
    os.makedirs("data/plots", exist_ok=True)
    plot_bias_per_book(bias_data)
    plot_entity_distribution(bias_data)
    plot_word_cloud(bias_data)
    print("✅ Visualization completed. Check data/plots folder for output images.")


if __name__ == "__main__":
    visualize_all()
