import os
import json
import shutil
import subprocess
from tqdm import tqdm
import re

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


def move_json(json_path, destination_dir):
    filename = os.path.basename(json_path)
    destination_path = os.path.join(destination_dir, filename)
    shutil.copy(json_path, destination_path)
    print(f"Moved {filename} to {destination_dir}")

def process_json(json_path):
    with open(json_path, 'r') as file:
        words = file.read().split()

        for i, word in enumerate(words):
            if "frame.protocols\":\"sll:ethertype:ip:" or "frame.protocols\": \"sll:ethertype:ip:" in word:
                remaining_content = ' '.join(words[i+1:])

                if "udp:data" in remaining_content:
                    move_json(json_path, directory_protocol[1])
                elif "udp:mavlink_proto" in remaining_content:
                    move_json(json_path, directory_protocol[2])
                    move_json(json_path, directory_protocol[1])
                elif "tcp:data" in remaining_content:
                    move_json(json_path, directory_protocol[0])
                else:
                    print(f"Skipping {json_path} - No matching frame.protocols")
                break

def run_move_jsons(target_directory):
    # Create destination directories if they don't exist
    for directory in directory_protocol:
        if not os.path.exists(directory):
            os.makedirs(directory)



    # Get the list of JSON files in the specified directory
    json_files = [file for file in os.listdir(target_directory) if file.endswith(".json")]

    for file in json_files:
        json_path = os.path.join(target_directory, file)
        process_json(json_path)


def process_dict_ml(data_dict, current_frame, prefix=''):
    result = current_frame
    if result is None:
        result = current_frame
    for key, value in data_dict.items():
        full_key = f"{prefix}_{key}" if prefix else key

        if isinstance(value, dict):
            process_dict_ml(value, result, prefix=full_key)
        else:
            # Extract the portion of the key after the last period
            key_string = key.rsplit('.', 1)[-1]
            current_frame[key_string] = value

    return result

def process_dict_udp(data_dict, prefix='', result=None):
    if result is None:
        result = {}
    for key, value in data_dict.items():
        full_key = f"{prefix}_{key}" if prefix else key

        if isinstance(value, dict):
            process_dict_udp(value, prefix=full_key, result=result)
        else:
            # Extract the portion of the key after the last period
            key_string = key.rsplit('.', 1)[-1]
            if key_string != "payload":
                result[key_string] = value

    return result




def process_dict_ml_ports(data_dict, prefix='', result=None):
    if result is None:
        result = {}
    for key, value in data_dict.items():
        full_key = f"{prefix}_{key}" if prefix else key

        if isinstance(value, dict):
            process_dict_ml_ports(value, prefix=full_key, result=result)
        else:
            # Extract the portion of the key after the last period
            key_string = key.rsplit('.', 1)[-1]
            if key_string == "srcport" or key_string == "dstport":
                result[key_string] = value

    return result


def process_dict_tcp(data_dict, prefix='', result=None):
    if result is None:
        result = {}
    valid_key_strings = ["srcport", "dstport", "len", "seq", "ack", "str"]
    wanted_key_strings = ["sport", "dport", "len", "seq", "ack", "flags"]
    for key, value in data_dict.items():
        full_key = f"{prefix}_{key}" if prefix else key

        if isinstance(value, dict):
            process_dict_tcp(value, prefix=full_key, result=result)
        else:
            # Extract the portion of the key after the last period
            key_string = key.rsplit('.', 1)[-1]
            if key_string in valid_key_strings:
                index = valid_key_strings.index(key_string)
                if index == 5:
                    matches = re.findall(r'\b[A-Z]+\b', value)
                    result[wanted_key_strings[5]] = matches[0]
                else:
                    result[wanted_key_strings[index]] = value

    return result

def filtered_jsons(input_directory, output_directory):

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            input_file_path = os.path.join(input_directory, filename)
            output_file_path = os.path.join(output_directory, f"filtered_{filename}")

            # Read the original JSON file
            with open(input_file_path, 'r') as file:
                data_list = json.load(file)

            filtered_data_list = []

            for item in data_list:
                if input_directory == directory_protocol[1]:
                    mavlink_proto_dict = item["_source"]["layers"]["udp"]
                    # print("filtering for UDP")
                    filtered_data = process_dict_udp(mavlink_proto_dict)
                elif input_directory == directory_protocol[0]:
                    mavlink_proto_dict = item["_source"]["layers"]["tcp"]
                    filtered_data = process_dict_tcp(mavlink_proto_dict)
                    # print("filtering for TCP")
                elif input_directory == directory_protocol[2]:
                    mavlink_proto_dict = item["_source"]["layers"]["udp"]
                    # print("filtering for UDP")
                    results = process_dict_ml_ports(mavlink_proto_dict)
                    # filtered_data_list.append(filtered_data)
                    mavlink_proto_dict = item["_source"]["layers"]["mavlink_proto"]
                    filtered_data = process_dict_ml(mavlink_proto_dict, results)
                    # print("filtering for Mavlink")
                else:
                    print("no protocol directory, something went wrong")
                    mavlink_proto_dict = "."
                    filtered_data = process_dict_ml(mavlink_proto_dict)
                # filtered_data = process_dict(mavlink_proto_dict)

                filtered_data_list.append(filtered_data)

            with open(output_file_path, 'w') as output_file:
                json.dump(filtered_data_list, output_file, indent=4)

            print(f"Filtered data from {filename} has been saved to: {output_file_path}")
'''def pcaps2jsons(output_directory):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get a list of all the pcap files in the current working directory
    pcap_files = [file for file in os.listdir() if file.endswith(".pcap")]

    # Create a progress bar to track the conversion process
    with tqdm(total=len(pcap_files), desc="Converting pcaps to json") as pbar:
        for pcap_file in pcap_files:
            input_pcap_path = os.path.join(os.getcwd(), pcap_file)
            output_json_file = os.path.join(output_directory, f"{pcap_file}.json")
            try:
                tshark_command = f'tshark -r "{input_pcap_path}" -T json > "{output_json_file}"'
                subprocess.run(tshark_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error converting {pcap_file}: {e}")
            pbar.update(1)

    print("Conversion complete.")'''


def pcaps2jsons(output_directory):
    # Create the output directory if it doesn't exist
    input_directory =  "processed_pcaps"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get a list of all the pcap files in the input directory
    pcap_files = [file for file in os.listdir(input_directory) if file.endswith(".pcap")]

    # Create a progress bar to track the conversion process
    with tqdm(total=len(pcap_files), desc="Converting pcaps to json") as pbar:
        for pcap_file in pcap_files:
            input_pcap_path = os.path.join(input_directory, pcap_file)
            output_json_file = os.path.join(output_directory, f"{pcap_file}.json")
            try:
                tshark_command = f'tshark -r "{input_pcap_path}" -T json > "{output_json_file}"'
                subprocess.run(tshark_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error converting {pcap_file}: {e}")
            pbar.update(1)

    print("Conversion complete.")


def combine_json_files(input_directory, output_file,):

    directory_path = input_directory

    combined_data = {}

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            with open(os.path.join(directory_path, filename)) as f:
                json_content = json.load(f)
                # Extract the original title from the filename (without the .json extension)
                title = os.path.splitext(filename)[0]
                combined_data[title] = json_content

    output_combined_file = output_file

    with open(output_combined_file, 'w') as f:
        json.dump(combined_data, f, indent=2)

    print(f"{output_combined_file} files combined successfully!")


def add_na_messages(json_data, Context_size):
    for section_name, section_data in json_data.items():
        new_messages = [
            {
                key: None  # Set each key to None for "n/a"
                for key in section_data[0].keys()
            }
            for _ in range(Context_size + 1)
        ]
        json_data[section_name] = new_messages + section_data
    return json_data


def convert_sets_to_lists(obj):
    if isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(element) for element in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj
    print("convert set to list finished")


def create_sliding_window(content, window_size):
    sliding_window_data = []

    window = []

    for message in content:
        window.append(message)  # Add the current message to the end of the window
        window = window[-window_size:]  # Truncate the window to the specified size

        if len(window) == window_size:  # Only append to output if the window is at the set size
            c_data = window[:-2]
            q_data = window[-2]
            a_data = window[-1]

            sliding_window_data.append({"Context": c_data, "Question": q_data, "Answer": a_data})

    print("Created sliding window")
    return sliding_window_data


def tcp_case(entries, output_entries, previous_flag, previous_source, previous_destination):
    for entry in entries:
        if 'flags' in entry:
            flags = entry['flags']
            source = entry['sport']
            destination = entry['dport']

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


def udp_case(entries, output_entries, previous_flag, previous_source, previous_destination):
    for entry in entries:
        if 'srcport' in entry:
            source = entry['srcport']
            destination = entry['dstport']
            flags = entry["port"]

            if flags is None or flags != previous_flag:
                output_entries.append(entry)
                previous_flag = flags
                previous_source = source
                previous_destination = destination

            if source != previous_source or destination != previous_destination:
                output_entries.append(entry)
                previous_source = source
                previous_destination = destination
            else:
                if output_entries:
                    output_entries[-1] = entry  # Replace the last entry with the current one

    return output_entries


def mvl_case(entries, output_entries, previous_flag, previous_source, previous_destination):
    for entry in entries:
        if 'srcport' in entry:
            source = entry['srcport']
            destination = entry['dstport']
            flags = entry["magic"]

            if flags is None or flags != previous_flag:
                output_entries.append(entry)
                previous_flag = flags
                previous_source = source
                previous_destination = destination

            if source != previous_source or destination != previous_destination:
                output_entries.append(entry)
                previous_source = source
                previous_destination = destination
            else:
                if output_entries:
                    output_entries[-1] = entry  # Replace the last entry with the current one

    return output_entries


def default(entries, output_entries, previous_flag, previous_source, previous_destination):
    result = "This is the default case"
    output_entries.append(result)
    return output_entries


def switch_case(case, entries, output_entries, previous_flag, previous_source, previous_destination):
    switch_dict = {
        0: tcp_case,
        1: udp_case,
        2: mvl_case,
    }

    return switch_dict.get(index, default)(entries, output_entries, previous_flag, previous_source,
                                           previous_destination)


def process_data(entries, protocol_index):
    output_entries = []
    previous_flag = None
    previous_source = None
    previous_destination = None

    output_entries = switch_case(protocol_index, entries, output_entries, previous_flag, previous_source, previous_destination)

    return output_entries


def finalize_json(Context_size, index, file):
    window_size = Context_size + 2

    na_file = f"output_na_{protocol_vector[index]}.json"

    with open(file, "r") as f:
        json_data = json.load(f)
    print("adding null messages")
    json_data_with_na = add_na_messages(json_data, Context_size)

    with open(na_file, "w") as f:
        json.dump(json_data_with_na, f, indent=2)

    print(f"Added {Context_size} 'n/a' messages to each section and saved to '{na_file}'")

    # Create a sliding window for JSON data
    with open(na_file, 'r') as f:
        data = json.load(f)




    output_file_json = f'output_file{protocol_vector[index]}.json'

    # Process data
    output_data = {}
    for key, entries in data.items():
        output_data[key] = process_data(entries, index)
    with open(output_file_json, 'w') as output_file:
        json.dump(output_data, output_file, indent=2) #4 - check if !=4

    with open(output_file_json, 'r') as f:
        data = json.load(f)

    sliding_window_data = {file_name: create_sliding_window(content, window_size) for file_name, content in data.items()}
    print("")
    # Convert sets to lists
    sliding_window_data = convert_sets_to_lists(sliding_window_data)
    print("")
    output_file_name = f"sliding_window_size_{protocol_vector[index]}.json"
    with open(output_file_name, 'w') as f:
        json.dump(sliding_window_data, f, indent=2)

    print(f"Sliding window JSON created successfully! Output file: {output_file_name}")

    with open(output_file_name, 'r') as f:
        data = json.load(f)



    # Extract the list of conversations from the modified data
    conversations = list(data.values())

    # Flatten the list of lists to remove the unnecessary layer
    flattened_conversations = [conv for sublist in conversations for conv in sublist]

    flattened_conversations_json = f'flattened_conversations_{protocol_vector[index]}.json'
    with open(flattened_conversations_json, 'w') as f:
        json.dump(flattened_conversations, f, indent=2)
    print("finished flattening")

    """with open(flattened_conversations_json, 'r') as input_file:
        data = json.load(input_file)"""


def run_pcap_splitter(pcap_file):
    command = f'~/Downloads/pcapplusplus-23.09-ubuntu-22.04-gcc-11.2.0-x86_64/bin/PcapSplitter -f "{pcap_file}" -o . -m connection'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Processed {pcap_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {pcap_file}: {e}")

def process_pcaps():
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
if __name__ == "__main__":

    directory_protocol = ["./jsons/Tcp_jsons", "./jsons/Udp_jsons", "./jsons/Mavlink_jsons"]
    protocol_vector = ["tcp", "udp" , "mavlink"]
    output_directory_filtered = ["output__filtered_tcp", "output__filtered_udp", "output__filtered_mavlink"]
    jsons_output_directory = "jsons"
    output_combined_file = "output_combined.json"
    #test2.py
    process_pcaps()
    pcaps2jsons(jsons_output_directory)
    target_directory = "./jsons"
    # move_jsons.py
    run_move_jsons(target_directory)
    output_directory = 'output_filtered_jsons1'
    #filtered_all7.py
    print("Beginning to filter pcaps, gaining the fields")
    for index, element in enumerate(directory_protocol):
         filtered_jsons(element, output_directory_filtered[index])

    # just for this trial-->
    #filtered_jsons(directory_protocol[2], output_directory_filtered[2])

    # combine.py
    for index, element in enumerate(protocol_vector):
        # if (index != 0):
        output_combined_file = f'output_combined{protocol_vector[index]}.json'
        combine_json_files(output_directory_filtered[index], output_combined_file)
        Context_size = 4
        # null.py
        finalize_json(Context_size, index, output_combined_file)
