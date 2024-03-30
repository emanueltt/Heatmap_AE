
# Aplicativo de Análise de Características Estudantis

Este aplicativo permite aos usuários selecionar um arquivo Excel com dados de estudantes, filtrar esses dados com base em características específicas como raça/cor, sexo, nome do curso, e ensino público, e, em seguida, visualizar a distribuição geográfica das informações por estado em um mapa do Brasil.

## Funcionalidades

- Seleção de um arquivo Excel com dados de estudantes.
- Filtragem de dados com base em critérios específicos.
- Visualização de um mapa do Brasil mostrando a distribuição geográfica dos dados filtrados.

## Pré-requisitos

Para executar este aplicativo, você precisará ter Python instalado em seu sistema, bem como as seguintes bibliotecas Python:

- pandas
- geopandas
- tkinter
- matplotlib

Você pode instalar todas as dependências necessárias executando:

```bash
pip install pandas geopandas matplotlib
```

**Importante:** Você precisará baixar manualmente o arquivo `bcim_2016_21_11_2018.gpkg` do IBGE para que o código funcione corretamente. Existem duas formas de obter o arquivo:

1. Download direto pelo link (o download começará automaticamente):
[https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/bcim/versao2016/geopackage/bcim_2016_21_11_2018.gpkg](https://geoftp.ibge.gov.br/cartas_e_mapas/bases_cartograficas_continuas/bcim/versao2016/geopackage/bcim_2016_21_11_2018.gpkg)

2. Caso prefira encontrar o arquivo manualmente, acesse [https://www.ibge.gov.br/geociencias/downloads-geociencias.html](https://www.ibge.gov.br/geociencias/downloads-geociencias.html), selecione "cartas_e_mapas" > "bases_cartograficas_continuas" > "bcim" > "versao2016" > "geopackage" > "bcim_2016_21_11_2018.gpkg".

Após o download, certifique-se de colocar o arquivo no mesmo diretório do script do aplicativo.

## Como Usar

1. Clone este repositório ou baixe o script do aplicativo.
2. Certifique-se de que todas as dependências estão instaladas e que o arquivo `bcim_2016_21_11_2018.gpkg` está no diretório correto.
3. Execute o script através do terminal ou comando de linha com `Tkinter_Heatmap.py`.
4. Uma interface gráfica será exibida. Clique em "Selecionar Arquivo" para escolher o arquivo Excel com os dados dos estudantes.
5. Após selecionar o arquivo, escolha os filtros desejados nas opções disponíveis.
6. Clique em "Aplicar Seleção" para filtrar os dados e visualizar o mapa com a distribuição geográfica.

