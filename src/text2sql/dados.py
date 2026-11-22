"""Criação do banco de dados de demonstração.

O banco combina dados públicos (as 27 unidades federativas do Brasil, com
região e capital) com dados SINTÉTICOS de uma loja fictícia, gerados com
semente fixa. Nenhum dado pessoal real é usado: os nomes de clientes são
combinações aleatórias de listas de nomes comuns.
"""

from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

# Dados públicos (IBGE): sigla, nome, região, capital.
ESTADOS = [
    ("AC", "Acre", "Norte", "Rio Branco"),
    ("AL", "Alagoas", "Nordeste", "Maceió"),
    ("AP", "Amapá", "Norte", "Macapá"),
    ("AM", "Amazonas", "Norte", "Manaus"),
    ("BA", "Bahia", "Nordeste", "Salvador"),
    ("CE", "Ceará", "Nordeste", "Fortaleza"),
    ("DF", "Distrito Federal", "Centro-Oeste", "Brasília"),
    ("ES", "Espírito Santo", "Sudeste", "Vitória"),
    ("GO", "Goiás", "Centro-Oeste", "Goiânia"),
    ("MA", "Maranhão", "Nordeste", "São Luís"),
    ("MT", "Mato Grosso", "Centro-Oeste", "Cuiabá"),
    ("MS", "Mato Grosso do Sul", "Centro-Oeste", "Campo Grande"),
    ("MG", "Minas Gerais", "Sudeste", "Belo Horizonte"),
    ("PA", "Pará", "Norte", "Belém"),
    ("PB", "Paraíba", "Nordeste", "João Pessoa"),
    ("PR", "Paraná", "Sul", "Curitiba"),
    ("PE", "Pernambuco", "Nordeste", "Recife"),
    ("PI", "Piauí", "Nordeste", "Teresina"),
    ("RJ", "Rio de Janeiro", "Sudeste", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte", "Nordeste", "Natal"),
    ("RS", "Rio Grande do Sul", "Sul", "Porto Alegre"),
    ("RO", "Rondônia", "Norte", "Porto Velho"),
    ("RR", "Roraima", "Norte", "Boa Vista"),
    ("SC", "Santa Catarina", "Sul", "Florianópolis"),
    ("SP", "São Paulo", "Sudeste", "São Paulo"),
    ("SE", "Sergipe", "Nordeste", "Aracaju"),
    ("TO", "Tocantins", "Norte", "Palmas"),
]

# Peso aproximado de clientes por UF (os maiores estados têm mais clientes).
_PESO_UF = {
    "SP": 22,
    "MG": 10,
    "RJ": 9,
    "BA": 7,
    "PR": 6,
    "RS": 6,
    "PE": 5,
    "CE": 5,
    "PA": 4,
    "SC": 4,
    "GO": 4,
    "DF": 3,
}

_NOMES = [
    "Ana",
    "Bruno",
    "Carla",
    "Diego",
    "Eduarda",
    "Felipe",
    "Gabriela",
    "Heitor",
    "Isabela",
    "João",
    "Larissa",
    "Marcos",
    "Natália",
    "Otávio",
    "Paula",
    "Rafael",
    "Sofia",
    "Thiago",
    "Vitória",
    "Yuri",
]
_SOBRENOMES = [
    "Almeida",
    "Barbosa",
    "Costa",
    "Dias",
    "Ferreira",
    "Gomes",
    "Lima",
    "Martins",
    "Nunes",
    "Oliveira",
    "Pereira",
    "Ribeiro",
    "Santos",
    "Silva",
    "Souza",
]

# categoria -> lista de (produto, preço base)
_CATALOGO = {
    "Eletrônicos": [
        ("Fone Bluetooth", 199.9),
        ("Carregador Turbo", 89.9),
        ("Caixa de Som", 349.0),
        ("Mouse sem Fio", 79.9),
        ("Teclado Mecânico", 429.0),
        ("Webcam HD", 259.0),
        ("Monitor 24", 899.0),
        ("Pendrive 64GB", 49.9),
    ],
    "Livros": [
        ("Introdução a Python", 119.0),
        ("Banco de Dados na Prática", 98.0),
        ("Algoritmos Explicados", 135.0),
        ("Romance Clássico", 45.9),
        ("Guia de Estatística", 89.0),
        ("História do Brasil", 72.5),
    ],
    "Casa": [
        ("Luminária de Mesa", 129.9),
        ("Jogo de Panelas", 389.0),
        ("Garrafa Térmica", 69.9),
        ("Organizador de Gaveta", 34.9),
        ("Cafeteira", 219.0),
        ("Toalha de Banho", 39.9),
        ("Liquidificador", 189.0),
    ],
    "Esportes": [
        ("Bola de Futebol", 99.9),
        ("Tapete de Yoga", 79.0),
        ("Garrafa Squeeze", 29.9),
        ("Corda de Pular", 24.9),
        ("Halteres 5kg", 149.0),
        ("Mochila Esportiva", 159.0),
    ],
    "Vestuário": [
        ("Camiseta Básica", 49.9),
        ("Moletom", 159.9),
        ("Tênis de Corrida", 399.0),
        ("Boné", 59.9),
        ("Meia (3 pares)", 29.9),
        ("Jaqueta Corta-vento", 249.0),
    ],
    "Papelaria": [
        ("Caderno Universitário", 32.9),
        ("Caneta Gel (kit)", 24.9),
        ("Agenda 2026", 54.9),
        ("Mochila Escolar", 189.9),
        ("Marca-texto (kit)", 19.9),
    ],
}

STATUS_PEDIDO = ["entregue", "enviado", "pago", "cancelado"]

ESQUEMA_SQL = """
CREATE TABLE estados (
    sigla TEXT PRIMARY KEY,          -- sigla da UF, ex.: 'SP'
    nome TEXT NOT NULL,              -- nome do estado
    regiao TEXT NOT NULL,            -- Norte, Nordeste, Centro-Oeste, Sudeste ou Sul
    capital TEXT NOT NULL
);
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,              -- nome fictício
    uf TEXT NOT NULL REFERENCES estados(sigla),
    data_cadastro TEXT NOT NULL      -- data ISO 'AAAA-MM-DD'
);
CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,         -- Eletrônicos, Livros, Casa, Esportes, Vestuário, Papelaria
    preco REAL NOT NULL              -- preço atual em reais
);
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    data_pedido TEXT NOT NULL,       -- data ISO 'AAAA-MM-DD'
    status TEXT NOT NULL             -- entregue, enviado, pago ou cancelado
);
CREATE TABLE itens_pedido (
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,    -- preço pago por unidade (pode ter desconto)
    PRIMARY KEY (pedido_id, produto_id)
);
"""

TABELAS = ["estados", "clientes", "produtos", "pedidos", "itens_pedido"]


def gerar_banco(caminho: Path | str, semente: int = 42, n_clientes: int = 500, n_pedidos: int = 3000) -> Path:
    """Cria (ou recria) o banco SQLite de demonstração de forma determinística."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if caminho.exists():
        caminho.unlink()

    rnd = random.Random(semente)
    conn = sqlite3.connect(caminho)
    try:
        conn.executescript(ESQUEMA_SQL)
        conn.executemany("INSERT INTO estados VALUES (?, ?, ?, ?)", ESTADOS)

        siglas = [e[0] for e in ESTADOS]
        pesos = [_PESO_UF.get(s, 1) for s in siglas]
        inicio = date(2024, 1, 1)
        clientes = []
        for i in range(1, n_clientes + 1):
            nome = f"{rnd.choice(_NOMES)} {rnd.choice(_SOBRENOMES)}"
            uf = rnd.choices(siglas, weights=pesos)[0]
            cadastro = inicio + timedelta(days=rnd.randint(0, 540))
            clientes.append((i, nome, uf, cadastro.isoformat()))
        conn.executemany("INSERT INTO clientes VALUES (?, ?, ?, ?)", clientes)

        produtos = []
        pid = 1
        for categoria, itens in _CATALOGO.items():
            for nome, preco in itens:
                produtos.append((pid, nome, categoria, preco))
                pid += 1
        conn.executemany("INSERT INTO produtos VALUES (?, ?, ?, ?)", produtos)

        pedidos, itens = [], []
        fim = date(2025, 12, 31)
        for pedido_id in range(1, n_pedidos + 1):
            cli = rnd.choice(clientes)
            cadastro = date.fromisoformat(cli[3])
            dias = (fim - cadastro).days
            data_pedido = cadastro + timedelta(days=rnd.randint(0, max(dias, 0)))
            status = rnd.choices(STATUS_PEDIDO, weights=[70, 10, 8, 12])[0]
            pedidos.append((pedido_id, cli[0], data_pedido.isoformat(), status))
            for prod in rnd.sample(produtos, rnd.randint(1, 4)):
                desconto = rnd.choice([1.0, 1.0, 1.0, 0.9, 0.85])
                itens.append((pedido_id, prod[0], rnd.randint(1, 3), round(prod[3] * desconto, 2)))
        conn.executemany("INSERT INTO pedidos VALUES (?, ?, ?, ?)", pedidos)
        conn.executemany("INSERT INTO itens_pedido VALUES (?, ?, ?, ?)", itens)
        conn.commit()
    finally:
        conn.close()
    return caminho


def esquema_para_prompt() -> str:
    """Esquema que é enviado ao modelo (DDL com comentários)."""
    return ESQUEMA_SQL.strip()


if __name__ == "__main__":
    import sys

    destino = sys.argv[1] if len(sys.argv) > 1 else "data/loja.db"
    print(f"Banco criado em {gerar_banco(destino)}")
