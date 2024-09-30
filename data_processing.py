import json
import os
from typing import List, Optional

import fire
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from tqdm import tqdm


# Define a function to compute credible intervals
def compute_credible_interval(data, confidence=0.95):
	"""
    Compute the 95% credible interval for a given dataset using the Bayesian approach.
    """
	n = len(data)
	mean = np.mean(data)
	sem = stats.sem(data)  # Standard error of the mean
	interval = stats.t.interval(confidence, n - 1, loc=mean, scale=sem)
	return interval


def compute_fitness(quality_value, controllability_value, diversity_value,
                    fitness_type):
	if fitness_type == 'quality':
		return quality_value
	elif fitness_type == 'quality_control':
		result = quality_value
		if quality_value >= 1:
			result += controllability_value
		return result / 2.0
	elif fitness_type == 'quality_control_diversity':
		result = quality_value
		if quality_value >= 1:
			result += controllability_value
		if controllability_value >= 1:
			result += diversity_value
		return result / 3.0

def process_environment(env_path: str) -> str:
	results = []
	
	for fitness_type in tqdm(os.listdir(env_path), desc="Processing fitness", leave=False, dynamic_ncols=True):
		fitness_path = os.path.join(env_path, fitness_type)
		if os.path.isdir(fitness_path):
			for algorithm in tqdm(os.listdir(fitness_path), desc="Processing algorithms", leave=False, dynamic_ncols=True):
				algorithm_path = os.path.join(fitness_path, algorithm)
				if os.path.isdir(algorithm_path):
					for run_n in tqdm(os.listdir(algorithm_path), desc="Processing runs", leave=False, dynamic_ncols=True):
						run_path = os.path.join(algorithm_path, run_n)
						if os.path.isdir(run_path):
							for iter_n in tqdm(os.listdir(run_path), desc=f"env={env_path}; f={fitness_type}; alg={algorithm}; run={run_n}", leave=False, dynamic_ncols=True):
								iter_path = os.path.join(run_path, iter_n)
								if os.path.isdir(iter_path):
									highest_quality_file = None
									highest_diversity_file = None
									highest_controlability_file = None
									
									highest_quality_value = -np.inf
									highest_diversity_value = -np.inf
									highest_controlability_value = -np.inf
									
									n_chromosomes_success_quality = 0
									n_chromosomes_success_diversity = 0
									n_chromosomes_success_controlability = 0
									
									best_fitness = -np.inf
									elite = None

									# Process each JSON file in iter_n
									for json_file in os.listdir(iter_path):
										if json_file.endswith(".json"):
											file_path = os.path.join(iter_path, json_file)
											with open(file_path, "r") as f:
												data = json.load(f)
												# Collect the values of interest
												quality = data["quality"]
												diversity = data["diversity"]
												controlability = data["controlability"]
												
												fitness = compute_fitness(quality, controlability, diversity, fitness_type)
												if fitness > best_fitness:
													best_fitness = fitness
													elite = json_file
												
												if quality == 1.0: n_chromosomes_success_quality += 1
												if diversity == 1.0: n_chromosomes_success_diversity += 1
												if controlability == 1.0: n_chromosomes_success_controlability += 1
												
												# Check for highest quality
												if quality > highest_quality_value:
													highest_quality_value = quality
													highest_quality_file = json_file
												
												# Check for highest diversity
												if diversity > highest_diversity_value:
													highest_diversity_value = diversity
													highest_diversity_file = json_file
												
												# Check for highest controlability
												if controlability > highest_controlability_value:
													highest_controlability_value = controlability
													highest_controlability_file = json_file
									
									# Fix for iter_n to preserve order
									iter_n = int(str(iter_n).replace("iter_", ""))
									run_n = int(run_n)
									
									# Append the results to the list
									results.append({
										"env_name": os.path.basename(os.path.normpath(env_path)),
										"fitness_type": fitness_type,
										"algorithm": algorithm,
										"run_n": run_n,
										"iter_n": iter_n,
										"quality": highest_quality_value,
										"diversity": highest_diversity_value,
										"controlability": highest_controlability_value,
										"quality_file": highest_quality_file,
										"diversity_file": highest_diversity_file,
										"controlability_file": highest_controlability_file,
										"success_quality": n_chromosomes_success_quality,
										"success_diversity": n_chromosomes_success_diversity,
										"success_controlability": n_chromosomes_success_controlability,
										"fitness": best_fitness,
										"elite": elite
									})

	# Create a DataFrame from the results
	df = pd.DataFrame(results)
	
	# Save the DataFrame to a CSV file
	filename = f"{env_path}.csv"
	df.to_csv(f"{env_path}.csv", index=False)
	return filename


def process_all_envs(root_dir: str) -> List[str]:
	fnames = []
	for env_path in tqdm([x for x in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, x))],
	                     desc="Processing environments", dynamic_ncols=True):
		fnames.append(process_environment(os.path.join(root_dir, env_path)))
	return fnames


def aggregate_envs_statistics(root_dir: str,
                              fnames: Optional[List[str]] = None) -> str:
	if fnames is None:
		fnames = [x for x in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, x)) and x.endswith(".csv") and not x.startswith("aggregated")]
	
	all_envs_results = pd.DataFrame()
	for fname in tqdm(fnames, desc="Aggregating environments", dynamic_ncols=True):
		df = pd.read_csv(os.path.join(root_dir, fname))
		all_envs_results = pd.concat([all_envs_results, df])
	
	filename = os.path.join(root_dir, "aggregated_raw_statistics.csv")
	all_envs_results.to_csv(filename, index=False)
	print(f"Aggregation complete. Results saved to '{filename}'.")
	
	return filename


# Function to further aggregate results over runs
def aggregate_over_runs(csv_file):
	"""
	Further aggregates the statistics over runs based on the `average` values in the CSV file.

	Args:
		csv_file (str): Path to the CSV file containing initial aggregated statistics.
	"""
	print(f"Aggregating statistics from '{csv_file}'...")
	
	# Load the initial aggregated statistics from the CSV file
	df = pd.read_csv(csv_file)
	
	# Group by columns excluding `run_n` and aggregate over runs
	grouped_df = df.sort_values(["run_n", "iter_n"], ascending=True).groupby(
		["env_name", "fitness_type", "algorithm", "iter_n"]
	).agg(
		mean_fitness=('fitness', 'mean'),
		std_fitness=('fitness', 'std'),
		lower_ci_fitness=('fitness', lambda x: compute_credible_interval(x)[0]),
		upper_ci_fitness=('fitness', lambda x: compute_credible_interval(x)[1]),
		
		mean_quality=('quality', 'mean'),
		std_quality=('quality', 'std'),
		lower_ci_quality=('quality', lambda x: compute_credible_interval(x)[0]),
		upper_ci_quality=('quality', lambda x: compute_credible_interval(x)[1]),
		
		mean_diversity=('diversity', 'mean'),
		std_diversity=('diversity', 'std'),
		lower_ci_diversity=('diversity', lambda x: compute_credible_interval(x)[0]),
		upper_ci_diversity=('diversity', lambda x: compute_credible_interval(x)[1]),
		
		mean_controlability=('controlability', 'mean'),
		std_controlability=('controlability', 'std'),
		lower_ci_controlability=('controlability', lambda x: compute_credible_interval(x)[0]),
		upper_ci_controlability=('controlability', lambda x: compute_credible_interval(x)[1]),
		
		mean_success_quality=('success_quality', 'mean'),
		std_success_quality=('success_quality', 'std'),
		lower_ci_success_quality=('success_quality', lambda x: compute_credible_interval(x)[0]),
		upper_ci_success_quality=('success_quality', lambda x: compute_credible_interval(x)[1]),
		
		mean_success_diversity=('success_diversity', 'mean'),
		std_success_diversity=('success_diversity', 'std'),
		lower_ci_success_diversity=('success_diversity', lambda x: compute_credible_interval(x)[0]),
		upper_ci_success_diversity=('success_diversity', lambda x: compute_credible_interval(x)[1]),
		
		mean_success_controlability=('success_controlability', 'mean'),
		std_success_controlability=('success_controlability', 'std'),
		lower_ci_success_controlability=('success_controlability', lambda x: compute_credible_interval(x)[0]),
		upper_ci_success_controlability=('success_controlability', lambda x: compute_credible_interval(x)[1]),
		
	).reset_index()
	
	# Save the new aggregated statistics to a new CSV file
	fname = csv_file.replace("raw", "aggr")
	grouped_df.to_csv(fname, index=False)
	
	print(f"Aggregated statistics saved to '{fname}'.")
	return fname


# Function to create line plots with credible intervals
def create_line_plots(csv_file, output_dir):
	"""
	Creates line plots with credible intervals over iterations for each fitness type across environments.

	Args:
		csv_file (str): Path to the CSV file containing aggregated statistics.
		output_dir (str): Directory where the plots will be saved.
	"""
	# Load the aggregated statistics from the CSV file
	df = pd.read_csv(csv_file)
	
	# Ensure the output directory exists
	os.makedirs(output_dir, exist_ok=True)
	
	# Iterate over each environment type to generate plots for all environments
	for env_name, env_group in df.groupby('env_name'):
		
		# Iterate over each property to plot
		for prop in ['fitness', 'quality', 'diversity', 'controlability']:
			plt.figure(figsize=(12, 8))
			sns.lineplot(
				data=env_group,
				x='iter_n',
				y=f'mean_{prop}',
				hue='algorithm',
				style='fitness_type',
				markers=False,
				dashes=True,
				errorbar=None
			)
			for key, grp in env_group.groupby(['fitness_type', 'algorithm']):
				plt.fill_between(
					grp['iter_n'],
					grp[f'lower_ci_{prop}'],
					grp[f'upper_ci_{prop}'],
					alpha=0.2,
					label=None#f'{key[0]} - {key[1]} {prop.title()} CI'
				)
				
			# Plot customization
			plt.title(f'{env_name} - {prop.title()} over Iterations')
			plt.xlabel('Iteration')
			plt.ylabel('Mean Values')
			
			# Custom legend
			handles, labels = plt.gca().get_legend_handles_labels()
			unique_labels = dict(zip(labels, handles))  # Remove duplicate labels
			plt.legend(unique_labels.values(), unique_labels.keys(), title='Fitness and Algorithm',
			           bbox_to_anchor=(1.05, 1), loc='upper left')
			
			# plt.ylim(0, 1)

			plt.tight_layout()
			
			# Save the plot
			plot_filename = f"{env_name}_{prop}_statistics_lineplot.png"
			plt.savefig(os.path.join(output_dir, plot_filename))
			plt.close()
			
			print(f"Plot saved: {plot_filename}")


# Define a class to wrap both functions
class DataCruncher:
	def run_pipeline(self,
	                 root_dir,
	                 output_dir):
		fnames = self.process_all_envs(root_dir)
		raw_csv = self.aggregate_envs_statistics(root_dir, fnames)
		aggr_csv = self.aggregate_over_runs(raw_csv)
		self.plot(aggr_csv, output_dir)
	
	def process_environment(self, env_path):
		process_environment(env_path)
	
	def process_all_envs(self, root_dir):
		process_all_envs(root_dir)
	
	def aggregate_envs_statistics(self, root_dir, fnames=None):
		aggregate_envs_statistics(root_dir, fnames)
	
	def aggregate_over_runs(self, csv_file):
		aggregate_over_runs(csv_file)
	
	def plot(self, csv_file, output_dir):
		create_line_plots(csv_file, output_dir)


if __name__ == "__main__":
	if not os.path.exists('./plots'):
		os.mkdir('./plots')
	if not os.path.exists('./results'):
		os.mkdir('./results')
		print(f'Please place all results in ./results/ and run again.')
		exit(-1)
		
	fire.Fire(DataCruncher)
