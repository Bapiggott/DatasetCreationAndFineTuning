import pandas as pd
import json

# Read the JSON file
with open("bigFlowWithLength100k.json", "r") as json_file:
    data = json.load(json_file)

formatted_data = []

# Loop through each record in the list
for record in data:
    formatted_record = {
        "Context": record["Context"],
        "Question": record["Question"],
        "Answer": record["Answer"]
    }
    formatted_data.append(formatted_record)

# Create a DataFrame from the formatted data
df = pd.DataFrame(formatted_data)

# Perform your operations on the DataFrame
df = df.fillna("")

text_col = []
for _, row in df.iterrows():
    prompt = "Provided below is a question detailing key attributes of a TCP packet. Preceding this question is a series of TCP packets, which together form the context. Please continue the sequence by providing the subsequent TCP packet that follows the question, serving as the answer. \n\n"
    question = str(row["Question"])
    context = str(row["Context"])
    answer = str(row["Answer"])

    text = prompt + "### Context:\n" + context + "\n### Question\n" + question + "\n### Answer:\n" + answer

    text_col.append(text)

df.loc[:, "text"] = text_col

# Print or save the DataFrame as needed
print(df.head())
df.to_csv("data_100k.csv", index=False)
