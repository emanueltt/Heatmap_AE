import os
import pandas as pd
import geopandas as gpd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Função chamada para selecionar o arquivo
def selecionar_arquivo():
    global caminho_arquivo  # Declara que vai utilizar a variável global
    caminho_arquivo = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if caminho_arquivo:  # Se um arquivo foi selecionado
        atualizar_interface_apos_selecao()


def atualizar_interface_apos_selecao():
    # Remove o botão "Selecionar Arquivo"
    selecionar_arquivo_button.grid_remove()
    # Adiciona o botão "Aplicar Seleção"
    aplicar_button.grid(row=5, columnspan=2, padx=5, pady=5)

# Função para converter números menores que 10 para texto
def converter_para_texto(numero):
    numeros_textuais = {
        0: 'Zero',
        1: 'Um',
        2: 'Dois',
        3: 'Três',
        4: 'Quatro',
        5: 'Cinco',
        6: 'Seis',
        7: 'Sete',
        8: 'Oito',
        9: 'Nove'
    }
    return numeros_textuais.get(numero, str(numero))

def conta_Caracteristicas():
    global fullscreen_ativado   

    # Verifica se um caminho foi fornecido
    if not caminho_arquivo: 
        print("Nenhum arquivo selecionado.")
        return
    
    if not fullscreen_ativado:  # Se for a primeira vez, ativa o modo fullscreen
        root.state('zoomed')
        fullscreen_ativado = True  # Atualiza a variável para não entrar mais aqui

    # Lendo os dados do arquivo Excel e definindo a linha 1 como cabeçalho
    dados_estudantis = pd.read_excel(caminho_arquivo, header=1)

    # Removendo espaços extras para todas as colunas de texto
    dados_estudantis = dados_estudantis.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Substitui os valores diferentes de "Sim" por "Não" na coluna "ensinoPublico?"
    dados_estudantis.loc[dados_estudantis['ensinoPublico?'] != 'Sim', 'ensinoPublico?'] = 'Não'

    # Divide os valores da coluna "anoSemestreIngresso" em ano e semestre. Os 4 primeiros digitos representam o ano, e o último o semestre
    dados_estudantis['ano'] = dados_estudantis['anoSemestreIngresso'].astype(str).str[:4]
    dados_estudantis['semestre'] = dados_estudantis['anoSemestreIngresso'].astype(str).str[-1]

    # Concatena o ano e o semestre formatados como uma data
    dados_estudantis['anoSemestreIngresso'] = dados_estudantis['semestre'] + '/' + dados_estudantis['ano']


    # Lista de estados
    estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
               "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
               "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

    caracteristicas = {
        'racaCor': racaCor_var.get(),
        'Sexo': sexo_var.get(),
        'nomeCurso': nomeCurso_var.get(),
        'ensinoPublico?': ensinoPublico_var.get()
    }

    # Filtrar o DataFrame com base nas características desejadas
    df_filtrado = dados_estudantis
    for coluna, valor in caracteristicas.items():
        if valor == 'Total':
            continue
        else:
            df_filtrado = df_filtrado[df_filtrado[coluna] == valor]

    # Contar o número de ocorrências para cada estado
    num_ocorrencias_por_estado = {}
    for estado in estados:
        df_estado = df_filtrado[df_filtrado['UFSG'] == estado]
        num_ocorrencias_por_estado[estado] = len(df_estado)

    # Criar DataFrame com os dados para a nova planilha
    df_nova_planilha = pd.DataFrame(num_ocorrencias_por_estado.items(), columns=['sigla', 'Total'])

    # Salvar DataFrame como uma nova planilha do Excel
    df_nova_planilha.to_excel('DadosCaracteristicasPorEstado.xlsx', index=False)

    # Carregar o mapa do Brasil
    mapa_Brasil = gpd.read_file('bcim_2016_21_11_2018.gpkg', layer='lim_unidade_federacao_a')

    # Carregar dados para o mapa
    dados = pd.read_excel('DadosCaracteristicasPorEstado.xlsx')

    # Mesclar mapa com dados
    misto = mapa_Brasil.merge(dados, on='sigla', how='left')

    # Criar nova figura e subplot
    fig = Figure(figsize=(16, 12))
    ax = fig.add_subplot(111)

    # Plotar heatmap
    misto.plot(column='Total',
               cmap='Reds',
               figsize=(16, 12),
               legend=True,
               edgecolor='black',
               ax=ax)

    # Adicionar rótulos com o número de pessoas em cada estado
    # for idx, row in misto.iterrows():
    #     ax.text(row.geometry.centroid.x, row.geometry.centroid.y, f"{row['sigla']}-{converter_para_texto(row['Total']) if row['Total'] < 10 else row['Total']}", fontsize=9, ha='center', color='blue')
    for idx, row in misto.iterrows():
        x = row.geometry.centroid.x
        y = row.geometry.centroid.y
        total = row['Total']
        # text = f"{row['sigla']} - {converter_para_texto(total) if total < 10 else total}"
        text = f"{total}"
        fontsize = 9
        color = 'blue'
        
        # Ajustar a posição do texto para não ultrapassar as bordas
        if row['sigla'] == "AL":
            ha = 'left'
            x += 0.1  # Ajuste para a direita
            y += -0.4
        elif row['sigla'] == "ES":
            ha = 'left'
            x += -0.1
            y += -0.1
        elif row['sigla'] == "RJ":
            ha = 'left'
            x += 0.2
            y += -0.1
        elif row['sigla'] == "RN":
            ha = 'left'
            x += -0.1  
            y += -0.1
        elif row['sigla'] == "PB":
            ha = 'left'
            x += 0.5  
            y += -0.1
        elif row['sigla'] == "SE":
            ha = 'left'
            x += -0.1  
            y += -0.1
        elif row['sigla'] == "DF":
            ha = 'center' 
            y += +0.4
        elif row['sigla'] == "PE":
            ha = 'left'
            x += 2.2
            y += -0.1 
        elif row['sigla'] == "PI":
            ha = 'left'
            x += 0.5  
        else:
            ha = 'center'

        ax.text(x, y, text, fontsize=fontsize, ha=ha, color=color)
    # Limpar frame_plot antes de plotar
    for widget in frame_plot.winfo_children():
        widget.destroy()

    # Atualizar plot no canvas
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


# Inicializar a interface gráfica
root = tk.Tk()
root.title("Selecione as Características")

# Tratamento de evento para fechar a janela
def on_close():
    root.quit()

root.protocol("WM_DELETE_WINDOW", on_close)

# Frame para dropdowns
frame_dropdowns = ttk.Frame(root)
frame_dropdowns.pack(side=tk.LEFT, padx=10, pady=10)

# Dropdowns
racaCor_var = tk.StringVar(frame_dropdowns)
sexo_var = tk.StringVar(frame_dropdowns)
nomeCurso_var = tk.StringVar(frame_dropdowns)
ensinoPublico_var = tk.StringVar(frame_dropdowns)

racaCor_label = ttk.Label(frame_dropdowns, text="Raça/Cor:")
racaCor_label.grid(row=0, column=0, padx=5, pady=5)
racaCor_dropdown = ttk.Combobox(frame_dropdowns, textvariable=racaCor_var, values=['Total', 
                                                                                   'branca', 
                                                                                   'parda', 
                                                                                   'preta', 
                                                                                   'amarela', 
                                                                                   'indígena', 
                                                                                   'não declarada'])
racaCor_dropdown.grid(row=0, column=1, padx=5, pady=5)
racaCor_dropdown.current(0)

sexo_label = ttk.Label(frame_dropdowns, text="Sexo:")
sexo_label.grid(row=1, column=0, padx=5, pady=5)
sexo_dropdown = ttk.Combobox(frame_dropdowns, textvariable=sexo_var, values=['Total', 
                                                                             'F', 
                                                                             'M'])
sexo_dropdown.grid(row=1, column=1, padx=5, pady=5)
sexo_dropdown.current(0)

nomeCurso_label = ttk.Label(frame_dropdowns, text="Nome do Curso:")
nomeCurso_label.grid(row=2, column=0, padx=5, pady=5)
nomeCurso_dropdown = ttk.Combobox(frame_dropdowns, textvariable=nomeCurso_var, values=['Total', 
                                                                                       'CIÊNCIA E TECNOLOGIA (Campus de Joinville]', 
                                                                                       'ENGENHARIA AEROESPACIAL [Campus Joinville]', 
                                                                                       'ENGENHARIA AUTOMOTIVA [Campus Joinville]', 
                                                                                       'ENGENHARIA CIVIL DE INFRAESTRUTURA [Campus Joinville]', 
                                                                                       'ENGENHARIA DE TRANSPORTES E LOGÍSTICA [Campus Joinville]', 
                                                                                       'ENGENHARIA FERROVIÁRIA E METROVIÁRIA [Campus Joinville]', 
                                                                                       'ENGENHARIA MECATRÔNICA [Campus Joinville]', 
                                                                                       'ENGENHARIA NAVAL [Campus Joinville]'])
nomeCurso_dropdown.grid(row=2, column=1, padx=5, pady=5)
nomeCurso_dropdown.current(0)

ensinoPublico_label = ttk.Label(frame_dropdowns, text="Ensino Público?")
ensinoPublico_label.grid(row=3, column=0, padx=5, pady=5)
ensinoPublico_dropdown = ttk.Combobox(frame_dropdowns, textvariable=ensinoPublico_var, values=['Total', 
                                                                                               'Sim', 
                                                                                               'Não'])
ensinoPublico_dropdown.grid(row=3, column=1, padx=5, pady=5)
ensinoPublico_dropdown.current(0)

caminho_arquivo = ""
fullscreen_ativado = False  # Variável para rastrear o estado do fullscreen

# Cria e posiciona o botão "Selecionar Arquivo"
selecionar_arquivo_button = ttk.Button(frame_dropdowns, text="Selecionar Arquivo", command=selecionar_arquivo)
selecionar_arquivo_button.grid(row=5, columnspan=2, padx=5, pady=5)

# Cria o botão "Aplicar Seleção" mas não o adiciona à interface ainda
aplicar_button = ttk.Button(frame_dropdowns, text="Aplicar Seleção", command=conta_Caracteristicas)

# Frame para plot
frame_plot = ttk.Frame(root)
frame_plot.pack(side=tk.RIGHT, padx=10, pady=10)

# Executar GUI
root.mainloop()
