import math


def _validar_colunas(df, colunas):
    faltantes = sorted(set(colunas) - set(df.columns))
    if faltantes:
        raise ValueError(f"Colunas necessárias para a análise ausentes: {', '.join(faltantes)}")


def identificar_baixo_estoque(df):
    _validar_colunas(df, ("qtd_atual", "qtd_minima"))
    return df.loc[df["qtd_atual"] <= df["qtd_minima"]].copy()


def calcular_reposicao(df_criticos):
    colunas = ("qtd_atual", "qtd_ideal", "compra_minima", "valor")
    _validar_colunas(df_criticos, colunas)

    resultado = df_criticos.copy()
    if resultado.empty:
        resultado["qtd_reposicao"] = []
        resultado["caixas_a_comprar"] = []
        resultado["custo_reposicao"] = []
        return resultado

    if (resultado["compra_minima"] <= 0).any():
        raise ValueError("'compra_minima' deve ser maior que zero.")

    resultado["qtd_reposicao"] = (
        resultado["qtd_ideal"] - resultado["qtd_atual"]
    ).clip(lower=0)
    resultado["caixas_a_comprar"] = (
        resultado["qtd_reposicao"] / resultado["compra_minima"]
    ).map(math.ceil)
    resultado["custo_reposicao"] = (
        resultado["caixas_a_comprar"]
        * resultado["compra_minima"]
        * resultado["valor"]
    )
    return resultado
