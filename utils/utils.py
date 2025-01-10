def formata_preco(val):
    return f'R$ {val:.2f}'.replace('.', ',')


import json

def cart_total_qtd(carrinho):
    # Se o carrinho for uma string JSON, converte para dicionário
    if isinstance(carrinho, str):
        try:
            carrinho = json.loads(carrinho)  # Converte JSON string para dicionário
        except json.JSONDecodeError:
            return 0  # Retorna 0 se não conseguir converter

    # Se o carrinho não for um dicionário, retorna 0
    if not isinstance(carrinho, dict):
        return 0

    return sum([item['quantidade'] for item in carrinho.values()])


def cart_totals(carrinho):
    # Se o carrinho for uma string JSON, converte para dicionário
    if isinstance(carrinho, str):
        try:
            carrinho = json.loads(carrinho)  # Converte JSON string para dicionário
        except json.JSONDecodeError:
            return 0  # Retorna 0 se não conseguir converter

    # Se o carrinho não for um dicionário, retorna 0
    if not isinstance(carrinho, dict):
        return 0

    return sum(
        [
            item.get('preco_quantitativo_promocional', 0)
            if item.get('preco_quantitativo_promocional')
            else item.get('preco_quantitativo', 0)
            for item in carrinho.values()
        ]
    )

