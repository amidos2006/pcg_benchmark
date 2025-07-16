# Testing file for all the problems in the pcg benchmark
import pcg_benchmark

if __name__ == '__main__':
    # list all the problems in the pcg benchmark
    for name in pcg_benchmark.list():
        # create an environment for the input named problem
        env = pcg_benchmark.make(name)
        # generate random content that is legal from this problem. It can be used for a starting point for your generator
        contents = [env.content_space.sample() for _ in range(100)]
        # the range of values that content can lies within. It can be used for mutation function for evolution
        content_range = env.content_space.range()
        # generate a random control parameters for this problem can be used to check if your generator can be controlled
        # The controls can be just one parameter for all the content and not one for each content
        controls = [env.control_space.sample() for _ in range(100)]
        # the range of values that the control parameter can have. It can be used to noramlize the control values
        control_range = env.control_space.range()
        # evaluate the current contents and controls with respect to each other and returns
        # q: percentage of content that passes the quality metric of the benchmark
        # d: percentage of content that passes the diversity metric of the benchmark
        # c: percentage of content that passes the controlability test of the benchmark
        # details: a dictionary of arrays for "quality", "diversity", and "controlability" 
        # where it have a value for each content between 0 and 1 where 1 passes the benchmark
        # info: details about all the content when it is being tested
        q,d,c,details,info = env.evaluate(contents, controls)
        # Print the details about the evaluation
        print(f"Testing {name}: ", q,d,c)
        print("\tContent Range: ", content_range)
        print("\tControl Range: ", control_range)