from scipy.fft import dct,dctn
import numpy as np
import math
import matplotlib.pyplot as plt


def dct2_from_lib(f):
    return dctn(f,type=2,norm="ortho")
   

# Funzione per creare la matrice di trasformazione D (DCT1)
def get_transformation_matrix(n):
    # Creazione del vettore alfa lungo quanto il vettore passato
    alpha = np.zeros(n)

    # Calcolo dei valori in base alla posizione
    alpha[0] = 1.0 / np.sqrt(n)
    alpha[1:] = np.sqrt(2.0/n)

    # Creazione della matrice di trasformazione
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = alpha[i] * np.cos((i * math.pi * (2 * j + 1)) / (2 * n))
    return D

# Funzione per DCT1 (una dimensione)
def my_dct1(sampled_vector):
    vector_dim = len(sampled_vector)

    D = get_transformation_matrix(vector_dim)

    # DCT utilizzando scipy.fft.dct (versione tipo I)
    return np.dot(D,sampled_vector)

# Funzione per DCT2 (due dimensioni) utilizzando scipy.fft.dct
def my_dct2(sampled_matrix):
    n,m = sampled_matrix.shape
    
    result = np.copy(sampled_matrix.astype('float64'))
        # DCT per ogni colonna
    for j in range(m):
        result[:, j] = my_dct1(result[:, j])
    
    # DCT per ogni riga
    for i in range(n):
        result[i, :] = my_dct1(result[i, :])
    
    return result


def generate_plot(my_dct2_time,dct2_lib_time, N_list):
    plt.figure(figsize=(10,6))

    n3 = [n**3/ 1e5 for n in N_list]
    n2logn = [n**2 * np.log(n) / 1e8 for n in N_list]

    plt.semilogy(N_list,my_dct2_time,label="My DCT2", color="blue")
    
    plt.semilogy(N_list,dct2_lib_time,label="DCT2 from lib", color="red")

    plt.semilogy(N_list,n3,label="Theorical n3", color="blue",linestyle="dashed")
    
    plt.semilogy(N_list,n2logn,label="Theorical n2log(n)", color="red", linestyle="dashed")
    # Impostazione delle etichette degli assi e del titolo del grafico
    plt.xlabel('N')
    plt.ylabel('Tempo di esecuzione in secondi')
    plt.title('Confronto tempi di esecuzione DCT2 homemade e DCT2 libreria')
    
    plt.legend()

    # Aggiunta di una griglia al grafico
    plt.grid(True)

    plt.savefig("Plot_Di_Confronto.png")
    # Visualizzazione del grafico
    plt.show()
    