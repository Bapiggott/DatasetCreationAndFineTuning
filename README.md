# DatasetCreationAndFineTuning
\begin{table*}[ht]
  \centering
\caption{The effectiveness of generating response (Llama-2-13B, 1 epoch) - In Percentage.} % title of Table
\label{table:experiment1:llama2-13b}
\begin{tabular}{|l|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|}
\hline
Model Name & Src\_IP & Dst\_IP & Src\_Port & Dst\_Port & Flag & Seq\# & Ack\# & Length & Overall Average\\
\hline \hline
Llama-2-13B (20k) & 98.851	& 98.851 & 98.851 & 98.851 & 88.506 & 96.552 & 87.356 & 100 & 95.977\\
Llama-2-13B (40k) & 97.590 & 97.594 & 97.590 & 97.590 & 85.542 & 96.386 & 87.952 & 98.795 & 94.88\\
Llama-2-13B (60k)  & 98.824 & 98.824 & 98.824 & 98.824 & 84.706 & 97.647 & 95.294 & 98.824 & 96.471\\
Llama-2-13B (80k) & 97.675 & 97.675 & 97.675 & 97.675 & 77.612	& 92.537	& 91.045	& 98.508	& 93.470
\\
Llama-2-13B (100k) & 98.851 & 98.851 & 98.851 & 98.851 & 80.46 & 97.701 & 93.103 & 98.851 & 95.69\\ \hline
Mean & 98.226 & 	98.226	 & 98.226 & 	98.226 & 	83.365	 & 96.165 & 	90.950	&98.995 & 	95.297\\
Standard Deviation & 0.867	 & 0.867	 & 0.867 & 	0.867 &	4.316	 & 2.116	 & 3.37	 & 0.578	 & 1.173\\
\hline
\end{tabular}
\end{table*}

\begin{table*}[ht]
  \centering
\caption{The effectiveness of generating response (Llama-2-7B, 1 epoch) - In Percentage.} % title of Table
\label{table:experiment1:llama2-7b}
\begin{tabular}{|l|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|p{1.2cm}|}
\hline 
Model Name & Src\_IP & Dst\_IP & Src\_Port & Dst\_Port & Flag & Seq\# & Ack\# & Length & Overall Average\\
\hline \hline
Llama-2-7B (20k) & 92.5 & 95 & 93.75 & 95 & 83.75 & 92.5 & 80 & 93.75 & 90.781 \\
Llama-2-7B (40k) & 100 & 100 & 100 & 100 & 85.542 & 95.181 & 90.361 & 98.795 & 96.235 \\
Llama-2-7B (60k)  & 100 & 100 & 100 & 100 & 86.25 & 98.75 & 93.75 & 97.5 & 97.031 \\
Llama-2-7B (80k) & 96.296 & 97.531 & 96.296 & 97.531 & 80.247 & 93.827 & 88.889 & 95.062 & 93.2099 \\
Llama-2-7B (100k) & 97.531 & 97.531 & 97.531 & 97.531 & 74.074 & 96.296 & 86.42 & 98.765 & 93.21 \\\hline
Mean & 97.265 & 98.012 & 97.515 & 98.012 & 81.973 & 95.311 & 87.884 & 96.775 & 94.094 \\
Standard Deviation & 3.11 & 2.088 & 2.646 & 2.088 & 4.989 & 2.394 & 5.144 & 2.272 & 2.537 \\

\hline
\end{tabular}
\end{table*}
