from typing import Union
from openai import OpenAI
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens, ajuste para produção
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os cabeçalhos
)


openai_api_key = os.getenv("OPENAI_API_KEY")


# É uma boa prática inicializar o cliente OpenAI uma vez
# A chave de API é lida automaticamente da variável de ambiente OPENAI_API_KEY
client = OpenAI(api_key=openai_api_key)


def build_prompt(content: str, url: str) -> str:
    """
    Constrói o prompt para a análise do conteúdo e credibilidade pela LLM.
    """
    credibility_criteria = (
        "1. Expertise do Autor: O autor é um especialista reconhecido no assunto? A identidade é clara?\n"
        "2. Qualidade das Fontes: As fontes são citadas, confiáveis e verificáveis?\n"
        "3. Tom e Viés: A linguagem é objetiva ou tendenciosa/emocional? Distingue fato de opinião?\n"
        "4. Data de Publicação: A informação está atualizada e a data é visível?\n"
        "5. Verificação e Corroboração: A informação pode ser verificada por outras fontes independentes?\n"
        "6. Padrões de Desinformação: Utiliza falácias, manipulação emocional ou títulos enganosos?"
    )

    return (
        f"Analise o seguinte conteúdo extraído do site {url}. "
        "Primeiro, retorne um resumo com os seguintes campos: 'fonte' (a URL original), "
        "'titulo', 'principais_assuntos' (uma lista de strings), 'data_publicacao' (se houver, em formato AAAA-MM-DD), "
        "'autor' (se houver), e 'resumo' (um resumo objetivo de até 2 linhas).\n\n"
        "Depois, faça uma análise de credibilidade do conteúdo com base nos seguintes critérios:\n"
        f"{credibility_criteria}\n\n"
        "Com base na sua análise, adicione os seguintes campos ao JSON: "
        "'credibility_score' (um número inteiro de 1 a 10, onde 1 é 'nada confiável' e 10 é 'muito confiável') e "
        "'credibility_explanation' (uma explicação concisa de até 3 linhas justificando a pontuação com base nos critérios).\n\n"
        "O formato final deve ser um único dicionário JSON."
        f"\n\nConteúdo para análise:\n'''{content[:4000]}'''" # Limita o conteúdo para evitar exceder o limite de tokens
    )

@app.get("/checks/")
def check_url(url: str):
    """
    Endpoint que recebe uma URL, extrai seu conteúdo, analisa com a LLM da OpenAI
    e retorna uma análise estruturada em JSON.
    """
    try:
        # 1. Obter o conteúdo da URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        page = requests.get(url, headers=headers, timeout=10)
        page.raise_for_status()  # Lança uma exceção para respostas de erro (4xx ou 5xx)

        # 2. Extrair o texto limpo do HTML usando BeautifulSoup
        soup = BeautifulSoup(page.content, 'html.parser')
        # Remove tags de script e style que não contêm texto útil
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        text_content = soup.get_text(separator=' ', strip=True)

        if not text_content:
            return {"error": "Não foi possível extrair conteúdo textual da URL."}

        # 3. Construir o prompt
        prompt = build_prompt(text_content, url)

        # 4. Chamar a API da OpenAI com o Modo JSON
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Modelo atual que suporta JSON mode
            response_format={"type": "json_object"}, # Habilita o Modo JSON
            messages=[
                {"role": "system", "content": "Você é um assistente útil desenhado para retornar dados em formato JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        # 5. Converter a string JSON da resposta em um dicionário Python
        analysis_content = response.choices[0].message.content
        llm_analysis = json.loads(analysis_content)

        return {"llm_analysis": llm_analysis}

    except requests.exceptions.RequestException as e:
        return {"error": f"Erro ao acessar a URL: {e}"}
    except Exception as e:
        return {"error": f"Ocorreu um erro inesperado: {e}"}
