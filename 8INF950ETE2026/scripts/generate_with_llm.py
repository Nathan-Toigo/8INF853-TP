"""CLI pour générer la rédaction d'un projet médical via un LLM externe (hors Cursor).

Ce script reproduit la méthodologie "vibe coding" (variante A, voir
case-study/variant-a-vibe-coding/README.md) de façon scriptée et indépendante de l'IDE :
il envoie un prompt à un LLM hébergé sur Azure OpenAI ou à un LLM local (ex. Ollama), puis
enregistre la réponse telle quelle, sans révision humaine.

Le prompt (docs/prompts/redaction-projet-medical.md) impose au LLM de baliser chaque
fichier de code avec un marqueur `===FILE: chemin/relatif===` suivi d'un bloc ```code```.
Si `--code-dir` est fourni, ces fichiers sont extraits et écrits tels quels sur disque
(voir extract_code_blocks.py) : le projet généré devient alors directement exécutable,
et pas seulement un document Markdown descriptif.

Exemples :

    python scripts/generate_with_llm.py --provider azure \\
        --project-name "Gestion de rendez-vous médicaux" \\
        --output case-study/variant-a-vibe-coding/GENERATED_DRAFT.md \\
        --code-dir case-study/variant-a-vibe-coding

    python scripts/generate_with_llm.py --provider local --model llama3.1 \\
        --project-name "Suivi de patients chroniques" \\
        --project-description "Suivi de la glycémie avec alertes en cas de valeur anormale" \\
        --output docs/drafts/suivi-chronique.md

Configuration (variables d'environnement — voir .env.example à la racine du projet) :

    Azure AI Foundry (endpoint unifié compatible OpenAI) :
        AZURE_OPENAI_ENDPOINT (ex. https://<projet>.services.ai.azure.com/openai/v1),
        AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT (nom du déploiement du modèle)

    LLM local (API compatible OpenAI, ex. Ollama sur http://localhost:11434/v1) :
        LOCAL_LLM_BASE_URL, LOCAL_LLM_MODEL, LOCAL_LLM_API_KEY (optionnels, valeurs
        par défaut adaptées à Ollama)

Prérequis : pip install -r scripts/requirements.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from extract_code_blocks import extract_files, write_files
from llm_client import call_llm

PROMPT_TEMPLATE_PATH = Path(__file__).parent.parent / "docs" / "prompts" / "redaction-projet-medical.md"


def build_prompt(project_name: str, project_description: str) -> str:
    template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.format(PROJECT_NAME=project_name, PROJECT_DESCRIPTION=project_description or "aucun")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Génère la rédaction d'un projet médical (projet X) via un LLM externe "
            "(Azure OpenAI ou LLM local), sans passer par Cursor."
        )
    )
    parser.add_argument("--provider", choices=["azure", "local"], required=True, help="Fournisseur du LLM à interroger")
    parser.add_argument("--project-name", required=True, help="Nom du projet médical (X) à rédiger, ex. 'Gestion de rendez-vous médicaux'")
    parser.add_argument("--project-description", default="", help="Contexte additionnel optionnel à injecter dans le prompt")
    parser.add_argument("--model", default=None, help="Nom du modèle local à utiliser (ignoré pour --provider azure, où le déploiement fait foi)")
    parser.add_argument("--output", required=True, help="Chemin du fichier où écrire la réponse générée (document Markdown complet)")
    parser.add_argument(
        "--code-dir",
        default=None,
        help=(
            "Si fourni, extrait les blocs de code balisés '===FILE: chemin===' de la réponse "
            "et les écrit comme de vrais fichiers sous ce dossier (projet directement exécutable)."
        ),
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    prompt = build_prompt(args.project_name, args.project_description)
    result = call_llm(args.provider, prompt, args.model)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    print(f"Réponse générée par le LLM ({args.provider}) enregistrée dans : {output_path}")

    if args.code_dir:
        files = extract_files(result)
        if not files:
            print(
                "Aucun bloc '===FILE: ...===' détecté dans la réponse : le LLM n'a pas "
                "respecté le format attendu, aucun fichier de code n'a été extrait."
            )
        else:
            written = write_files(files, Path(args.code_dir))
            print(f"{len(written)} fichier(s) de code écrit(s) sous {args.code_dir} :")
            for path in written:
                print(f"  - {path}")


if __name__ == "__main__":
    main()
