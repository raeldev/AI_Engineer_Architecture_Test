"""Sub-agente de conhecimento (RAG simplificado).

Em produção isso seria o Motor RAG/GraphRAG sobre Cloud Spanner (busca
vetorial + grafo, seção 1.4 da proposta). Aqui, pra manter o PoC elementar, a
"busca" é por substring sobre um JSON local — o contrato (função com
docstring, retorno com `status`) é o que importa pra trocar a implementação
depois sem mudar o agente.
"""

import json
from pathlib import Path

from google.adk.agents import LlmAgent

_KB_PATH = Path(__file__).resolve().parent.parent / "data" / "base_conhecimento.json"


def buscar_conhecimento(pergunta: str) -> dict:
    """Busca informação relevante na base de conhecimento do banco.

    Guardrail embutido: chunks marcados como "interno" nunca são retornados,
    mesmo que o termo de busca bata com o conteúdo — ver seção 3 da proposta
    (vazamento de dado sensível via RAG).

    Args:
        pergunta (str): pergunta ou termo de busca do cliente.

    Returns:
        dict: status ("success" ou "sem_resultado") e uma lista de trechos
            relevantes já filtrados por sensibilidade.
    """
    with open(_KB_PATH, encoding="utf-8") as f:
        base = json.load(f)

    termos = [t for t in pergunta.lower().split() if len(t) > 2]
    resultados = []
    for item in base:
        if item["categoria"] == "interno":
            continue  # guardrail: nunca expõe conteúdo interno
        alvo = f"{item['produto']} {item['conteudo']}".lower()
        if any(termo in alvo for termo in termos):
            resultados.append({"produto": item["produto"], "trecho": item["conteudo"]})

    if not resultados:
        return {"status": "sem_resultado", "trechos": []}
    return {"status": "success", "trechos": resultados[:3]}


conhecimento_agent = LlmAgent(
    name="conhecimento_agent",
    model="gemini-2.5-flash",
    description=(
        "Responde dúvidas sobre produtos e políticas do banco usando a base de "
        "conhecimento."
    ),
    instruction=(
        "Use sempre a ferramenta buscar_conhecimento antes de responder dúvidas "
        "sobre produtos ou políticas. Nunca cite o nome exato do documento-fonte, "
        "versão ou data — use referência genérica como 'em nossos termos de "
        "uso...' ou 'conforme a política vigente...' (seção 3 da proposta de "
        "arquitetura: citação precisa é vedada por segurança). Se a busca "
        "retornar 'sem_resultado', diga que vai confirmar a informação."
    ),
    tools=[buscar_conhecimento],
)
