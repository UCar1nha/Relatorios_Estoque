import os
from src.cleaner import clean_data

def main():
  print("Iniciando Automacao de Relatorios de Estoque")
  arquivo_entrada = "data/raw/estoque_atual.csv"

  if not os.path.exists(arquivo_entrada):
        print(f"[ERRO] Arquivo não encontrado em '{arquivo_entrada}'. Verifique se salvou na pasta correta.")
        return

  # Executa a limpeza
  df_processado = clean_data(arquivo_entrada)
  print("\n[INFO] Amostra dos dados após a limpeza:")
  print(df_processado[['produto', 'qtd_atual', 'qtd_minima']])

if __name__ == "__main__":
  main()