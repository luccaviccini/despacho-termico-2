import pandas as pd

# BARRA  a  b  c  e  f  PMIN(MW) PMAX(MW)
barras =  [[1,26.97, 1.3975 , 0.002176, 0.2697  , -3.975, 0, 250],
           [2,1.865, 22.355 , 0.001938, 0.002155, -0.428, 0, 157],
           [3,69.79, 15.3116, 0.001457, 0.03979 , -3.116, 0, 388]]

DADOS_BARRAS = pd.DataFrame(barras, columns=['NUM_BARRA', "a","b","c","e","f", 'PMIN(MW)',  "PMAX(MW)",])

# DE   PARA  CONDUTÂNCIA(OHMS) SUSCEPTÂNCIA(OHMS)  LIMITE (MW)
linhas = [[1, 2, 10, 70,  200],
          [1, 3, 10, 100, 300],
          [2, 3, 20, 40 , 100]]

DADOS_LINHA = pd.DataFrame(linhas, columns=['DE', 'PARA', 'CONDUTÂNCIA(OHMS)','SUSCEPTÂNCIA(OHMS)', 'LIMITE(MW)'])

DADOS_DEMANDA = [[1,0,57,480]] # HORA, DEMANDA BARRA 1, DEMANDA BARRA 2, DEMANDA BARRA 3

CDEF = 1000000000 # Custo do DEFICIT

