import os
import re
import matplotlib.pyplot as plt

experiments = [3]
modes = ['randselFedavg', 'fedavg', 'WLRC', 'LRC_Sampling', 'Mixed_Sampling', 'Mixed_WLRC_FedAvg']
names = {}

for exp in experiments:
	for mode in modes:
		base_dir = f'./Experiment_{exp}/{mode}'
		if os.path.exists(base_dir):
			subdirs = [
			    name for name in os.listdir(base_dir)
			    if os.path.isdir(os.path.join(base_dir, name))
			]
			names[mode] = subdirs
		else:
			names[mode] = []
			print(f"Skipping mode {mode}: base dir not found")

# Regex patterns
# Global metrics with wrong confidence
pattern = re.compile(
    r"Round (\d+): loss=([\d.]+), accuracy=([\d.]+), avg_wrong_confidence=([\d.]+)"
)

# Per-class accuracy: extract the dict
per_class_pattern = re.compile(
    r"accuracy_class_(\d+)'?: ([\d.]+)"
)

# For randselFedavg
pattern_randsel = re.compile(r"Round (\d+): avg_loss=([\d.]+), avg_accuracy=([\d.]+)")

for e in experiments:
    for mode in modes:
        for attr in names[mode]:
            base_dir = f'./Experiment_{e}/{mode}/{attr}'
            file = 'final_results.txt' if mode == 'randselFedavg' else 'summary.txt'
            path = os.path.join(base_dir, file)

            if not os.path.exists(path):
                print(f"Skipping: {path} (not found)")
                continue

            rounds, losses, accuracies, wrong_confs = [], [], [], []
            per_class_accuracies = {i: [] for i in range(10)}  

            with open(path, 'r') as f:
                round_buffer = {}
                for line in f:
                    # Match normal loss/accuracy line
                    if mode == 'randselFedavg':
                        match = pattern_randsel.search(line)
                    else:
                        match = pattern.search(line)

                    if match:
                        round_num = int(match.group(1))
                        loss = float(match.group(2))
                        acc = float(match.group(3))
                        avg_wrong_conf = float(match.group(4))
                        rounds.append(round_num)
                        losses.append(loss)
                        accuracies.append(acc)
                        wrong_confs.append(avg_wrong_conf)
                        current_round = round_num

                    # Match per-class accuracy line
                    class_matches = per_class_pattern.findall(line)
                    if class_matches:
                        for class_id, acc_str in class_matches:
                            per_class_accuracies[int(class_id)].append(float(acc_str))

            if not rounds:
                print(f"No valid data in {path}")
                continue

            # Plot global loss and accuracy
            plt.figure(figsize=(12, 4))

            plt.subplot(1, 2, 1)
            plt.plot(rounds, losses, marker='o', label='Loss')
            plt.title(f'Loss - {mode} {attr} (Exp {e})')
            plt.xlabel('Round')
            plt.ylabel('Loss')
            plt.grid(True)

            plt.subplot(1, 2, 2)
            plt.plot(rounds, accuracies, marker='o', label='Accuracy')
            plt.title(f'Accuracy - {mode} {attr} (Exp {e})')
            plt.xlabel('Round')
            plt.ylabel('Accuracy')
            plt.grid(True)

            plt.tight_layout()
            os.makedirs(f"plots/Experiment_{e}/{mode}", exist_ok=True)
            plot_path = f"plots/Experiment_{e}/{mode}/metrics_{attr or 'default'}.png"
            plt.savefig(plot_path)
            plt.close()
            print(f"Saved global plot to {plot_path}")

            # Plot per-class accuracy
            plt.figure(figsize=(10, 6))
            for i in range(10):
                if per_class_accuracies[i]:
                    plt.plot(range(len(per_class_accuracies[i])), per_class_accuracies[i], label=f'Class {i}')

            plt.title(f'Per-Class Accuracy - {mode} {attr} (Exp {e})')
            plt.xlabel('Round')
            plt.ylabel('Accuracy')
            plt.grid(True)
            plt.legend(loc='lower right', fontsize=8)
            plt.tight_layout()
            perclass_path = f"plots/Experiment_{e}/{mode}/per_class_{attr or 'default'}.png"
            plt.savefig(perclass_path)
            plt.close()
            print(f"Saved per-class plot to {perclass_path}")

