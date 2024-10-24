import json
import os
from typing import List, Optional

import fire
import matplotlib.pyplot as plt
import matplotlib
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
	sem = stats.sem(data)
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
	
	df = df.loc[df['fitness_type'] == 'quality']
	
	# Ensure the output directory exists
	os.makedirs(output_dir, exist_ok=True)
	
	# Change matplotlib font properties
	matplotlib.rcParams.update({'font.size': 40})
	
	# Iterate over each environment type to generate plots for all environments
	for env_name, env_group in df.groupby('env_name'):
		
		# Iterate over each property to plot
		for prop in ['fitness']:#, 'quality', 'diversity', 'controlability']:
			plt.figure(figsize=(12, 8))
			lineplot = sns.lineplot(
				data=env_group,
				x='iter_n',
				y=f'mean_{prop}',
				hue='algorithm',
				hue_order=['random', 'ga', 'es'],  # Custom sorting of the algorithms
				#style='fitness_type',
				markers=False,
				dashes=True,
				errorbar=None
			)
			#for key, grp in env_group.groupby(['fitness_type', 'algorithm']):
			for key, grp in env_group.groupby(['algorithm']):
				color = lineplot.get_lines()[['random', 'ga', 'es'].index(key[0])].get_color()
				plt.fill_between(
					grp['iter_n'],
					grp[f'lower_ci_{prop}'],
					grp[f'upper_ci_{prop}'],
					alpha=0.2,
					color=color,
					label=None#f'{key[0]} - {key[1]} {prop.title()} CI'
				)
				
			# Plot customization
			#plt.title(f'{env_name} - {prop.title()} over Iterations')
			#plt.xlabel('Iteration')
			#plt.ylabel(f'Mean {prop.title()}')
						
			plt.xticks([0, 50, 100, 150, 200])
			plt.yticks([0., 0.25, 0.5, 0.75, 1.0])
			
			plt.xlabel('Generation' if env_name in ['smb-v0', 'sokoban-v0', 'talakat-v0', 'zelda-v0'] else '')
			plt.ylabel(f'Mean {prop.title()}' if env_name in ['arcade-v0', 'elimination-v0', 'smb-v0'] else '')
			plt.legend([],[],frameon=False)
			plt.ylim(0, 1.1)

			plt.tight_layout()
			
			# Save the plot
			plot_filename = f"{env_name}_{prop}_statistics_lineplot.png"
			plt.savefig(os.path.join(output_dir, plot_filename))
			
			
			# Custom legend
			handles, labels = plt.gca().get_legend_handles_labels()
			for i, label in enumerate(labels):
				if label == 'fitness_type':
					labels[i] = 'Fitness function'
					handles[i].set_linewidth(0.0)
				if label == 'algorithm':
					labels[i] = 'Algorithm'
					handles[i].set_linewidth(0.0)
			unique_labels = dict(zip(labels, handles))  # Remove duplicate labels
			legend = plt.legend(unique_labels.values(), unique_labels.keys(), title='',
								ncol=len(unique_labels), loc='lower left')
			for legend_obj in legend.legend_handles:
				legend_obj.set_linewidth(4.0)
			fig = legend.figure
			fig.patch.set_alpha(0.0)
			fig.canvas.draw()
			bbox = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
			fig.savefig(os.path.join(output_dir, 'legend.png'), bbox_inches=bbox, transparent=True)
			
			plt.close()
			
			print(f"Plot saved: {plot_filename}")


def render_elites(csv_file, output_dir):
	import pcg_benchmark
	
	df = pd.read_csv(csv_file)
	folder_path = os.path.join(csv_file, '..')  # This is a hack, I know, but it works
		
	for env_name in df['env_name'].unique():
		for fitness_type in df['fitness_type'].unique():
			for algorithm in df['algorithm'].unique():
				elites = []
				fitnesses = []
				runs = []
				for run_n in df['run_n'].unique():
					print(f'Processing {env_name} ({fitness_type} - {algorithm} - {run_n})')
					run_data = df.loc[
						(df['env_name'] == env_name) &
						(df['fitness_type'] == fitness_type) &
						(df['algorithm'] == algorithm) &
						(df['run_n'] == run_n)]
					last_iter = max(run_data['iter_n'])
					elites.append(run_data.loc[run_data['iter_n'] == last_iter]['elite'].values[0])
					fitnesses.append(run_data.loc[run_data['iter_n'] == last_iter]['fitness'].values[0])
					runs.append(run_n)
					
				idxs = np.argsort(fitnesses)[::-1]
				elites_sorted = [elites[idx] for idx in idxs]
				fitnesses_sorted = [fitnesses[idx] for idx in idxs]
				runs_sorted = [runs[idx] for idx in idxs]
				
				for i, (elite, fitness, run_n) in enumerate(zip(elites_sorted, fitnesses_sorted, runs_sorted)):
					with open(f'{folder_path}/{env_name}/{fitness_type}/{algorithm}/{run_n}/iter_{last_iter}/{elite}', 'r') as f:
						latest_elite = json.load(f)
					
					env = pcg_benchmark.make(env_name)
					str_fitness = '__' + str(fitness).replace('.', '_') + '__'
					
					if env_name != 'talakat-v0':
						env.render(latest_elite['content']).save(os.path.join(output_dir, f'{env_name}_{fitness_type}_{algorithm}_n{i}{str_fitness}{run_n}_elite.png'))
					else:
						frames = env.render(latest_elite['content'])
						frames[0].save(os.path.join(output_dir, f'{env_name}_{fitness_type}_{algorithm}_n{i}{str_fitness}{run_n}_elite.gif'), append_images=frames[1:], save_all=True, duration=100, loop=0)
					
					if i == 2: break

						
def to_latex_table(csv_file,
				   metric,
				   output_dir):
	env_names_latex = [
		"Arcade Rules", "Binary", "Building", "Dangerous Dave", "Elimination", 
		"The Binding of Isaac", "Lode Runner", "Mini Dungeons", "Super Mario Bros", 
		"Sokoban", "Talakat", "Zelda"
	]

	env_names_df = [
		"arcade-v0", "binary-v0", "building-v0", "ddave-v0", "elimination-v0", 
		"isaac-v0", "loderunner-v0", "mdungeons-v0", "smb-v0", 
		"sokoban-v0", "talakat-v0", "zelda-v0"
	]

	algorithms_latex = ['Random Search', '$\mu + \lambda$ Evolution Strategy', 'Genetic Algorithm']
	algorithms_df = ['random', 'es', 'ga']

	# Initialize LaTeX table
	latex_code = r'''
	\begin{table*}
		\centering
		\begin{tabular}{|l||c|c|c|c|c|c|c|c|c|}
			\hline
			& \multicolumn{3}{|c|}{Random Search} & \multicolumn{3}{|c|}{$\mu + \lambda$ Evolution Strategy} & \multicolumn{3}{|c|}{Genetic Algorithm} \\\cline{2-10}
			& Q & QC & QCD & Q & QC & QCD & Q & QC & QCD \\
			\hline \hline
	'''

	df = pd.read_csv(csv_file)
	
	# Iterate through environment names and append data
	for env_name_latex, env_name_df in zip(env_names_latex, env_names_df):
		# Initialize row with environment name
		row = f'        {env_name_latex}'

		means = []
		ci_diffs = []

		# Fetch data for the environment and different algorithms
		for algo in algorithms_df:
			for fitness in ['quality', 'quality_control', 'quality_control_diversity']:
				# Filter the dataframe for the current environment and algorithm
				row_data = df[(df['env_name'] == env_name_df) & 
								(df['algorithm'] == algo) &
								(df['fitness_type'] == fitness) & 
								(df['iter_n'] == max(df['iter_n'].unique()))
								]
				mean_value = row_data[f'mean_success_{metric}'].values[-1]
				means.append(mean_value)
				ci_diff_value = row_data[f'upper_ci_success_{metric}'].values[-1]
				ci_diffs.append(ci_diff_value)
				
		max_mean_value = np.max(means)

		for (mean, ci_diff) in zip(means, ci_diffs):
			if mean == max_mean_value:
				row += '& \\textbf{' + f'{mean:.2f}' + '}'
				if not np.isnan(ci_diff):
					row += '$\\mathbf{\\pm}$\\textbf{' + f'{(ci_diff - mean):2f}' + '}'
			else:
				row += f'& {mean:.2f}'
				if not np.isnan(ci_diff):
					row += f'$\\pm${(ci_diff - mean):2f}'

		# Close the row
		row += r' \\\hline'
		
		# Append row to LaTeX table
		latex_code += row + '\n'

	# Close the table
	latex_code += r'''
		\end{tabular}
		\caption{This table shows the number of individuals in the final generation that pass the benchmark criteria for the \textit{controllability} metric for every different problem. The reported value is the mean between 10 runs followed by the 95\% confidence interval.}
		\label{tab:benchmark_control}
	\end{table*}
	'''

	with open(os.path.join(output_dir, f'{metric}.tex'), 'w') as f:
		f.write(latex_code)


def compute_runs_diversity(csv_file,
						   output_dir):
	import pcg_benchmark
	df = pd.read_csv(csv_file)

	folder_path = os.path.join(csv_file, '..')  # This is a hack, I know, but it works
	
	matplotlib.rcParams.update({'font.size': 30})
	
	plot_data = pd.DataFrame(columns=[
		'fitness_type', 'env_name', 'algorithm', 'elites_diversity', 'mean_success'
	])
	
	for fitness_type in tqdm(df['fitness_type'].unique(), desc='Fitness type', leave=False, dynamic_ncols=True):
		for env_name in tqdm(df['env_name'].unique(), desc='Environment', leave=False, dynamic_ncols=True):

			env = pcg_benchmark.make(env_name)

			for algorithm in tqdm(df['algorithm'].unique(), desc='Algorithm', leave=False, dynamic_ncols=True):
				elites = []
				controls = []
				n_success_quality = []
				for run_n in tqdm(df['run_n'].unique(), desc='Run number', leave=False, dynamic_ncols=True):
					run_data = df.loc[
						(df['env_name'] == env_name) &
						(df['fitness_type'] == fitness_type) &
						(df['algorithm'] == algorithm) &
						(df['run_n'] == run_n)]
					last_iter = max(run_data['iter_n'])
					elite_fname = run_data.loc[run_data['iter_n'] == last_iter]['elite'].values[0]
					with open(f'{folder_path}/{env_name}/{fitness_type}/{algorithm}/{run_n}/iter_{last_iter}/{elite_fname}', 'r') as f:
						elite = json.load(f)
					elites.append(elite['content'])
					controls.append(elite['control'])
					n_success_quality = run_data.loc[run_data['iter_n'] == last_iter]['success_quality'].values[0]
				diversity = env.diversity(elites)[0] * 100
				controlability = env.controlability(elites, controls)[0] * 100
				mean_success = np.mean(n_success_quality)
				plot_data = plot_data._append({'fitness_type': fitness_type, 'env_name': env_name, 'algorithm': algorithm, 'elites_diversity': diversity, 'elites_controlability': controlability, 'mean_success': mean_success}, ignore_index=True)
		
	fitness_types = plot_data['fitness_type'].unique()

	for fitness in fitness_types:
		fitness_data = plot_data[plot_data['fitness_type'] == fitness]

		plt.figure(figsize=(12, 8))
		sns.barplot(x='env_name', y='elites_diversity',
					hue='algorithm', hue_order=['random', 'ga', 'es'],  # Custom sorting of the algorithms,
					data=fitness_data)
		
		plt.title('')
		plt.xlabel('Problems')
		plt.xticks(rotation=45, ha='right')
		plt.ylabel('% Unique Individuals')
		plt.yticks([0, 25, 50, 75, 100])
		
		plt.legend([],[],frameon=False)
		plt.tight_layout()
		
		plot_filename = f"diversity_{fitness}.png"
		plt.savefig(os.path.join(output_dir, plot_filename))
		
	for fitness in fitness_types:
		fitness_data = plot_data[plot_data['fitness_type'] == fitness]

		plt.figure(figsize=(12, 8))
		sns.barplot(x='env_name', y='elites_controlability',
					hue='algorithm', hue_order=['random', 'ga', 'es'],  # Custom sorting of the algorithms,
					data=fitness_data)
		
		plt.title('')
		plt.xlabel('Problems')
		plt.xticks(rotation=45, ha='right')
		plt.ylabel('% Unique Individuals')
		plt.yticks([0, 25, 50, 75, 100])
		
		plt.legend([],[],frameon=False)
		plt.tight_layout()
		
		plot_filename = f"controlability_{fitness}.png"
		plt.savefig(os.path.join(output_dir, plot_filename))

	for fitness in fitness_types:
		fitness_data = plot_data[plot_data['fitness_type'] == fitness]

		plt.figure(figsize=(12, 8))
		sns.barplot(x='env_name', y='mean_success',
					hue='algorithm', hue_order=['random', 'ga', 'es'],  # Custom sorting of the algorithms,
					data=fitness_data)
		
		plt.title('')
		plt.xlabel('Problems')
		plt.xticks(rotation=45, ha='right')
		plt.ylabel('Mean % Success')
		plt.yticks([0, 25, 50, 75, 100])
		
		plt.legend([],[],frameon=False)
		plt.tight_layout()
		
		plot_filename = f"success_{fitness}.png"
		plt.savefig(os.path.join(output_dir, plot_filename))
		
	
class DataCruncher:
	def run_pipeline(self,
	                 root_dir,
	                 output_dir,
					 renders_dir,
					 latex_dir):
		fnames = self.process_all_envs(root_dir)
		raw_csv = self.aggregate_envs_statistics(root_dir, fnames)
		aggr_csv = self.aggregate_over_runs(raw_csv)
		self.plot(aggr_csv, output_dir)
		self.render_elites(raw_csv, renders_dir)
		self.to_latex(aggr_csv, latex_dir)
	
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
	
	def render_elites(self, csv_file, renders_dir):
		render_elites(csv_file, renders_dir)
	
	def to_latex(self, csv_file, latex_dir):
		for metric in ['quality', 'controlability', 'diversity']:
			to_latex_table(csv_file, metric, latex_dir)
	
	def compute_runs_diversity(self, csv_file, output_dir):
		compute_runs_diversity(csv_file, output_dir)
	

if __name__ == "__main__":
	if not os.path.exists('./plots'):
		os.mkdir('./plots')
	if not os.path.exists('./results'):
		os.mkdir('./results')
		print(f'Please place all results in ./results/ and run again.')
		exit(-1)
		
	fire.Fire(DataCruncher)
