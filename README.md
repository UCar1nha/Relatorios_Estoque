# Relatorios_Estoque
Um script em Python que lê arquivos brutos (como CSV ou planilhas Excel desorganizadas de controle de estoque), processa os dados, calcula métricas de itens em falta ou giro e gera um relatório limpo em PDF.

## Como executar

1. Instale as dependências com `python -m pip install -r requirements.txt`.
2. Coloque o arquivo de estoque em `data/raw/estoque_atual.csv`.
3. Execute `python main.py` a partir de qualquer diretório.
4. Confirme se deseja gerar o PDF, salvo em `data/processed/relatorio_compras.pdf`.

O arquivo de entrada deve conter as colunas `produto`, `qtd_atual`,
`qtd_minima`, `qtd_ideal`, `valor`, `fornecedor` e `compra_minima`.
Valores monetários no formato brasileiro, como `R$ 1.234,56`, são aceitos.
Produtos identificados para reposição são calculados até `qtd_ideal`, respeitando
o múltiplo de `compra_minima`.
