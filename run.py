from generators.utils import fitness_quality, fitness_quality_control, fitness_quality_control_diversity
import argparse
import pcg_benchmark
from importlib import import_module
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Running a Generato from the list of generators.')
    parser.add_argument('outputfolder', type=str, help='the folder to save the search')
    parser.add_argument('-p', '--problem', type=str, default='binary-v0', help='what is the problem that you are trying to solve (`binary-v0`, `zelda-v0`, `sokoban-v0`, ...).')
    parser.add_argument('-g', '--generator', type=str, default='random', help='what is the generator file name from generators folder (`ga`, `es`, `random`, ...).')
    parser.add_argument('-f', '--fitness', type=str, default='quality', help='what is the fitness function (`quality`, `quality_control`, `quality_control_diversity`, ...)')
    parser.add_argument('-s', '--steps', type=int, default=100, help='the number of iterations to run that generator')
    parser.add_argument('-e', '--early_stop', action="store_true", help="stop evolution when the max fitness is 1")

    args = parser.parse_args()

    env = pcg_benchmark.make(args.problem)

    module = import_module(f"generators.utils")
    if not hasattr(module, f"{args.fitness}"):
        if not hasattr(module, f"fitness_{args.fitness}"):
            raise ValueError(f"{args.fitness} function or fitness_{args.fitness} doesn't exist in generators.utils")
        fitness_fn = getattr(module, f"fitness_{args.fitness}")
    else:
        fitness_fn = getattr(module, f"{args.fitness}")

    module = import_module(f"generators.{args.generator}")
    if not hasattr(module, "Generator"):
        raise ValueError(f"generators.{args.generator}.Generator doesn't exist.")
    generator = module.Generator(env, fitness_fn)

    print(f"Starting {args.generator}:")
    generator.reset()
    fitness = [fitness_fn(c) for c in generator._chromosomes]
    print(f"  Iteration 0: {np.max(fitness):.2f}, {np.mean(fitness):.2f}, {np.std(fitness):.2f}")
    generator.save(f"{args.outputfolder}/iter_0")
    for i in range(args.steps):
        generator.update()
        fitness = [fitness_fn(c) for c in generator._chromosomes]
        print(f"  Iteration {i}: {np.max(fitness):.2f}, {np.mean(fitness):.2f}, {np.std(fitness):.2f}")
        generator.save(f"{args.outputfolder}/iter_{i+1}")
        if args.early_stop and np.max(fitness) >= 1:
            break
