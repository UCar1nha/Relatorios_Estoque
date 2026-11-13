import os
from src.cleaner import clean_data
from src.analyzer import identificar_baixo_estoque, calcular_reposicao

def main():
  print("--Iniciando Automacao de Relatorios de Estoque--")
  arquivo_entrada = "data/raw/estoque_atual.csv"

  if not os.path.exists(arquivo_entrada):
        print(f"[ERRO] Arquivo não encontrado em '{arquivo_entrada}'. Verifique se salvou na pasta correta.")
        return

  # Executa a limpeza
  df_processado = clean_data(arquivo_entrada)
  #print("\n[INFO] Amostra dos dados após a limpeza:")
  #print(df_processado[['produto', 'qtd_atual', 'qtd_minima']])

  # Identifica itens com baixo estoque
  df_criticos = identificar_baixo_estoque(df_processado)
  #print("\n[INFO] Itens com estoque abaixo do mínimo:")
  #print(df_criticos[['produto', 'qtd_atual', 'qtd_minima']])

  # Calcula a reposição necessária
  df_resultado = calcular_reposicao(df_criticos)
  print("\n[INFO] Resultado da análise de reposição:")
  print(df_resultado[['produto', 'qtd_atual', 'qtd_minima', 'caixas_a_comprar', 'custo_reposicao']])

if __name__ == "__main__":
  main()