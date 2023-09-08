import os
import subprocess
import json
import shutil
import datetime


def run_pcap_splitter(pcap_file):
    command = f'PcapSplitter -f "{pcap_file}" -o . -m connection'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Processed {pcap_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {pcap_file}: {e}")


# Function to run the commands on a given pcap file
def process_pcap_file(pcap_file):
    pcap_name = os.path.splitext(pcap_file)[0]
    output5_file = f"output5_{pcap_name}.json"
    output6_file = f"output6_{pcap_name}.json"

    # Command 1: tshark
    # command1 = f'tshark -2 -R "tcp" -r "{pcap_file}" -T json -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags.str -e tcp.seq_raw -e tcp.ack_raw -x > {output5_file}'
    # f'tshark -2 -R "tcp and not tcp.flags.window_update" -r "{pcap_file}" -T json -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags.str -e tcp.seq_raw -e tcp.ack_raw -x > {output5_file}'

    # command1 = f'tshark -2 -R "tcp and not Update" -r "{pcap_file}" -T json -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags.str -e tcp.seq_raw -e tcp.ack_raw -e tcp.len -x > {output5_file}'
    command1 = f'tshark -2 -R "tcp" -r "{pcap_file}" -T json -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags.str -e tcp.seq_raw -e tcp.ack_raw -e tcp.len -e tcp.analysis.flags -x > {output5_file}'

    try:
        subprocess.run(command1, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {pcap_file}: {e}")
        return

    with open(output5_file, 'r') as f:
        data = json.load(f)

    total_messages = len(data)

    # Filter out messages with tcp.analysis.flags
    filtered_data = [message for message in data if
                     "_source" in message and "layers" in message["_source"] and "tcp.analysis.flags" not in
                     message["_source"]["layers"]]

    filtered_messages = len(filtered_data)

    if total_messages != filtered_messages:
        print(f"Total messages: {total_messages}")
        print(f"Filtered messages: {filtered_messages}")

        # Overwrite the original JSON file with the filtered data, preserving special characters
        with open(output5_file, 'w') as f:
            json.dump(filtered_data, f, indent=2, ensure_ascii=False)



    # Command 2: jq
    # command2 = f'jq \'map({{ "source": ."_source".layers."ip.src"[0], "destination": ."_source".layers."ip.dst"[0], "sport": (."_source".layers."tcp.srcport"[0] | tonumber), "dport": (."_source".layers."tcp.dstport"[0] | tonumber), "flags": (."_source".layers."tcp.flags.str"[0] | gsub("·"; "")), "seq": (."_source".layers."tcp.seq_raw"[0] | tonumber), "ack": (."_source".layers."tcp.ack_raw"[0] | tonumber) }})\' {output5_file} > {output6_file}'
    command2 = f'jq \'map({{ "source": ."_source".layers."ip.src"[0], "destination": ."_source".layers."ip.dst"[0], "sport": (."_source".layers."tcp.srcport"[0] | tonumber), "dport": (."_source".layers."tcp.dstport"[0] | tonumber), "flags": (."_source".layers."tcp.flags.str"[0] | gsub("·"; "")), "seq": (."_source".layers."tcp.seq_raw"[0] | tonumber), "ack": (."_source".layers."tcp.ack_raw"[0] | tonumber), "length": (."_source".layers."tcp.len"[0] | tonumber) }})\' {output5_file} > {output6_file}'

    try:
        subprocess.run(command2, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {pcap_file}: {e}")
        return

    print(f"Processed {pcap_file}")


def add_na_messages(json_data, Context_size):
    for section_name, section_data in json_data.items():
        new_messages = [
            {
                "source": None, # "n/a",
                "destination": None, # "n/a",
                "sport": None,
                "dport": None,
                "flags": None, # "n/a",
                "seq": None,
                "ack": None,
                "length": None
            }
            for _ in range(Context_size + 1)
        ]
        json_data[section_name] = new_messages + section_data
    return json_data


def create_pcaps_directory():
    if not os.path.exists("pcaps"):
        os.makedirs("pcaps")


# Function to move *.pcap files to the 'pcaps' directory
def move_pcap_files():
    pcap_files = [file for file in os.listdir(".") if file.endswith(".pcap")]

    if not pcap_files:
        print("No *.pcap files found in the current directory.")
        return

    create_pcaps_directory()

    for pcap_file in pcap_files:
        src_path = os.path.join(".", pcap_file)
        dst_path = os.path.join("pcaps", pcap_file)
        shutil.move(src_path, dst_path)
        print(f"Moved {pcap_file} to pcaps directory.")


# Function to extract the first three flags from a JSON file
def extract_flags(json_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        return [entry['flags'] for entry in data[:3]]
    except (json.JSONDecodeError, FileNotFoundError):
        return None


# Function to combine JSON files into one
def combine_json_files(directory_path, output_file):
    combined_data = {}

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            with open(os.path.join(directory_path, filename)) as f:
                json_content = json.load(f)
                # Extract the original title from the filename (without the .json extension)
                title = os.path.splitext(filename)[0]
                combined_data[title] = json_content

    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)

    print("JSON files combined successfully!")


# Function to create a sliding window for JSON data
def create_sliding_window(input_json_file, window_size):
    with open(input_json_file) as f:
        data = json.load(f)

    sliding_window_data = {}

    for file_name, content in data.items():
        sliding_window_data[file_name] = []
        window = []  # Initialize an empty window for each conversation

        for message in content:
            window.append(message)  # Add the current message to the end of the window
            window = window[-window_size:]  # Truncate the window to the specified size

            if len(window) == window_size:  # Only append to output if the window is at the set size
                c_data = window[:-2]
                q_data = window[-2]
                a_data = window[-1]

                sliding_window_data[file_name].append({"Context": c_data, "Question": q_data, "Answer": a_data})

    # Convert sets to lists
    sliding_window_data = convert_sets_to_lists(sliding_window_data)

    output_file_name = f"sliding_window_size.json"
    with open(output_file_name, 'w') as f:
        json.dump(sliding_window_data, f, indent=2)

    print(f"Sliding window JSON created successfully! Output file: {output_file_name}")


# Function to correct flags in JSON data
def flip_flags(flags):
    flag_map = {
        'F': 0,
        'S': 1,
        'R': 2,
        'P': 3,
        'A': 4,
        'U': 5,
        'E': 6,
        'C': 7
    }

    # Initialize the result_flags list with empty strings
    result_flags = ['', '', '', '', '', '', '', '']

    # Assign the characters to their respective positions in result_flags
    for flag in flags:
        if flag in flag_map:
            result_flags[flag_map[flag]] = flag

    # Filter out the empty strings and join the non-empty flags into a single string
    corrected_flags = ''.join(filter(lambda x: x != '', result_flags))

    return corrected_flags


def correct_flags_in_json(json_file):
    # Read the JSON data from the file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Correct the "flags" field in each entry of the JSON data
    for entry in data:
        if 'flags' in entry:
            entry['flags'] = flip_flags(entry['flags'])

    # Save the modified JSON back to the file
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)


def convert_sets_to_lists(obj):
    if isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(element) for element in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj


def process_data(entries):
    output_entries = []
    previous_flag = None
    previous_source = None
    previous_destination = None


    for entry in entries:
        if 'flags' in entry:
            flags = entry['flags']
            source = entry['source']
            destination = entry['source']

            if flags is None or flags != previous_flag:
                output_entries.append(entry)
                previous_flag = flags
                previous_source = source
                previous_destination = destination
            if source != previous_source or destination != previous_destination:
                output_entries.append(entry)
                previous_flag = flags
                previous_source = source
                previous_destination = destination
            else:
                if output_entries:
                    output_entries[-1] = entry  # Replace the last entry with the current one

    return output_entries


# Create a directory to store the processed pcaps
processed_directory = "processed_pcaps"
if not os.path.exists(processed_directory):
    os.makedirs(processed_directory)

# Get a list of all pcap files in the current directory
pcap_files = [file for file in os.listdir(".") if file.endswith(".pcap")]

# Process each pcap file with PcapSplitter command and move the original pcap to the processed directory
for pcap_file in pcap_files:
    run_pcap_splitter(pcap_file)
    shutil.move(pcap_file, os.path.join(processed_directory, pcap_file))

print("All pcap files processed and moved.")

# CODE OF CONVERT_PCAP2JSON.PY

# Record the start time
pcap_files = [file for file in os.listdir(".") if file.endswith(".pcap")]
start_time = datetime.datetime.now()

# Process each pcap file
file_count = len(pcap_files)
interval = 20
for index, pcap_file in enumerate(pcap_files, 1):
    process_pcap_file(pcap_file)

    # Print status after every 'interval' files processed
    if index % interval == 0 or index == file_count:
        elapsed_time = datetime.datetime.now() - start_time
        elapsed_seconds = elapsed_time.total_seconds()
        timestamp = str(datetime.timedelta(seconds=elapsed_seconds))
        print(f"Time elapsed: {timestamp} - {index} files processed out of {file_count}")

# Print the final elapsed time
end_time = datetime.datetime.now()
total_elapsed_time = end_time - start_time
total_elapsed_seconds = total_elapsed_time.total_seconds()
total_timestamp = str(datetime.timedelta(seconds=total_elapsed_seconds))
print(f"\nTotal time elapsed: {total_timestamp}")

for file in os.listdir("."):
    if file.startswith("output5_") and file.endswith(".json"):
        os.remove(file)

# CODE OF TEST.PY

# Get the list of JSON files starting with 'output6_' in the current directory
json_files = [f for f in os.listdir('.') if f.startswith('output6_') and f.endswith('.json')]

# Desired flag sequence to check
desired_flags_sequence = ["S", "AS", "A"]

# Create the output directory if it doesn't exist
output_directory = "output_filtered"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Create a separate directory for files that don't meet the requirements
non_matching_directory = "non_matching_jsons"
if not os.path.exists(non_matching_directory):
    os.makedirs(non_matching_directory)

# Counter for the number of processed files
processed_count = 0

# Filter and copy the matching JSON files
for json_file in json_files:
    # Extract the first three flags from the JSON file
    flags_sequence = extract_flags(json_file)

    # Check if the extracted flags match the desired sequence
    if flags_sequence == desired_flags_sequence:
        # Move the JSON file to the output directory
        shutil.move(json_file, os.path.join(output_directory, json_file))
        processed_count += 1
        print(f"Moved {json_file} to {output_directory}")
    else:
        # Move the JSON file to the non-matching directory
        shutil.move(json_file, os.path.join(non_matching_directory, json_file))
        print(f"Moved {json_file} to {non_matching_directory}")

    # Print progress after processing every 30 files
    if processed_count % 30 == 0:
        total_files = len(json_files)
        progress = processed_count / total_files * 100
        print(f"Progress: {processed_count}/{total_files} files processed ({progress:.2f}%)")

print("Filtering and copying completed.")

# CODE FOR FLAG_MAP.PY
# Path to the directory containing JSON files
json_directory = './output_filtered'

# Get a list of all JSON files in the directory
json_files = [file for file in os.listdir(json_directory) if file.endswith('.json')]

# Correct flags in each JSON file
for json_file in json_files:
    file_path = os.path.join(json_directory, json_file)
    correct_flags_in_json(file_path)

'''# flag_map.py for non-mathing
json_directory = './non_matching_jsons'

# Get a list of all JSON files in the directory
json_files = [file for file in os.listdir(json_directory) if file.endswith('.json')]

# Correct flags in each JSON file
for json_file in json_files:
    file_path = os.path.join(json_directory, json_file)
    correct_flags_in_json(file_path)
'''
# CODE FOR COMBINE_JSON.PY

# Combine JSON files into one
output_combined_file = "output_combined.json"
combine_json_files("./output_filtered", output_combined_file)

# CODE FOR SLIDDING_WINDOW.PY


# Correct flags in the combined JSON file
# correct_flags_in_json(output_combined_file)

# Prompt the user to enter the window size
Context_size = 4
# (int(input("Enter the context size: ")))
window_size = Context_size + 2

# CODE FOR NA_MESSAGES.PY
na_file = "output_na.json"  # Replace with the desired output JSON file path

with open(output_combined_file, "r") as f:
    json_data = json.load(f)

json_data_with_na = add_na_messages(json_data, Context_size)

with open(na_file, "w") as f:
    json.dump(json_data_with_na, f, indent=2)

print("Added {} 'n/a' messages to each section and saved to '{}'".format(Context_size, na_file))



# Create a sliding window for JSON data
create_sliding_window(na_file, window_size)

print("Flag correction and sliding window creation completed.")

with open("sliding_window_size.json", 'r') as f:
    data = json.load(f)

# Extract the list of conversations from the modified data
conversations = list(data.values())

# Flatten the list of lists to remove the unnecessary layer
flattened_conversations = [conv for sublist in conversations for conv in sublist]

# Save the flattened conversations list back to a new JSON file
with open('flattened_conversations.json', 'w') as f:
    json.dump(flattened_conversations, f, indent=2)

move_pcap_files()

"""input_file_path = 'output_na.json'
output_file = 'output_na_wo_rep_flags_5.json'

# Read input JSON
with open(input_file_path, 'r') as input_file:
    input_data = json.load(input_file)

# Process data
output_data = {}
for key, entries in input_data.items():
    output_data[key] = process_data(entries)

# Write output JSON
with open(output_file, 'w') as output_file:
    json.dump(output_data, output_file, indent=4)"""

# create_sliding_window('output_na_wo_rep_flags_5.json', window_size)
