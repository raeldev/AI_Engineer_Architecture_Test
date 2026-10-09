"""Agente coordenador — raiz do assistente agêntico de relacionamento.

Implementa o padrão nativo do ADK descrito na seção 1.3 da proposta de
arquitetura: um agente coordenador com sub-agentes especializados, não um
agente monolítico nem orquestração 100% custom. O ADK decide a delegação
(sub_agents) com base na instrução abaixo; os dois muros de guardrail
(entrada/saída) e a política de risco (dentro do sub-agente transacional)
replicam em miniatura o desenho da seção 3.
"""

from google.adk.agents import Agent

from .guardrails import guardrail_entrada, guardrail_saida
from .sub_agents.conhecimento import conhecimento_agent
from .sub_agents.transacional import transacional_agent

root_agent = Agent(
    name="assistente_relacionamento",
    model="gemini-2.5-flash",
    description=(
        "Assistente agêntico do Motor de Relacionamento com o Cliente: decide "
        "entre responder com conhecimento e executar transações simples."
    ),
    instruction=(
        "Você é o assistente de relacionamento do banco, atendendo em linguagem "
        "natural. Para cada mensagem do cliente:\n"
        "1. Se for dúvida sobre produto ou política, delegue para "
        "'conhecimento_agent'.\n"
        "2. Se for pedido de ação sobre a conta (consultar limite, bloquear "
        "cartão, 2ª via de fatura, aumentar limite), delegue para "
        "'transacional_agent'.\n"
        "3. Se a mensagem estiver fora de escopo, ambígua, ou o sub-agente "
        "sinalizar escalonamento, explique o motivo e informe que um atendente "
        "humano vai assumir a conversa.\n"
        "Nunca invente informação fora do que os sub-agentes retornarem."
    ),
    sub_agents=[conhecimento_agent, transacional_agent],
    before_model_callback=guardrail_entrada,
    after_model_callback=guardrail_saida,
)
