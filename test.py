import pcg_benchmark

for name in pcg_benchmark.list():
    env = pcg_benchmark.make(name)
    contents = env.random_content()
    content_range = env.content_range()
    controls = env.random_control()
    control_range = env.control_range()
    q,d,c,details,info = env.evaluate(contents, controls)
    print(f"Testing {name}: ", q,d,c)
    print("\tContent Range: ", content_range)
    print("\tControl Range: ", control_range)