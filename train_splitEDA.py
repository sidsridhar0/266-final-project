#!/usr/bin/env python
# coding: utf-8

# ### Installs and Imports

# In[43]:


get_ipython().system('pip install -q  -U transformers')
get_ipython().system('pip install -q -U datasets')
get_ipython().system('pip install -q -U evaluate')
get_ipython().system('pip install -q tokenizers')


# In[44]:


import os
import re
import json
import random
import numpy as np
import pandas as pd
import torch


# In[45]:


from datasets import Dataset, DatasetDict
import evaluate


# In[46]:


from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback
)


# In[47]:


print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))


# ### Load Training split

# In[48]:


from google.colab import drive
drive.mount('/content/drive')


# In[49]:


save_dir = "/content/drive/MyDrive/Colab Notebooks/266/266_final_project/"

train_file = os.path.join(save_dir, "train_split.json")
test_file = os.path.join(save_dir, "test_split.json")

train_df = pd.read_json(train_file)
test_df = pd.read_json(test_file)

print("Train shape:", train_df.shape)
print("Test shape:", test_df.shape)

print(train_df.columns.tolist())


# In[50]:


display(train_df.head(2))


# In[51]:


print(train_df["report"].isna().sum())
print(test_df["report"].isna().sum())

print(train_df["report"].str.len().describe())


# In[52]:


# inspect the raw table format
print(train_df.iloc[0]["table_data"])

for i in range(3):
    print(f"\n===== EXAMPLE {i} =====")
    print(train_df.iloc[i]["table_data"][:3000])



# #### Convert data in long format - table linearization

# In[53]:


from io import StringIO

def linearize_table(table_str):
    # Convert the raw string to a DataFrame using fixed-width format
    df = pd.read_fwf(StringIO(table_str))

    # Build "col: value" pairs row by row
    rows = []
    for _, row in df.iterrows():
        parts = [f"{col}: {row[col]}" for col in df.columns]
        rows.append(", ".join(parts))

    # Join rows with separator
    return " | ".join(rows)



# In[54]:


sample = train_df.iloc[0]["table_data"]
print(linearize_table(sample)[:2000])


# In[55]:


print(repr(sample[:300]))


# check the linearized table

# In[56]:


sample = train_df.iloc[0]["table_data"]

parsed = pd.read_fwf(StringIO(sample))

print(parsed.shape)
print(parsed.columns.tolist())
print(parsed.head())
print(parsed.tail())
print(parsed.isna().sum())


# By doing linearization, we are fine-tuning the model's weights on paired (input, output) examples. It's the serialized form of structured data, because the encoder needs a linear sequence of tokens as input.
# 
# We are doing serialization because we are using pretrained encoder-decoder T5 or BART. Since these models were pretrained on text, their embeddings and positional encodings are built for token sequences, so the format cannot be a table cell or row or column.

# Loading model t5-small

# In[57]:


model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)


# In[58]:


#  encoder input
def build_encoder_input(row):

    linear_table = linearize_table(row["table_data"])

    return (
        "Generate a financial market report. "
        f"Instruction: {row['instruction']} "
        f"Financial data: {linear_table}"
    )

# apply to df
train_df["encoder_input"] = train_df.apply(build_encoder_input, axis=1)
test_df["encoder_input"] = test_df.apply(build_encoder_input, axis=1)
train_df["decoder_target"] = train_df["report"]
test_df["decoder_target"] = test_df["report"]


# In[59]:


#  check input output length
def token_length(text):
    return len(tokenizer(str(text),truncation=False)["input_ids"])


# In[60]:


# calculate length
train_df["input_length"] = train_df["encoder_input"].apply(token_length)
train_df["target_length"] = train_df["decoder_target"].apply(token_length)


# In[61]:


print(train_df["input_length"].describe(percentiles=[0.50, 0.75, 0.90, 0.95, 0.99]))
print(train_df["target_length"].describe(percentiles=[0.50, 0.75, 0.90, 0.95, 0.99]))

print("Input > 512:",(train_df["input_length"] > 512).mean())
print("Target > 256:",(train_df["target_length"] > 256).mean())


# In[62]:


#  input lengths are too long
sample = train_df.iloc[0]
print("Raw table_data length (chars):", len(sample["table_data"]))
print(sample["table_data"][:2000])
print("...")
print("Number of rows in raw table_data:", sample["table_data"].count("\n"))


# In[63]:


# quick check: how many rows does the raw table actually have?
train_df["raw_table_rows"] = train_df["table_data"].apply(lambda x: len([l for l in x.split("\n") if l.strip()]))
print(train_df["raw_table_rows"].describe())


# The length inputs are too long, we need to shorten the length so that the tokenizer can work on max 512 tokens. This is same with T5 base/ T5 large models

# ## Redoing Linearized table to reduce input length
# 
# 

# In[64]:


from io import StringIO

def linearize_table_compact(table_str):

    table_df = pd.read_fwf(StringIO(str(table_str)))

    # Remove completely empty rows and columns
    table_df = table_df.dropna(how="all")
    table_df = table_df.dropna(axis=1, how="all")

    # Constant metadata
    metadata_parts = []

    for col in ["Product Name", "Symbol"]:
        if col in table_df.columns:
            values = table_df[col].dropna().unique()

            if len(values) > 0:
                metadata_parts.append(f"{col}: {values[0]}")

    # Keep only useful numerical/time-series columns
    keep_cols = [
        col for col in [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]if col in table_df.columns]

    table_df = table_df[keep_cols]

    # Convert rows into compact text
    header = " | ".join(table_df.columns)

    rows = []

    for _, row in table_df.iterrows():

        values = []

        for value in row:

            if pd.isna(value):
                values.append("N/A")
            else:
                values.append(str(value))

        rows.append(" | ".join(values))

    table_text = "\n".join(rows)

    return "\n".join(metadata_parts) + "\n\n" + header + "\n" + table_text


# In[65]:


sample = train_df.iloc[0]["table_data"]
print(linearize_table(sample)[:2000])


# In[66]:


sample = train_df.iloc[0]["table_data"]

parsed = pd.read_fwf(StringIO(sample))

print(parsed.shape)
print(parsed.columns.tolist())
print(parsed.head())
print(parsed.tail())
print(parsed.isna().sum())


# The above function did not reduce the length.

# In[67]:


# recreate encoder
def build_encoder_input(row):

    linear_table = linearize_table_compact(row["table_data"])

    return (
        "Generate a financial market report.\n"
        f"Instruction: {row['instruction']}\n\n"
        f"Financial data:\n{linear_table}")


# In[68]:


train_df["encoder_input"] = train_df.apply(build_encoder_input,axis=1)

test_df["encoder_input"] = test_df.apply(build_encoder_input,axis=1)


# In[69]:


# recalculate
train_df["input_length"] = train_df["encoder_input"].apply(token_length)

train_df["target_length"] = train_df["decoder_target"].apply(token_length)

print(train_df["input_length"].describe(
    percentiles=[0.50, 0.75, 0.90, 0.95, 0.99]))


# The above function did not help reduce the input length. The table contains multiple futures contracts in the same table_data. The first summary function incorrectly treated the entire table as one continuous time series. Each trading day has actually multiple contracts × observation. This needs to be fixed before training. We need to summarize each contract separately and calculate statistics within each Symbol. We should also remove blank row/columns, metadata, use correct datatypes etc.

# In[70]:


def summarize_market_table(table_str):

    table_df = pd.read_fwf(StringIO(str(table_str)))

    # Remove completely empty rows/columns
    table_df = table_df.dropna(how="all")
    table_df = table_df.dropna(axis=1, how="all")

    # Convert date
    if "Date" in table_df.columns:
        table_df["Date"] = pd.to_datetime(table_df["Date"],errors="coerce")

    # Convert numerical columns
    numeric_cols = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]
    for col in numeric_cols:
        if col in table_df.columns:
            table_df[col] = pd.to_numeric(table_df[col],errors="coerce")
    table_df = table_df.dropna(subset=["Close"]).reset_index(drop=True)

    if len(table_df) == 0:
        return ""

    summary = []

    # Metadata
    if "Product Name" in table_df.columns:
        product_name = table_df["Product Name"].dropna()

        if len(product_name) > 0:
            summary.append(f"Product: {product_name.iloc[0]}")

    if "Symbol" in table_df.columns:
        symbol = table_df["Symbol"].dropna()

        if len(symbol) > 0:
            summary.append(f"Symbol: {symbol.iloc[0]}")

    # Period information
    if "Date" in table_df.columns:

        start_date = table_df["Date"].min()
        end_date = table_df["Date"].max()

        summary.extend([
            f"Period start: {start_date.date()}",
            f"Period end: {end_date.date()}",
            f"Trading days: {len(table_df)}"
        ])

    # Price statistics
    close = table_df["Close"]
    start_close = close.iloc[0]
    end_close = close.iloc[-1]
    absolute_change = end_close - start_close
    percentage_change = ((end_close - start_close)/ start_close* 100)

    summary.extend([
        f"Starting close: {start_close:.2f}",
        f"Ending close: {end_close:.2f}",
        f"Period high: {table_df['High'].max():.2f}",
        f"Period low: {table_df['Low'].min():.2f}",
        f"Absolute price change: {absolute_change:.2f}",
        f"Percentage price change: {percentage_change:.2f}%"
    ])

    # Volatility
    daily_returns = close.pct_change().dropna()

    if len(daily_returns) > 0:
        volatility = daily_returns.std() * 100

        summary.append(f"Daily return volatility: {volatility:.2f}%")

        max_daily_gain = daily_returns.max() * 100
        max_daily_loss = daily_returns.min() * 100

        summary.extend([
            f"Maximum daily gain: {max_daily_gain:.2f}%",
            f"Maximum daily loss: {max_daily_loss:.2f}%"
        ])

    # Volume
    if "Volume" in table_df.columns:
        volume = table_df["Volume"].dropna()

        if len(volume) > 0:
            summary.extend([
                f"Average volume: {volume.mean():.0f}",
                f"Maximum volume: {volume.max():.0f}",
                f"Minimum volume: {volume.min():.0f}"
            ])

    # Trend
    if percentage_change > 0:
        trend = "Upward"
    elif percentage_change < 0:
        trend = "Downward"
    else:
        trend = "Flat"

    summary.append(f"Overall price trend: {trend}")

    return "\n".join(summary)


# In[71]:


summary = summarize_market_table(train_df.iloc[0]["table_data"])

print(summary)


# Great! now the output looks smaller

# In[72]:


sample_df = pd.read_fwf(StringIO(str(train_df.iloc[0]["table_data"])))

sample_df["Date"] = pd.to_datetime(
    sample_df["Date"],
    errors="coerce"
)

print(sample_df.shape)
print(sample_df["Date"].min())
print(sample_df["Date"].max())
print(sample_df["Date"].nunique())

# print(sample_df[15:40])
print(sample_df.head())
print(sample_df.tail())


# In[73]:


print(sample_df[["Date", "Close", "Volume"]].head(10))

print(sample_df[["Date", "Close", "Volume"]].tail(10))


# In[74]:


print(sample_df["Date"].value_counts().head(10))


# In[76]:


# Converting to .py file and continuing in model1_encoder-decoder.piynb
get_ipython().system('jupyter nbconvert --to python "/content/drive/MyDrive/Colab Notebooks/266/266_final_project/train_splitEDA.ipynb"')


# In[77]:


get_ipython().system('ls -l "/content/drive/MyDrive/Colab Notebooks/266/266_final_project"')


# In[ ]:


# train_df["market_summary"] = train_df["table_data"].apply(summarize_market_table)
# test_df["market_summary"] = test_df["table_data"].apply(summarize_market_table)


# In[ ]:


# train_df["decoder_target"] = train_df["report"]
# test_df["decoder_target"] = test_df["report"]


# ### Build encoder again

# In[ ]:


# def build_encoder_input(row):

#     return (
#         "Generate a financial market report.\n\n"
#         f"Instruction:\n"
#         f"{row['instruction']}\n\n"
#         f"Market summary:\n"
#         f"{row['market_summary']}"
#     )


# In[ ]:


# train_df["encoder_input"] = train_df.apply(build_encoder_input,axis=1)

# test_df["encoder_input"] = test_df.apply(build_encoder_input,axis=1)


# In[ ]:


# train_df["input_length"] = train_df["encoder_input"].apply(token_length)

# print(train_df["input_length"].describe(percentiles=[
#             0.50,
#             0.75,
#             0.90,
#             0.95,
#             0.99
#         ]))


# In[ ]:


# train_df["market_summary"] = train_df["table_data"].apply(summarize_market_table)

# test_df["market_summary"] = test_df["table_data"].apply(summarize_market_table)

