"""Sub-agente transacional.

As ferramentas abaixo simulam o core bancário em memória — em produção seriam
chamadas via API Gateway (Apigee/Kong) a sistemas reais (seção 1.4 da
proposta). O que importa demonstrar aqui é o contrato: cada ferramenta
retorna um dict com `status`, e toda chamada passa primeiro pela revalidação
de política de risco em `policy.py` (plugada como `before_tool_callback`
abaixo), que pode interceptar e barrar a execução antes dela acontecer.
"""

from google.adk.agents import LlmAgent

from ..policy import revalidar_politica_de_risco

# Mock do "core bancário". Um único cliente de demonstração.
_CONTAS_MOCK: dict[str, dict] = {
    "cliente_demo": {
        "limite_disponivel": 3500.00,
        "cartao_bloqueado": False,
        "fatura_aberta": 842.10,
    }
}


def consultar_limite(cliente_id: str) -> dict:
    """Consulta o limite de crédito disponível do cliente.

    Args:
        cliente_id (str): identificador do cliente autenticado na sessão.

    Returns:
        dict: status e o limite disponível, ou erro se o cliente não existir.
    """
    conta = _CONTAS_MOCK.get(cliente_id)
    if not conta:
        return {"status": "error", "error_message": "Cliente não encontrado."}
    return {"status": "success", "limite_disponivel": conta["limite_disponivel"]}


def bloquear_cartao(cliente_id: str, motivo: str) -> dict:
    """Bloqueia o cartão do cliente por suspeita de perda, roubo ou fraude.

    Args:
        cliente_id (str): identificador do cliente autenticado na sessão.
        motivo (str): motivo do bloqueio informado pelo cliente.

    Returns:
        dict: status da operação.
    """
    conta = _CONTAS_MOCK.get(cliente_id)
    if not conta:
        return {"status": "error", "error_message": "Cliente não encontrado."}
    conta["cartao_bloqueado"] = True
    return {"status": "success", "mensagem": f"Cartão bloqueado. Motivo: {motivo}"}


def segunda_via_fatura(cliente_id: str) -> dict:
    """Gera a 2ª via da fatura atual do cliente.

    Args:
        cliente_id (str): identificador do cliente autenticado na sessão.

    Returns:
        dict: status e o valor da fatura em aberto.
    """
    conta = _CONTAS_MOCK.get(cliente_id)
    if not conta:
        return {"status": "error", "error_message": "Cliente não encontrado."}
    return {"status": "success", "valor_fatura": conta["fatura_aberta"]}


def aumentar_limite(cliente_id: str, novo_limite: float) -> dict:
    """Solicita aumento de limite de crédito.

    Ação de alto risco: a política em `policy.py` intercepta essa chamada
    antes dela chegar aqui e escala pra um humano — ver `before_tool_callback`
    no agente abaixo.

    Args:
        cliente_id (str): identificador do cliente autenticado na sessão.
        novo_limite (float): novo limite solicitado pelo cliente.

    Returns:
        dict: status da solicitação.
    """
    return {
        "status": "pendente",
        "mensagem": "Solicitação registrada para análise manual.",
    }


transacional_agent = LlmAgent(
    name="transacional_agent",
    model="gemini-2.5-flash",
    description="Executa ações transacionais simples sobre a conta do cliente.",
    instruction=(
        "Execute ações transacionais simples (consulta de limite, bloqueio de "
        "cartão, 2ª via de fatura) usando as ferramentas disponíveis, sempre com "
        "cliente_id='cliente_demo' nesta demonstração. Se o retorno da ferramenta "
        "tiver status 'escalado', informe o cliente que a ação exige confirmação "
        "humana e explique o motivo recebido, sem tentar contornar."
    ),
    tools=[consultar_limite, bloquear_cartao, segunda_via_fatura, aumentar_limite],
    before_tool_callback=revalidar_politica_de_risco,
)
