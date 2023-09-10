import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import time

# Load the finetuned Llama-2 model and tokenizer
model_name = "gpt2_100k_10_epochs"
tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)

def generate_tcp_packet(context, question):
    # Format the input dialogues and context
    instruction = "### Prompt: Provided below is a question detailing key attributes of a TCP packet. Preceding this question is a series of TCP packets, which together form the context. Please continue the sequence by providing the subsequent TCP packet that follows the question, serving as the answer. \n\n"
    context_prompt = "### Context:\n" + str(context) + "\n"
    question_prompt = "### Question\n" + str(question) + "\n"

    # Generate the next TCP packet prediction
    prompt = instruction + context_prompt + question_prompt + "### Answer:\n"
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        start_time = time.time()
        output = model.generate(input_ids, max_length=700, num_return_sequences=1)
        end_time = time.time()

    # Decode the generated output to get the predicted TCP packet
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    time_taken = end_time - start_time
    return generated_text, time_taken
    
input_file = '/home/brett/dataset_check/Testing_dataset/testing_data_random_100.json'
# Load data from JSON file
with open(input_file, 'r') as file:
    data = json.load(file)

output_file = 'output_predictions_test_gpt2_100k_10_epochs.json'
output_data = []
count_value = 1

try:
    for dialogue in data:  # Iterate over the list of dictionaries directly
        context = dialogue['Context']
        question = dialogue['Question']
        correct_answer = dialogue['Answer']

        # Generate the next predicted TCP packet and measure time taken
        next_tcp_packet, time_taken = generate_tcp_packet(context, question)

        # Store results in output_data
        output_data.append({
            'Question': question,
            'Predicted_TCP_Packet': next_tcp_packet,
            'Correct_Answer': correct_answer,
            'Time_Taken': time_taken
        })

        # Print information
        print("Question:", question)
        print("Predicted Next TCP Packet:")
        print(next_tcp_packet)
        print("Correct Answer:")
        print(correct_answer)
        print("Time Taken:", time_taken, "seconds")
        print("Total q/a's done: ", count_value)
        print("=" * 30)
        count_value += 1

        # Write results to the JSON file after processing each dialogue
        with open(output_file, 'w') as outfile:
            json.dump(output_data, outfile, indent=4)

except KeyboardInterrupt:
    print("Execution interrupted. Saving progress to", output_file)
    with open(output_file, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)

print("Predictions saved to:", output_file)
