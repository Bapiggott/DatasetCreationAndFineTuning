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
#python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_20k/ --final_model_name llama-7b-tcp-20k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_40k/ --final_model_name llama-7b-tcp-40k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_60k/ --final_model_name llama-7b-tcp-60k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_100k/ --final_model_name llama-7b-tcp-80k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_100k_real/ --final_model_name llama-7b-tcp-100k
# python3 testing_modal_8_14_qna_1.py; wait 90; python3 testing_modal_8_14_qna_2.py; wait 90; python3 testing_modal_8_14_qna_3.py; wait 90; python3 testing_modal_8_14_qna_4.py; wait 90; python3 testing_modal_8_14_qna_5.py
# test_modal_100_2_e.py
# python3 test_modal_100_2_a.py; wait 90; python3 test_modal_100_2_b.py; wait 90; python3 test_modal_100_2_c.py; wait 90; python3 test_modal_100_2_d.py; wait 90; python3 test_modal_100_2_e.py