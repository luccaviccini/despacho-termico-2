from pyomo.environ import ConcreteModel, Var, Objective, Constraint, NonNegativeReals, minimize, RealSet, sin, Set
from math import pi  # Importar pi do módulo math
from pyomo.opt import SolverFactory
from config_2 import DADOS_BARRAS, DADOS_LINHA, DADOS_DEMANDA, CDEF


modelo = ConcreteModel()

modelo.geracao = Var(DADOS_BARRAS['NUM_BARRA'], within=NonNegativeReals)
modelo.deficit = Var(within=NonNegativeReals)# Variáveis para os fluxos de potência nas linhas

# Variáveis para os ângulos de fase das tensões, com a barra de referência fixada em 0 e as outras barras entre -pi e pi
modelo.theta = Var(DADOS_BARRAS['NUM_BARRA'], bounds=(-pi, pi))
modelo.theta[1].fix(0)  # Fixar o ângulo da barra de referência em 0



def custo_geracao_e_deficit(modelo):
    custo_geracao = sum(DADOS_BARRAS.loc[barra-1, 'a'] * modelo.geracao[barra] + 
                        (DADOS_BARRAS.loc[barra-1, 'b'] / 2) * modelo.geracao[barra]**2 + 
                        (DADOS_BARRAS.loc[barra-1, 'c'] / 3) * modelo.geracao[barra]**3 +
                        DADOS_BARRAS.loc[barra-1, 'e'] * sin(DADOS_BARRAS.loc[barra-1, 'f'] * 
                        (DADOS_BARRAS.loc[barra-1, 'PMIN(MW)'] - modelo.geracao[barra]))
                        for barra in DADOS_BARRAS['NUM_BARRA'])
    custo_deficit = CDEF * modelo.deficit
    return custo_geracao + custo_deficit

modelo.custo_total = Objective(rule=custo_geracao_e_deficit, sense=minimize)


def limites_geracao_min(modelo, i):
    return modelo.geracao[i] >= DADOS_BARRAS.loc[i-1, 'PMIN(MW)']

def limites_geracao_max(modelo, i):
    return modelo.geracao[i] <= DADOS_BARRAS.loc[i-1, 'PMAX(MW)']

modelo.limites_min = Constraint(DADOS_BARRAS['NUM_BARRA'], rule=limites_geracao_min)
modelo.limites_max = Constraint(DADOS_BARRAS['NUM_BARRA'], rule=limites_geracao_max)

def balanco_demanda_oferta_com_deficit(modelo):
    total_geracao = sum(modelo.geracao[i] for i in DADOS_BARRAS['NUM_BARRA'])
    total_demanda = sum(DADOS_DEMANDA[0][i+1] for i in range(len(DADOS_BARRAS)))
    return total_geracao + modelo.deficit == total_demanda

modelo.balanco = Constraint(rule=balanco_demanda_oferta_com_deficit)

modelo.LINHAS = Set(initialize=[(de, para) for de, para in zip(DADOS_LINHA['DE'], DADOS_LINHA['PARA'])])
modelo.P = Var(modelo.LINHAS, within=RealSet)

# Definindo a regra da restrição
def fluxo_potencia_nl_rule(modelo, i, j):
    X_ij = DADOS_LINHA[(DADOS_LINHA['DE'] == i) & (DADOS_LINHA['PARA'] == j)].iloc[0]['SUSCEPTÂNCIA(OHMS)']
    return modelo.P[i, j] == ((modelo.theta[i] - modelo.theta[j])**2 / X_ij)

modelo.fluxo_potencia_nl = Constraint(modelo.LINHAS, rule=fluxo_potencia_nl_rule)

def limites_potencia_rule(modelo, i, j):
    limite = DADOS_LINHA[(DADOS_LINHA['DE'] == i) & (DADOS_LINHA['PARA'] == j)].iloc[0]['LIMITE(MW)']
    return (-limite, modelo.P[i, j], limite)

modelo.limites_potencia = Constraint(modelo.LINHAS, rule=limites_potencia_rule)





solver = SolverFactory('ipopt', executable='F:\\ipopt\\bin\\ipopt.exe')  
resultado = solver.solve(modelo, tee=True)

print("Status da Solução:", resultado.solver.status)
print("Terminação devido a:", resultado.solver.termination_condition)

for barra in DADOS_BARRAS['NUM_BARRA']:
    print(f"Geração na Barra {barra}: {modelo.geracao[barra].value} MW")
print("Custo Total da Geração: $", modelo.custo_total())

# Para cada barra, verificar se os limites de geração foram respeitados
for i in DADOS_BARRAS['NUM_BARRA']:
    print(f"Barra {i} - Geração Mínima: {modelo.limites_min[i].lower}, Geração: {modelo.geracao[i].value}, Geração Máxima: {modelo.limites_max[i].upper}")

# Verificar o balanço de demanda e oferta
total_gerado = sum(modelo.geracao[i].value for i in DADOS_BARRAS['NUM_BARRA'])
total_demandado = sum(DADOS_DEMANDA[0][i+1] for i in range(len(DADOS_BARRAS)))
print(f"Total Gerado: {total_gerado} MW, Total Demandado: {total_demandado} MW")
print("Déficit de Energia: ", modelo.deficit.value, "MW")