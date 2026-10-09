"""Política de risco transacional.

Espelha a decisão da seção 1.4/3 da proposta de arquitetura: a política de
risco é um dado versionado fora do prompt, avaliada por regra determinística
(nunca por um LLM) antes de qualquer execução transacional. Aqui ela roda como
um `before_tool_callback` do ADK, plugado no agente transacional — o mesmo
ponto de interceptação que, em produção, seria replicado de forma independente
no API Gateway (ver seção 1.4 e Apêndice E da proposta).
"""

from typing import Any

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

# Risco por tipo de transação. Em produção isso viria de uma tabela de
# configuração/feature flag, não de uma constante no código.
POLITICA_RISCO: dict[str, str] = {
    "consultar_limite": "baixo",
    "bloquear_cartao": "baixo",
    "segunda_via_fatura": "baixo",
    "aumentar_limite": "alto",
}


def revalidar_politica_de_risco(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any] | None:
    """Revalida o risco da transação antes de executar a ferramenta.

    Retornar um dict aqui faz o ADK pular a execução real da ferramenta e usar
    esse dict como resultado — é exatamente o "a chamada nunca chega ao core
    bancário, mesmo que o agente tenha decidido executar" descrito na seção
    1.4 da proposta.
    """
    risco = POLITICA_RISCO.get(tool.name, "alto")  # desconhecido = trata como alto risco
    if risco == "alto":
        return {
            "status": "escalado",
            "motivo": (
                f"A ação '{tool.name}' é de alto risco e exige confirmação humana "
                "ou autenticação forte — não é executada de forma autônoma."
            ),
        }
    return None  # risco baixo: segue para a execução normal da ferramenta
