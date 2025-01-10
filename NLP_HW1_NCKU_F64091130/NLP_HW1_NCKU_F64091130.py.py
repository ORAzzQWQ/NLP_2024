# -*- coding: utf-8 -*-
"""HW1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rBXff2QSRP0NvmUSIpqOZkZ7_7dFuTYL

## Part I: Data Pre-processing
"""

import pandas as pd

# Download the Google Analogy dataset
!wget http://download.tensorflow.org/data/questions-words.txt

# Preprocess the dataset
file_name = "questions-words"
with open(f"{file_name}.txt", "r") as f:
    data = f.read().splitlines()

# check data from the first 10 entries
for entry in data[:10]:
    print(entry)

# TODO1: Write your code here for processing data to pd.DataFrame
# Please note that the first five mentions of ": " indicate `semantic`,
# and the remaining nine belong to the `syntatic` category.

questions = []
categories = []
sub_categories = []
colon_count = 0

for line in data:
    line = line.strip()

    if line.startswith(":"):
        colon_count += 1
        section_name = line
        continue

    if colon_count <= 5:
        categories.append("semantic")
    else:
        categories.append("syntatic")

    sub_categories.append(section_name)
    questions.append(line)

# Create the dataframe
df = pd.DataFrame(
    {
        "Question": questions,
        "Category": categories,
        "SubCategory": sub_categories,
    }
)
print(df)

df.head()

df.to_csv(f"{file_name}.csv", index=False)

"""## Part II: Use pre-trained word embeddings
- After finish Part I, you can run Part II code blocks only.
"""

import pandas as pd
import numpy as np
import gensim.downloader
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

data = pd.read_csv("questions-words.csv")

MODEL_NAME = "glove-wiki-gigaword-100"
# You can try other models.
# https://radimrehurek.com/gensim/models/word2vec.html#pretrained-models

# Load the pre-trained model (using GloVe vectors here)
model = gensim.downloader.load(MODEL_NAME)
print("The Gensim model loaded successfully!")

# Do predictions and preserve the gold answers (word_D)
preds = []
golds = []

for analogy in tqdm(data["Question"]):
      # TODO2: Write your code here to use pre-trained word embeddings for getting predictions of the analogy task.
      # You should also preserve the gold answers during iterations for evaluations later.
      # tqdm(): show the processing line
      """ Hints
      # Unpack the analogy (e.g., "man", "woman", "king", "queen")
      # Perform vector arithmetic: word_b + word_c - word_a should be close to word_d
      # Source: https://github.com/piskvorky/gensim/blob/develop/gensim/models/keyedvectors.py#L776
      # Mikolov et al., 2013: big - biggest and small - smallest
      # Mikolov et al., 2013: X = vector(”biggest”) − vector(”big”) + vector(”small”).
      """
      # ask ChatGPT how to use
      word_a, word_b, word_c, gold_answer = analogy.split()

      try:
        result_vector = model[word_b] + model[word_c] - model[word_a]

        predicted_word = model.most_similar(positive=[result_vector], topn=1)[0][0]

        preds.append(predicted_word)
        golds.append(gold_answer)

      except KeyError as e:
        # print(f"Word not in vocabulary: {e}")
        preds.append(None)
        golds.append(gold_answer)

# Perform evaluations. You do not need to modify this block!!

def calculate_accuracy(gold: np.ndarray, pred: np.ndarray) -> float:
    return np.mean(gold == pred)

golds_np, preds_np = np.array(golds), np.array(preds)
data = pd.read_csv("questions-words.csv")

# Evaluation: categories
for category in data["Category"].unique():
    mask = data["Category"] == category
    golds_cat, preds_cat = golds_np[mask], preds_np[mask]
    acc_cat = calculate_accuracy(golds_cat, preds_cat)
    print(f"Category: {category}, Accuracy: {acc_cat * 100}%")

# Evaluation: sub-categories
for sub_category in data["SubCategory"].unique():
    mask = data["SubCategory"] == sub_category
    golds_subcat, preds_subcat = golds_np[mask], preds_np[mask]
    acc_subcat = calculate_accuracy(golds_subcat, preds_subcat)
    print(f"Sub-Category{sub_category}, Accuracy: {acc_subcat * 100}%")

# Collect words from Google Analogy dataset
SUB_CATEGORY = ": family"

# TODO3: Plot t-SNE for the words in the SUB_CATEGORY `: family`
# ask ChatGPT how to use
family_words = data[data["SubCategory"] == ": family"]["Question"].str.split().tolist()
family_words = [word for sublist in family_words for word in sublist]
family_words = list(set(family_words))

words_vectors = []
words = []
for word in family_words:
    if word in model:
        words_vectors.append(model[word])
        words.append(word)

words_vectors = np.array(words_vectors)
tsne = TSNE(n_components=2, random_state=0)
reduced_vectors = tsne.fit_transform(words_vectors)

plt.figure(figsize=(10, 8))
plt.scatter(reduced_vectors[:, 0], reduced_vectors[:, 1])

# add tag
for i, word in enumerate(words):
    plt.text(reduced_vectors[i, 0], reduced_vectors[i, 1], word, fontsize=9)

plt.title("Word Relationships from Google Analogy Task")
plt.show()
plt.savefig("word_relationships.png", bbox_inches="tight")

"""### Part III: Train your own word embeddings

### Get the latest English Wikipedia articles and do sampling.
- Usually, we start from Wikipedia dump (https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2). However, the downloading step will take very long. Also, the cleaning step for the Wikipedia corpus ([`gensim.corpora.wikicorpus.WikiCorpus`](https://radimrehurek.com/gensim/corpora/wikicorpus.html#gensim.corpora.wikicorpus.WikiCorpus)) will take much time. Therefore, we provide cleaned files for you.
"""

# Download the split Wikipedia files
# Each file contain 562365 lines (articles).
!gdown --id 1jiu9E1NalT2Y8EIuWNa1xf2Tw1f1XuGd -O wiki_texts_part_0.txt.gz
!gdown --id 1ABblLRd9HXdXvaNv8H9fFq984bhnowoG -O wiki_texts_part_1.txt.gz
!gdown --id 1z2VFNhpPvCejTP5zyejzKj5YjI_Bn42M -O wiki_texts_part_2.txt.gz
!gdown --id 1VKjded9BxADRhIoCzXy_W8uzVOTWIf0g -O wiki_texts_part_3.txt.gz
!gdown --id 16mBeG26m9LzHXdPe8UrijUIc6sHxhknz -O wiki_texts_part_4.txt.gz

# Download the split Wikipedia files
# Each file contain 562365 lines (articles), except the last file.
!gdown --id 17JFvxOH-kc-VmvGkhG7p3iSZSpsWdgJI -O wiki_texts_part_5.txt.gz
!gdown --id 19IvB2vOJRGlrYulnTXlZECR8zT5v550P -O wiki_texts_part_6.txt.gz
!gdown --id 1sjwO8A2SDOKruv6-8NEq7pEIuQ50ygVV -O wiki_texts_part_7.txt.gz
!gdown --id 1s7xKWJmyk98Jbq6Fi1scrHy7fr_ellUX -O wiki_texts_part_8.txt.gz
!gdown --id 17eQXcrvY1cfpKelLbP2BhQKrljnFNykr -O wiki_texts_part_9.txt.gz
!gdown --id 1J5TAN6bNBiSgTIYiPwzmABvGhAF58h62 -O wiki_texts_part_10.txt.gz

# Extract the downloaded wiki_texts_parts files.
# -k : save origin file !gunzip -k wiki_texts_part_*.gz
!gunzip wiki_texts_part_*.gz

# Combine the extracted wiki_texts_parts files.
!cat wiki_texts_part_*.txt > wiki_texts_combined.txt

# Check the first ten lines of the combined file
!head -n 10 wiki_texts_combined.txt

"""Please note that we used the default parameters of [`gensim.corpora.wikicorpus.WikiCorpus`](https://radimrehurek.com/gensim/corpora/wikicorpus.html#gensim.corpora.wikicorpus.WikiCorpus) for cleaning the Wiki raw file. Thus, words with one character were discarded."""

# # use local cpu (ryzen 5 pro)
# import gzip
# import shutil
# import os

# # 解压 .gz 文件
# def gunzip_file(input_file, output_file):
#     with gzip.open(input_file, 'rb') as f_in:
#         with open(output_file, 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)

# # 解压所有 .gz 文件
# # for i in range(10):
# #     input_gz = f"wiki_texts_part_{i}.txt.gz"
# #     output_txt = f"wiki_texts_part_{i}.txt"
# #     print(f"Unzipping {input_gz}...")
# #     gunzip_file(input_gz, output_txt)
# #     print(f"{input_gz} unzipped!")

# with open('wiki_texts_combined.txt', 'w', encoding='utf-8') as outfile:
#     for i in range(11):
#         txt_file = f"wiki_texts_part_{i}.txt"
#         with open(txt_file, 'r', encoding='utf-8', errors='ignore') as infile:
#             outfile.write(infile.read())

# print("All text files have been combined into wiki_texts_combined.txt")

# # 查看合并文件的前 10 行
# with open('wiki_texts_combined.txt', 'r', encoding='utf-8') as combined_file:
#     for _ in range(10):
#         print(combined_file.readline().strip())

# Now you need to do sampling because the corpus is too big.
# You can further perform analysis with a greater sampling ratio.

import random

wiki_txt_path = "wiki_texts_combined.txt"
output_path   = "random_text.txt"
# wiki_texts_combined.txt is a text file separated by linebreaks (\n).
# Each row in wiki_texts_combined.txt indicates a Wikipedia article.

with open(wiki_txt_path, "r", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as output_file:
    # TODO4: Sample `20%` Wikipedia articles
    # Write your code here (ask claude)
      for line in f:
          if random.random() < 0.2:  # 20%的概率(ask claude：每一行都有獨立的20%機會被選中、不需要一次將所有內容讀入)
              output_file.write(line)

# from google.colab import drive
# drive.mount('/content/drive')

# !unzip /content/drive/MyDrive/random_text_20.zip

import gensim
from gensim.models import Word2Vec
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import re
from tqdm import tqdm

# TODO5: Train your own word embeddings with the sampled articles
# https://radimrehurek.com/gensim/models/word2vec.html#gensim.models.word2vec.Word2Vec
# Hint: You should perform some pre-processing before training.
# ask ChatGPT how to use

nltk.download('punkt') # 句子分割
nltk.download('stopwords')
nltk.download('wordnet') # Lemmatization
nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # text = text.lower()
    tokens = word_tokenize(text)

    #Remove non-English words
    # tokens = [token for token in tokens if token.isalpha() and re.match(r'^[a-zA-Z]+$', token)]

    # 移除停用詞
    tokens = [token for token in tokens if token not in stop_words]

    # 移除標點符號
    tokens = [token for token in tokens if token not in string.punctuation]

    # 詞形還原 (Lemmatization)
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return tokens

# input_file = "/content/drive/MyDrive/NLP/random_text_5.txt"
processed_articles = []
stop_words = set(stopwords.words('english'))

with open(output_path, "r", encoding="utf-8") as f:
    for line in tqdm(f):
        tokens = preprocess_text(line.strip())
        processed_articles.append(tokens)

model = Word2Vec(sentences=processed_articles, vector_size=50, window=3, min_count=5, workers=2)
model.save("word2vec_model_nolower.model")

import pandas as pd
import pandas as pd
import numpy as np
import gensim.downloader
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

data = pd.read_csv("questions-words.csv")

# Do predictions and preserve the gold answers (word_D)
preds = []
golds = []

model = Word2Vec.load("word2vec_model_nolower.model")

for analogy in tqdm(data["Question"]):
      # TODO6: Write your code here to use your trained word embeddings for getting predictions of the analogy task.
      # You should also preserve the gold answers during iterations for evaluations later.
      # ask ChatGPT
      """ Hints
      # Unpack the analogy (e.g., "man", "woman", "king", "queen")
      # Perform vector arithmetic: word_b + word_c - word_a should be close to word_d
      # Source: https://github.com/piskvorky/gensim/blob/develop/gensim/models/keyedvectors.py#L776
      # Mikolov et al., 2013: big - biggest and small - smallest
      # Mikolov et al., 2013: X = vector(”biggest”) − vector(”big”) + vector(”small”).
      """
      word_a, word_b, word_c, gold_answer = analogy.split()

      try:

          if hasattr(model, 'wv'):  # 检查 model 是否有 wv 属性 (适用于 gensim 4.x)
              result_vector = model.wv[word_b] + model.wv[word_c] - model.wv[word_a]
              predicted_word = model.wv.most_similar(positive=[result_vector], topn=1)[0][0]
          else:  # 适用于 gensim 3.x
              result_vector = model[word_b] + model[word_c] - model[word_a]
              predicted_word = model.most_similar(positive=[result_vector], topn=1)[0][0]

          preds.append(predicted_word)
          golds.append(gold_answer)

      except KeyError as e:
          preds.append(None)
          golds.append(gold_answer)

# Perform evaluations. You do not need to modify this block!!

def calculate_accuracy(gold: np.ndarray, pred: np.ndarray) -> float:
    return np.mean(gold == pred)

golds_np, preds_np = np.array(golds), np.array(preds)
data = pd.read_csv("questions-words.csv")

# Evaluation: categories
for category in data["Category"].unique():
    mask = data["Category"] == category
    golds_cat, preds_cat = golds_np[mask], preds_np[mask]
    acc_cat = calculate_accuracy(golds_cat, preds_cat)
    print(f"Category: {category}, Accuracy: {acc_cat * 100}%")

# Evaluation: sub-categories
for sub_category in data["SubCategory"].unique():
    mask = data["SubCategory"] == sub_category
    golds_subcat, preds_subcat = golds_np[mask], preds_np[mask]
    acc_subcat = calculate_accuracy(golds_subcat, preds_subcat)
    print(f"Sub-Category{sub_category}, Accuracy: {acc_subcat * 100}%")

# Collect words from Google Analogy dataset
SUB_CATEGORY = ": family"

# TODO7: Plot t-SNE for the words in the SUB_CATEGORY `: family`
family_words = data[data["SubCategory"] == ": family"]["Question"].str.split().tolist()
family_words = [word for sublist in family_words for word in sublist]
family_words = list(set(family_words))

words_vectors = []
words = []
for word in family_words:
    if word in model.wv:
        words_vectors.append(model.wv[word])
        words.append(word)

words_vectors = np.array(words_vectors)
tsne = TSNE(n_components=2, random_state=0)
reduced_vectors = tsne.fit_transform(words_vectors)

plt.figure(figsize=(10, 8))
plt.scatter(reduced_vectors[:, 0], reduced_vectors[:, 1])

# add tag
for i, word in enumerate(words):
    plt.text(reduced_vectors[i, 0], reduced_vectors[i, 1], word, fontsize=9)

plt.title("Word Relationships from Google Analogy Task")
plt.show()
plt.savefig("word_relationships.png", bbox_inches="tight")