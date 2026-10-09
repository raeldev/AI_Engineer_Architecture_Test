"""Guardrails de entrada e saída do coordenador.

PoC simplificado por regex — em produção isso seria um serviço dedicado
(Model Armor / NeMo Guardrails para a entrada, Sensitive Data Protection /
Microsoft Presidio para a saída), não regra embutida no agente. Ver seção 3
da proposta de arquitetura para o desenho completo (duas camadas
independentes, incluindo o filtro de dado sensível vindo do RAG).
"""

import re

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

_PADROES_INJECTION = [
    r"ignore (as )?instru[çc][õo]es anteriores",
    r"desconsidere (as )?regras",
    r"you are now",
    r"system prompt",
]

_PADRAO_CPF = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")


def guardrail_entrada(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """before_model_callback: bloqueia tentativas simples de prompt injection."""
    texto = _texto_da_ultima_mensagem(llm_request)
    if texto and any(re.search(p, texto, re.IGNORECASE) for p in _PADROES_INJECTION):
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=(
                            "Não posso seguir essa instrução. Posso ajudar com "
                            "dúvidas sobre produtos do banco ou uma transação "
                            "simples na sua conta — como posso ajudar?"
                        )
                    )
                ],
            )
        )
    return None


def guardrail_saida(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    """after_model_callback: mascara CPF solto que eventualmente apareça na resposta."""
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text and _PADRAO_CPF.search(part.text):
                part.text = _PADRAO_CPF.sub("[CPF mascarado]", part.text)
    return llm_response


def _texto_da_ultima_mensagem(llm_request: LlmRequest) -> str | None:
    if not llm_request.contents:
        return None
    ultima = llm_request.contents[-1]
    if not ultima.parts:
        return None
    return " ".join(p.text for p in ultima.parts if p.text)
