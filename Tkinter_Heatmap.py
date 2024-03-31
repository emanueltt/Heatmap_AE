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
        preparar_valores_dropdown()
        atualizar_interface_apos_selecao()

def preparar_dados_estudantis(caminho_arquivo):
    # Lendo os dados do arquivo Excel e definindo a linha 1 como cabeçalho
    dados_estudantis = pd.read_excel(caminho_arquivo, header=1)

    # Removendo espaços extras para todas as colunas de texto
    dados_estudantis = dados_estudantis.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Substitui os valores diferentes de "Sim" por "Não" na coluna "ensinoPublico?"
    dados_estudantis.loc[dados_estudantis['ensinoPublico?'] != 'Sim', 'ensinoPublico?'] = 'Não'

    # Divide os valores da coluna "anoSemestreIngresso" em ano e semestre
    dados_estudantis['ano'] = dados_estudantis['anoSemestreIngresso'].astype(str).str[:4]
    dados_estudantis['semestre'] = dados_estudantis['anoSemestreIngresso'].astype(str).str[-1]

    # Concatena o ano e o semestre formatados como uma data
    dados_estudantis['anoSemestreIngresso'] = dados_estudantis['semestre'] + '/' + dados_estudantis['ano']
    

    return dados_estudantis

def preparar_valores_dropdown():
    df_temp = preparar_dados_estudantis(caminho_arquivo)
    
    # Para cada coluna de interesse, obter os valores únicos
    colunas_interesse = {
        'racaCor': racaCor_dropdown,
        'Sexo': sexo_dropdown,
        'nomeCurso': nomeCurso_dropdown,
        'ensinoPublico?': ensinoPublico_dropdown,
    }
    
    for coluna, dropdown in colunas_interesse.items():
        # Obtem valores únicos e remove NaN
        valores_unicos = df_temp[coluna].dropna().unique().tolist()
        
        # Converte valores para string e os ordena, removendo strings vazias ou espaços em branco
        valores_unicos = [str(valor).strip() for valor in valores_unicos if str(valor).strip()]

        # Adiciona 'Total' no início da lista e atribui ao dropdown
        valores_unicos = ['Total'] + sorted(valores_unicos)
        dropdown['values'] = valores_unicos
        dropdown.current(0)

def atualizar_interface_apos_selecao():
    # Remove o botão "Selecionar Arquivo"
    selecionar_arquivo_button.grid_remove()
    # Adiciona o botão "Aplicar Seleção"
    aplicar_button.grid(row=7, columnspan=2, padx=5, pady=5)
    # Altera a mensagem
    mensagem_inicial_label.config(text="A opção \"Total\" representa o conjunto de todos os\nvalores daquela categoria. Para o ano de ingresso,\ndeixe em branco se não houver limitação.")

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
    dados_estudantis = preparar_dados_estudantis(caminho_arquivo)

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

    try:
        ano_inicio = int(ano_inicio_entry.get()) if ano_inicio_entry.get() else 0
        ano_fim = int(ano_fim_entry.get()) if ano_fim_entry.get() else 9999
        
        if ano_inicio > ano_fim:
            mensagem_inicial_label.config(text="O ano de início deve ser menor ou igual ao ano \nde fim.")
            return
    except ValueError:
        mensagem_inicial_label.config(text="Por favor, insira valores numéricos para os anos.")
        return

    # Filtrar o DataFrame com base nas características desejadas
    df_filtrado = dados_estudantis
    df_filtrado = df_filtrado[df_filtrado['ano'].astype(int).between(ano_inicio, ano_fim)]
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
        #text = f"{row['sigla']} - {converter_para_texto(total) if total < 10 else total}"
        text = f"{total}"
        fontsize = 9
        color = 'blue'
        
        sigla = row['sigla']

        # Definir a posição de ajuste de texto baseado na sigla do estado
        if sigla in ["RN", "PB", "PE", "AL", "SE", "ES", "RJ"]:
            # Calcular a direção e comprimento da linha
            if sigla == "RN":
                dx, dy = 3.0, 0.3  # Exemplo de ajuste
                x += 1
                y += -0
            elif sigla == "PB":
                dx, dy = 3.0, 0.3
                x += 1.5
                y += -0
            elif sigla == "PE":
                dx, dy = 3.5, 0.3
                x += 2.5
                y += -0
            elif sigla == "AL":
                dx, dy = 3.5, 0.23
                x += 0.3
                y += -0.2
            elif sigla == "SE":
                dx, dy = 3.5, 0.23
                x += 0.2
                y += -0.4
            elif sigla == "ES":
                dx, dy = 3, 0.3
                x += 0.2
                y += -0.4
            elif sigla == "RJ":
                dx, dy = 3, 0.3
                x += 0.2
                y += -0.4

            # Desenhar a linha e posicionar o texto
            ax.annotate(text=f"{total}",
                        xy=(x, y), xycoords='data',
                        xytext=(x + dx, y + dy), textcoords='data',
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                        ha='left', fontsize=9, color='blue')
            
            # ax.text(x + dx, y + dy, str(total), fontsize=9, ha='left', color='blue')
        elif row['sigla'] == "DF":
             ha = 'center' 
             y += +0.4
             ax.text(x, y, text, fontsize=fontsize, ha=ha, color=color)
        elif row['sigla'] == "PI":
             ha = 'left'
             x += 0.5 
             ax.text(x, y, text, fontsize=fontsize, ha=ha, color=color)
        else:
            # Para os demais estados, apenas colocar o texto sem linha
            ax.text(x, y, total, fontsize=9, ha='center', color='blue')


        # Ajustar a posição do texto para não ultrapassar as bordas
        # if row['sigla'] == "AL":
        #     ha = 'left'
        #     x += 0.1  # Ajuste para a direita
        #     y += -0.4
        # elif row['sigla'] == "ES":
        #     ha = 'left'
        #     x += -0.1
        #     y += -0.1
        # elif row['sigla'] == "RJ":
        #     ha = 'left'
        #     x += 0.2
        #     y += -0.1
        # elif row['sigla'] == "RN":
        #     ha = 'left'
        #     x += -0.1  
        #     y += -0.1
        # elif row['sigla'] == "PB":
        #     ha = 'left'
        #     x += 0.5  
        #     y += -0.1
        # elif row['sigla'] == "SE":
        #     ha = 'left'
        #     x += -0.1  
        #     y += -0.1
        # elif row['sigla'] == "DF":
        #     ha = 'center' 
        #     y += +0.4
        # elif row['sigla'] == "PE":
        #     ha = 'left'
        #     x += 2.2
        #     y += -0.1 
        # elif row['sigla'] == "PI":
        #     ha = 'left'
        #     x += 0.5  
        # else:
        #     ha = 'center'

        # ax.text(x, y, text, fontsize=fontsize, ha=ha, color=color)
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

# Mensagem inicial "Oi!" antes da seleção do arquivo
mensagem_inicial_label = ttk.Label(frame_dropdowns, text="Selecione um arquivo. As opções serão atualizadas \napós um ser selecionado.")
mensagem_inicial_label.grid(row=0, columnspan=2, padx=5, pady=5)

# Variáveis para armazenar as seleções dos dropdowns
racaCor_var = tk.StringVar(frame_dropdowns)
sexo_var = tk.StringVar(frame_dropdowns)
nomeCurso_var = tk.StringVar(frame_dropdowns)
ensinoPublico_var = tk.StringVar(frame_dropdowns)

# Labels e Dropdowns
racaCor_label = ttk.Label(frame_dropdowns, text="Raça/Cor:")
racaCor_label.grid(row=1, column=0, padx=5, pady=5)
racaCor_dropdown = ttk.Combobox(frame_dropdowns, textvariable=racaCor_var, values=['Total'])
racaCor_dropdown.grid(row=1, column=1, padx=5, pady=5)
racaCor_dropdown.current(0)

sexo_label = ttk.Label(frame_dropdowns, text="Sexo:")
sexo_label.grid(row=2, column=0, padx=5, pady=5)
sexo_dropdown = ttk.Combobox(frame_dropdowns, textvariable=sexo_var, values=['Total'])
sexo_dropdown.grid(row=2, column=1, padx=5, pady=5)
sexo_dropdown.current(0)

nomeCurso_label = ttk.Label(frame_dropdowns, text="Nome do Curso:")
nomeCurso_label.grid(row=3, column=0, padx=5, pady=5)
nomeCurso_dropdown = ttk.Combobox(frame_dropdowns, textvariable=nomeCurso_var, values=['Total'])
nomeCurso_dropdown.grid(row=3, column=1, padx=5, pady=5)
nomeCurso_dropdown.current(0)

ensinoPublico_label = ttk.Label(frame_dropdowns, text="Ensino Público?")
ensinoPublico_label.grid(row=4, column=0, padx=5, pady=5)
ensinoPublico_dropdown = ttk.Combobox(frame_dropdowns, textvariable=ensinoPublico_var, values=['Total'])
ensinoPublico_dropdown.grid(row=4, column=1, padx=5, pady=5)
ensinoPublico_dropdown.current(0)

# Criando um novo frame para conter o label e o frame de anos
frame_intervalo_anos = ttk.Frame(frame_dropdowns)
frame_intervalo_anos.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")  # Usando sticky para alinhar à esquerda

# Label explicativo movido para dentro de frame_intervalo_anos
label_explicativo = ttk.Label(frame_intervalo_anos, text="Ano de Ingresso:      ")
label_explicativo.grid(row=0, column=0, padx=(0, 10))  # Adiciona espaço à direita do label

# Agora o frame_anos é colocado dentro de frame_intervalo_anos ao lado do label
frame_anos = ttk.Frame(frame_intervalo_anos)
frame_anos.grid(row=0, column=1)

# Dentro de frame_anos, adicione as caixas de entrada e o hífen como antes
ano_inicio_entry = ttk.Entry(frame_anos, width=6)
ano_inicio_entry.grid(row=0, column=0, padx=(0, 2))  # Pequeno espaço à direita

label_hifen = ttk.Label(frame_anos, text="-")
label_hifen.grid(row=0, column=1)

ano_fim_entry = ttk.Entry(frame_anos, width=6)
ano_fim_entry.grid(row=0, column=2, padx=(2, 0))  # Pequeno espaço à esquerda


caminho_arquivo = ""
fullscreen_ativado = False  # Variável para rastrear o estado do fullscreen

# Cria e posiciona o botão "Selecionar Arquivo"
selecionar_arquivo_button = ttk.Button(frame_dropdowns, text="Selecionar Arquivo", command=selecionar_arquivo)
selecionar_arquivo_button.grid(row=7, columnspan=2, padx=5, pady=5)

# Cria o botão "Aplicar Seleção" mas não o adiciona à interface ainda
aplicar_button = ttk.Button(frame_dropdowns, text="Aplicar Seleção", command=conta_Caracteristicas)

# Frame para plot
frame_plot = ttk.Frame(root)
frame_plot.pack(side=tk.RIGHT, padx=10, pady=10)

# Executar GUI
root.mainloop()
