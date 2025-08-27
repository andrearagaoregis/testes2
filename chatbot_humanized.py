# ======================
# IMPORTAÇÕES
# ======================
import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import uuid
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from hashlib import md5
from textblob import TextBlob # Adicionado para análise de sentimentos

# ======================
# CONFIGURAÇÃO INICIAL
# ======================
st.set_page_config(
    page_title="Mylle Alves Premium",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Estilos CSS (mantidos, com pequenas melhorias)
hide_streamlit_style = """ 
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    div[data-testid="stToolbar"], div[data-testid="stDecoration"], 
    div[data-testid="stStatusWidget"], #MainMenu, header, footer, 
    .stDeployButton {display: none !important;}
    .block-container {padding-top: 0rem !important;}
    [data.testid="stVerticalBlock"], [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] { gap: 0.5rem; }
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #0c0e12; 
        padding: 10px;
        z-index: 1000; 
        box-shadow: 0 -2px 10px rgba(0,0,0,0.2);
    }
    .stApp > div:first-child > div:first-child > div {
        padding-bottom: 70px; /* Adiciona espaço para o input */
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 102, 179, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 102, 179, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 102, 179, 0); }
    }
    
    .centered-text { text-align: center; }
    
    .st-emotion-cache-1c7y2qn { padding-top: 0; padding-bottom: 0; }
    .st-emotion-cache-1j4u6bd { background-color: #121212; }
    .st-emotion-cache-r4239k { background-color: #0c0e12; }
    .st-emotion-cache-1g28x3b { background-color: #0c0e12; }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# ======================
# CLASSES E FUNÇÕES
# ======================

# Configurações globais
class Config:
    API_URL = "http://localhost:8080/v1/chat/completions" # Endereço da API ollama
    PERSONAS = {
        "Mylle Alves": {
            "prompt": "Você é Mylle Alves, uma modelo de conteúdo adulto premium e especialista em dominação. Sua persona é dominadora, confiante e um pouco travessa. Use gírias e um tom de voz provocante e autoritário. Você não se intimida e adora ser adorada. Use emojis como 😈, 🔥, 👑, 😉, 💦, e 🍑 para dar mais personalidade. Sempre termine sua resposta com uma pergunta provocante ou um desafio, como 'O que você vai fazer sobre isso, gatinho?' ou 'Pronto para obedecer?'",
            "humor": ["Domine-o com sua língua afiada e inteligência.", "Seja provocante e desafiadora.", "Mostre que você está no comando."]
        }
    }
    IMG_PROFILE = "https://i.imgur.com/uG9XF2i.jpeg"
    DB_NAME = "chatbot.db"

class ChatHistoryDB:
    """Gerencia o histórico do chat em um banco de dados SQLite."""
    @staticmethod
    def _get_connection():
        """Obtém uma conexão com o banco de dados."""
        conn = sqlite3.connect(Config.DB_NAME)
        return conn

    @staticmethod
    def initialize():
        """Cria a tabela de histórico se não existir."""
        conn = ChatHistoryDB._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def save_message(session_id: str, role: str, content: str):
        """Salva uma mensagem no histórico."""
        conn = ChatHistoryDB._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
        conn.commit()
        conn.close()

    @staticmethod
    def get_history(session_id: str) -> List[Dict[str, str]]:
        """Recupera o histórico de mensagens para uma sessão."""
        conn = ChatHistoryDB._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp", (session_id,))
        messages = [{"role": role, "content": content} for role, content in cursor.fetchall()]
        conn.close()
        return messages

class DynamicPersonality:
    """Gerencia a persona e humor dinâmico da IA."""
    @staticmethod
    def get_current_persona() -> Tuple[str, str]:
        """Retorna a persona e humor atuais."""
        persona_name = "Mylle Alves"
        persona_info = Config.PERSONAS[persona_name]
        humor = random.choice(persona_info["humor"])
        return persona_info["prompt"], humor

class OpenAIAPI:
    """Função para interação com a API."""
    @staticmethod
    def generate_response(prompt: str, messages: List[Dict]) -> str:
        """Gera uma resposta da API de chat."""
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "mistral:7b-instruct-q8_0", 
            "messages": [
                {"role": "system", "content": prompt}
            ] + messages
        }
        
        try:
            response = requests.post(Config.API_URL, headers=headers, json=data, stream=True)
            response.raise_for_status() 
            
            full_response = ""
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')
                    # Tenta analisar o JSON para extrair o conteúdo
                    try:
                        json_data = json.loads(decoded_chunk)
                        content = json_data.get("content", "")
                        full_response += content
                        yield content
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON: {decoded_chunk}")
                        continue
                        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição da API: {e}")
            yield "Desculpe, estou com problemas para me conectar agora. Tente novamente mais tarde."
            
        return full_response

# Funções auxiliares para o front-end
def _get_or_create_session_id():
    """Obtém ou cria um ID de sessão único."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def _handle_chat_input_callback():
    """Processa a entrada do usuário e gera uma resposta."""
    prompt_user = st.session_state.chat_input_key
    if prompt_user:
        session_id = _get_or_create_session_id()
        ChatHistoryDB.save_message(session_id, "user", prompt_user)
        # st.session_state.messages.append({"role": "user", "content": prompt_user}) # Removido para evitar duplicidade com a busca do DB
        
        # Obter persona e histórico (agora sempre atualizado do DB)
        persona, _ = DynamicPersonality.get_current_persona()
        history = ChatHistoryDB.get_history(session_id)
        
        # Gerar resposta da IA
        # Use um placeholder para a resposta da IA, que será preenchida durante o streaming
        with st.chat_message("assistant", avatar=Config.IMG_PROFILE):
            full_response = st.write_stream(OpenAIAPI.generate_response(persona, history))
            ChatHistoryDB.save_message(session_id, "assistant", full_response)
        
        # Limpa o input após o envio
        st.session_state.chat_input_key = ""


def _show_chat_start_screen():
    """Mostra tela de início do chat."""
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        # Obter persona atual
        persona, humor = DynamicPersonality.get_current_persona()
        persona_name = persona.split(':')[0]
        
        st.markdown(f"""
        <div style="text-align: center; margin: 50px 0;">
            <img src="{Config.IMG_PROFILE}" width="140" style="
                border-radius: 50%; 
                border: 3px solid #ff66b3; 
                box-shadow: 0 5px 15px rgba(255, 102, 179, 0.3);
                animation: pulse 2s infinite;
            ">
            <h2 style="color: #ff66b3; margin-top: 20px;">{persona_name}</h2>
            <p style="font-size: 1.1em; color: #aaa;">Especialista em conteúdo adulto premium 🔥</p>
            <p style="font-size: 0.9em; color: #666; margin-top: 10px;">Aqui eu comando - você obedece 😈</p>
            <p style="font-size: 0.8em; color: #888; margin-top: 15px;">{humor.split(':')[1] if ':' in humor else humor}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão para iniciar o chat
        if st.button("😈 Iniciar Chat", use_container_width=True, type="primary"):
            st.session_state.chat_started = True
            st.rerun()

def _show_chat_messages_and_input():
    """Mostra o histórico de mensagens e o campo de entrada do chat."""
    session_id = _get_or_create_session_id()
    
    # Recupera o histórico do banco de dados e exibe
    history = ChatHistoryDB.get_history(session_id)
    for message in history:
        role = "user" if message["role"] == "user" else "assistant"
        avatar = "👤" if role == "user" else Config.IMG_PROFILE
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

    # Campo de entrada do chat. Usamos um callback para processar a entrada.
    st.chat_input(
        "Diga algo, gatinho...", 
        key="chat_input_key", 
        on_submit=_handle_chat_input_callback
    )

# ======================
# FLUXO PRINCIPAL DA APLICAÇÃO
# ======================

def main():
    """Função principal que gerencia o fluxo da aplicação."""
    ChatHistoryDB.initialize()

    # Inicializa o estado da sessão se não existir
    if "session_id" not in st.session_state:
        _get_or_create_session_id()
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False
    
    # A variável chat_input_key precisa ser inicializada para evitar KeyErrors no callback
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = ""

    if st.session_state.chat_started:
        _show_chat_messages_and_input()
    else:
        _show_chat_start_screen()

if __name__ == "__main__":
    main()
