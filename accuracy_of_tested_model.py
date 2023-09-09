import json
import csv
import math
import pandas as pd



# input_vector = ['output_predictions_test_20k_reformatted_1.json', 'output_predictions_test_60k_reformatted.json', 'output_predictions_test_80k_reformatted.json', 'output_predictions_test_100k_reformatted.json', 'output_predictions_test_llama-7b-tcp-20k_reformatted.json', 'output_predictions_test_llama-7b-tcp-40k_reformatted.json', 'output_predictions_test_llama-7b-tcp-60k_reformatted.json', 'output_predictions_test_llama-7b-tcp-80k_reformatted.json', 'output_predictions_test_llama-7b-tcp-100k_reformatted.json']
# name = ["Llama-2-13b-20k-dataset", "Llama-2-13b-60k-dataset", "Llama-2-13b-80k-dataset", "Llama-2-13b-100k-dataset", "Llama-2-7b-20k-dataset", "Llama-2-7b-40k-dataset", "Llama-2-7b-60k-dataset", "Llama-2-7b-80k-dataset", "Llama-2-7b-100k-dataset"]
# input_vector = ['output_predictions_test_20k_final_version.json','output_predictions_test_40k_final_version.json' , 'output_predictions_test_60k_final_version.json', 'output_predictions_test_80k_final_version.json', 'output_predictions_test_100k_final_version.json', 'output_predictions_test_llama-7b-tcp-20k_final_version.json', 'output_predictions_test_llama-7b-tcp-40k_final_version.json','output_predictions_test_llama-7b-tcp-100k_final_version.json', 'output_predictions_test_20k_10_epochs_final_version.json', 'output_predictions_test_50k_4_epochs_final_version.json', 'output_predictions_test_100k_2_epochs_final_version.json'] # , 'output_predictions_test_llama-7b-tcp-80k_reformatted.json', 'output_predictions_test_llama-7b-tcp-100k_reformatted.json']
# name = ["Llama-2-13b-20k-dataset", "Llama-2-13b-40k-dataset", "Llama-2-13b-60k-dataset", "Llama-2-13b-80k-dataset", "Llama-2-13b-100k-dataset", "Llama-2-7b-20k-dataset", "Llama-2-7b-40k-dataset", "Llama-2-7b-100k-dataset", "Llama-2-13b-20k-dataset_10_epoch", "Llama-2-13b-50k-dataset_4_epoch", "Llama-2-13b-100k-dataset_2_epoch"] #, "Llama-2-7b-80k-dataset", "Llama-2-7b-100k-dataset"]

input_vector = ['distilgpt2-20k-epoch1_final_version.json','distilgpt2-50k-epoch1_final_version.json' , 'distilgpt2-100k-epoch1_final_version.json', 'distilgpt2-100k-epoch5_final_version.json', 'distilgpt2-100k-epoch10_final_version.json'] # , 'output_predictions_test_gpt2_100k_5_epochs_final_version.json', 'output_predictions_test_gpt2_100k_10_epochs_final_version.json'] # , 'output_predictions_test_llama-7b-tcp-20k_final_version.json', 'output_predictions_test_llama-7b-tcp-40k_final_version.json', 'output_predictions_test_llama-7b-tcp-60k_final_version.json', 'output_predictions_test_llama-7b-tcp-80k_final_version.json','output_predictions_test_llama-7b-tcp-100k_final_version.json', 'output_predictions_test_20k_10_epochs_final_version.json', 'output_predictions_test_50k_4_epochs_final_version.json', 'output_predictions_test_100k_2_epochs_final_version.json'] # , 'output_predictions_test_llama-7b-tcp-80k_reformatted.json', 'output_predictions_test_llama-7b-tcp-100k_reformatted.json']
name = ["distilgpt2-20k-epoch1", "distilgpt2-50k-epoch1", "distilgpt2-100k-epoch1", "distilgpt2-100k-epoch5", "distilgpt2-100k-epoch10"] # , "Llama-2-7b-20k-dataset", "Llama-2-7b-40k-dataset", "Llama-2-7b-60k-dataset", "Llama-2-7b-80k-dataset", "Llama-2-7b-100k-dataset", "Llama-2-13b-20k-dataset_10_epoch", "Llama-2-13b-50k-dataset_4_epoch", "Llama-2-13b-100k-dataset_2_epoch"]

fields_vector = ["source", "destination", "sport", "dport", "flags", "seq", "ack", "length"]
message_vectors = [[] for _ in range(9)]
message_vectors_shorten = [0, 0]
field_mesg_wrong = [[0.0 for _ in range(len(fields_vector))] for _ in range(len(input_vector))]
field_pct_right = [[0.0 for _ in range(len(fields_vector))] for _ in range(len(input_vector))]
stnd_dev, avg_time, entries_total,average_amnt_errors = [], [], [], []
file_count = 0
for input_file_path in input_vector:
    field_vector = fields_vector
    section_vector  = ["Question", "Predicted_TCP_Packet", "Correct_Answer"]
    entry_vector = ['Entry']
    field_data = {section: {field: [] for field in field_vector} for section in section_vector}
    field_correction_check = {field: [] for field in field_vector}
    time_list= []
    error_vector = [[] for _ in range(9)]

    with open(input_file_path, 'r') as f:
        data = json.load(f)
    context_data = {entry_num: [{field: [] for field in field_vector} for _ in range(len(entry['Context']))] for entry_num, entry in enumerate(data)}

    for entry_num, entry in enumerate(data):
        context_list = entry['Context']
        for context_num, context in enumerate(context_list):
            for field in field_vector:
                context_data[entry_num][context_num][field] = context[field]


    for entry in data:
        for field in field_vector:
            for section in section_vector:
                value = entry[section][field]
                field_data[section][field].append(value)
        time = entry["Time_Taken"]
        time_list.append(time)

    for index in range(len(field_data["Question"]["flags"])):
        for field in field_vector:
            if field_data["Predicted_TCP_Packet"][field][index] != field_data["Correct_Answer"][field][index]:
                field_correction_check[field].append(1)
                # field_correction_check[field= 1
            elif field_data["Predicted_TCP_Packet"][field][index] == field_data["Correct_Answer"][field][index]:
                field_correction_check[field].append(0)

    all_wrong = 0
    all_right = 0
    field_errors = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    seq_and_ack_wrong = 0
    only_seq_and_ack_wrong = 0
    source_des_sport_dport_wrong = 0
    source_des_sport_dport_right = 0
    source_des_sport_dport_correctness_level = 0
    source_des__right = 0
    seq_and_ack_correctness_level = 0
    total_entries = len(field_data["Question"]["flags"])
    total_errors = 0
    errors = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for index in range(len(field_data["Question"]["flags"])):
        if field_correction_check[field_vector[5]][index] == field_correction_check[field_vector[6]][index] == 1:
            if "F" in field_data[section_vector[0]][field_vector[4]][index] or "S" in field_data[section_vector[0]][field_vector[4]][index]:
                if (field_data[section_vector[0]][field_vector[5]][index] + 1) == field_data[section_vector[1]][field_vector[6]][index]:
                    if field_data[section_vector[0]][field_vector[6]][index] == field_data[section_vector[1]][field_vector[5]][index]:
                        if field_data[section_vector[0]][field_vector[0]][index] == field_data[section_vector[1]][field_vector[1]][index]:
                            for field_num in range(len(field_vector)):
                                if field_num != 4 or field_num != 7:
                                    field_correction_check[field_vector[field_num]][index] = 0
            if (field_data[section_vector[0]][field_vector[5]][index] + field_data[section_vector[0]][field_vector[7]][index]) == field_data[section_vector[1]][field_vector[6]][index]:
                if field_data[section_vector[0]][field_vector[6]][index] == field_data[section_vector[1]][field_vector[5]][index]:
                    if field_data[section_vector[0]][field_vector[0]][index] == field_data[section_vector[1]][field_vector[1]][index]:
                        for field_num in range(len(field_vector)):
                            if field_num != 4 or field_num != 7:
                                field_correction_check[field_vector[field_num]][index] = 0
            if field_data[section_vector[0]][field_vector[0]][index] == field_data[section_vector[1]][field_vector[0]][index]:
                if field_data[section_vector[0]][field_vector[6]][index] == field_data[section_vector[1]][field_vector[6]][index]:
                    if field_data[section_vector[0]][field_vector[7]][index] == field_data[section_vector[1]][field_vector[7]][index]:
                        for field_num in range(len(field_vector)):
                            if field_num != 4 or field_num != 7:
                                field_correction_check[field_vector[field_num]][index] = 0

            # for value in range(len(field_data["Question"]["flags"])):  # range(index -1, -1, -1):
            for context_range in range(len(data[0]['Context'])):
                if "F" in context_data[index][context_range][field_vector[4]] or "S" in context_data[index][context_range][field_vector[4]]:
                    if (context_data[index][context_range][field_vector[5]] + 1) == field_data[section_vector[1]][field_vector[6]][index]:
                        if context_data[index][context_range][field_vector[6]] == field_data[section_vector[1]][field_vector[5]][index]:
                            if context_data[index][context_range][field_vector[0]] == field_data[section_vector[1]][field_vector[1]][index]:
                                for field_num in range(len(field_vector)):
                                    if field_num != 4 or field_num != 7:
                                        field_correction_check[field_vector[field_num]][index] = 0
                                    if field_num == 4:
                                        if "A" in field_data[section_vector[1]][field_vector[field_num]][index]:
                                            field_correction_check[field_vector[field_num]][index] = 0
                if (context_data[index][context_range][field_vector[5]] + context_data[index][context_range][field_vector[7]]) == field_data[section_vector[1]][field_vector[6]][index]:
                    if context_data[index][context_range][field_vector[6]] == field_data[section_vector[1]][field_vector[5]][index]:
                        if context_data[index][context_range][field_vector[0]] == field_data[section_vector[1]][field_vector[1]][index]:
                            for field_num in range(len(field_vector)):
                                if field_num != 4 or field_num != 7:
                                    field_correction_check[field_vector[field_num]][index] = 0
                                if field_num == 4 and "P" in context_data[index][context_range][field_vector[4]] and "A" in context_data[index][context_range][field_vector[4]]:
                                    field_correction_check[field_vector[field_num]][index] = 0
                                if field_num == 4 and "A" in context_data[index][context_range][field_vector[4]] and "P" in context_data[index][context_range][field_vector[4]]:
                                    field_correction_check[field_vector[field_num]][index] = 0
                            if field_data[section_vector[1]][field_vector[4]][index] == "A" and field_data[section_vector[1]][field_vector[7]][index] == 0:
                                field_correction_check[field_vector[7]][index] = 0

                if context_data[index][context_range][field_vector[0]]  == field_data[section_vector[1]][field_vector[0]][index]:
                    if context_data[index][context_range][field_vector[6]]  == field_data[section_vector[1]][field_vector[6]][index]:
                        if context_data[index][context_range][field_vector[7]]  == field_data[section_vector[1]][field_vector[7]][index]:
                            for field_num in range(len(field_vector)):
                                if field_num != 4 or field_num != 7:
                                    field_correction_check[field_vector[field_num]][index] = 0
                                if field_num == 4 and "P" in context_data[index][context_range][field_vector[4]] and "A" in context_data[index][context_range][field_vector[4]]:
                                    field_correction_check[field_vector[field_num]][index] = 0
                                if field_num == 4 and "A" in context_data[index][context_range][field_vector[4]] and "P" in context_data[index][context_range][field_vector[4]]:
                                    field_correction_check[field_vector[field_num]][index] = 0

        if field_data[section_vector[2]][field_vector[7]][index] != 0 and field_data[section_vector[1]][field_vector[3]][index] != "A" and field_data[section_vector[2]][field_vector[7]][index] != 0:
            field_correction_check[field_vector[7]][index] = 0

        if field_data[section_vector[1]][field_vector[5]][index] != field_data[section_vector[2]][field_vector[5]][index]:
            if field_data[section_vector[0]][field_vector[6]][index] == 0 or field_data[section_vector[0]][field_vector[6]][
                index] is None:
                field_correction_check[field_vector[5]][index] = 0
        if field_data[section_vector[0]][field_vector[1]][index] is None:
            for i in range(4):
                field_correction_check[field_vector[i]][index] = 0
        value = field_correction_check[field_vector[0]][index]
        checking_num = 0
        checking_num_1 = 0
        checking_num_2 = 0
        for field_num in range(len(field_vector)):
            if 0 == field_correction_check[field_vector[field_num]][index]:
                checking_num += 1
        if checking_num == (len(field_vector)):
            all_right += 1
        for checking_first_four_fields in range(4):
            if value == field_correction_check[field_vector[checking_first_four_fields]][index]:
                checking_num_1 += 1
        if checking_num_1 == 4:
            source_des_sport_dport_correctness_level += 1
        for checking_first_four_fields in range(4):
            if 0 == field_correction_check[field_vector[checking_first_four_fields]][index]:
                checking_num_2 += 1
        if checking_num_2 == 4:
            source_des_sport_dport_right += 1
        if 1 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[1] += 1
            if field_correction_check["source"][index] == 1:
                field_errors[0] += 1
            elif field_correction_check["destination"][index] == 1:
                field_errors[1] += 1
            elif field_correction_check["sport"][index] == 1:
                field_errors[2] += 1
            elif field_correction_check["dport"][index] == 1:
                field_errors[3] += 1
            elif field_correction_check["flags"][index] == 1:
                field_errors[4] += 1
            elif field_correction_check["seq"][index] == 1:
                field_errors[5] += 1
            elif field_correction_check["ack"][index] == 1:
                field_errors[6] += 1
            elif field_correction_check["length"][index] == 1:
                field_errors[7] += 1
        if field_correction_check["seq"][index] == field_correction_check["ack"][index]:
            seq_and_ack_correctness_level += 1
        if 2 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[2] += 1
            if field_correction_check["seq"][index] == field_correction_check["ack"][index] == 1:
                only_seq_and_ack_wrong += 1
        if (len(field_vector) - 2) >= sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            if field_correction_check["source"][index] == field_correction_check["destination"][index] == 0:
                source_des__right += 1
        if len(field_vector)  == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            all_wrong += 1
        total_errors += sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index)
        if 0 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[0] += 1
        if 3 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[3] += 1
        if 4 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[4] += 1
        if 5 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[5] += 1
        if 6 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[6] += 1
        if 7 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[7] += 1
        if 8 == sum(field_correction_check[field][index] for field in field_vector if len(field_correction_check[field]) > index):
            errors[8] += 1

    def print_percentage(name, percentage):
        print(f"{name} is correct: {(percentage * 100) :.4f}%")

    def print_percentage2(name, percentage):
        print(f"{name} is only wrong: {(percentage * 100) :.4f}%")

    def print_percentage3(name, percentage):
        print(f"{name}: {(percentage * 100) :.4f}%")

    def print_1(variable, name):
        print(f"Total messages with {name} errors: {variable}")

    for field_count in range(len(field_vector)):
        print_percentage(field_vector[field_count], 1 - (sum(field_correction_check[field_vector[field_count]])) / len(field_data["Question"]["source"]))
        field_pct_right[file_count][field_count] = round((1 - (sum(field_correction_check[field_vector[field_count]])) / len(field_data["Question"]["source"])) * 100, 4)

    print_percentage3("all is right", all_right / len(field_data["Question"]["source"]))
    print_percentage3("all is wrong", all_wrong / len(field_data["Question"]["source"]))
    print_percentage3("First 4 fields have same correctness level", source_des_sport_dport_correctness_level / len(field_correction_check[field_vector[0]]))
    print_percentage3("seq and ack have same correctness level", seq_and_ack_correctness_level / len(field_correction_check[field_vector[0]]))
    print_percentage3("First 4 fields are right", source_des_sport_dport_right / len(field_correction_check[field_vector[0]]))
    print_percentage3("Source and destination are right", source_des__right / len(field_correction_check[field_vector[0]]))

    for index in range(len(field_vector)):
        print_percentage2(field_vector[index], field_errors[index] / len(field_correction_check[field_vector[0]]))
        field_mesg_wrong[file_count][index] = round((field_errors[index] / len(field_correction_check[field_vector[0]])) * 100, 4)

    error_mean = total_errors / total_entries
    average_amnt_errors.append(error_mean)
    standard_deviation_sum = 0

    print(f"Average amount of errors:  {error_mean :.4f}")

    for index in range(len(errors)):
        standard_deviation_sum += (errors[index] * (index - error_mean) ** 2)


    for index in range(len(errors)):
        print_1(errors[index], index)
        message_vectors[index].append(errors[index])

    standard_deviation =  math.sqrt(standard_deviation_sum / (total_entries -1))
    stnd_dev.append(standard_deviation)
    print(f"Standard Deviation: {standard_deviation :.4f}")
    print(f"Average time: {sum(time_list) / total_entries :.4f}")
    avg_time.append(sum(time_list) / total_entries)
    print("Total entries", total_entries)
    entries_total.append(total_entries)
    print("\n", input_file_path)
    print("=" * 30)

    file_count += 1

data = {
    "Name": name,
    "Total Entries": entries_total,
    "Standard Deviation": stnd_dev,
    "Average Amount of Errors": average_amnt_errors,
    "Average time": avg_time,
}
for count in range(len(fields_vector)):
        data[f"{fields_vector[count]} is right"] = [field_placement[count] for field_placement in field_pct_right]

for i in range(9):
    data[f"Messages with {i} errors"] = message_vectors[i]

for count in range(len(fields_vector)):
        data[f"{fields_vector[count]} is only wrong"] = [field_placement[count] for field_placement in field_mesg_wrong]

# data[f"Messages with 1-2 errors"] = (((message_vectors[1] + message_vectors[2]) / total_entries) * 100)
# data[f"Messages with 1-2 errors"] = (((message_vectors[3] + message_vectors[4] + message_vectors[5] + message_vectors[6] + message_vectors[7] + message_vectors[8]) / total_entries) * 100)
df = pd.DataFrame(data)

columns_to_drop = df.columns[df.eq(0).all()]
df = df.drop(columns=columns_to_drop)
df = df.round(4)


df.to_csv("aug_15.csv", index=False)
