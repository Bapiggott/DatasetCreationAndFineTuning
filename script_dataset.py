import os
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import re
from multiprocessing import Pool
import concurrent.futures


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


def move_json(json_path, destination_dir, chunk_size=1024*1024*10):  # 10 MB chunks by default
    filename = os.path.basename(json_path)
    destination_path = os.path.join(destination_dir, filename)

    # Check if the file already exists in the destination directory
    if not os.path.exists(destination_path):
        with open(json_path, 'rb') as source_file, open(destination_path, 'wb') as dest_file:
            while True:
                chunk = source_file.read(chunk_size)
                if not chunk:
                    break
                dest_file.write(chunk)

        print(f"Moved {filename} to {destination_dir}")
    else:
        print(f"{filename} already exists in {destination_dir}. Skipped.")


def move_json_2(json_path, destination_dir1, destination_dir2, chunk_size=1024*1024*10):  # 10 MB chunks by default
    filename = os.path.basename(json_path)

    destination_path1 = os.path.join(destination_dir1, filename)
    destination_path2 = os.path.join(destination_dir2, filename)

    # Check if the file already exists in the destination directories
    if not os.path.exists(destination_path1) or not os.path.exists(destination_path2):
        with open(json_path, 'rb') as source_file, open(destination_path1, 'wb') as dest_file1, \
                open(destination_path2, 'wb') as dest_file2:
            while True:
                print("chunk")
                chunk = source_file.read(chunk_size)
                if not chunk:
                    break
                dest_file1.write(chunk)
                dest_file2.write(chunk)

        print(f"Moved {filename} to {destination_dir1} and {destination_dir2}")
    else:
        print(f"{filename} already exists in {destination_dir1} and {destination_dir2}. Skipped.")


def process_json(json_path):
    print(f"working on: {json_path}")
    with open(json_path, 'r') as file:
        # Create a JSON decoder
        true_statement = True
        decoder = json.JSONDecoder()
        index_i = 0

        # Initialize an empty string to accumulate partial JSON content
        partial_json = ''
        prev_chunk = ''
        while true_statement:
            print(f"itereation {index_i} for file: {json_path}")
            index_i += 1
            chunk = file.read(496)  # Read a chunk of the file
            if not chunk:
                print("not chunk")
                break  # End of file

            partial_json += chunk + prev_chunk
            prev_chunk = chunk
            words = partial_json.split()
            # words = partial_json.read().split()
            try:
                # Try to decode the JSON content in the accumulated string
                # print("--\n\n")
                # print(words)
                # Process the decoded JSON object
                for i, word in enumerate(words):
                    # print(word)

                    # x = "frame.protocols\":\', \'\"sll: ethertype:ip"
                    if '"sll:ethertype:ip:' in word:
                        print(word)
                        if "udp:data" in word:
                            move_json(json_path, directory_protocol[1])
                            true_statement = False
                            break
                        elif "udp:mavlink_proto" in word:
                            print("mav/")
                            move_json_2(json_path, directory_protocol[2], directory_protocol[1])
                            # move_json(json_path, directory_protocol[1])
                            true_statement = False
                            break
                        elif "tcp:data" in word or "\"sll:ethertype:ip:tcp\"" in word:
                            print("tcp/")
                            move_json(json_path, directory_protocol[0])
                            true_statement = False
                            break

            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
                pass
    print(f"Finished: {json_path}\n")


def process_files(target_directory, json_files):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_json, os.path.join(target_directory, file)): file for file in json_files}

        # Wrap tqdm around as_completed to create a progress bar
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing JSON files"):
            file = futures[future]
            try:
                future.result()  # Wait for the result, or raise an exception if an error occurred in the thread
                print(f"Finished: {file}")
            except Exception as e:
                print(f"Error processing {file}: {e}")


def run_move_jsons(target_directory):
    delete_empty_json_files(target_directory)

    for directory in directory_protocol:
        if not os.path.exists(directory):
            os.makedirs(directory)
    print(f"protocol directories are created")

    # Get the list of JSON files in the specified directory
    json_files = [file for file in os.listdir(target_directory) if file.endswith(".json")]

    # for file in json_files:
    # json_path = os.path.join(target_directory, file)
    #   print(f"working on: {file}")
    process_files(target_directory, json_files)
    # process_json(json_path)
    #  print(f"finished: {file}")


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


def delete_empty_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            if os.path.getsize(file_path) == 0:
                print(f"Deleting {filename}")
                os.remove(file_path)


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


def chunked_json_load(file, chunk_size=1024):
    decoder = json.JSONDecoder()
    buffer = ""
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        buffer += chunk
        pos = 0
        while True:
            try:
                obj, pos = decoder.raw_decode(buffer, pos)
                yield obj
            except json.JSONDecodeError:
                # Incomplete JSON in the chunk, read more data
                break
        buffer = buffer[pos:]


def filtered_jsons(input_directory, output_directory, chunk_size=1024):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            input_file_path = os.path.join(input_directory, filename)
            output_file_path = os.path.join(output_directory, f"filtered_{filename}")
            remove_incomplete_package(input_file_path, f'{input_file_path}_temp.json')
            remove_trailing_comma(f'{input_file_path}_temp.json', input_file_path)
            delete_file(f'{input_file_path}_temp.json')
            with open(input_file_path, 'r') as file:
                print(input_file_path)
                # Use chunked JSON loading
                data_list = [item for item in chunked_json_load(file, chunk_size)]

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


def convert_pcap_to_json(input_pcap, output_json):
    try:
        tshark_command = f'tshark -r "{input_pcap}" -T json > "{output_json}"'
        subprocess.run(tshark_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_pcap}: {e}")


def pcaps2jsons(output_directory):
    # Create the output directory if it doesn't exist
    input_directory = "."  # Change this to the desired input directory
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get a list of all the pcap files in the input directory
    pcap_files = [file for file in os.listdir(input_directory) if file.endswith(".pcap")]

    # Create a progress bar to track the conversion process
    with tqdm(total=len(pcap_files), desc="Converting pcaps to json") as pbar, \
            ThreadPoolExecutor() as executor:
        # Use ThreadPoolExecutor to parallelize the conversion process
        futures = []
        for pcap_file in pcap_files:
            input_pcap_path = os.path.join(input_directory, pcap_file)
            output_json_file = os.path.join(output_directory, f"{pcap_file}.json")
            futures.append(executor.submit(convert_pcap_to_json, input_pcap_path, output_json_file))

        # Wait for all tasks to complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing"):
            future.result()
            pbar.update(1)

    print("Conversion complete.")


def combine_json_files(input_directory, output_file, ):
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
        print("convert set to list finished")
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        print("convert set to list finished")
        return [convert_sets_to_lists(element) for element in obj]
    elif isinstance(obj, set):
        print("convert set to list finished")
        return list(obj)
    else:
        return obj


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

    # return switch_dict.get(index, default)(entries, output_entries, previous_flag, previous_source, previous_destination)
    return switch_dict.get(case, default)(entries, output_entries, previous_flag, previous_source,
                                          previous_destination)


def process_data(entries, protocol_index):
    output_entries = []
    previous_flag = None
    previous_source = None
    previous_destination = None

    output_entries = switch_case(protocol_index, entries, output_entries, previous_flag, previous_source,
                                 previous_destination)

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
        json.dump(output_data, output_file, indent=2)  # 4 - check if !=4

    with open(output_file_json, 'r') as f:
        data = json.load(f)

    sliding_window_data = {file_name: create_sliding_window(content, window_size) for file_name, content in
                           data.items()}
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


def filtered_jsons_wrapper(args):
    filtered_jsons(*args)


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

    pcap_files = [file for file in os.listdir(".") if file.endswith(".pcap")]

    for pcap_file in pcap_files:
        run_pcap_splitter(pcap_file)
        shutil.move(pcap_file, os.path.join(processed_directory, pcap_file))

    print("All pcap files processed and moved.")


def combine_and_finalize_wrapper(args):
    combine_and_finalize(*args)


def combine_and_finalize(output_directory, protocol_vector, index):
    output_combined_file = f'output_combined{protocol_vector}.json'
    combine_json_files(output_directory, output_combined_file)
    Context_size = 4
    finalize_json(Context_size, index, output_combined_file)


def process_directory(index, element, output_directory):
    filtered_jsons(element, output_directory)
    print(f"Processed index {index}")


def remove_trailing_comma(file_path, output_file, chunk_size=1024*1024*10):
    with open(file_path, 'r') as source_file:
        with open(output_file, 'w') as dest_file:
            last_brace_index = None
            while True:
                chunk = source_file.read(chunk_size)
                if not chunk:
                    break

                # Find the index of the last '}'
                last_brace_index = chunk.rfind(',') # }')
                dest_file.write(chunk[:last_brace_index - 1])

            if last_brace_index is not None:
                # Append ']' to the last chunk
                dest_file.write(' }\n]')

    print(f"Removed incomplete packages from {file_path} and saved to {output_file}")


def remove_incomplete_package(file_path, output_file, chunk_size=1024*1024*10):
    with open(file_path, 'r') as source_file:
        with open(output_file, 'w') as dest_file:
            last_brace_index = None
            while True:
                chunk = source_file.read(chunk_size)
                if not chunk:
                    break

                # Find the index of the last '}'
                last_brace_index = chunk.rfind('"_index"') # }')
                dest_file.write(chunk[:last_brace_index - 3])

            if last_brace_index is not None:
                # Append ']' to the last chunk
                dest_file.write(']')

    print(f"Removed incomplete packages from {file_path} and saved to {output_file}")


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' successfully deleted.")
    except OSError as e:
        print(f"Error deleting file '{file_path}': {e}")


if __name__ == "__main__":

    directory_protocol = ["./jsons1/Tcp_jsons", "./jsons1/Udp_jsons", "./jsons1/Mavlink_jsons"]
    protocol_vector = ["tcp", "udp", "mavlink"]
    output_directory_filtered = ["output__filtered_tcp", "output__filtered_udp", "output__filtered_mavlink"]
    jsons_output_directory = "jsons1"
    output_combined_file = "output_combined.json"
    # test2.py
    process_pcaps()
    pcaps2jsons(jsons_output_directory)
    target_directory = "./jsons1"
    # move_jsons.py
    run_move_jsons(target_directory)

    output_directory = 'output_filtered_jsons1'
    # filtered_all7.py
    print("Beginning to filter pcaps, gaining the fields")
    for index, element in enumerate(directory_protocol):
        filtered_jsons(element, output_directory_filtered[index])
    num_cores = min(len(directory_protocol), len(output_directory_filtered))
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        # Use executor.map to parallelize the processing across multiple threads
        executor.map(process_directory, range(len(directory_protocol)), directory_protocol, output_directory_filtered)

    # with ThreadPoolExecutor() as executor:
    # executor.map(filtered_jsons, range(len(file_list)), [f'output_combined{pv}.json' for pv in protocol_vector])
    # num_processes = os.cpu_count()

    # Create a list of argument tuples for the filtered_jsons function
    # args_list = [(directory_protocol[i], output_directory_filtered[i]) for i in range(len(directory_protocol))]

    # Create a pool of processes and map the function to the arguments
    # with Pool(num_processes) as pool:
    #   pool.map(filtered_jsons_wrapper, args_list)
    # just for this trial-->
    # filtered_jsons(directory_protocol[2], output_directory_filtered[2])
    # combine.py
    for index, element in enumerate(protocol_vector):
        # if (index != 0):
        output_combined_file = f'output_combined{protocol_vector[index]}.json'
        combine_json_files(output_directory_filtered[index], output_combined_file)
        Context_size = 4
        # null.py
        finalize_json(Context_size, index, output_combined_file)

    # num_processes = os.cpu_count()

    # Create a list of argument tuples for the combine_and_finalize function
    # args_list = [(output_directory_filtered[i], protocol_vector[i], i) for i in range(len(protocol_vector))]

    # Create a pool of processes and map the function to the arguments
    # with Pool(num_processes) as pool:
    #   pool.map(combine_and_finalize_wrapper, args_list)
