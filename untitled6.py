# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1htxcaBxvH-GDnhM7QXqN78zld7ePelgs
"""

!pip install transformers datasets evaluate

from google.colab import files
files.upload()

!mkdir ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
!unzip imdb-dataset-of-50k-movie-reviews.zip

import pandas as pd

df = pd.read_csv("IMDB Dataset.csv")
df.head()

import pandas as pd
from datasets import Dataset

df = pd.read_csv("IMDB Dataset.csv")
df = df.sample(frac=1).reset_index(drop=True)
df["label"] = df["sentiment"].map({"negative": 0, "positive": 1})
df_small = df[:5000]
dataset = Dataset.from_pandas(df_small[["review", "label"]])

from transformers import AutoTokenizer
checkpoint = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
def tokenize_function(example):
    return tokenizer(example["review"], truncation=True, padding="max_length", max_length=256)
tokenized_dataset = dataset.map(tokenize_function, batched=True)

tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.2)

from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
import evaluate
import os
os.environ["WANDB_DISABLED"] = "true"
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)
accuracy = evaluate.load("accuracy")
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = logits.argmax(axis=-1)
    return accuracy.compute(predictions=predictions, references=labels)
training_args = TrainingArguments(
    output_dir="bert-finetuned-imdb",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    logging_dir="logs",
    logging_steps=10,
    load_best_model_at_end=True
)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)
trainer.train()

trainer.evaluate()

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = logits.argmax().item()
    return "positive" if predicted_class == 1 else "negative"
predict_sentiment("This movie was absolutely wonderful!")