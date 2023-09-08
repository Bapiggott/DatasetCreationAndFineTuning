from transformers import AutoModelForCausalLM, PretrainedConfig, AutoModelForSeq2SeqLM
import torch
import argparse


parser = argparse.ArgumentParser(description="Merge adapters with a base model and save the final model and tokenizer.")
parser.add_argument("--base_model_name", type=str, default="meta-llama/Llama-2-13b-hf", help="Name or path of the base model.")
parser.add_argument("--adapters_path", type=str, default="", help="Path to the adapters folder.")
parser.add_argument("--final_model_name", type=str, default="llama-13b-tcp", help="Name for the final merged model.")
args = parser.parse_args()

base_model_name = args.base_model_name
adapters_path = args.adapters_path
final_model_name = args.final_model_name

model = AutoModelForCausalLM.from_pretrained(base_model_name, trust_remote_code=True, torch_dtype=torch.float16)

from peft import PeftModel

# load perf model with new adapters
model = PeftModel.from_pretrained(
    model,
    adapters_path,
)

print("Merging...")

model = model.merge_and_unload() # merge adapters and base model

print("Saving Final Merged Model")

model.save_pretrained(final_model_name)

from transformers import AutoTokenizer

print("Saving Tokenizer")

tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
tokenizer.save_pretrained(final_model_name)

#python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_20k/ --final_model_name llama-7b-tcp-20k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_40k/ --final_model_name llama-7b-tcp-40k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_60k/ --final_model_name llama-7b-tcp-60k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_100k/ --final_model_name llama-7b-tcp-80k
# python3 mergeAdapters.py --base_model_name meta-llama/Llama-2-7b-hf --adapters_path ./adaptersLlama7B_100k_real/ --final_model_name llama-7b-tcp-100k
# python3 testing_modal_8_14_qna_1.py; wait 90; python3 testing_modal_8_14_qna_2.py; wait 90; python3 testing_modal_8_14_qna_3.py; wait 90; python3 testing_modal_8_14_qna_4.py; wait 90; python3 testing_modal_8_14_qna_5.py
# test_modal_100_2_e.py
# python3 test_modal_100_2_a.py; wait 90; python3 test_modal_100_2_b.py; wait 90; python3 test_modal_100_2_c.py; wait 90; python3 test_modal_100_2_d.py; wait 90; python3 test_modal_100_2_e.py
