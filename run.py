import argparse
import pcg_benchmark
from importlib import import_module

def isFloat(number):
    try:
        test = float(number)
        return True
    except:
        return False

def convert2Dic(commands):
    if len(commands) % 2 == 1:
        raise ValueError("inputs have to be tuples example (--fitness quality).")
    result = {}
    for i in range(0, len(commands), 2):
        key = commands[i]
        if key.startswith('--'):
            key = key.split('--')[-1]
        if commands[i+1].isnumeric():
            result[key] = int(commands[i+1])
        elif isFloat(commands[i+1]):
            result[key] = float(commands[i+1])
        else:
            result[key] = commands[i+1]
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Running a Generato from the list of generators. You can adjust any hyperparameter of any algorithm based on their extra inputs. For example, GA/ES/Random can set the fitness function by --fitness followed by name of the function in the search.py file.')
    parser.add_argument('outputfolder', type=str, help='the folder to save the search')
    parser.add_argument('-p', '--problem', type=str, default='binary-v0', help='what is the problem that you are trying to solve (`binary-v0`, `zelda-v0`, `sokoban-v0`, ...).')
    parser.add_argument('-g', '--generator', type=str, default='random', help='what is the generator file name from generators folder (`ga`, `es`, `random`, ...).')
    parser.add_argument('-s', '--steps', type=int, default=100, help='the number of iterations to run that generator')
    parser.add_argument('-e', '--early_stop', action="store_true", help="stop generation when the best function is 1")

    args, additional = parser.parse_known_args()
    add_args = convert2Dic(additional)

    env = pcg_benchmark.make(args.problem)
    if "seed" in add_args:
        env.seed(add_args["seed"])

    module = import_module(f"generators.{args.generator}")
    if not hasattr(module, "Generator"):
        raise ValueError(f"generators.{args.generator}.Generator doesn't exist.")
    generator = module.Generator(env)

    print(f"Starting {args.generator}:")
    generator.reset(**add_args)
    print(f"  Iteration 0: {generator.best():.2f}")
    generator.save(f"{args.outputfolder}/iter_0")
    for i in range(args.steps):
        generator.update()
        print(f"  Iteration {i}: {generator.best():.2f}")
        generator.save(f"{args.outputfolder}/iter_{i+1}")
        if args.early_stop and generator.best() >= 1:
            break
