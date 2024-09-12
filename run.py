from generators.utils import fitness_quality, fitness_quality_control, fitness_quality_control_diversity
import argparse
import pcg_benchmark
from importlib import import_module
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Running a Generato from the list of generators.')
    parser.add_argument('foldername', type=str, help='the folder to save the search')
    parser.add_argument('-p', '--problem', type=str, default='binary', help='what is the problem that you are trying to solve.')
    parser.add_argument('-g', '--generator', type=str, default='random', help='what is the generator file name from generators folder (ga, es, random).')
    parser.add_argument('-f', '--fitness', type=str, default='quality', help='what is the fitness function (quality, quality_control, quality_control_diversity)')
    parser.add_argument('-s', '--steps', type=int, default=1000, help='the number of generations to run that generator')

    args = parser.parse_args()

    env = pcg_benchmark.make(args.problem)

    module = import_module(f"generators.utils")
    if not hasattr(module, f"fitness_{args.fitness}"):
        raise ValueError("")
    fitness_fn = getattr(module, f"fitness_{args.fitness}")

    module = import_module(f"generators.{args.generator}")
    if not hasattr(module, "Generator"):
        raise ValueError("")
    generator = module.Generator(env, fitness_fn)

    print(f"Starting {args.generator}:")
    generator.reset()
    fitness = [fitness_fn(c) for c in generator._chromosomes]
    print(f"  Generation 0: {np.max(fitness):.2f}, {np.mean(fitness):.2f}, {np.std(fitness):.2f}")
    generator.save(f"{args.foldername}/gen_0")
    for i in range(args.steps):
        generator.update()
        fitness = [fitness_fn(c) for c in generator._chromosomes]
        print(f"  Generation {i}: {np.max(fitness):.2f}, {np.mean(fitness):.2f}, {np.std(fitness):.2f}")
        generator.save(f"{args.foldername}/gen_{i+1}")
