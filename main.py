from pathlib import Path

from src.analyzer import calcular_reposicao, identificar_baixo_estoque
from src.cleaner import clean_data
from src.generator import gerar_pdf


def main():
    print("-- Iniciando automação de relatórios de estoque --")
    raiz_projeto = Path(__file__).resolve().parent
    arquivo_entrada = raiz_projeto / "data" / "raw" / "estoque_atual.csv"
    caminho_pdf = raiz_projeto / "data" / "processed" / "relatorio_compras.pdf"

    if not arquivo_entrada.is_file():
        print(f"[ERRO] Arquivo não encontrado: {arquivo_entrada}")
        return 1

    df_processado = clean_data(arquivo_entrada)
    df_criticos = identificar_baixo_estoque(df_processado)
    df_resultado = calcular_reposicao(df_criticos)

    print(f"[INFO] Produtos que precisam de reposição: {len(df_resultado)}")
    if df_resultado.empty:
        print("[INFO] Nenhum produto está abaixo do estoque mínimo.")
    else:
        colunas_relatorio = [
            "produto",
            "qtd_atual",
            "qtd_minima",
            "qtd_ideal",
            "caixas_a_comprar",
            "custo_reposicao",
        ]
        print("\n[INFO] Detalhes da reposição:")
        print(df_resultado[colunas_relatorio].to_string(index=False))
        custo_total = df_resultado["custo_reposicao"].sum()
        print(f"[INFO] Custo total estimado para reposição: R$ {custo_total:.2f}")

    resposta = input("\nDeseja gerar o relatório em PDF? (S/N): ").strip().upper()
    if resposta in {"S", "SIM", "Y", "YES"}:
        gerar_pdf(df_resultado, caminho_pdf)
    else:
        print("[INFO] Geração de PDF cancelada pelo usuário.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
