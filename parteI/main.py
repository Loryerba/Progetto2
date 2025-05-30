from utils import *
import numpy as np
import timeit

def main():
    N_list = list(range(50,1001,50))

    my_dct2_time = []
    dct2_from_lib_time = []


    for n in N_list:
        print("Dimension: ",n)

        np.random.seed(10)

        samnpled_matrix = np.random.uniform(0.0, 255.0, size=(n,n))

        my_dct2_time.append(timeit.timeit(lambda: my_dct2(samnpled_matrix),number = 1))

        dct2_from_lib_time.append(timeit.timeit(lambda: dct2_from_lib(samnpled_matrix),number = 1))
    

    generate_plot(my_dct2_time,dct2_from_lib_time,N_list)

if(__name__ == "__main__"):
    main()

