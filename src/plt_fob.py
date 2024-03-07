import matplotlib.pyplot as plt

# Dados dos três cenários
resultados = {
    "Base": {
        "Funcao_Objetivo": 687486.08,
        "Geracao": {"Barra1": 250.00, "Barra2": 102.13, "Barra3": 251.17},
        "Deficit": {"Barra1": 0.0, "Barra2": 0.0, "Barra3": 0.0},
        "Fluxo_Potencia": {"1-2": 36.87, "1-3": 178.50, "2-3": 50.33},
        "Angulos_Fase": {"Barra1": 0, "Barra2": -0.53, "Barra3": -1.78},
        "Perdas": {"1-2": 2.77, "1-3": 31.86, "2-3": 31.67},
        "Total_Gerado": 603.30,
        "Total_Demandado": 537,
        "Deficit_Total": 0.0
    },
    "Sem_Perda": {
        "Funcao_Objetivo": 451447.44,
        "Geracao": {"Barra1": 250.00, "Barra2": 118.83, "Barra3": 168.17},
        "Deficit": {"Barra1": 0.0, "Barra2": 0.0, "Barra3": 0.0},
        "Fluxo_Potencia": {"1-2": 19.36, "1-3": 230.64, "2-3": 81.19},
        "Angulos_Fase": {"Barra1": 0, "Barra2": -0.28, "Barra3": -2.31},
        "Perdas": {"1-2": 0.0, "1-3": 0.0, "2-3": 0.0},
        "Total_Gerado": 537.00,
        "Total_Demandado": 537,
        "Deficit_Total": 0.0
    },
    "Sem_Efeito_Valvula": {
        "Funcao_Objetivo": 687485.86,
        "Geracao": {"Barra1": 250.00, "Barra2": 102.13, "Barra3": 251.17},
        "Deficit": {"Barra1": 0.0, "Barra2": 0.0, "Barra3": 0.0},
        "Fluxo_Potencia": {"1-2": 36.87, "1-3": 178.50, "2-3": 50.33},
        "Angulos_Fase": {"Barra1": 0, "Barra2": -0.53, "Barra3": -1.78},
        "Perdas": {"1-2": 2.77, "1-3": 31.86, "2-3": 31.67},
        "Total_Gerado": 603.30,
        "Total_Demandado": 537,
        "Deficit_Total": 0.0
    }
}

# Função para plotar gráficos de barras para comparação
def plotar_comparacao(resultados, titulo, y_label, chave):
    # Configurando os dados para o gráfico
    cenarios = resultados.keys()
    valores = [resultados[cenario][chave] for cenario in cenarios]

    # Criando o gráfico de barras
    plt.figure(figsize=(8, 5))
    plt.bar(cenarios, valores, color=['blue', 'red', 'green'])
    plt.title(titulo)
    plt.ylabel(y_label)
    
    
    

    # Adicionando rótulos de valor nas barras
    for i, v in enumerate(valores):
        plt.text(i, v, f'{v:.2f}', ha='center', va='bottom')

    # Exibindo o gráfico
    plt.show()

# Plotando a comparação da função objetivo
plotar_comparacao(resultados, "Comparação da Função Objetivo", "Valor da Função Objetivo", "Funcao_Objetivo")

# Plotando a comparação do total gerado
plotar_comparacao(resultados, "Comparação do Total Gerado", "Energia (MW)", "Total_Gerado")
