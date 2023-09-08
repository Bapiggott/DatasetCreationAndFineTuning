# DatasetCreationAndFineTuning

1. Install `conda` by running the following commands:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-VERSION-Linux-x86_64.sh
chmod +x Miniconda3-VERSION-Linux-x86_64.sh
./Miniconda3-VERSION-Linux-x86_64.sh
source ~/.bashrc
```
2. Create a `conda` envirnment by running the following commands:
```
conda create --name myfinetuningenv
conda activate myfinetuningenv
```
To deactive the `conda` envirnment, run the following command:
```
conda deactivate
```
3. Install the required dependencies by executing the following command:
```
pip --all dependecines needed
```
### Table 1: The effectiveness of generating response (Llama-2-13B, 1 epoch) - In Percentage.

| Model Name         | Src_IP | Dst_IP | Src_Port | Dst_Port | Flag   | Seq#   | Ack#   | Length | Overall Average |
|--------------------|--------|--------|----------|----------|--------|--------|--------|--------|-----------------|
| Llama-2-13B (20k)  | 98.851 | 98.851 | 98.851   | 98.851   | 88.506 | 96.552 | 87.356 | 100    | 95.977          |
| Llama-2-13B (40k)  | 97.590 | 97.594 | 97.590   | 97.590   | 85.542 | 96.386 | 87.952 | 98.795 | 94.88           |
| Llama-2-13B (60k)  | 98.824 | 98.824 | 98.824   | 98.824   | 84.706 | 97.647 | 95.294 | 98.824 | 96.471          |
| Llama-2-13B (80k)  | 97.675 | 97.675 | 97.675   | 97.675   | 77.612 | 92.537 | 91.045 | 98.508 | 93.470          |
| Llama-2-13B (100k) | 98.851 | 98.851 | 98.851   | 98.851   | 80.46  | 97.701 | 93.103 | 98.851 | 95.69           |

- Mean: 98.226
- Standard Deviation: 0.867

### Table 2: The effectiveness of generating response (Llama-2-7B, 1 epoch) - In Percentage.

| Model Name        | Src_IP | Dst_IP | Src_Port | Dst_Port | Flag   | Seq#   | Ack#   | Length | Overall Average |
|-------------------|--------|--------|----------|----------|--------|--------|--------|--------|-----------------|
| Llama-2-7B (20k)  | 92.5   | 95     | 93.75    | 95       | 83.75  | 92.5   | 80     | 93.75  | 90.781          |
| Llama-2-7B (40k)  | 100    | 100    | 100      | 100      | 85.542 | 95.181 | 90.361 | 98.795 | 96.235          |
| Llama-2-7B (60k)  | 100    | 100    | 100      | 100      | 86.25  | 98.75  | 93.75  | 97.5   | 97.031          |
| Llama-2-7B (80k)  | 96.296 | 97.531 | 96.296   | 97.531   | 80.247 | 93.827 | 88.889 | 95.062 | 93.2099         |
| Llama-2-7B (100k) | 97.531 | 97.531 | 97.531   | 97.531   | 74.074 | 96.296 | 86.42  | 98.765 | 93.21           |

- Mean: 97.265
- Standard Deviation: 3.11

### Table 3: The analysis of generative errors (Llama-2-13B, 1 epoch) - In Percentage.

| Model Name         | 0 err. | 1 err. | 2 errs. | 3 - 5 errs. | 6 errs. | 7 errs. | 8 errs. | Flags  | Seq#  | Ack#  |
|--------------------|--------|--------|---------|--------------|---------|---------|---------|--------|-------|-------|
| Llama-2-13B (20k)  | 77.012 | 18.391 | 3.448   | 0            | 1.149   | 0       | 0       | 8.046  | 2.299 | 8.046 |
| Llama-2-13B (40k)  | 75.904 | 19.277 | 2.41    | 0            | 0       | 2.41    | 0       | 9.639  | 0     | 9.639 |
| Llama-2-13B (60k)  | 80     | 17.647 | 1.177   | 0            | 0       | 1.177   | 0       | 12.941 | 1.177 | 3.529 |
| Llama-2-13B (80k)  | 74.419 | 20.930 | 2.326   | 0            | 0       | 1.163   | 1.163   | 13.954 | 1.163 | 5.814 |
| Llama-2-13B (100k) | 73.563 | 25.287 | 0       | 0            | 0       | 0       | 1.149   | 18.391 | 1.149 | 5.747 |

- Mean: 76.179
- Standard Deviation: 2.516

### Table 4: The effectiveness of generative errors (Llama-2-7B, 1 epoch) - In Percentage.

| Model Name        | 0 err. | 1 err. | 2 errs. | 3 errs. | 4 errs. | 5 errs. | 6 errs. | 7 errs. | 8 errs. | Flags  | Seq#  | Ack#  |
|-------------------|--------|--------|---------|---------|---------|---------|---------|---------|---------|--------|-------|-------|
| Llama-2-7B (20k) | 68.750 | 17.5   | 5       | 2.5     | 0       | 0       | 5       | 1.25    | 0       | 6.25   | 1.25  | 8.75  |
| Llama-2-7B (40k) | 73.494 | 24.096 | 1.205   | 1.205   | 0       | 0       | 0       | 0       | 0       | 12.048 | 4.819 | 7.228 |
| Llama-2-7B (60k) | 78.75  | 18.75  | 2.5     | 0       | 0       | 0       | 0       | 0       | 0       | 11.25  | 1.25  | 6.25  |
| Llama-2-7B (80k) | 69.136 | 23.457 | 2.469   | 1.235   | 1.235   | 0       | 1.235   | 0       | 1.235   | 0      | 0     | 0     |
| Llama-2-7B (100k)| 64.198 | 29.63  | 3.704   | 0       | 0       | 0       | 1.235   | 0       | 1.235   | 20.988 | 0     | 8.642 |

- Mean: 70.866
- Standard Deviation: 5.5

### Table 5: The analysis of generative errors (GPT-2) - In Percentage.

| Model Name               | 0 err. | 1 err. | 2 errs. | 3 errs. | 4 errs. | 5 errs. | 6 errs. | 7 errs. | 8 errs. | Flags  | Seq#  | Ack#  |
|--------------------------|--------|--------|---------|---------|---------|---------|---------|---------|---------|--------|-------|-------|
| GPT-2 (20k, 1 Epoch)     | 33.333 | 20.69  | 14.943  | 8.046   | 4.598   | 4.598   | 12.644  | 1.149   | 0       | 2.299  | 18.391 | 0     |
| GPT-2 (50k, 1 Epoch)     | 42.529 | 14.943 | 16.092  | 5.747   | 4.598   | 5.747   | 5.747   | 3.448   | 1.149   | 1.149  | 4.598  | 8.046 |
| GPT-2 (100k, 1 Epoch)    | 47.126 | 10.345 | 18.391  | 5.747   | 4.598   | 0       | 6.897   | 3.448   | 3.448   | 0      | 0     | 5.747 |
| GPT-2 (100k, 5 Epoch)    | 26.744 | 22.093 | 13.954  | 4.651   | 1.163   | 1.163   | 19.767  | 5.814   | 4.651   | 1.163  | 4.651 | 5.814 |
| GPT-2 (100k, 10 Epoch)   | 11.494 | 20.69  | 12.644  | 9.195   | 6.897   | 5.747   | 25.287  | 5.747   | 2.299   | 1.149  | 4.598 | 4.598 |

- Mean: 32.245
- Standard Deviation: 14.047

### Table 6: The effectiveness of generating response (GPT-2) - In percentage.

| Model Name               | Src\_IP | Dst\_IP | Src\_Port | Dst\_Port | Flag  | Seq\#  | Ack\#  | Length | Overall Avg. |
|--------------------------|---------|---------|-----------|-----------|-------|-------|-------|--------|--------------|
| GPT-2 (20k, 1 Epoch)     | 74.713  | 75.862  | 78.161    | 78.161    | 78.161| 44.828| 73.563| 96.552 | 75           |
| GPT-2 (50k, 1 Epoch)     | 58.621  | 81.609  | 81.609    | 81.609    | 80.46 | 71.264| 71.264| 94.253 | 77.586       |
| GPT-2 (100k, 1 Epoch)    | 56.322  | 82.759  | 83.908    | 83.908    | 82.759| 78.161| 63.218| 93.103 | 78.017       |
| GPT-2 (100k, 5 Epoch)    | 41.861  | 65.116  | 67.442    | 67.442    | 83.721| 60.465| 48.837| 94.186 | 66.134       |
| GPT-2 (100k, 10 Epoch)   | 34.483  | 50.575  | 63.218    | 63.218    | 70.115| 47.126| 41.379| 89.655 | 57.471       |

- Mean: 53.2
- Standard Deviation: 15.659

### Table 7: The analysis of generative errors (Distil-GPT-2) - In Percentage.

| Model Name                 | 0 err. | 1 err. | 2 errs. | 3 errs. | 4 errs. | 5 errs. | 6 errs. | 7 errs. | 8 errs. | Flags | Seq#  | Ack#  |
|----------------------------|--------|--------|---------|---------|---------|---------|---------|---------|---------|-------|-------|-------|
| Distil-GPT-2 (20k, 1 Epoch)| 32.184 | 18.391 | 18.391  | 8.046   | 13.793  | 3.448   | 4.598   | 1.149   | 0       | 0     | 14.943| 0     |
| Distil-GPT-2 (50k, 1 Epoch)| 28.736 | 13.793 | 19.54   | 13.793  | 11.494  | 4.598   | 5.747   | 2.299   | 0       | 0     | 8.046 | 0     |
| Distil-GPT-2 (100k, 1 Epoch)| 26.437 | 5.747  | 21.839  | 8.046   | 8.046   | 16.092  | 10.345  | 3.448   | 0       | 0     | 0     | 0     |
| Distil-GPT-2 (100k, 5 Epoch)| 36.145 | 13.253 | 21.687  | 7.229   | 4.819   | 2.41    | 4.819   | 8.434   | 0.012   | 0     | 0     | 1.205 |
| Distil-GPT-2 (100k, 10 Epoch)| 32.184 | 18.391 | 18.391  | 8.046   | 13.793  | 3.448   | 4.598   | 1.149   | 0       | 0     | 14.943| 0     |

- Mean: 31.137
- Standard Deviation: 3.712

### Table 8: The effectiveness of generating response (Distil-GPT-2) - In Percentage.

| Model Name                 | Src\_IP | Dst\_IP | Src\_Port | Dst\_Port | Flag  | Seq\#  | Ack\#  | Length | Overall Avg. |
|----------------------------|---------|---------|-----------|-----------|-------|-------|-------|--------|--------------|
| Distil-GPT-2 (20k, 1 Epoch)| 85.058  | 81.609  | 63.218    | 74.713    | 82.759| 47.126| 82.759| 95.402 | 76.58        |
| Distil-GPT-2 (50k, 1 Epoch)| 83.908  | 48.276  | 77.012    | 81.609    | 83.908| 37.931| 78.161| 95.402 | 73.276       |
| Distil-GPT-2 (100k, 1 Epoch)| 59.770  | 41.379  | 67.816    | 67.816    | 75.862| 43.678| 72.414| 98.851 | 65.948       |
| Distil-GPT-2 (100k, 5 Epoch)| 51.807  | 69.880  | 83.133    | 83.133    | 78.313| 71.084| 62.651| 92.771 | 74.096       |
| Distil-GPT-2 (100k, 10 Epoch)| 85.058 | 81.609 | 63.218    | 74.713    | 82.759| 47.126| 82.759| 95.402 | 76.58        |

- Mean: 73.12
- Standard Deviation: 16.077

