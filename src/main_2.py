from pyomo.environ import ConcreteModel, Var, Constraint, NonNegativeReals, Set, sin, Objective, minimize, Reals
from math import pi
from pyomo.opt import SolverFactory
from config_2 import DADOS_BARRAS, DADOS_LINHA, DADOS_DEMANDA, CDEF

# Criação do modelo
modelo = ConcreteModel()

# Definição dos conjuntos
modelo.LINHAS = Set(initialize=[(de, para) for de, para in zip(DADOS_LINHA['DE'], DADOS_LINHA['PARA'])])

# Definição das variáveis
modelo.geracao = Var(DADOS_BARRAS['NUM_BARRA'], within=NonNegativeReals)
modelo.deficit = Var(within=NonNegativeReals)
modelo.theta = Var(DADOS_BARRAS['NUM_BARRA'], bounds=(-pi, pi))
modelo.theta[1].fix(0)  # Fixar o ângulo da barra de referência em 0
modelo.P = Var(modelo.LINHAS, within=Reals)

# Função objetivo
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

# Restrições de limites de geração
def limites_geracao_min(modelo, i):
    return modelo.geracao[i] >= DADOS_BARRAS.loc[i-1, 'PMIN(MW)']
modelo.limites_min = Constraint(DADOS_BARRAS['NUM_BARRA'], rule=limites_geracao_min)

def limites_geracao_max(modelo, i):
    return modelo.geracao[i] <= DADOS_BARRAS.loc[i-1, 'PMAX(MW)']
modelo.limites_max = Constraint(DADOS_BARRAS['NUM_BARRA'], rule=limites_geracao_max)

# Restrição de balanço de demanda e oferta com déficit e fluxo de potência
def balanco_demanda_oferta_rule(modelo, barra):
    balanco = modelo.geracao[barra] + modelo.deficit

    for (i, j) in modelo.LINHAS:
        susceptancia = DADOS_LINHA.loc[(DADOS_LINHA['DE'] == i) & (DADOS_LINHA['PARA'] == j), 'SUSCEPTÂNCIA(OHMS)'].iloc[0]
        if i == barra:  # Fluxo saindo da barra
            balanco -= modelo.P[i, j]
        elif j == barra:  # Fluxo entrando na barra
            balanco += modelo.P[i, j]

    demanda = DADOS_DEMANDA[0][barra]
    return balanco == demanda

modelo.balanco_demanda_oferta = Constraint(DADOS_BARRAS['NUM_BARRA'], rule=balanco_demanda_oferta_rule)


# Restrições de fluxo de potência e limites de potência
def fluxo_potencia_rule(modelo, i, j):
    susceptancia = DADOS_LINHA.loc[(DADOS_LINHA['DE'] == i) & (DADOS_LINHA['PARA'] == j), 'SUSCEPTÂNCIA(OHMS)'].iloc[0]
    return modelo.P[i, j] == susceptancia * (modelo.theta[i] - modelo.theta[j])
modelo.fluxo_potencia = Constraint(modelo.LINHAS, rule=fluxo_potencia_rule)

def limites_potencia_rule(modelo, i, j):
    limite = DADOS_LINHA.loc[(DADOS_LINHA['DE'] == i) & (DADOS_LINHA['PARA'] == j), 'LIMITE(MW)'].iloc[0]
    return (-limite, modelo.P[i, j], limite)
modelo.limites_potencia = Constraint(modelo.LINHAS, rule=limites_potencia_rule)

# Solução do modelo
solver = SolverFactory('ipopt', executable='F:\\ipopt\\bin\\ipopt.exe')  
resultado = solver.solve(modelo, tee=True)

# Status da Solução
print("Status da Solução:", resultado.solver.status)
print("Terminação devido a:", resultado.solver.termination_condition)
print("Valor da Função Objetivo:", modelo.custo_total())

# Resultados da Geração e Déficit
print("\nResultados da Geração e Déficit em Cada Barra:")
for barra in DADOS_BARRAS['NUM_BARRA']:
    print(f"Barra {barra} - Geração: {modelo.geracao[barra].value} MW, Déficit: {modelo.deficit.value} MW")

# Balanço de Demanda e Oferta
print("\nBalanço de Demanda e Oferta:")
for barra in DADOS_BARRAS['NUM_BARRA']:
    total_gerado = modelo.geracao[barra].value
    total_demandado = DADOS_DEMANDA[0][barra]
    print(f"Barra {barra} - Total Gerado: {total_gerado} MW, Total Demandado: {total_demandado} MW")

# Total Geral
total_gerado = sum(modelo.geracao[i].value for i in DADOS_BARRAS['NUM_BARRA'])
total_demandado = sum(DADOS_DEMANDA[0][i+1] for i in range(len(DADOS_BARRAS)))
print(f"\nTotal Geral Gerado: {total_gerado} MW, Total Geral Demandado: {total_demandado} MW")
print("Déficit Total de Energia: {modelo.deficit.value} MW")

# Fluxos de Potência entre as Barras
print("\nFluxos de Potência entre as Barras:")
for (i, j) in modelo.LINHAS:
    fluxo_potencia = modelo.P[i, j].value
    limite = DADOS_LINHA.loc[(DADOS_LINHA['DE'] == i) & (DADOS_LINHA['PARA'] == j), 'LIMITE(MW)'].iloc[0]
    print(f"De {i} para {j} - Fluxo: {fluxo_potencia} MW, Limite: {limite} MW")
    if abs(fluxo_potencia) > limite:
        print(f"  Atenção: Fluxo excede o limite!")

# Ângulos de Fase
print("\nÂngulos de Fase nas Barras:")
for barra in modelo.theta:
    angulo = modelo.theta[barra].value
    print(f"Barra {barra} - Ângulo: {angulo} radianos")

# Verificação do Balanço de Energia
print("\nVerificação do Balanço de Energia em Cada Barra:")
for barra in DADOS_BARRAS['NUM_BARRA']:
    geracao = modelo.geracao[barra].value
    deficit = modelo.deficit.value
    fluxo_total = sum(modelo.P[i, j].value for (i, j) in modelo.LINHAS if i == barra) - \
                  sum(modelo.P[i, j].value for (i, j) in modelo.LINHAS if j == barra)
    demanda = DADOS_DEMANDA[0][barra]
    balanco = geracao + deficit - fluxo_total
    print(f"Barra {barra} - Balanço: {balanco} MW, Demanda: {demanda} MW")
    if abs(balanco - demanda) > 1e-6:
        print(f"  Atenção: Desbalanceamento detectado na Barra {barra}!")
