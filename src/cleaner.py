from pathlib import Path

import pandas as pd


COLUNAS_OBRIGATORIAS = {
    "produto",
    "qtd_atual",
    "qtd_minima",
    "qtd_ideal",
    "valor",
    "fornecedor",
    "compra_minima",
}
COLUNAS_NUMERICAS = {
    "qtd_atual",
    "qtd_minima",
    "qtd_ideal",
    "valor",
    "compra_minima",
}


def _converter_coluna_numerica(valores, coluna):
    texto = valores.astype("string").str.strip()
    texto = texto.str.replace(r"R\$\s*", "", regex=True)
    texto = texto.str.replace(r"\s+", "", regex=True)

    formato_brasileiro = texto.str.contains(",", na=False)
    texto.loc[formato_brasileiro] = (
        texto.loc[formato_brasileiro]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    texto = texto.mask(texto.eq(""))

    convertido = pd.to_numeric(texto, errors="coerce")
    invalidos = valores.notna() & texto.notna() & convertido.isna()
    if invalidos.any():
        exemplos = valores.loc[invalidos].astype(str).head(3).tolist()
        raise ValueError(
            f"Valores numéricos inválidos na coluna '{coluna}': {exemplos}"
        )
    return convertido


def clean_data(arquivo):
    caminho = Path(arquivo)
    extensao = caminho.suffix.lower()
    if extensao == ".csv":
        df = pd.read_csv(caminho, encoding="utf-8-sig")
    elif extensao in {".xlsx", ".xls"}:
        df = pd.read_excel(caminho)
    else:
        raise ValueError(
            "Formato de arquivo não suportado. Use .csv, .xlsx ou .xls."
        )

    df.columns = [str(coluna).strip().lower() for coluna in df.columns]
    if df.columns.duplicated().any():
        duplicadas = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(f"Colunas duplicadas após padronização: {duplicadas}")

    faltantes = sorted(COLUNAS_OBRIGATORIAS - set(df.columns))
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

    linhas_originais = len(df)
    df = df.dropna(how="all").copy()
    linhas_removidas = linhas_originais - len(df)
    if linhas_removidas:
        print(f"[INFO] Linhas completamente vazias removidas: {linhas_removidas}")

    for coluna in ("produto", "fornecedor"):
        df[coluna] = df[coluna].astype("string").str.strip().str.title()
        df[coluna] = df[coluna].mask(df[coluna].eq(""))

    sem_produto = df["produto"].isna()
    if sem_produto.any():
        linhas = (df.index[sem_produto] + 2).tolist()[:5]
        raise ValueError(
            f"Produto não informado nas linhas do arquivo: {linhas}"
        )

    sem_fornecedor = df["fornecedor"].isna()
    if sem_fornecedor.any():
        linhas = (df.index[sem_fornecedor] + 2).tolist()[:5]
        raise ValueError(
            f"Fornecedor não informado nas linhas do arquivo: {linhas}"
        )

    for coluna in COLUNAS_NUMERICAS:
        df[coluna] = _converter_coluna_numerica(df[coluna], coluna)

    if df["qtd_atual"].isna().any():
        quantidade = int(df["qtd_atual"].isna().sum())
        print(
            f"[AVISO] {quantidade} valor(es) ausente(s) em 'qtd_atual' "
            "foram considerados como zero."
        )
        df["qtd_atual"] = df["qtd_atual"].fillna(0)

    numericas_obrigatorias = COLUNAS_NUMERICAS - {"qtd_atual"}
    for coluna in numericas_obrigatorias:
        if df[coluna].isna().any():
            linhas = (df.index[df[coluna].isna()] + 2).tolist()[:5]
            raise ValueError(
                f"Valor ausente na coluna obrigatória '{coluna}', "
                f"linhas do arquivo: {linhas}"
            )

    for coluna in COLUNAS_NUMERICAS:
        if (df[coluna] < 0).any():
            raise ValueError(f"A coluna '{coluna}' não pode conter valores negativos.")

    if (df["compra_minima"] <= 0).any():
        raise ValueError("'compra_minima' deve ser maior que zero.")
    if (df["qtd_ideal"] < df["qtd_minima"]).any():
        raise ValueError("'qtd_ideal' não pode ser menor que 'qtd_minima'.")

    linhas_antes = len(df)
    df = df.drop_duplicates(subset=["produto"], keep="first").copy()
    duplicadas = linhas_antes - len(df)
    if duplicadas:
        print(f"[AVISO] {duplicadas} linha(s) duplicada(s) removida(s).")

    print(f"[INFO] Dados processados: {len(df)} produto(s).")
    return df


if __name__ == "__main__":
    caminho = Path(__file__).resolve().parents[1] / "data" / "raw" / "estoque_atual.csv"
    try:
        df_limpo = clean_data(caminho)
        print(df_limpo.head())
    except (OSError, ValueError, pd.errors.ParserError) as erro:
        print(f"[ERRO] {erro}")
