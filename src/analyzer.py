import math

def identificar_baixo_estoque(df):
    # Verifica itens com estoque atual menor ou igual ao estoque mínimo
    df_criticos = df[df['qtd_atual'] <= df['qtd_minima']].copy()
    return df_criticos

def calcular_reposicao(df_criticos):
    # Calcula a quantidade necessária para repor o estoque até o nível ideal
    if df_criticos.empty:
        return df_criticos
    df_criticos['qtd_reposicao'] = df_criticos['qtd_minima'] - df_criticos['qtd_atual']
    # Calcula caixas a comprar com base na compra mínima.
    df_criticos['caixas_a_comprar'] = df_criticos.apply(
        lambda row: math.ceil(row['qtd_reposicao'] / row['compra_minima']) 
        if row['compra_minima'] > 0 else row['qtd_reposicao'], 
        axis=1
    )
    # Valor total de reposição.
    df_criticos['custo_reposicao'] = df_criticos['caixas_a_comprar'] * df_criticos['compra_minima'] * df_criticos['valor']
    return df_criticos

if __name__ == "__main__":
    # Teste rápido do analyzer simulando dados limpos
    from cleaner import clean_data
    try:
        df_limpo = clean_data("data/raw/estoque_atual.csv")
        df_criticos = identificar_baixo_estoque(df_limpo)
        df_resultado = calcular_reposicao(df_criticos)
        
        print("\n--- TESTE RÁPIDO: ITENS CRÍTICOS PARA REPOSIÇÃO ---")
        if not df_resultado.empty:
            print(df_resultado[['produto', 'qtd_atual', 'qtd_minima', 'caixas_a_comprar', 'custo_reposicao']])
        else:
            print("Nenhum item abaixo do estoque mínimo!")
    except Exception as e:
        print(f"[ERRO] {e}")