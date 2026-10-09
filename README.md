# AI_Engineer_Architecture_Test

Resposta ao desafio técnico de Arquiteto(a) de Soluções Especialista em IA (Banco Carrefour) - arquitetura de um assistente agêntico para o Motor de Relacionamento com o Cliente.

## O que tem aqui

- `proposta-arquitetura-assistente-agentico.md` / `.pdf` - documento principal da proposta, 6 páginas, cobre os 7 pontos pedidos no desafio (arquitetura, fluxo agêntico, guardrails, avaliação/observabilidade, FinOps, reusabilidade/CoE, roadmap).
- `apendices.md` / `.pdf` - material de apoio: diagramas extras, tabelas comparativas detalhadas, exemplos de produtos, roteiro pra sessão de defesa. Sem limite de página.
- `diagramas/` - os diagramas C4 (contexto, container, componentes), fluxo agêntico e roadmap, em PNG, com o `.dot` (Graphviz) de cada um junto.
- `poc-agente-adk/` - projeto inicial em Python com o Google ADK, implementando o núcleo do agente descrito na proposta (coordenador + sub-agentes, guardrails de entrada/saída, política de risco antes de cada ação). Não é o sistema completo, só o esqueleto principal. Tem README próprio com instruções de setup.
