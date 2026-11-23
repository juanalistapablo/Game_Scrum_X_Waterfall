"""Catálogo de personagens técnicos e de negócio do jogo.

Cada personagem pode ser acionado em etapas específicas da árvore de decisão
para apresentar demandas, riscos técnicos e reagir às escolhas do jogador.
"""

from typing import Dict
from game.models import Character


CHARACTERS: Dict[str, Character] = {
    "backend_dev": Character(
        id="backend_dev",
        name="Lucas Mendes",
        role="Desenvolvedor Backend Sênior",
        specialty="APIs, microsserviços, banco de dados e integrações críticas",
        avatar_tag="[BACKEND]",
    ),
    "frontend_dev": Character(
        id="frontend_dev",
        name="Camila Rocha",
        role="Desenvolvedora Frontend Sênior",
        specialty="Interfaces web/mobile, dashboards em tempo real e responsividade",
        avatar_tag="[FRONTEND]",
    ),
    "architect": Character(
        id="architect",
        name="Rafael Costa",
        role="Arquiteto de Software / Tech Lead",
        specialty="Arquitetura de sistemas, segurança, escalabilidade e dívida técnica",
        avatar_tag="[ARQUITETO]",
    ),
    "qa_engineer": Character(
        id="qa_engineer",
        name="Beatriz Lima",
        role="Engenheira de QA & Testes",
        specialty="Testes automatizados, homologação, regressão e certificação",
        avatar_tag="[QA]",
    ),
    "devops": Character(
        id="devops",
        name="Diego Ferreira",
        role="Engenheiro DevOps / SRE",
        specialty="CI/CD, infraestrutura em nuvem, observabilidade e deploy seguro",
        avatar_tag="[DEVOPS]",
    ),
    "ux_designer": Character(
        id="ux_designer",
        name="Marina Alves",
        role="UX/UI Designer",
        specialty="Pesquisa com usuários, prototipação e jornada do cliente",
        avatar_tag="[UX/UI]",
    ),
    "product_owner": Character(
        id="product_owner",
        name="Helena Duarte",
        role="Product Owner / Analista de Requisitos & Compliance",
        specialty="Gestão de escopo, negociação com stakeholders e auditoria regulatória",
        avatar_tag="[PO/COMPLIANCE]",
    ),
}


def get_character(character_id: str) -> Character:
    """Retorna um personagem pelo ID ou levanta KeyError informativo."""
    if character_id not in CHARACTERS:
        raise KeyError(f"Personagem não encontrado: '{character_id}'")
    return CHARACTERS[character_id]
