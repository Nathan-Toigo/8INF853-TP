"""Abstraction minimale pour appeler un LLM externe (hors Cursor).

Deux fournisseurs sont supportés, tous deux via le SDK `openai` (API compatible) :

- "azure" : un projet Azure AI Foundry, via son endpoint unifié compatible OpenAI
  (`https://<projet>.services.ai.azure.com/openai/v1`) et la Responses API
  (`client.responses.create`). Contrairement à l'ancienne intégration `AzureOpenAI`
  (endpoint `https://<ressource>.openai.azure.com/` + `api_version`), cet endpoint "v1"
  se pilote avec le client `OpenAI` standard, juste en changeant `base_url`.
- "local" : un LLM auto-hébergé exposant une API compatible OpenAI, ex. Ollama
  (http://localhost:11434/v1) ou LM Studio — utile pour garder les prompts/données
  entièrement on-prem, ce qui est pertinent pour le domaine de la santé (voir
  docs/etat-de-lart-outils-ia.md, section "Considérations spécifiques au domaine de la
  santé").

Nécessite openai>=1.66.0 (Responses API introduite dans cette version du SDK).
"""

from __future__ import annotations

import os

from openai import OpenAI


def call_azure_openai(prompt: str) -> str:
    """Envoie le prompt à un déploiement Azure AI Foundry et retourne le texte généré."""
    client = OpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )
    response = client.responses.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        input=prompt,
    )
    return response.output_text


def call_local_llm(prompt: str, model: str | None = None) -> str:
    """Envoie le prompt à un LLM local exposant une API compatible OpenAI."""
    client = OpenAI(
        base_url=os.environ.get("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.environ.get("LOCAL_LLM_API_KEY", "local"),  # valeur factice : la plupart des serveurs locaux n'exigent pas de clé
    )
    response = client.chat.completions.create(
        model=model or os.environ.get("LOCAL_LLM_MODEL", "llama3.1"),
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


def call_llm(provider: str, prompt: str, model: str | None = None) -> str:
    if provider == "azure":
        return call_azure_openai(prompt)
    if provider == "local":
        return call_local_llm(prompt, model)
    raise ValueError(f"Fournisseur LLM inconnu : {provider!r} (attendu : 'azure' ou 'local')")
