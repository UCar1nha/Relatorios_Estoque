import pandas as pd

def clean_data(arquivo):
    #1 Carrega o arquivo de dados
    if arquivo.endswith('.csv'):
        df = pd.read_csv(arquivo)
    elif arquivo.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(arquivo)
    else:
        raise ValueError("Formato de arquivo não suportado. Use .csv ou .xlsx/.xls")
    print(f"[INFO] Dados brutos carregados: {len(df)} linhas encontradas.")
    #2 Remove linhas completamente vazias
    df = df.dropna(how='all')
    linhas_removidas = len(df) - df.dropna(how='all').shape[0]
    if linhas_removidas > 0:
        print(f"[INFO] Linhas completamente vazias removidas: {linhas_removidas}")
    #3 Padroniza as colunas
    colunas_texto = ['produto', 'fornecedor']
    for col in colunas_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    #4 Converte para zero os valores nulos nas colunas numéricas
    colunas_numericas = ['qtd_atual', 'qtd_minima', 'qtd_ideal', 'valor', 'compra_minima']
    for col in colunas_numericas:
        if col in df.columns:
            if col == 'valor':
                valores = df[col].astype('string').str.replace('R$', '', regex=False).str.strip()
                formato_brasileiro = valores.str.contains(',', na=False)
                valores.loc[formato_brasileiro] = (
                    valores.loc[formato_brasileiro]
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                )
                df[col] = valores
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    #5 Remove duplicatas
    if 'produto' in df.columns:
        linhas_antes = len(df)
        df = df.drop_duplicates(subset=['produto'], keep='first')
        linhas_depois = len(df)
        if linhas_antes > linhas_depois:
            print(f"[AVISO] {linhas_antes - linhas_depois} linha(s) duplicada(s) removida(s).")

    print("[SUCESSO] Dados limpos e padronizados com sucesso!")
    return df

if __name__ == "__main__":
    # Teste rápido do cleaner isolado
    caminho = "data/raw/estoque_atual.csv" 
    try:
        df_limpo = clean_data(caminho)
        print(df_limpo.head())
    except Exception as e:
        print(f"[ERRO] {e}")