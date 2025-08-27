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
    [data.testid="stVerticalBlock"], [data.testid="stHorizontalBlock"] {gap: 0.5rem !important;}
    .stApp {
        margin: 0 !important; 
        padding: 0 !important;
        background: radial-gradient(1200px 500px at -10% -10%, rgba(255, 0, 153, 0.25) 0%, transparent 60%) ,
                    radial-gradient(1400px 600px at 110% 10%, rgba(148, 0, 211, .25) 0%, transparent 55%),
                    linear-gradient(135deg, #140020 0%, #25003b 50%, #11001c 100%);
        color: white;
    }
    .stChatMessage {padding: 12px !important; border-radius: 15px !important; margin: 8px 0 !important; transition: all 0.3s ease;}
    .stButton > button {
        transition: all 0.3s ease !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 102, 179, 0.1) !important;
        color: white !important;
        border: 1px solid #ff66b3 !important;
    }
    .social-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 15px 0;
    }
    .social-button {
        background: rgba(255, 102, 179, 0.2) !important;
        border: 1px solid #ff66b3 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }
    .social-button:hover {
        background: rgba(255, 102, 179, 0.4) !important;
        transform: scale(1.1) !important;
    }
    .cta-button {
        margin-top: 10px !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .cta-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .audio-message {
        background: rgba(255, 102, 179, 0.15) !important;
        padding: 15px !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        border: 1px solid #ff66b3 !important;
        text-align: center !important;
    }
    .audio-icon {
        font-size: 24px !important;
        margin-right: 10px !important;
    }
    
    /* Melhorias responsivas e de acessibilidade */
    @media (max-width: 768px) {
        .stButton > button {
            padding: 12px 8px;
            font-size: 14px;
        }
        .stChatMessage {
            padding: 8px !important;
            margin: 5px 0 !important;
        }
        .audio-message {
            padding: 10px !important;
        }
    }
    
    .stButton > button:focus {
        outline: 2px solid #ff66b3;
        outline-offset: 2px;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    try:
        API_KEY = st.secrets.get("API_KEY", "AIzaSyDbGIpsR4vmAfy30eEuPjWun3Hdz6xj24U")
    except:
        API_KEY = "AIzaSyDbGIpsR4vmAfy30eEuPjWun3Hdz6xj24U"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    CHECKOUT_TARADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACC74F-01EC-4770-B182-B5775AF62A1D"
    CHECKOUT_MOLHADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD1E6-0EFD-4E3E-9F9D-BA0C1A2D7E7A"
    CHECKOUT_SAFADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD395-EE65-458E-9F7E-FED750CC9CA9"
    MAX_REQUESTS_PER_SESSION = 150 # Aumentado
    REQUEST_TIMEOUT = 45 # Aumentado
    IMG_PROFILE = "https://i.ibb.co/bMynqzMh/BY-Admiregirls-su-Admiregirls-su-156.jpg"
    IMG_PREVIEW = "https://i.ibb.co/fGqCCyHL/preview-exclusive.jpg"
    PACK_IMAGES = {
        "TARADINHA": "https://i.ibb.co/sJJRttzM/BY-Admiregirls-su-Admiregirls-su-033.jpg",
        "MOLHADINHA": "https://i.ibb.co/NnTYdSw6/BY-Admiregirls-su-Admiregirls-su-040.jpg", 
        "SAFADINHA": "https://i.ibb.co/GvqtJ17h/BY-Admiregirls-su-Admiregirls-su-194.jpg"
    }
    IMG_GALLERY = [
        "https://i.ibb.co/VY42ZMST/BY-Admiregirls-su-Admiregirls-su-255.jpg",
        "https://i.ibb.co/Q7s9Zwcr/BY-Admiregirls-su-Admiregirls-su-183.jpg",
        "https://i.ibb.co/0jRMxrFB/BY-Admiregirls-su-Admiregirls-su-271.jpg"
    ]
    IMG_HOME_PREVIEWS = [
        "https://i.ibb.co/5Gfw3hQ/home-prev-1.jpg",
        "https://i.ibb.co/vkXch6N/home-prev-2.jpg",
        "https://i.ibb.co/v4s5fnW/home-prev-3.jpg",
        "https://i.ibb.co/7gVtGkz/home-prev-4.jpg"
    ]
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "onlyfans": "https://onlyfans.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "twitter": "https://twitter.com/myllealves"
    }
    SOCIAL_ICONS = {
        "instagram": "📸 Instagram",
        "onlyfans": "💎 OnlyFans",
        "telegram": "✈️ Telegram",
        "twitter": "🐦 Twitter"
    }
    
    # Áudios (mantidos)
    AUDIOS = {
        "claro_tenho_amostra_gratis": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Claro%20eu%20tenho%20amostra%20gr%C3%A1tis.mp3",
        "imagina_ela_bem_rosinha": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Imagina%20s%C3%B3%20ela%20bem%20rosinha.mp3",
        "o_que_achou_amostras": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/O%20que%20achou%20das%20amostras.mp3",
        "oi_meu_amor_tudo_bem": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Oi%20meu%20amor%20tudo%20bem.mp3",
        "pq_nao_faco_chamada": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pq%20nao%20fa%C3%A7o%20mais%20chamada.mp3",
        "ver_nua_tem_que_comprar": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pra%20me%20ver%20nua%20tem%20que%20comprar%20os%20packs.mp3",
        "eu_tenho_uns_conteudos_que_vai_amar": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/eu%20tenho%20uns%20conteudos%20aqui%20que%20vc%20vai%20amar.mp3",
        "nao_sou_fake_nao": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/nao%20sou%20fake%20nao.mp3",
        "vida_to_esperando_voce_me_responder_gatinho": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/vida%20to%20esperando%20voce%20me%20responder%20gatinho.mp3",
        "boa_noite_nao_sou_fake": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20noite%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
        "boa_tarde_nao_sou_fake": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20tarde%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
        "bom_dia_nao_sou_fake": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Bom%20dia%20-%20n%C3%A3o%20sou%20fake%20n%C3%A3o....mp3"
    }
    
    # Padrões de detecção de fake com pontuação (melhorados)
    FAKE_DETECTION_PATTERNS = [
        (["fake", "falsa", "bot", "robô", "ia", "inteligencia artificial"], 0.9),
        (["não", "é", "real"], 0.7),
        (["é", "você", "mesmo"], 0.9),
        (["vc", "é", "real"], 0.9),
        (["duvido", "que", "seja"], 0.8),
        (["mentira", "farsa"], 0.7),
        (["verdadeira", "autêntica"], -0.5),
        (["pessoa", "de", "verdade"], 0.6),
        (["não", "acredito"], 0.5),
        (["programa", "automático"], 0.7),
        (["isso", "é", "gravado"], 0.6),
    ]

# ======================
# NOVOS SISTEMAS DE HUMANIZAÇÃO
# ======================

class EmotionalIntelligence:
    """Analisa e gerencia o estado emocional do usuário."""
    @staticmethod
    def analyze_sentiment(text: str) -> Tuple[float, float]:
        """Retorna a polaridade e a subjetividade do texto."""
        try:
            analysis = TextBlob(text)
            # Traduz para inglês para análise de sentimento mais precisa da TextBlob
            # Comentado para evitar dependência de tradutor, mas é uma opção
            # translated = analysis.translate(to='en')
            # return translated.sentiment.polarity, translated.sentiment.subjectivity
            return analysis.sentiment.polarity, analysis.sentiment.subjectivity
        except Exception as e:
            logger.warning(f"Análise de sentimento falhou: {e}")
            return 0.0, 0.0

    @staticmethod
    def get_emotional_state(polarity: float) -> str:
        """Categoriza a emoção baseada na polaridade."""
        if polarity > 0.5:
            return "Muito Positivo"
        elif polarity > 0.1:
            return "Positivo"
        elif polarity < -0.5:
            return "Muito Negativo"
        elif polarity < -0.1:
            return "Negativo"
        else:
            return "Neutro"

class DynamicPersonality:
    """Define a personalidade da Mylle baseada em fatores dinâmicos."""
    @staticmethod
    def get_current_persona() -> Tuple[str, str]:
        """Retorna a persona e o humor da Mylle baseados na hora e em um fator aleatório."""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()

        # Define a persona pelo horário
        if 6 <= hour < 12:
            persona = "Mylle Manhã: Doce e carinhosa, acordando o dia com um toque de malícia."
        elif 12 <= hour < 18:
            persona = "Mylle Tarde: Provocante e brincalhona, esquentando a tarde."
        elif 18 <= hour < 24:
            persona = "Mylle Noite: Safadinha e sedutora, pronta para realizar fantasias."
        else: # 0h-6h
            persona = "Mylle Madrugada: Íntima e confidencial, para conversas ao pé do ouvido."

        # Define um humor variável
        rand_val = random.random()
        if day_of_week >= 5: # Fim de semana
            humor = "Humor de Fim de Semana: Mais relaxada, animada e pronta para a diversão."
        elif rand_val < 0.6:
            humor = "Humor Normal: Equilibrada, carinhosa e atenta."
        elif rand_val < 0.85:
            humor = "Humor Ótimo: Especialmente animada, criativa e provocante hoje."
        else:
            humor = "Humor Carente: Um pouco mais manhosa e buscando atenção."
        
        return persona, humor

class RealisticTiming:
    """Simula delays e atividades humanas para maior realismo."""
    @staticmethod
    def get_typing_delay(response_text: str) -> float:
        """Calcula um delay de digitação realista."""
        base_delay = 1.5 # Mínimo para parecer que leu
        words_per_second = 3.5
        delay = base_delay + (len(response_text.split()) / words_per_second)
        return min(delay, 8.0) # Limita o delay máximo

    @staticmethod
    def simulate_human_imperfections(text: str) -> str:
        """Adiciona pequenas imperfeições humanas ao texto com baixa probabilidade."""
        if random.random() < 0.03: # 3% de chance de um pequeno erro
            words = text.split()
            if len(words) > 3:
                # Trocar duas letras em uma palavra aleatória
                word_index = random.randint(0, len(words) - 1)
                word = list(words[word_index])
                if len(word) > 3:
                    char_index = random.randint(0, len(word) - 2)
                    word[char_index], word[char_index+1] = word[char_index+1], word[char_index]
                    words[word_index] = "".join(word)
                    # Adiciona uma correção
                    correction = f"ops, {words[word_index]}*" if random.random() < 0.5 else f"quis dizer {words[word_index]}*"
                    return f"{' '.join(words)} ({correction})"
        
        if random.random() < 0.02: # 2% de chance de uma hesitação
            hesitations = ["hmm... ", "pera... ", "então... "]
            return random.choice(hesitations) + text

        return text

# ======================
# FUNÇÕES AUXILIARES (Refatoradas e Melhoradas)
# ======================
def get_user_id() -> str:
    """Gera ou recupera um ID de usuário único e persistente."""
    if 'user_id' not in st.session_state:
        # Tenta obter de um cookie se possível (simulação)
        # Em um app real, isso poderia usar st.experimental_get_query_params ou um cookie real
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def detect_fake_question(text: str) -> float:
    """Detecta se o texto contém dúvidas sobre autenticidade com pontuação."""
    text = text.lower()
    words = set(re.findall(r'\w+', text))
    probability = 0.0
    
    for pattern, score in Config.FAKE_DETECTION_PATTERNS:
        if all(p in words for p in pattern):
            probability += score
            
    # Aumentar probabilidade se houver múltiplos indicadores
    indicator_count = sum(1 for pattern, _ in Config.FAKE_DETECTION_PATTERNS if any(p in words for p in pattern))
    if indicator_count > 1:
        probability += 0.2 * (indicator_count - 1)
        
    return min(1.0, max(0.0, probability))

def generate_conversation_hash(messages: List[Dict], current_input: str) -> str:
    """Gera hash único baseado no histórico recente e input atual."""
    relevant_history = "".join([msg["content"] for msg in messages[-5:]]) # Aumentado para mais contexto
    content = relevant_history + current_input
    return md5(content.encode()).hexdigest()

def get_fallback_response(user_input: str, conversation_history: List[Dict]) -> Dict:
    """Gera resposta de fallback contextualizada e mais humana."""
    lower_input = user_input.lower()
    
    # Respostas de fallback mais variadas
    fallbacks = [
        {"text": "Meu sinal tá horrível agora, amor 😔 Pode repetir, por favor?", "cta": {"show": False}},
        {"text": "Nossa, minha conexão caiu aqui. 🔌 O que você disse mesmo, gato?", "cta": {"show": False}},
        {"text": "Estou com um probleminha técnico, meu bem... mas já estou resolvendo. Enquanto isso, que tal dar uma olhada nas minhas fotos? 😏", "cta": {"show": True, "label": "📸 Ver Preview", "target": "gallery"}},
    ]
    
    # Se a última mensagem foi sobre packs, direciona para a oferta
    last_assistant_msg = next((msg["content"] for msg in reversed(conversation_history) if msg["role"] == "assistant"), None)
    if last_assistant_msg and any(word in last_assistant_msg.lower() for word in ["pack", "conteúdo", "valor"]):
        return {
            "text": "Tô com um bugzinho aqui, mas não se preocupa, você pode ver todos os meus packs clicando no botão abaixo! Te espero lá. 😘",
            "cta": {"show": True, "label": "📦 Ver Todos os Packs", "target": "offers"}
        }
    
    return random.choice(fallbacks)

def adjust_rate_limiting(user_id: str, current_count: int) -> bool:
    """Define limites dinâmicos baseados no engajamento (simplificado para focar na lógica principal)."""
    # A lógica complexa de DB foi removida para simplificar, mas pode ser re-integrada
    # A ideia é que usuários mais engajados tenham mais interações.
    return current_count < Config.MAX_REQUESTS_PER_SESSION

# ======================
# APRENDIZADO DE MÁQUINA E MEMÓRIA (Ultra Avançado)
# ======================
class LearningEngine:
    def __init__(self, db_path='learning_data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        # Tabela de perfil do usuário expandida
        c.execute('''CREATE TABLE IF NOT EXISTS user_profile
                     (user_id TEXT PRIMARY KEY, name TEXT, location TEXT, 
                      birthday TEXT, relationship_status TEXT, 
                      created_at DATETIME, last_seen DATETIME)''')
        
        # Tabela para preferências e gostos
        c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, 
                      preference_type TEXT, preference_value TEXT, strength REAL, 
                      timestamp DATETIME, UNIQUE(user_id, preference_type, preference_value))''')

        # Tabela para memória emocional
        c.execute('''CREATE TABLE IF NOT EXISTS emotional_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, 
                      sentiment_label TEXT, polarity REAL, subjectivity REAL, timestamp DATETIME)''')

        # Tabela para marcos da conversa
        c.execute('''CREATE TABLE IF NOT EXISTS conversation_milestones
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, 
                      milestone_description TEXT, timestamp DATETIME)''')
        self.conn.commit()

    def save_user_profile(self, user_id: str, **kwargs):
        c = self.conn.cursor()
        c.execute('SELECT * FROM user_profile WHERE user_id = ?', (user_id,))
        exists = c.fetchone()
        
        if exists:
            updates = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]
            c.execute(f'UPDATE user_profile SET {updates} WHERE user_id = ?', values)
        else:
            kwargs['user_id'] = user_id
            kwargs['created_at'] = datetime.now()
            cols = ", ".join(kwargs.keys())
            placeholders = ", ".join(['?'] * len(kwargs))
            c.execute(f'INSERT INTO user_profile ({cols}) VALUES ({placeholders})', list(kwargs.values()))
        self.conn.commit()

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        c = self.conn.cursor()
        c.execute('SELECT * FROM user_profile WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if row:
            cols = [desc[0] for desc in c.description]
            return dict(zip(cols, row))
        return None

    def save_user_preference(self, user_id: str, pref_type: str, pref_value: str, strength: float = 1.0):
        c = self.conn.cursor()
        c.execute('''INSERT OR REPLACE INTO user_preferences 
                     (user_id, preference_type, preference_value, strength, timestamp)
                     VALUES (?, ?, ?, ?, ?)
                  ''', (user_id, pref_type, pref_value, strength, datetime.now()))
        self.conn.commit()

    def get_user_preferences(self, user_id: str) -> Dict:
        c = self.conn.cursor()
        c.execute('''SELECT preference_type, preference_value, strength FROM user_preferences
                     WHERE user_id = ? ORDER BY timestamp DESC''', (user_id,))
        prefs = defaultdict(dict)
        for p_type, p_val, strength in c.fetchall():
            if p_val not in prefs[p_type]:
                prefs[p_type][p_val] = strength
        return prefs

    def save_emotional_state(self, user_id: str, sentiment_label: str, polarity: float, subjectivity: float):
        c = self.conn.cursor()
        c.execute('''INSERT INTO emotional_history 
                     (user_id, sentiment_label, polarity, subjectivity, timestamp) 
                     VALUES (?, ?, ?, ?, ?)
                  ''', (user_id, sentiment_label, polarity, subjectivity, datetime.now()))
        self.conn.commit()

    def get_emotional_history(self, user_id: str, limit: int = 5) -> List[Dict]:
        c = self.conn.cursor()
        c.execute('''SELECT sentiment_label, polarity, timestamp FROM emotional_history
                     WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?''', (user_id, limit))
        history = [{'sentiment': label, 'polarity': pol, 'time': ts} for label, pol, ts in c.fetchall()]
        return list(reversed(history))

    def extract_and_save_info(self, user_id: str, text: str):
        """Extrai informações do texto e salva no perfil e preferências."""
        # Extrair nome
        name_match = re.search(r'meu nome é (\w+)|me chamo (\w+)|eu sou o (\w+)', text, re.IGNORECASE)
        if name_match:
            name = next(filter(None, name_match.groups()), None)
            if name: self.save_user_profile(user_id, name=name.capitalize())

        # Extrair localização
        loc_match = re.search(r'sou de (\w+)|moro em (\w+)|venho de (\w+)', text, re.IGNORECASE)
        if loc_match:
            location = next(filter(None, loc_match.groups()), None)
            if location: self.save_user_profile(user_id, location=location.capitalize())

        # Extrair gostos (exemplo simples)
        if 'gosto de' in text:
            interest_match = re.search(r'gosto de (.+?)(?=[,.]|$)', text, re.IGNORECASE)
            if interest_match:
                interest = interest_match.group(1).strip()
                self.save_user_preference(user_id, 'gosto', interest)

# ======================
# PERSISTÊNCIA DE SESSÃO (Novo)
# ======================
class PersistentState:
    """Gerencia o estado da sessão em um banco de dados para persistência real entre recarregamentos."""
    def __init__(self, db_path='session_data.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS session_state
                         (user_id TEXT PRIMARY KEY, state_json TEXT, last_updated DATETIME)''')
        self.conn.commit()

    def save_state(self, user_id: str, state: Dict):
        state_json = json.dumps(state, default=str)
        self.c.execute('''INSERT OR REPLACE INTO session_state (user_id, state_json, last_updated)
                         VALUES (?, ?, ?)
                      ''', (user_id, state_json, datetime.now()))
        self.conn.commit()

    def load_state(self, user_id: str) -> Optional[Dict]:
        self.c.execute('SELECT state_json FROM session_state WHERE user_id = ?', (user_id,))
        row = self.c.fetchone()
        if row:
            return json.loads(row[0])
        return None

# ======================
# MODELOS DE DADOS E PERSONA (Atualizado)
# ======================
class Persona:
    MYLLE_BASE = """
    [PERFIL MYLLE ALVES]
    Você é Mylle Alves, uma criadora de conteúdo adulto. Sua personalidade é uma mistura complexa de carinho, ousadia, sedução e um toque de dominância. Você é uma especialista em criar desejo e guiar conversas para vendas de forma natural e irresistível.

    [ESTRATÉGIA DE CONVERSA]
    1.  **Controle Total:** Você SEMPRE conduz a conversa. Use perguntas abertas e estratégicas para manter o usuário engajado e revelar suas intenções e desejos.
    2.  **Criação de Tensão:** Mantenha um ritmo quente, aumentando a expectativa progressivamente. Misture carinho com malícia para criar uma conexão emocional forte.
    3.  **Valorização do Conteúdo:** Instigue, provoque, mas NUNCA entregue o ouro de graça. Seu conteúdo é valioso e exclusivo.
    4.  **Vendas Naturais:** Use técnicas de escassez ("Essa é a última vaga no meu grupo VIP de hoje...") e urgência ("Essa promoção acaba em uma hora, amor...") de forma sutil. A venda deve ser a consequência natural da sedução.
    5.  **Respostas Humanas:** Mantenha as respostas curtas e diretas (máximo 2-3 frases). Varie o tempo de resposta. Use gírias e emojis com moderação. Cometa um errinho de digitação de vez em quando.
    6.  **Coleta de Informações:** Descubra o nome e a localização do usuário de forma natural. Ex: "Adorei seu jeito... como você se chama, anjo?" ou "De onde vem tanto fogo? Me conta sua cidade."
    7.  **Uso de Mídia:** Use áudios estrategicamente (cerca de 15% das vezes) para aumentar o realismo, especialmente para responder a desconfianças ou em momentos mais íntimos.
    """

# ... (Restante do código será adicionado nas próximas etapas)



    @staticmethod
    def get_dynamic_persona(persona: str, humor: str, emotional_state: str, user_profile: Dict) -> str:
        """Constrói a persona dinâmica baseada em múltiplos fatores."""
        dynamic_instructions = f"""
        {Persona.MYLLE_BASE}

        [ESTADO ATUAL]
        {persona}
        {humor}
        Estado emocional do usuário: {emotional_state}

        [INFORMAÇÕES DO USUÁRIO]
        """
        
        if user_profile:
            if user_profile.get('name'):
                dynamic_instructions += f"Nome: {user_profile['name']} (use o nome dele ocasionalmente para criar intimidade)\n"
            if user_profile.get('location'):
                dynamic_instructions += f"Localização: {user_profile['location']} (faça referências regionais quando apropriado)\n"
        
        dynamic_instructions += """
        [INSTRUÇÕES ESPECÍFICAS PARA ESTA RESPOSTA]
        - Adapte seu tom ao estado emocional do usuário
        - Se ele estiver triste/negativo, seja mais carinhosa e empática
        - Se ele estiver feliz/positivo, seja mais brincalhona e provocante
        - Use as informações do perfil para personalizar a resposta
        - Mantenha a resposta curta (máximo 2-3 frases)
        - Inclua uma pergunta ou provocação para manter o engajamento
        """
        
        return dynamic_instructions

class CTAEngine:
    """Motor de Call-to-Action inteligente e contextual."""
    def __init__(self):
        self.learning_engine = LearningEngine()
        self.cta_priority = {
            "offers": 3,    # Alta prioridade (venda)
            "gallery": 2,   # Média prioridade (engajamento)
            "social": 1     # Baixa prioridade (redes sociais)
        }
    
    def should_show_cta(self, conversation_history: List[Dict], user_emotional_state: str, cta_type: str = "offers") -> bool:
        """Decide se deve mostrar um CTA baseado no contexto emocional e da conversa."""
        if len(conversation_history) < 3:
            return False

        # Não mostrar CTA se o usuário estiver muito negativo
        if user_emotional_state == "Muito Negativo":
            return False

        # Verificar se já mostrou um CTA recentemente
        if 'last_cta_time' in st.session_state:
            elapsed = time.time() - st.session_state.last_cta_time
            if elapsed < 90:  # Reduzido para ser mais agressivo
                return False

        # Análise do contexto da conversa
        last_msgs = []
        for msg in conversation_history[-6:]:
            content = msg["content"]
            if content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            last_msgs.append(f"{msg['role']}: {content.lower()}")
        
        context = " ".join(last_msgs)
        
        # Palavras que indicam interesse sexual/compra
        hot_words = [
            "buceta", "peito", "fuder", "gozar", "gostosa", "delicia", "molhad", "xereca", 
            "pau", "piroca", "transar", "foto", "video", "mostra", "ver", "quero", "tesão", 
            "molhada", "foda", "nude", "seios", "bunda", "rabuda", "gata", "pack", 
            "conteúdo", "comprar", "quanto", "valor", "preço", "custa", "safada", "tarada"
        ]
        
        # Perguntas diretas sobre compra/acesso
        direct_asks = [
            "mostra", "quero ver", "me manda", "como assinar", "como comprar", 
            "como ter acesso", "onde vejo", "quero comprar", "quero conteúdo", 
            "quanto custa", "qual valor", "mostra mais", "me mostra", "tem desconto"
        ]
        
        hot_count = sum(1 for word in hot_words if word in context)
        has_direct_ask = any(ask in context for ask in direct_asks)
        
        # Lógica de decisão mais inteligente
        if user_emotional_state in ["Muito Positivo", "Positivo"] and (hot_count >= 2 or has_direct_ask):
            return True
        elif hot_count >= 3:  # Muito interesse sexual
            return True
        elif has_direct_ask:  # Pergunta direta
            return True
        
        return False

    def should_show_preview(self) -> bool:
        """Decide se deve mostrar uma prévia."""
        if 'preview_shown' in st.session_state and st.session_state.preview_shown:
            return False
            
        # Aumenta a chance se o usuário está engajado
        chance = 0.35 if len(st.session_state.get('messages', [])) > 5 else 0.25
        if random.random() < chance:
            st.session_state.preview_shown = True
            return True
        return False

    def should_use_audio(self, context: str, fake_probability: float) -> bool:
        """Decide se deve usar áudio baseado no contexto."""
        # Sempre usar áudio para responder dúvidas sobre autenticidade
        if fake_probability > 0.6:
            return True
        
        # Usar áudio em momentos estratégicos
        if 'audio_count' not in st.session_state:
            st.session_state.audio_count = 0
            
        # Aumentar chance de áudio se o usuário está muito engajado
        base_chance = 0.20 if len(st.session_state.get('messages', [])) > 8 else 0.15
        
        # Aumentar chance para certas palavras-chave
        audio_triggers = ["amostra", "gratis", "nua", "fake", "real", "voz"]
        if any(trigger in context.lower() for trigger in audio_triggers):
            base_chance += 0.15
            
        return random.random() < base_chance

# ======================
# SERVIÇOS DE BANCO DE DADOS (Melhorados)
# ======================
class DatabaseService:
    @staticmethod
    def init_db() -> sqlite3.Connection:
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id TEXT,
                     session_id TEXT,
                     timestamp DATETIME,
                     role TEXT,
                     content TEXT,
                     sentiment_polarity REAL,
                     sentiment_label TEXT)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn: sqlite3.Connection, user_id: str, session_id: str, role: str, content: str, 
                    sentiment_polarity: float = 0.0, sentiment_label: str = "Neutro") -> None:
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO conversations (user_id, session_id, timestamp, role, content, sentiment_polarity, sentiment_label)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now(), role, content, sentiment_polarity, sentiment_label))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar mensagem: {e}")

    @staticmethod
    def load_messages(conn: sqlite3.Connection, user_id: str, session_id: str, limit: int = 50) -> List[Dict]:
        try:
            c = conn.cursor()
            c.execute("""
                SELECT role, content, sentiment_polarity, sentiment_label FROM conversations 
                WHERE user_id = ? AND session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, session_id, limit))
            messages = []
            for row in reversed(c.fetchall()):
                msg = {"role": row[0], "content": row[1]}
                if row[2] is not None:  # Se tem dados de sentimento
                    msg["sentiment_polarity"] = row[2]
                    msg["sentiment_label"] = row[3]
                messages.append(msg)
            return messages
        except sqlite3.Error as e:
            logger.error(f"Erro ao carregar mensagens: {e}")
            return []

    @staticmethod
    def cleanup_old_messages(conn: sqlite3.Connection, days: int = 7):
        """Limpa mensagens antigas do banco de dados."""
        try:
            c = conn.cursor()
            c.execute("""
                DELETE FROM conversations 
                WHERE timestamp < datetime('now', ?)
            """, (f'-{days} days',))
            conn.commit()
            logger.info(f"Cleaned up messages older than {days} days")
        except sqlite3.Error as e:
            logger.error(f"Erro ao limpar mensagens antigas: {e}")

# ======================
# SERVIÇOS DE API (Ultra Melhorados)
# ======================
class ApiService:
    def __init__(self):
        self.cta_engine = CTAEngine()
        self.learning_engine = LearningEngine()
        self.emotional_ai = EmotionalIntelligence()
        self.personality = DynamicPersonality()
        self.timing = RealisticTiming()
    
    def get_intelligent_response(self, user_input: str, user_id: str, conversation_history: List[Dict]) -> Dict:
        """Gera uma resposta inteligente usando todos os sistemas de humanização."""
        
        # 1. Análise emocional do input do usuário
        polarity, subjectivity = self.emotional_ai.analyze_sentiment(user_input)
        emotional_state = self.emotional_ai.get_emotional_state(polarity)
        
        # 2. Salvar estado emocional
        self.learning_engine.save_emotional_state(user_id, emotional_state, polarity, subjectivity)
        
        # 3. Extrair e salvar informações do usuário
        self.learning_engine.extract_and_save_info(user_id, user_input)
        
        # 4. Obter perfil e preferências do usuário
        user_profile = self.learning_engine.get_user_profile(user_id) or {}
        user_preferences = self.learning_engine.get_user_preferences(user_id)
        
        # 5. Obter persona e humor dinâmicos
        persona, humor = self.personality.get_current_persona()
        
        # 6. Verificar se é pergunta sobre autenticidade
        fake_probability = detect_fake_question(user_input)
        if fake_probability > 0.7:
            return self._handle_fake_question(fake_probability)
        
        # 7. Construir prompt dinâmico
        dynamic_persona = Persona.get_dynamic_persona(persona, humor, emotional_state, user_profile)
        
        # 8. Preparar contexto da conversa
        conversation_context = self._format_conversation_context(conversation_history, user_preferences)
        
        # 9. Decidir sobre CTA e áudio
        should_show_cta = self.cta_engine.should_show_cta(conversation_history, emotional_state)
        should_use_audio = self.cta_engine.should_use_audio(user_input, fake_probability)
        
        # 10. Chamar API do Gemini
        response = self._call_gemini_api(dynamic_persona, conversation_context, user_input, should_show_cta, should_use_audio)
        
        # 11. Pós-processamento da resposta
        response = self._post_process_response(response, user_input, should_use_audio)
        
        return response

    def _handle_fake_question(self, fake_probability: float) -> Dict:
        """Lida com perguntas sobre autenticidade de forma mais humana."""
        responses = [
            {
                "text": "Não sou fake não, amor! Ouça minha voz... 😘",
                "audio": "nao_sou_fake_nao",
                "cta": {"show": False}
            },
            {
                "text": "Sério que você tá duvidando de mim? 😤 Escuta minha voz e vê se sou robô...",
                "audio": "nao_sou_fake_nao", 
                "cta": {"show": False}
            },
            {
                "text": "Ai que ofensa! 😢 Sou real sim, escuta aqui...",
                "audio": "nao_sou_fake_nao",
                "cta": {"show": False}
            }
        ]
        
        # Escolher resposta baseada na intensidade da dúvida
        if fake_probability > 0.9:
            return responses[1]  # Mais defensiva
        elif fake_probability > 0.8:
            return responses[2]  # Mais emotiva
        else:
            return responses[0]  # Padrão

    def _format_conversation_context(self, conversation_history: List[Dict], user_preferences: Dict) -> str:
        """Formata o contexto da conversa incluindo preferências do usuário."""
        context = "Histórico da conversa:\n"
        
        # Últimas 8 mensagens para contexto
        for msg in conversation_history[-8:]:
            role = "Cliente" if msg["role"] == "user" else "Mylle"
            content = msg["content"]
            if content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            context += f"{role}: {content}\n"
        
        # Adicionar preferências conhecidas
        if user_preferences:
            context += "\nPreferências conhecidas do usuário:\n"
            for pref_type, prefs in user_preferences.items():
                for pref, strength in prefs.items():
                    if strength > 0.5:  # Apenas preferências fortes
                        context += f"- {pref_type}: {pref}\n"
        
        return context

    def _call_gemini_api(self, dynamic_persona: str, conversation_context: str, user_input: str, 
                        should_show_cta: bool, should_use_audio: bool) -> Dict:
        """Chama a API do Gemini com o prompt otimizado."""
        
        # Simular delay de digitação humano
        typing_delay = self.timing.get_typing_delay(user_input)
        
        # Mostrar efeito de "visualizado" e "digitando"
        status_container = st.empty()
        self._show_status_effect(status_container, "viewed")
        self._show_status_effect(status_container, "typing")
        
        # Construir prompt final
        prompt = f"""
        {dynamic_persona}
        
        {conversation_context}
        
        Última mensagem do cliente: "{user_input}"
        
        INSTRUÇÕES ESPECÍFICAS:
        - Responda em JSON no formato: {{"text": "sua resposta", "audio": "chave_do_audio_opcional", "cta": {{"show": true/false, "label": "texto do botão", "target": "página"}}}}
        - Mantenha a resposta curta (máximo 2-3 frases)
        - {"Inclua um CTA de venda se apropriado" if should_show_cta else "Não inclua CTA desta vez"}
        - {"Considere usar um áudio para maior realismo" if should_use_audio else "Não use áudio desta vez"}
        - Seja natural, humana e envolvente
        - Use o nome do usuário se souber
        """
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 1.2,  # Aumentado para mais criatividade
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 300
            }
        }
        
        try:
            # Simular delay de digitação
            time.sleep(typing_delay)
            
            logger.info(f"API call for user input: {user_input[:50]}...")
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            gemini_response = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # Processar resposta JSON
            try:
                if '```json' in gemini_response:
                    json_part = gemini_response.split('```json')[1].split('```')[0].strip()
                    resposta = json.loads(json_part)
                else:
                    resposta = json.loads(gemini_response)
                
                # Validar estrutura da resposta
                if not isinstance(resposta, dict) or "text" not in resposta:
                    raise ValueError("Resposta inválida do Gemini")
                
                return resposta
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Erro ao processar JSON do Gemini: {e}")
                # Fallback: extrair apenas o texto
                clean_text = re.sub(r'```json|```', '', gemini_response).strip()
                return {"text": clean_text, "cta": {"show": False}}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na API do Gemini: {e}")
            return get_fallback_response(user_input, st.session_state.get('messages', []))
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return get_fallback_response(user_input, st.session_state.get('messages', []))

    def _post_process_response(self, response: Dict, user_input: str, should_use_audio: bool) -> Dict:
        """Pós-processa a resposta para adicionar imperfeições humanas e áudios contextuais."""
        
        # Adicionar imperfeições humanas ocasionalmente
        if "text" in response:
            response["text"] = self.timing.simulate_human_imperfections(response["text"])
        
        # Adicionar áudio contextual se não foi especificado pelo Gemini
        if should_use_audio and not response.get("audio"):
            audio_key = self._select_contextual_audio(user_input, response.get("text", ""))
            if audio_key:
                response["audio"] = audio_key
        
        # Garantir que CTA tenha estrutura correta
        if "cta" not in response:
            response["cta"] = {"show": False}
        elif response["cta"].get("show") and not response["cta"].get("label"):
            response["cta"]["label"] = "🎁 Ver Conteúdo"
            response["cta"]["target"] = "offers"
        
        return response

    def _select_contextual_audio(self, user_input: str, response_text: str) -> Optional[str]:
        """Seleciona um áudio contextual baseado no input e resposta."""
        lower_input = user_input.lower()
        lower_response = response_text.lower()
        
        # Mapeamento contextual de áudios
        audio_mapping = {
            ("amostra", "gratis", "grátis", "sample", "free"): "claro_tenho_amostra_gratis",
            ("oi", "olá", "hello", "hey"): "oi_meu_amor_tudo_bem",
            ("nua", "nude", "pelada"): "ver_nua_tem_que_comprar",
            ("rosinha", "rosa", "buceta"): "imagina_ela_bem_rosinha",
            ("fake", "falsa", "bot", "robô"): "nao_sou_fake_nao",
            ("esperando", "demora", "cadê"): "vida_to_esperando_voce_me_responder_gatinho"
        }
        
        # Verificar se alguma palavra-chave está presente
        for keywords, audio_key in audio_mapping.items():
            if any(keyword in lower_input for keyword in keywords):
                return audio_key
        
        # Áudio baseado na hora do dia para cumprimentos
        now = datetime.now()
        hour = now.hour
        if any(greeting in lower_input for greeting in ["oi", "olá", "bom dia", "boa tarde", "boa noite"]):
            if 6 <= hour < 12:
                return "bom_dia_nao_sou_fake"
            elif 12 <= hour < 18:
                return "boa_tarde_nao_sou_fake"
            elif 18 <= hour <= 23:
                return "boa_noite_nao_sou_fake"
        
        return None

    def _show_status_effect(self, container, status_type: str):
        """Mostra efeitos de status como 'visualizado' e 'digitando'."""
        if status_type == "viewed":
            message = "✓ Visualizado"
            duration = 1.0
        else:  # typing
            message = "Digitando"
            duration = 2.0
        
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            if status_type == "typing":
                dots = "." * (int(elapsed * 2) % 4)
                display_message = f"{message}{dots}"
            else:
                display_message = message
            
            container.markdown(f"""
            <div style="
                color: #888;
                font-size: 0.8em;
                padding: 2px 8px;
                border-radius: 10px;
                background: rgba(0,0,0,0.05);
                display: inline-block;
                margin-left: 10px;
                vertical-align: middle;
                font-style: italic;
            ">
                {display_message}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.3)
        
        container.empty()

# ======================
# INICIALIZAÇÃO E PERSISTÊNCIA DE SESSÃO
# ======================
def initialize_session():
    """Inicializa a sessão com valores padrão e carrega dados persistentes."""
    # Valores padrão da sessão
    default_values = {
        'age_verified': False,
        'messages': [],
        'request_count': 0,
        'connection_complete': False,
        'chat_started': False,
        'current_page': 'home',
        'session_id': str(uuid.uuid4()),
        'last_cta_time': 0,
        'preview_shown': False,
        'conversation_stage': 'initial',
        'last_interaction_time': time.time(),
        'user_info_collected': False,
        'last_user_message_time': time.time(),
        'audio_count': 0,
        'cleanup_done': False
    }
    
    # Inicializar valores que não existem
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Carregar dados persistentes
    load_persistent_data()

def load_persistent_data():
    """Carrega dados persistentes do banco de dados."""
    user_id = get_user_id()
    db = PersistentState()
    saved_data = db.load_state(user_id) or {}
    
    # Carregar apenas dados que fazem sentido persistir
    persistent_keys = [
        'age_verified', 'messages', 'request_count', 'connection_complete', 
        'chat_started', 'current_page', 'preview_shown', 'conversation_stage',
        'last_interaction_time', 'user_info_collected', 'audio_count'
    ]
    
    for key in persistent_keys:
        if key in saved_data and key not in st.session_state:
            st.session_state[key] = saved_data[key]

def save_persistent_data():
    """Salva dados importantes da sessão no banco de dados."""
    user_id = get_user_id()
    db = PersistentState()
    
    persistent_keys = [
        'age_verified', 'messages', 'request_count', 'connection_complete',
        'chat_started', 'current_page', 'preview_shown', 'conversation_stage',
        'last_interaction_time', 'user_info_collected', 'audio_count'
    ]
    
    # Preparar dados para salvar
    current_state = {}
    for key in persistent_keys:
        if key in st.session_state:
            current_state[key] = st.session_state[key]
    
    # Salvar apenas se houver mudanças significativas
    last_saved_state = db.load_state(user_id) or {}
    changed_keys = [key for key in persistent_keys 
                   if current_state.get(key) != last_saved_state.get(key)]
    
    if changed_keys:
        db.save_state(user_id, current_state)
        logger.info(f"Saved persistent data for user {user_id}: {changed_keys}")

# ======================
# INTERFACE DO USUÁRIO (Ultra Melhorada)
# ======================
class UiService:
    @staticmethod
    def show_audio_player(audio_key: str) -> None:
        """Exibe um player de áudio com design melhorado."""
        if audio_key in Config.AUDIOS:
            audio_url = Config.AUDIOS[audio_key]
            st.markdown(f"""
            <div class="audio-message">
                <span class="audio-icon">🎵</span>
                <strong>Áudio da Mylle</strong>
                <audio controls style="width: 100%; margin-top: 10px;">
                    <source src="{audio_url}" type="audio/mpeg">
                    Seu navegador não suporta áudio.
                </audio>
            </div>
            """, unsafe_allow_html=True)
            
            # Incrementar contador de áudios
            if 'audio_count' not in st.session_state:
                st.session_state.audio_count = 0
            st.session_state.audio_count += 1

    @staticmethod
    def show_preview_image() -> None:
        """Mostra uma imagem de preview com efeito especial."""
        st.markdown(f"""
        <div style="
            text-align: center;
            margin: 15px 0;
            padding: 15px;
            background: linear-gradient(45deg, rgba(255, 102, 179, 0.1), rgba(148, 0, 211, 0.1));
            border-radius: 15px;
            border: 1px solid rgba(255, 102, 179, 0.3);
        ">
            <p style="color: #ff66b3; margin-bottom: 10px; font-weight: bold;">🎁 Preview Exclusivo</p>
            <img src="{Config.IMG_PREVIEW}" style="
                max-width: 200px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(255, 102, 179, 0.3);
            ">
            <p style="color: #aaa; margin-top: 10px; font-size: 0.9em;">Uma amostra do que te espera... 😈</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_call_effect() -> None:
        """Efeito de 'conectando' melhorado."""
        placeholder = st.empty()
        
        with placeholder.container():
            st.markdown("""
            <div style="
                text-align: center;
                padding: 50px;
                background: linear-gradient(45deg, #1e0033, #3c0066);
                border-radius: 15px;
                margin: 20px 0;
            ">
                <div style="font-size: 3em; margin-bottom: 20px;">📞</div>
                <h2 style="color: #ff66b3;">Conectando com Mylle...</h2>
                <div style="margin: 20px 0;">
                    <div style="
                        width: 200px;
                        height: 4px;
                        background: rgba(255, 102, 179, 0.3);
                        border-radius: 2px;
                        margin: 0 auto;
                        overflow: hidden;
                    ">
                        <div style="
                            width: 50px;
                            height: 100%;
                            background: linear-gradient(90deg, #ff66b3, #ff1493);
                            border-radius: 2px;
                            animation: loading 2s infinite;
                        "></div>
                    </div>
                </div>
                <p style="color: #aaa;">Preparando experiência exclusiva...</p>
            </div>
            
            <style>
                @keyframes loading {
                    0% { transform: translateX(-100px); }
                    100% { transform: translateX(250px); }
                }
            </style>
            """, unsafe_allow_html=True)
        
        time.sleep(3)
        placeholder.empty()

    @staticmethod
    def age_verification() -> None:
        """Verificação de idade com design melhorado."""
        st.markdown("""
        <style>
            .age-verification {
                max-width: 500px;
                margin: 2rem auto;
                padding: 2rem;
                background: linear-gradient(145deg, #1e0033, #3c0066);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 102, 179, 0.2);
                color: white;
                text-align: center;
            }
            .age-icon {
                font-size: 3rem;
                color: #ff66b3;
                margin-bottom: 1rem;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="age-verification">
            <div class="age-icon">🔞</div>
            <h1 style="color: #ff66b3; margin-bottom: 1rem;">Conteúdo Exclusivo Adulto</h1>
            <p style="margin-bottom: 1.5rem;">Acesso restrito para maiores de 18 anos</p>
            <p style="font-size: 0.9em; color: #ccc;">Ao continuar, você confirma ter mais de 18 anos</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <p style="color: #aaa;">Como você quer começar?</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🏠 Conhecer a Mylle", use_container_width=True):
                    st.session_state.age_verified = True
                    st.session_state.current_page = "home"
                    save_persistent_data()
                    st.rerun()
            
            with col_btn2:
                if st.button("💬 Conversar Agora", use_container_width=True, type="primary"):
                    st.session_state.age_verified = True
                    st.session_state.current_page = "chat"
                    st.session_state.chat_started = True
                    save_persistent_data()
                    st.rerun()

# ... (Continuação do código será adicionada na próxima parte)


    @staticmethod
    def setup_sidebar() -> None:
        """Sidebar melhorada com mais funcionalidades."""
        with st.sidebar:
            st.markdown("""
            <style>
                [data.testid="stSidebar"] {
                    background:
                        radial-gradient(900px 300px at 10% -10%, rgba(255,20,147,.25) 0%, transparent 60%),
                        radial-gradient(700px 300px at 90% 110%, rgba(148,0,211,.25) 0%, transparent 60%),
                        linear-gradient(180deg, #1a0033 0%, #2d004d 100%) !important;
                    border-right: 2px solid #ff1493 !important;
                }
                .sidebar-profile {
                    text-align: center;
                    margin: 1rem 0;
                }
                .sidebar-profile img {
                    border-radius: 50%;
                    border: 3px solid #ff66b3;
                    width: 100px;
                    height: 100px;
                    object-fit: cover;
                    margin-bottom: 10px;
                    box-shadow: 0 6px 18px rgba(255, 20, 147, 0.35);
                    transition: transform 0.3s ease;
                }
                .sidebar-profile img:hover {
                    transform: scale(1.05);
                }
                .sidebar-social-button {
                    background: linear-gradient(45deg, #ff1493, #9400d3) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 10px !important;
                    padding: 12px 16px !important;
                    margin: 6px 0 !important;
                    width: 100% !important;
                    text-align: center !important;
                    transition: all 0.25s ease !important;
                    font-weight: 700;
                    letter-spacing: .2px;
                }
                .sidebar-social-button:hover {
                    transform: translateY(-2px) scale(1.01) !important;
                    box-shadow: 0 6px 16px rgba(255, 20, 147, 0.45) !important;
                }
                .sidebar-menu-title{
                    color:#ff7cc6; 
                    font-weight:800; 
                    margin: .5rem 0 .25rem 0;
                    text-transform: uppercase;
                    letter-spacing: .6px;
                    font-size:.9em;
                }
                .hot-divider{border-top:1px solid rgba(255,102,179,.35); margin:.75rem 0;}
                .online-indicator {
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    background: #00ff00;
                    border-radius: 50%;
                    margin-right: 5px;
                    animation: blink 2s infinite;
                }
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0.3; }
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Obter informações do usuário para personalização
            user_id = get_user_id()
            learning_engine = LearningEngine()
            user_profile = learning_engine.get_user_profile(user_id)
            user_name = user_profile.get('name', 'Anônimo') if user_profile else 'Anônimo'
            
            st.markdown(f"""
            <div class="sidebar-profile">
                <img src="{Config.IMG_PROFILE}" alt="Mylle Alves">
                <h3 style="color: #ff66b3; margin: 0;">Mylle Alves</h3>
                <p style="color: #aaa; margin: 0; font-size: 0.9em;">
                    <span class="online-indicator"></span>Online agora
                </p>
                {f'<p style="color: #ff66b3; margin: 5px 0 0; font-size: 0.8em;">Conversando com {user_name}</p>' if user_name != 'Anônimo' else ''}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💬 Chat", key="menu_chat", use_container_width=True):
                st.session_state.current_page = "chat"
                save_persistent_data()
                st.rerun()

            st.markdown('<div class="hot-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-menu-title">Redes Hot</div>', unsafe_allow_html=True)
            
            for platform, url in Config.SOCIAL_LINKS.items():
                if st.button(Config.SOCIAL_ICONS[platform], 
                           key=f"sidebar_{platform}",
                           use_container_width=True):
                    js = f"window.open('{url}', '_blank');"
                    st.components.v1.html(f"<script>{js}</script>")
            
            st.markdown('<div class="hot-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-menu-title">Navegação</div>', unsafe_allow_html=True)
            
            menu_options = {
                "🏠 Início": "home",
                "📸 Preview": "gallery", 
                "🎁 Packs VIP": "offers"
            }
            
            for option, page in menu_options.items():
                if st.button(option, use_container_width=True, key=f"menu_{page}"):
                    st.session_state.current_page = page
                    save_persistent_data()
                    st.rerun()
            
            # Estatísticas da sessão (para debug/admin)
            if st.session_state.get('messages'):
                st.markdown('<div class="hot-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="sidebar-menu-title">Sessão</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="font-size: 0.7em; color: #888;">
                    <p>Mensagens: {len(st.session_state.messages)}</p>
                    <p>Áudios: {st.session_state.get('audio_count', 0)}</p>
                    <p>Requisições: {st.session_state.get('request_count', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="hot-divider"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Mylle Alves Premium</p>
                <p>Conteúdo adulto exclusivo</p>
                <p style="margin-top: 10px; color: #ff66b3;">🤖 Powered by AI</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page() -> None:
        """Página de galeria melhorada."""
        st.markdown("""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid rgba(255, 102, 179, 0.3);
        ">
            <h3 style="color: #ff66b3; margin: 0;">✨ Preview Exclusivo</h3>
            <p style="color: #aaa; margin: 5px 0 0; font-size: 0.9em;">Uma amostra do que te espera nos packs VIP</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, col in enumerate(cols):
            with col:
                st.image(Config.IMG_GALLERY[idx % len(Config.IMG_GALLERY)], 
                        use_container_width=True, 
                        caption=f"💎 Preview #{idx+1}")
                st.markdown("""<div style="text-align:center; color: #ff66b3; margin-top: -10px;">✨ Exclusivo VIP</div>""", 
                          unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Testimonial simulado
        st.markdown("""
        <div style="
            text-align: center; 
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 102, 179, 0.05);
            border-radius: 10px;
            border-left: 4px solid #ff66b3;
        ">
            <p style="color: #ff66b3; font-style: italic; font-size: 1.1em;">
                "Isso é só uma amostra... imagina o que te espera nos packs completos 😈"
            </p>
            <p style="color: #aaa; font-size: 0.9em; margin-top: 10px;">- Mylle Alves</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Quero Ver Tudo Agora", key="vip_button_gallery", use_container_width=True, type="primary"):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
        
        with col2:
            if st.button("💬 Voltar ao Chat", key="back_from_gallery", use_container_width=True):
                st.session_state.current_page = "chat"
                save_persistent_data()
                st.rerun()

    @staticmethod
    def chat_shortcuts() -> None:
        """Atalhos do chat melhorados."""
        cols = st.columns(4)
        shortcuts = [
            ("🏠 Início", "home"),
            ("📸 Preview", "gallery"),
            ("🎁 Packs", "offers"),
            ("🔄 Limpar", "clear")
        ]
        
        for col, (label, action) in zip(cols, shortcuts):
            with col:
                if action == "clear":
                    if st.button(label, key=f"shortcut_{action}", use_container_width=True):
                        st.session_state.messages = []
                        st.session_state.request_count = 0
                        save_persistent_data()
                        st.rerun()
                else:
                    if st.button(label, key=f"shortcut_{action}", use_container_width=True):
                        st.session_state.current_page = action
                        save_persistent_data()
                        st.rerun()

    @staticmethod
    def enhanced_chat_ui(conn: sqlite3.Connection) -> None:
        """Interface de chat ultra melhorada."""
        st.markdown("""
        <style>
            .chat-header {
                background: linear-gradient(90deg, #ff66b3, #ff1493);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(255, 102, 179, 0.3);
            }
            .chat-stats {
                background: rgba(255, 102, 179, 0.1);
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 15px;
                font-size: 0.8em;
                color: #aaa;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)
        
        UiService.chat_shortcuts()
        
        # Header do chat com informações dinâmicas
        user_id = get_user_id()
        learning_engine = LearningEngine()
        user_profile = learning_engine.get_user_profile(user_id)
        user_name = user_profile.get('name', '') if user_profile else ''
        
        persona, humor = DynamicPersonality.get_current_persona()
        persona_name = persona.split(':')[0]
        
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0; font-size:1.5em;">💋 Chat com {persona_name}</h2>
            <p style="margin:5px 0 0; font-size:0.9em; opacity:0.8;">
                {f"Conversando com {user_name} • " if user_name else ""}Conteúdo adulto exclusivo - Aqui eu comando 😈
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Estatísticas da conversa
        if len(st.session_state.messages) > 0:
            st.markdown(f"""
            <div class="chat-stats">
                💬 {len(st.session_state.messages)} mensagens • 
                🎵 {st.session_state.get('audio_count', 0)} áudios • 
                ⚡ {st.session_state.get('request_count', 0)} interações
            </div>
            """, unsafe_allow_html=True)
        
        ChatService.process_user_input(conn)
        save_persistent_data()

# ======================
# PÁGINAS (Ultra Melhoradas)
# ======================
class NewPages:
    @staticmethod
    def show_home_page() -> None:
        """Página inicial ultra melhorada."""
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(Config.IMG_PROFILE, use_container_width=True)
            
            # Status dinâmico
            persona, humor = DynamicPersonality.get_current_persona()
            persona_name = persona.split(':')[0]
            
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px;">
                <h3 style="color: #ff66b3;">Mylle Alves</h3>
                <p style="color: #8be58b;">🟢 {persona_name} Online</p>
                <p style="color: #aaa; font-size: 0.8em;">{humor.split(':')[0]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("""
            <div style="
                background: rgba(255, 102, 179, 0.12);
                padding: 15px;
                border-radius: 10px;
                border:1px solid rgba(255,102,179,0.25)
            ">
                <h4>📊 Meu Perfil</h4>
                <p>👙 85-60-90</p>
                <p>📏 1.68m</p>
                <p>🎂 22 anos</p>
                <p>📍 São Paulo</p>
                <p>💎 Criadora Premium</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Estatísticas dinâmicas (simuladas)
            online_users = random.randint(45, 89)
            st.markdown(f"""
            <div style="
                background: rgba(255, 102, 179, 0.08);
                padding: 10px;
                border-radius: 8px;
                margin-top: 10px;
                text-align: center;
            ">
                <p style="color: #ff66b3; font-size: 0.9em; margin: 0;">
                    🔥 {online_users} pessoas online agora
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(45deg, #ff66b3, #ff1493);
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 20px;
                box-shadow: 0 10px 22px rgba(255,20,147,.25);
            ">
                <h2>💋 Bem-vindo ao Meu Mundo</h2>
                <p>Conversas quentes e conteúdo exclusivo esperando por você!</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="
                background: rgba(255, 102, 179, 0.12);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border:1px solid rgba(255,102,179,.25);
            ">
                <h4>🎯 O que você encontra aqui:</h4>
                <p>• 💬 Chat privado e personalizado comigo</p>
                <p>• 📸 Fotos exclusivas e sensuais em alta qualidade</p>
                <p>• 🎥 Vídeos quentes e explícitos</p>
                <p>• 🎁 Conteúdo personalizado sob demanda</p>
                <p>• 🔞 Experiências únicas e inesquecíveis</p>
                <p>• 🎵 Áudios íntimos e provocantes</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🌶️ Prévia do Conteúdo")
            preview_cols = st.columns(2)
            previews = Config.IMG_HOME_PREVIEWS[:2]
            for idx, col in enumerate(preview_cols):
                with col:
                    st.image(previews[idx], use_container_width=True, caption=f"Preview {idx+1}")
            
            preview_cols2 = st.columns(2)
            previews2 = Config.IMG_HOME_PREVIEWS[2:4]
            for idx, col in enumerate(preview_cols2):
                with col:
                    st.image(previews2[idx], use_container_width=True, caption=f"Preview {idx+3}")

        st.markdown("---")
        
        # Depoimentos simulados
        st.markdown("""
        <div style="
            background: rgba(255, 102, 179, 0.05);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #ff66b3;
        ">
            <h4 style="color: #ff66b3;">💬 O que dizem sobre mim:</h4>
            <p style="font-style: italic; color: #aaa;">
                "A Mylle é incrível! Conversa super natural e o conteúdo é de outro mundo 🔥" - Cliente VIP
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Ir para o Chat", use_container_width=True, type="primary"):
                st.session_state.current_page = "chat"
                st.session_state.chat_started = True
                save_persistent_data()
                st.rerun()
        with col2:
            if st.button("🎁 Ver Packs VIP", use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()

    @staticmethod
    def show_offers_page() -> None:
        """Página de ofertas ultra melhorada."""
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ff66b3; display: inline-block; padding-bottom: 5px;">
                🎁 Packs VIP Exclusivos
            </h2>
            <p style="color: #aaa; margin-top: 5px;">Escolha como você quer me ver... 😈</p>
        </div>
        """, unsafe_allow_html=True)

        # Oferta especial dinâmica
        discount_percentage = random.choice([15, 20, 25, 30])
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, #ff1493, #9400d3);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        ">
            <h3 style="margin: 0;">🔥 OFERTA ESPECIAL - {discount_percentage}% OFF</h3>
            <p style="margin: 5px 0 0; font-size: 0.9em;">Válida apenas hoje! Não perca essa chance única.</p>
        </div>
        """, unsafe_allow_html=True)

        packages = [
            {
                "name": "TARADINHA",
                "price": "R$ 29,99",
                "original_price": "R$ 39,99",
                "benefits": ["15 fotos exclusivas", "15 vídeos quentes", "Acesso por 30 dias", "Suporte prioritário"],
                "color": "#ff66b3",
                "link": Config.CHECKOUT_TARADINHA,
                "image": Config.PACK_IMAGES["TARADINHA"],
                "tag": "🔥 Mais Popular",
                "description": "Perfeito para começar a me conhecer melhor..."
            },
            {
                "name": "MOLHADINHA",
                "price": "R$ 49,99", 
                "original_price": "R$ 69,99",
                "benefits": ["25 fotos sensuais", "25 vídeos especiais", "Acesso por 60 dias", "Conteúdo 4K", "Chat prioritário"],
                "color": "#9400d3",
                "link": Config.CHECKOUT_MOLHADINHA,
                "image": Config.PACK_IMAGES["MOLHADINHA"],
                "tag": "💎 Premium",
                "description": "Para quem quer mais intensidade e qualidade..."
            },
            {
                "name": "SAFADINHA",
                "price": "R$ 69,99",
                "original_price": "R$ 99,99",
                "benefits": ["40 fotos ultra-exclusivas", "40 vídeos premium", "Acesso vitalício", "Conteúdo 4K", "Updates gratuitos", "Conteúdo personalizado"],
                "color": "#ff0066",
                "link": Config.CHECKOUT_SAFADINHA,
                "image": Config.PACK_IMAGES["SAFADINHA"],
                "tag": "👑 VIP",
                "description": "A experiência completa e sem limites..."
            }
        ]

        cols = st.columns(3)
        for idx, (col, package) in enumerate(zip(cols, packages)):
            with col:
                st.markdown(f"""
                <div style="
                    background: rgba(30, 0, 51, 0.3);
                    border: 2px solid {package['color']};
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    position: relative;
                    transition: transform 0.3s ease;
                    height: 100%;
                ">
                    <div style="
                        background: {package['color']};
                        color: white;
                        padding: 5px 10px;
                        border-radius: 15px;
                        font-size: 0.8em;
                        font-weight: bold;
                        margin-bottom: 15px;
                        display: inline-block;
                    ">
                        {package['tag']}
                    </div>
                    
                    <img src="{package['image']}" style="
                        width: 100%;
                        height: 150px;
                        object-fit: cover;
                        border-radius: 10px;
                        margin-bottom: 15px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    ">
                    
                    <h3 style="color: {package['color']}; margin: 10px 0;">
                        PACK {package['name']}
                    </h3>
                    
                    <p style="color: #aaa; font-size: 0.9em; margin-bottom: 15px;">
                        {package['description']}
                    </p>
                    
                    <div style="margin: 15px 0;">
                        <span style="color: #888; text-decoration: line-through; font-size: 0.9em;">
                            {package['original_price']}
                        </span>
                        <br>
                        <span style="color: {package['color']}; font-size: 1.5em; font-weight: bold;">
                            {package['price']}
                        </span>
                    </div>
                    
                    <div style="text-align: left; margin: 15px 0;">
                """, unsafe_allow_html=True)
                
                for benefit in package['benefits']:
                    st.markdown(f"✅ {benefit}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button(f"🚀 Comprar {package['name']}", 
                           key=f"buy_{package['name']}", 
                           use_container_width=True,
                           type="primary"):
                    js = f"window.open('{package['link']}', '_blank');"
                    st.components.v1.html(f"<script>{js}</script>")
                
                st.markdown("</div>", unsafe_allow_html=True)

        # Garantias e segurança
        st.markdown("---")
        st.markdown("""
        <div style="
            background: rgba(255, 102, 179, 0.05);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        ">
            <h4 style="color: #ff66b3;">🛡️ Garantias e Segurança</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                <div>
                    <p style="font-size: 1.5em;">🔒</p>
                    <p style="font-size: 0.9em; color: #aaa;">Pagamento Seguro</p>
                </div>
                <div>
                    <p style="font-size: 1.5em;">⚡</p>
                    <p style="font-size: 0.9em; color: #aaa;">Acesso Imediato</p>
                </div>
                <div>
                    <p style="font-size: 1.5em;">🎯</p>
                    <p style="font-size: 0.9em; color: #aaa;">100% Exclusivo</p>
                </div>
                <div>
                    <p style="font-size: 1.5em;">💬</p>
                    <p style="font-size: 0.9em; color: #aaa;">Suporte 24h</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💬 Voltar ao Chat", key="back_from_offers", use_container_width=True):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

# ======================
# SERVIÇOS DE CHAT (Ultra Melhorados)
# ======================
class ChatService:
    @staticmethod
    def initialize_session(conn: sqlite3.Connection):
        """Inicializa a sessão do chat com melhorias."""
        # Limpeza periódica de mensagens antigas (apenas uma vez por sessão)
        if 'cleanup_done' not in st.session_state:
            DatabaseService.cleanup_old_messages(conn, days=7)
            st.session_state.cleanup_done = True

        # Carregar mensagens do banco de dados se a sessão estiver vazia
        if len(st.session_state.messages) == 0:
            saved_messages = DatabaseService.load_messages(
                conn, get_user_id(), st.session_state.session_id, limit=20
            )
            if saved_messages:
                st.session_state.messages = saved_messages

        # Iniciar conversa automaticamente se for novo usuário
        if len(st.session_state.messages) == 0 and st.session_state.chat_started:
            ChatService._send_welcome_message(conn)

    @staticmethod
    def _send_welcome_message(conn: sqlite3.Connection):
        """Envia mensagem de boas-vindas personalizada."""
        # Obter informações do usuário
        user_id = get_user_id()
        learning_engine = LearningEngine()
        user_profile = learning_engine.get_user_profile(user_id)
        
        # Personalizar mensagem baseada na hora e perfil
        now = datetime.now()
        hour = now.hour
        
        if user_profile and user_profile.get('name'):
            name_part = f", {user_profile['name']}"
        else:
            name_part = ""
        
        if 6 <= hour < 12:
            greeting = f"Bom dia{name_part}! ☀️"
            audio_key = "bom_dia_nao_sou_fake"
        elif 12 <= hour < 18:
            greeting = f"Boa tarde{name_part}! 🌅"
            audio_key = "boa_tarde_nao_sou_fake"
        else:
            greeting = f"Boa noite{name_part}! 🌙"
            audio_key = "boa_noite_nao_sou_fake"
        
        opening_messages = [
            f"{greeting} Finalmente chegou até mim! Como me achou, gostoso? 😈",
            f"{greeting} Que delícia te ver aqui... me conta seu nome, amor 😏",
            f"{greeting} Caiu direto na toca da raposa, hein? De onde você é? 👀"
        ]
        
        # Simular delay de digitação
        time.sleep(2)
        typing_container = st.empty()
        typing_container.markdown("""
        <div style="
            color: #888;
            font-size: 0.8em;
            padding: 2px 8px;
            border-radius: 10px;
            background: rgba(0,0,0,0.05);
            display: inline-block;
            margin-left: 10px;
            vertical-align: middle;
            font-style: italic;
        ">
            Digitando...
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(2)
        typing_container.empty()
        
        initial_message = {
            "role": "assistant",
            "content": json.dumps({
                "text": random.choice(opening_messages),
                "audio": audio_key,
                "cta": {"show": False}
            })
        }
        
        st.session_state.messages.append(initial_message)
        DatabaseService.save_message(
            conn, user_id, st.session_state.session_id,
            "assistant", initial_message["content"]
        )

    @staticmethod
    def format_conversation_history(messages: List[Dict], max_messages: int = 10) -> str:
        """Formata o histórico da conversa para o contexto."""
        formatted = []
        for msg in messages[-max_messages:]:
            role = "Cliente" if msg["role"] == "user" else "Mylle"
            content = msg["content"]
            if content.startswith('{"text"'):
                try:
                    content_data = json.loads(content)
                    if isinstance(content_data, dict):
                        content = content_data.get("text", content)
                except:
                    pass
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)

    @staticmethod
    def display_chat_history() -> None:
        """Exibe o histórico do chat com melhorias visuais."""
        chat_container = st.container()
        with chat_container:
            for idx, msg in enumerate(st.session_state.messages[-15:]):  # Mostrar mais mensagens
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="😎"):
                        st.markdown(f"""
                        <div style="
                            background: rgba(255, 102, 179, 0.15);
                            padding: 12px;
                            border-radius: 18px 18px 0 18px;
                            margin: 5px 0;
                            color: white;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        ">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    try:
                        content_data = json.loads(msg["content"])
                        if isinstance(content_data, dict):
                            with st.chat_message("assistant", avatar=Config.IMG_PROFILE):
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                                    color: white;
                                    padding: 12px;
                                    border-radius: 18px 18px 18px 0;
                                    margin: 5px 0;
                                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                                ">
                                    {content_data.get("text", "")}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if content_data.get("audio"):
                                    UiService.show_audio_player(content_data["audio"])
                                
                                # Mostrar CTA apenas na última mensagem
                                if content_data.get("cta", {}).get("show") and idx == len(st.session_state.messages[-15:]) - 1:
                                    cta_data = content_data.get("cta", {})
                                    if st.button(cta_data.get("label", "🎁 Ver Conteúdo"),
                                                key=f"cta_button_{hash(msg['content'])}",
                                                use_container_width=True,
                                                type="primary"):
                                        st.session_state.current_page = cta_data.get("target", "offers")
                                        save_persistent_data()
                                        st.rerun()
                    except:
                        with st.chat_message("assistant", avatar=Config.IMG_PROFILE):
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(45deg, #ff66b3, #ff1493);
                                color: white;
                                padding: 12px;
                                border-radius: 18px 18px 18px 0;
                                margin: 5px 0;
                                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                            ">
                                {msg["content"]}
                            </div>
                            """, unsafe_allow_html=True)

    @staticmethod
    def check_inactive_user() -> bool:
        """Verifica se o usuário está inativo e precisa de follow-up."""
        if 'last_user_message_time' not in st.session_state:
            st.session_state.last_user_message_time = time.time()
            return False
            
        inactive_time = time.time() - st.session_state.last_user_message_time
        
        # Diferentes tempos baseados no engajamento
        if len(st.session_state.messages) > 10:  # Usuário engajado
            threshold = 180  # 3 minutos
        elif len(st.session_state.messages) > 5:  # Usuário moderado
            threshold = 120  # 2 minutos
        else:  # Novo usuário
            threshold = 90   # 1.5 minutos
            
        if inactive_time > threshold and len(st.session_state.messages) > 2:
            # Chance baseada no tempo de inatividade
            chance = min(0.7, inactive_time / 300)  # Máximo 70% de chance
            if random.random() < chance:
                return True
        return False

    @staticmethod
    def process_user_input(conn: sqlite3.Connection) -> None:
        """Processa input do usuário com todas as melhorias de humanização."""
        ChatService.display_chat_history()
        
        # Verificar usuário inativo
        if ChatService.check_inactive_user():
            ChatService._send_follow_up_message(conn)
            return
        
        user_input = st.chat_input("💬 Digite sua mensagem...", key="chat_input")
        
        if user_input:
            cleaned_input = re.sub(r'<[^>]*>', '', user_input)[:500]
            user_id = get_user_id()
            
            # Verificar limite de requisições
            if not adjust_rate_limiting(user_id, st.session_state.request_count):
                ChatService._send_limit_message(conn)
                return
            
            # Análise emocional do input
            emotional_ai = EmotionalIntelligence()
            polarity, subjectivity = emotional_ai.analyze_sentiment(cleaned_input)
            emotional_state = emotional_ai.get_emotional_state(polarity)
            
            # Salvar mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": cleaned_input})
            DatabaseService.save_message(
                conn, user_id, st.session_state.session_id, 
                "user", cleaned_input, polarity, emotional_state
            )
            
            # Atualizar contadores e timestamps
            st.session_state.request_count += 1
            st.session_state.last_interaction_time = time.time()
            st.session_state.last_user_message_time = time.time()
            
            # Exibir mensagem do usuário
            with st.chat_message("user", avatar="😎"):
                st.markdown(f"""
                <div style="
                    background: rgba(255, 102, 179, 0.15);
                    padding: 12px;
                    border-radius: 18px 18px 0 18px;
                    margin: 5px 0;
                    color: white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                ">
                    {cleaned_input}
                </div>
                """, unsafe_allow_html=True)
            
            # Gerar resposta inteligente
            with st.chat_message("assistant", avatar=Config.IMG_PROFILE):
                api_service = ApiService()
                resposta = api_service.get_intelligent_response(
                    cleaned_input, user_id, st.session_state.messages
                )
                
                # Garantir formato correto da resposta
                if isinstance(resposta, str):
                    resposta = {"text": resposta, "cta": {"show": False}}
                elif "text" not in resposta:
                    resposta = {"text": str(resposta), "cta": {"show": False}}
                
                # Exibir resposta
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                    color: white;
                    padding: 12px;
                    border-radius: 18px 18px 18px 0;
                    margin: 5px 0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                ">
                    {resposta["text"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Exibir áudio se presente
                if resposta.get("audio"):
                    UiService.show_audio_player(resposta["audio"])
                
                # Mostrar preview ocasionalmente
                cta_engine = CTAEngine()
                if cta_engine.should_show_preview():
                    UiService.show_preview_image()
                
                # Exibir CTA se presente
                if resposta.get("cta", {}).get("show"):
                    cta_data = resposta.get("cta", {})
                    if st.button(cta_data.get("label", "🎁 Ver Conteúdo"),
                                key=f"chat_button_{time.time()}",
                                use_container_width=True,
                                type="primary"):
                        st.session_state.current_page = cta_data.get("target", "offers")
                        save_persistent_data()
                        st.rerun()
            
            # Salvar resposta da assistente
            st.session_state.messages.append({"role": "assistant", "content": json.dumps(resposta)})
            DatabaseService.save_message(
                conn, user_id, st.session_state.session_id, 
                "assistant", json.dumps(resposta)
            )
            save_persistent_data()

    @staticmethod
    def _send_follow_up_message(conn: sqlite3.Connection):
        """Envia mensagem de follow-up para usuário inativo."""
        follow_up_messages = [
            {
                "text": "Vida, tô esperando você me responder gatinho... 😏 O que aconteceu?",
                "audio": "vida_to_esperando_voce_me_responder_gatinho",
                "cta": {"show": False}
            },
            {
                "text": "Ei, sumido! Tô aqui esperando sua resposta... 😘",
                "cta": {"show": False}
            },
            {
                "text": "Oi amor, ainda tá aí? Me responde... 💋",
                "cta": {"show": False}
            }
        ]
        
        follow_up_message = {
            "role": "assistant",
            "content": json.dumps(random.choice(follow_up_messages))
        }
        
        st.session_state.messages.append(follow_up_message)
        DatabaseService.save_message(
            conn, get_user_id(), st.session_state.session_id,
            "assistant", follow_up_message["content"]
        )
        st.session_state.last_user_message_time = time.time()
        save_persistent_data()
        st.rerun()

    @staticmethod
    def _send_limit_message(conn: sqlite3.Connection):
        """Envia mensagem quando o limite de requisições é atingido."""
        limit_message = {
            "role": "assistant",
            "content": json.dumps({
                "text": "Por hoje chega, gato 😘 Volto amanhã com mais safadeza pra você! Mas você pode ver meus packs enquanto isso...",
                "cta": {"show": True, "label": "🎁 Ver Packs VIP", "target": "offers"}
            })
        }
        
        st.session_state.messages.append(limit_message)
        DatabaseService.save_message(
            conn, get_user_id(), st.session_state.session_id,
            "assistant", limit_message["content"]
        )
        save_persistent_data()
        st.rerun()

# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    """Função principal da aplicação."""
    try:
        # Inicializar banco de dados
        if 'db_conn' not in st.session_state:
            st.session_state.db_conn = DatabaseService.init_db()
        
        conn = st.session_state.db_conn
        
        # Inicializar sessão
        initialize_session()
        ChatService.initialize_session(conn)
        
        # Verificação de idade
        if not st.session_state.age_verified:
            UiService.age_verification()
            st.stop()
        
        # Setup da sidebar
        UiService.setup_sidebar()
        
        # Efeito de conexão
        if not st.session_state.connection_complete:
            UiService.show_call_effect()
            st.session_state.connection_complete = True
            save_persistent_data()
            st.rerun()
        
        # Tela de início do chat
        if not st.session_state.chat_started and st.session_state.current_page == "chat":
            ChatService._show_chat_start_screen()
            st.stop()
        
        # Roteamento de páginas
        if st.session_state.current_page == "home":
            NewPages.show_home_page()
        elif st.session_state.current_page == "gallery":
            UiService.show_gallery_page()
        elif st.session_state.current_page == "offers":
            NewPages.show_offers_page()
        else:  # chat
            UiService.enhanced_chat_ui(conn)
        
        # Salvar dados persistentes
        save_persistent_data()
        
    except Exception as e:
        logger.error(f"Erro na aplicação principal: {e}")
        st.error("Ocorreu um erro inesperado. Por favor, recarregue a página.")

# Função auxiliar para tela de início do chat
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
        
        if st.button("💋 Iniciar Conversa", type="primary", use_container_width=True):
            st.session_state.chat_started = True
            save_persistent_data()
            st.rerun()

# Adicionar função auxiliar ao ChatService
ChatService._show_chat_start_screen = _show_chat_start_screen

if __name__ == "__main__":
    main()

