import json
import os
import re

# Read the JSON file
json_files = [f for f in os.listdir('.') if f.endswith('.json')]


def extract_context_and_packet(packet_text):
    context_match = re.search(r"Context:\n(.*?)\n### Question", packet_text, re.DOTALL)
    packet_match = re.search(r"Answer:\n(.*?)\n(### Previous Attempt:|### Answer:|### Question:|### Context:|###)",
packet_text, re.DOTALL)

    if context_match and packet_match:
        context_text = context_match.group(1)
        packet_text = packet_match.group(1)

        context_text = context_text.replace("'", "\"")
        packet_text = packet_text.replace("'", "\"")

        # Replace "None" or "none" with JSON null
        packet_text = packet_text.replace("None", "null").replace("none", "null")

        try:
            parsed_context = json.loads(context_text)
            parsed_packet = json.loads(packet_text)
            if "### Previous Attempt:" in packet_match.group(2):
                packet_type = "Previous Attempt"
            elif "### Answer:" in packet_match.group(2):
                packet_type = "Answer"
            elif '### Context:' in packet_match.group(2):
                packet_type = 'Context'
            elif '###' in packet_match.group(2):
                packet_type = 'Something'
            else:
                packet_type = "Question"
            return parsed_context, parsed_packet, packet_type
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return None, None, None

    return None, None, None


for input_file_path in json_files:
    if  input_file_path.endswith(".json"): # input_file_path.startswith("7b_output_predictions_") and
        output_file_path = input_file_path.replace(".json", "_final_version.json")

        with open(input_file_path, 'r') as input_file:
            data = json.load(input_file)

        new_data = []
        for entry in data:
            if 'Predicted_TCP_Packet' in entry:
                predicted_tcp_packet = entry['Predicted_TCP_Packet']
                context, packet, packet_type = extract_context_and_packet(predicted_tcp_packet)
                if context and packet:
                    entry['Context'] = context
                    entry['Predicted_TCP_Packet'] = packet
                    entry['Packet_Type'] = packet_type
                    new_data.append(entry)

                    with open(output_file_path, 'w') as output_file:
                        json.dump(new_data, output_file, indent=4)

                    print(f"File {input_file_path} processed. Output saved as {output_file_path}")
