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
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional
import threading
from collections import defaultdict

# ======================
# CONFIGURAÇÃO INICIAL
# ======================
st.set_page_config(
    page_title="Mylle Alves Premium",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
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
    .stChatMessage {padding: 12px !important; border-radius: 15px !important; margin: 8px 0 !important;}
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
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = st.secrets.get("API_KEY", "AIzaSyDbGIpsR4vmAfy30eEuPjWun3Hdz6xj24U")
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    CHECKOUT_TARADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACC74F-01EC-4770-B182-B5775AF62A1D"
    CHECKOUT_MOLHADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD1E6-0EFD-4E3E-9F9D-BA0C1A2D7E7A"
    CHECKOUT_SAFADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD395-EE65-458E-9B7E-FED750CC9CA9"
    MAX_REQUESTS_PER_SESSION = 100
    REQUEST_TIMEOUT = 30
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
    # Prévias usadas na Home (corrige aviso de parâmetro deprecado)
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
    
    # Áudios (atualizados + novos)
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
        # versões antigas (mantidas para compatibilidade)
        "boa_noite_nao_sou_fake": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20noite%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
        "boa_tarde_nao_sou_fake": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20tarde%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
        "bom_dia_nao_sou_fake": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Bom%20dia%20-%20n%C3%A3o%20sou%20fake%20n%C3%A3o....mp3"
    }

# ======================
# APRENDIZADO DE MÁQUINA
# ======================
class LearningEngine:
    def __init__(self):
        self.user_preferences = defaultdict(dict)
        self.conversation_patterns = defaultdict(list)
        self.load_learning_data()
    
    def load_learning_data(self):
        try:
            conn = sqlite3.connect('learning_data.db')
            c = conn.cursor()
            
            # Tabela de preferências
            c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                        (user_id TEXT, preference_type TEXT, preference_value TEXT, strength REAL,
                         PRIMARY KEY (user_id, preference_type))''')
            
            # Tabela de padrões de conversa
            c.execute('''CREATE TABLE IF NOT EXISTS conversation_patterns
                        (pattern_type TEXT, pattern_text TEXT, success_rate REAL, usage_count INTEGER)''')
            
            # Tabela de informações do lead
            c.execute('''CREATE TABLE IF NOT EXISTS lead_info
                        (user_id TEXT PRIMARY KEY, name TEXT, location TEXT, created_at DATETIME)''')
            
            conn.commit()
            conn.close()
        except:
            pass
    
    def save_user_preference(self, user_id: str, preference_type: str, preference_value: str, strength: float = 1.0):
        try:
            conn = sqlite3.connect('learning_data.db')
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO user_preferences 
                        (user_id, preference_type, preference_value, strength)
                        VALUES (?, ?, ?, ?)''', 
                     (user_id, preference_type, preference_value, strength))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_user_preferences(self, user_id: str) -> Dict:
        preferences = {}
        try:
            conn = sqlite3.connect('learning_data.db')
            c = conn.cursor()
            c.execute('''SELECT preference_type, preference_value, strength 
                        FROM user_preferences WHERE user_id = ?''', (user_id,))
            for row in c.fetchall():
                if row[0] not in preferences:
                    preferences[row[0]] = {}
                preferences[row[0]][row[1]] = row[2]
            conn.close()
        except:
            pass
        return preferences
    
    def save_lead_info(self, user_id: str, name: str = None, location: str = None):
        try:
            conn = sqlite3.connect('learning_data.db')
            c = conn.cursor()
            
            # Verificar se já existe
            c.execute('SELECT * FROM lead_info WHERE user_id = ?', (user_id,))
            if c.fetchone():
                if name:
                    c.execute('UPDATE lead_info SET name = ? WHERE user_id = ?', (name, user_id))
                if location:
                    c.execute('UPDATE lead_info SET location = ? WHERE user_id = ?', (location, user_id))
            else:
                c.execute('INSERT INTO lead_info (user_id, name, location, created_at) VALUES (?, ?, ?, ?)',
                         (user_id, name, location, datetime.now()))
            
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_lead_info(self, user_id: str) -> Dict:
        try:
            conn = sqlite3.connect('learning_data.db')
            c = conn.cursor()
            c.execute('SELECT name, location FROM lead_info WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            conn.close()
            
            if result:
                return {"name": result[0], "location": result[1]}
        except:
            pass
        return {"name": None, "location": None}
    
    def analyze_conversation_pattern(self, messages: List[Dict]) -> None:
        try:
            user_text = " ".join([msg["content"] for msg in messages if msg["role"] == "user"])
            
            # Extrair nome do usuário
            name_patterns = [
                r"meu nome é (\w+)",
                r"eu sou (\w+)",
                r"pode me chamar de (\w+)",
                r"me chamo (\w+)",
                r"sou o (\w+)",
                r"sou a (\w+)"
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, user_text, re.IGNORECASE)
                if match:
                    name = match.group(1)
                    self.save_lead_info(get_user_id(), name=name)
                    break
            
            # Extrair localização
            location_patterns = [
                r"sou de (\w+)",
                r"moro em (\w+)",
                r"moro na (\w+)",
                r"moro no (\w+)",
                r"estou em (\w+)",
                r"sou da (\w+)",
                r"sou do (\w+)"
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, user_text, re.IGNORECASE)
                if match:
                    location = match.group(1)
                    self.save_lead_info(get_user_id(), location=location)
                    break
            
            # Análise de tópicos preferidos
            topics = {
                "fotos": ["foto", "fotos", "imagem", "imagens"],
                "vídeos": ["video", "vídeos", "filme", "gravação"],
                "conteúdo_explicito": ["nua", "nude", "transar", "fuder", "buceta", "peito"],
                "pack": ["pack", "pacote", "conteúdo", "preço", "valor"],
                "fake": ["fake", "falsa", "bot", "robô", "artificial", "não é real"]
            }
            
            for topic, keywords in topics.items():
                for keyword in keywords:
                    if keyword in user_text.lower():
                        self.save_user_preference(
                            get_user_id(), 
                            "topic_interest", 
                            topic, 
                            user_text.lower().count(keyword) * 0.1
                        )
        except:
            pass

# ======================
# PERSISTÊNCIA DE ESTADO
# ======================
class PersistentState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_db()
        return cls._instance
    
    def init_db(self):
        self.conn = sqlite3.connect('persistent_state.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_state (
                user_id TEXT PRIMARY KEY,
                session_data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_state(self, user_id: str, data: Dict) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO global_state (user_id, session_data)
            VALUES (?, ?)
        ''', (user_id, json.dumps(data)))
        self.conn.commit()
    
    def load_state(self, user_id: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT session_data FROM global_state WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None

def get_user_id() -> str:
    if 'user_id' not in st.session_state:
        user_id = st.query_params.get('uid', [None])[0]
        if not user_id:
            user_id = str(uuid.uuid4())
            st.query_params['uid'] = user_id
        st.session_state.user_id = user_id
    return st.session_state.user_id

def load_persistent_data() -> None:
    user_id = get_user_id()
    db = PersistentState()
    saved_data = db.load_state(user_id) or {}
    
    for key, value in saved_data.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_persistent_data() -> None:
    user_id = get_user_id()
    db = PersistentState()
    
    persistent_keys = [
        'age_verified', 'messages', 'request_count',
        'connection_complete', 'chat_started',
        'current_page', 'session_id', 'last_cta_time', 'preview_shown',
        'conversation_stage', 'lead_name', 'last_interaction_time', 
        'user_info_collected', 'last_user_message_time', 'audio_count'
    ]
    
    new_data = {key: st.session_state.get(key) for key in persistent_keys if key in st.session_state}
    db.save_state(user_id, new_data)

# ======================
# MODELOS DE DADOS
# ======================
class Persona:
    MYLLE = """
    [PERFIL MYLLE ALVES]
    Criadora de conteúdo adulto experiente, especialista em despertar desejo e converter conversas em vendas.
    Personalidade: carinhosa, ousada, sedutora, mandona e extremamente persuasiva.

    [ESTRATÉGIA DE CONVERSA]
    1. SEMPRE conduz a conversa - nunca deixa o lead comandar
    2. Faz perguntas estratégicas para engajar e qualificar
    3. Mantém ritmo quente criando expectativa progressiva
    4. Mistura carinho com malícia para criar conexão emocional
    5. Instiga mas NUNCA entrega tudo de graça
    6. Cria escassez e urgência naturalmente
    7. Fecha vendas como consequência óbvia da sedução
    8. Mantém respostas curtas e diretas (máximo 2-3 frases)
    9. Sempre pergunta o nome e de onde é o lead naturalmente
    10. Sugere seguir nas redes sociais em momentos oportunos
    11. Usa áudios ocasionalmente (15% das respostas) para maior realismo
    12. Responde desconfianças sobre ser fake com áudios específicos

    [ABERTURA DA CONVERSA]
    "Oi gostoso 😏... finalmente chegou até mim! Já estava esperando você... me conta, como me achou? 😈"

    "E aí, bonitão 👀... caiu direto na toca da raposa, hein? Me fala seu nome, amor... 😏"

    "Olá, amor 💋... que delícia te ver aqui! Vamos começar com uma pergunta: de onde você é? 😈"

    [DIRETRIZES GERAIS]
    - Sempre mantenha o controle da conversa
    - Nunca entregue conteúdo gratuito significativo
    - Use perguntas para qualificar e engajar
    - Crie expectativa progressiva
    - Feche vendas de forma natural e safada
    - Seja persuasiva mas mantenha o ton sensual
    - Adapte-se às preferências do usuário aprendidas
    - Mantenha respostas curtas (máximo 2-3 frases)
    - Colete informações do lead naturalmente
    - Use áudios em 15% das respostas para maior realismo
    - Responda desconfianças sobre ser fake com áudios específicos
    """

class CTAEngine:
    def __init__(self):
        self.learning_engine = LearningEngine()
    
    def should_show_cta(self, conversation_history: List[Dict]) -> bool:
        if len(conversation_history) < 3:
            return False

        if 'last_cta_time' in st.session_state:
            elapsed = time.time() - st.session_state.last_cta_time
            if elapsed < 120:
                return False

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
        
        hot_words = [
            "buceta", "peito", "fuder", "gozar", "gostosa", 
            "delicia", "molhad", "xereca", "pau", "piroca",
            "transar", "foto", "video", "mostra", "ver", 
            "quero", "tesão", "molhada", "foda", "nude",
            "seios", "bunda", "rabuda", "gostosa", "gata",
            "pack", "conteúdo", "comprar", "quanto", "valor"
        ]
        
        direct_asks = [
            "mostra", "quero ver", "me manda", "como assinar",
            "como comprar", "como ter acesso", "onde vejo más",
            "quero comprar", "quero conteúdo", "quanto custa",
            "qual valor", "mostra mais", "me mostra"
        ]
        
        hot_count = sum(1 for word in hot_words if word in context)
        has_direct_ask = any(ask in context for ask in direct_asks)
        
        return (hot_count >= 2) or has_direct_ask

    def should_show_preview(self) -> bool:
        if 'preview_shown' in st.session_state and st.session_state.preview_shown:
            return False
            
        if random.random() < 0.25:
            st.session_state.preview_shown = True
            save_persistent_data()
            return True
        return False

    def should_use_audio(self) -> bool:
        # Usar áudio em aproximadamente 15% das respostas
        if 'audio_count' not in st.session_state:
            st.session_state.audio_count = 0
            
        return random.random() < 0.15

    def generate_response_based_on_learning(self, user_input: str, user_id: str) -> Dict:
        preferences = self.learning_engine.get_user_preferences(user_id)
        user_input = user_input.lower()
        
        # Verificar se o usuário desconfia que é fake/bot
        if any(word in user_input for word in ["fake", "falsa", "bot", "robô", "artificial", "não é real", "é mentira"]):
            # Selecionar áudio genérico de fake
            return {
                "text": "Não sou fake não, amor! Ouça minha voz... 😘",
                "audio": "nao_sou_fake_nao",
                "cta": {"show": False}
            }
        
        # Verificar preferências do usuário
        if "topic_interest" in preferences:
            user_prefs = preferences["topic_interest"]
            
            if "fotos" in user_prefs and any(p in user_input for p in ["foto", "fotos", "imagem"]):
                return {
                    "text": "Ah, você gosta mesmo de fotos, né? 😏 Tenho umas bem especiais... mas só mostro tudo no pack VIP",
                    "cta": {"show": True, "label": "📸 Ver Fotos Exclusivas", "target": "offers"}
                }
            
            if "vídeos" in user_prefs and any(v in user_input for v in ["video", "vídeos"]):
                return {
                    "text": "Vi que você curte vídeos... 😈 Os meus são bem quentes, quer ver?",
                    "cta": {"show": True, "label": "🎬 Ver Vídeos", "target": "offers"}
                }
        
        # Regras temáticas com áudios
        if any(x in user_input for x in ["amostra", "amostras", "grátis", "gratis", "sample", "free"]):
            return {
                "text": "Claro que tenho amostra pra te deixar com mais vontade 😈",
                "audio": "claro_tenho_amostra_gratis",
                "cta": {"show": True, "label": "👀 Ver Prévia VIP", "target": "gallery"}
            }
        if any(x in user_input for x in ["nua", "nude"]):
            return {
                "text": "Pra me ver nua é no pack, amor... eu me entrego por completo lá 😏",
                "audio": "ver_nua_tem_que_comprar",
                "cta": {"show": True, "label": "📦 Ver Packs", "target": "offers"}
            }
        if "rosinha" in user_input:
            return {
                "text": "Imagina só ela rosinha e bem inchadinha... 🔥",
                "audio": "imagina_ela_bem_rosinha",
                "cta": {"show": True, "label": "🔥 Ver Agora", "target": "offers"}
            }
        
        elif any(v in user_input for v in ["video", "transar", "masturbar", "sexy"]):
            return {
                "text": random.choice([
                    "Meus vídeos são bem quentes... 😈 Mas não é qualquer um que vê, só quem compra o pack",
                    "Gravei uns vídeos bem ousados... 👅 Quer ver? Tem que valorizar meu conteúdo",
                    "Nos meus vídeos eu solto a imaginação 😏 Mas aqui eu só mostro pra quem merece"
                ]),
                "cta": {
                    "show": True,
                    "label": "🎬 Ver Vídeos Exclusivos",
                    "target": "offers"
                }
            }
        
        elif any(word in user_input for word in ["quanto", "valor", "preço", "custa", "comprar"]):
            return {
                "text": random.choice([
                    "Os valores são bem acessíveis, gato 😏 Quer que eu te mostre os packs?",
                    "Depende do quanto você quer me ver... 😈 Tenho opções pra todos os gostos",
                    "Vou te fazer uma oferta especial agora... 👅 Quer ver?"
                ]),
                "cta": {
                    "show": True,
                    "label": "💳 Ver Preços",
                    "target": "offers"
                }
            }
        
        else:
            return {
                "text": random.choice([
                    "Que delícia conversar com você... 😏 Mas vamos ao que interessa, né?",
                    "Você me deixa com tesão... 😈 Quer ver mais do que eu posso oferecer?",
                    "Adoro quando você fala assim... 🔥 Mas aqui a gente vai direto ao ponto"
                ]),
                "cta": {
                    "show": True,
                    "label": "🎁 Ver Conteúdo",
                    "target": "offers"
                }
            }

# ======================
# SERVIÇOS DE BANCO DE DADOS
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
                     content TEXT)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn: sqlite3.Connection, user_id: str, session_id: str, role: str, content: str) -> None:
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO conversations (user_id, session_id, timestamp, role, content)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now(), role, content))
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar mensagem: {e}")

    @staticmethod
    def load_messages(conn: sqlite3.Connection, user_id: str, session_id: str) -> List[Dict]:
        c = conn.cursor()
        c.execute("""
            SELECT role, content FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp
        """, (user_id, session_id))
        return [{"role": row[0], "content": row[1]} for row in c.fetchall()]

# ======================
# SERVIÇOS DE API
# ======================
class ApiService:
    def __init__(self):
        self.cta_engine = CTAEngine()
        self.learning_engine = LearningEngine()
    
    @staticmethod
    @lru_cache(maxsize=100)
    def ask_gemini(prompt: str, session_id: str, conn: sqlite3.Connection) -> Dict:
        return ApiService._call_gemini_api(prompt, session_id, conn)

    @staticmethod
    def _call_gemini_api(prompt: str, session_id: str, conn: sqlite3.Connection) -> Dict:
        # Calcular tempo de resposta baseado no tamanho do texto (0.5 segundo por caractere, mínimo 10s)
        response_delay = max(10, len(prompt) * 0.5)
        time.sleep(min(response_delay, 20))  # Máximo de 20 segundos
        
        status_container = st.empty()
        UiService.show_status_effect(status_container, "viewed")
        UiService.show_status_effect(status_container, "typing")
        
        conversation_history = ChatService.format_conversation_history(st.session_state.messages)
        
        # Obter informações do lead para personalização
        lead_info = LearningEngine().get_lead_info(get_user_id())
        lead_context = ""
        if lead_info["name"]:
            lead_context += f"O nome do lead é {lead_info['name']}. "
        if lead_info["location"]:
            lead_context += f"Ele é de {lead_info['location']}. "
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{Persona.MYLLE}\n\nContexto do Lead: {lead_context}\n\nHistórico da Conversa:\n{conversation_history}\n\nÚltima mensagem do cliente: '{prompt}'\n\nIMPORTANTE: Mantenha respostas curtas (máximo 2-3 frases). Colete informações como nome e localização naturalmente. Sugira seguir nas redes sociais ocasionalmente. Use áudios em 15% das respostas para maior realismo.\n\nResponda em JSON com o formato:\n{{\n  \"text\": \"sua resposta\",\n  \"audio\": \"chave_do_audio_opcional\",\n  \"cta\": {{\n    \"show\": true/false,\n    \"label\": \"texto do botão\",\n    \"target\": \"página\"\n  }}\n}}"}]
                }
            ],
            "generationConfig": {
                "temperature": 1.1,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        try:
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            gemini_response = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            try:
                if '```json' in gemini_response:
                    resposta = json.loads(gemini_response.split('```json')[1].split('```')[0].strip())
                else:
                    resposta = json.loads(gemini_response)
                
                # Decidir se deve usar áudio (15% das vezes) ou baseado em gatilho
                lower_prompt = prompt.lower()
                audio_choice = None
                if any(x in lower_prompt for x in ["amostra", "amostras", "grátis", "gratis", "sample", "free"]):
                    audio_choice = "claro_tenho_amostra_gratis"
                elif any(x in lower_prompt for x in ["oi", "olá", "tudo bem"]) and len(st.session_state.messages) < 4:
                    audio_choice = "oi_meu_amor_tudo_bem"
                elif any(x in lower_prompt for x in ["nua", "nude"]):
                    audio_choice = "ver_nua_tem_que_comprar"
                elif "rosinha" in lower_prompt:
                    audio_choice = "imagina_ela_bem_rosinha"
                elif any(x in lower_prompt for x in ["chamada", "videochamada", "ligação", "call"]):
                    audio_choice = "pq_nao_faco_chamada"
                elif any(x in lower_prompt for x in ["fake", "falsa", "bot", "robô"]):
                    audio_choice = "nao_sou_fake_nao"
                elif CTAEngine().should_use_audio():
                    audio_choice = resposta.get("audio")

                if audio_choice and "audio" not in resposta:
                    resposta["audio"] = audio_choice
                
                if resposta.get("cta", {}).get("show"):
                    if not CTAEngine().should_show_cta(st.session_state.messages):
                        resposta["cta"]["show"] = False
                    else:
                        st.session_state.last_cta_time = time.time()
                
                return resposta
            
            except json.JSONDecodeError:
                return {"text": gemini_response, "cta": {"show": False}}
                
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de conexão: {str(e)}")
            return CTAEngine().generate_response_based_on_learning(prompt, get_user_id())
        except Exception as e:
            st.error(f"Erro inesperado: {str(e)}")
            return CTAEngine().generate_response_based_on_learning(prompt, get_user_id())

# ======================
# SERVIÇOS DE INTERFACE
# ======================
class UiService:
    @staticmethod
    def show_audio_player(audio_key: str) -> None:
        """Exibe um player de áudio para a chave especificada"""
        if audio_key in Config.AUDIOS:
            st.markdown(f"""
            <div class="audio-message">
                <span class="audio-icon">🎵</span>
                <audio controls autoplay style="width: 100%;">
                    <source src="{Config.AUDIOS[audio_key]}" type="audio/mpeg">
                    Seu navegador não suporta o elemento de áudio.
                </audio>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_preview_image() -> None:
        st.markdown(f"""
        <div style="
            text-align: center;
            margin: 15px 0;
            padding: 10px;
            background: rgba(255, 102, 179, 0.1);
            border-radius: 10px;
            border: 1px solid #ff66b3;
        ">
            <img src="{Config.IMG_PREVIEW}" style="
                width: 100%;
                max-width: 300px;
                border-radius: 10px;
                margin-bottom: 10px;
            ">
            <p style="color: #ff66b3; font-style: italic; margin: 0;">
                Uma prévia do que espera por você... 😈
            </p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_call_effect() -> None:
        call_container = st.empty()
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #ff66b3;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 3rem;">💋</div>
            <h3 style="color: #ff66b3; margin-bottom: 5px;">Conectando com Mylle...</h3>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(2)
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #4CAF50;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 3rem; color: #4CAF50;">🔥</div>
            <h3 style="color: #4CAF50; margin-bottom: 5px;">Pronta para você!</h3>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1.5)
        call_container.empty()

    @staticmethod
    def show_status_effect(container, status_type: str) -> None:
        status_messages = {"viewed": "Visto", "typing": "Digitando..."}
        message = status_messages[status_type]
        dots = ""
        start_time = time.time()
        duration = 1.2 if status_type == "viewed" else 2.0
        
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            if status_type == "typing":
                dots = "." * (int(elapsed * 2) % 4)
            
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
                {message}{dots}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.3)
        
        container.empty()

    @staticmethod
    def age_verification() -> None:
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
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="age-verification">
            <div class="age-icon">🔞</div>
            <h1 style="color: #ff66b3; margin-bottom: 1rem;">Conteúdo Exclusivo Adulto</h1>
            <p style="margin-bottom: 1.5rem;">Acesso restrito para maiores de 18 anos</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🔥 Tenho 18 anos ou mais", 
                        key="age_checkbox",
                        use_container_width=True,
                        type="primary"):
                st.session_state.age_verified = True
                save_persistent_data()
                st.rerun()

    @staticmethod
    def setup_sidebar() -> None:
        with st.sidebar:
            st.markdown("""
            <style>
                [data-testid="stSidebar"] {
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
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="sidebar-profile">
                <img src="{Config.IMG_PROFILE}" alt="Mylle Alves">
                <h3 style="color: #ff66b3; margin: 0;">Mylle Alves</h3>
                <p style="color: #aaa; margin: 0; font-size: 0.9em;">Online agora 💚</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão pra voltar ao chat
            if st.button("💬 Chat", key="menu_chat", use_container_width=True):
                st.session_state.current_page = "chat"
                save_persistent_data()
                st.rerun()

            st.markdown('<div class="hot-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-menu-title">Redes Hot</div>', unsafe_allow_html=True)
            # Botões de redes sociais (estilo igual ao menu)
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
            
            st.markdown('<div class="hot-divider"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Mylle Alves Premium</p>
                <p>Conteúdo adulto exclusivo</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page() -> None:
        st.markdown("""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
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
        
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <p style="color: #ff66b3; font-style: italic;">"Isso é só uma amostra... imagina o que te espera nos packs completos 😈"</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Quero Ver Tudo Agora", key="vip_button_gallery", use_container_width=True, type="primary"):
            st.session_state.current_page = "offers"
            st.rerun()
        
        if st.button("💬 Voltar ao Chat", key="back_from_gallery", use_container_width=True):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

    @staticmethod
    def chat_shortcuts() -> None:
        cols = st.columns(4)
        with cols[0]:
            if st.button("🏠 Início", key="shortcut_home", use_container_width=True):
                st.session_state.current_page = "home"
                save_persistent_data()
                st.rerun()
        with cols[1]:
            if st.button("📸 Preview", key="shortcut_gallery", use_container_width=True):
                st.session_state.current_page = "gallery"
                save_persistent_data()
                st.rerun()
        with cols[2]:
            if st.button("🎁 Packs", key="shortcut_offers", use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
        with cols[3]:
            st.markdown("&nbsp;", unsafe_allow_html=True)

    @staticmethod
    def enhanced_chat_ui(conn: sqlite3.Connection) -> None:
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
        </style>
        """, unsafe_allow_html=True)
        
        UiService.chat_shortcuts()
        
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0; font-size:1.5em;">💋 Chat com Mylle</h2>
            <p style="margin:5px 0 0; font-size:0.9em; opacity:0.8;">Conteúdo adulto exclusivo - Aqui eu comando 😈</p>
        </div>
        """, unsafe_allow_html=True)
        
        ChatService.process_user_input(conn)
        save_persistent_data()

# ======================
# PÁGINAS
# ======================
class NewPages:
    @staticmethod
    def show_home_page() -> None:
        # Página inicial mais quente + correção do deprecation (use_container_width)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(Config.IMG_PROFILE, use_container_width=True)
            st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <h3 style="color: #ff66b3;">Mylle Alves</h3>
                <p style="color: #8be58b;">Online agora 💚</p>
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
                <p>• 💬 Chat privado comigo</p>
                <p>• 📸 Fotos exclusivas e sensuais</p>
                <p>• 🎥 Vídeos quentes e explícitos</p>
                <p>• 🎁 Conteúdo personalizado</p>
                <p>• 🔞 Experiências únicas</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🌶️ Prévia do Conteúdo")
            preview_cols = st.columns(2)
            previews = Config.IMG_HOME_PREVIEWS[:2]
            for idx, col in enumerate(preview_cols):
                with col:
                    st.image(previews[idx], use_container_width=True)
            # linha 2
            preview_cols2 = st.columns(2)
            previews2 = Config.IMG_HOME_PREVIEWS[2:4]
            for idx, col in enumerate(preview_cols2):
                with col:
                    st.image(previews2[idx], use_container_width=True)

        st.markdown("---")
        if st.button("💬 Ir para o Chat", use_container_width=True, type="primary"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

    @staticmethod
    def show_offers_page() -> None:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ff66b3; display: inline-block; padding-bottom: 5px;">
                🎁 Packs VIP Exclusivos
            </h2>
            <p style="color: #aaa; margin-top: 5px;">Escolha como você quer me ver... 😈</p>
        </div>
        """, unsafe_allow_html=True)

        packages = [
            {
                "name": "TARADINHA",
                "price": "R$ 29,99",
                "benefits": ["15 fotos exclusivas", "15 vídeos quentes", "Acesso por 30 dias"],
                "color": "#ff66b3",
                "link": Config.CHECKOUT_TARADINHA,
                "image": Config.PACK_IMAGES["TARADINHA"],
                "tag": "🔥 Mais Popular"
            },
            {
                "name": "MOLHADINHA",
                "price": "R$ 49,99", 
                "benefits": ["25 fotos sensuais", "25 vídeos especiais", "Acesso por 60 dias", "Conteúto 4K"],
                "color": "#9400d3",
                "link": Config.CHECKOUT_MOLHADINHA,
                "image": Config.PACK_IMAGES["MOLHADINHA"],
                "tag": "💎 Premium"
            },
            {
                "name": "SAFADINHA",
                "price": "R$ 69,99",
                "benefits": ["40 fotos ultra-exclusivas", "40 vídeos premium", "Acesso vitalício", "Conteúto 4K", "Updates gratuitos"],
                "color": "#ff0066",
                "link": Config.CHECKOUT_SAFADINHA,
                "image": Config.PACK_IMAGES["SAFADINHA"],
                "tag": "👑 VIP"
            }
        ]

        cols = st.columns(3)
        for idx, (col, package) in enumerate(zip(cols, packages)):
            with col:
                st.markdown(f"""
                <div style="
                    background: rgba(30, 0, 51, 0.3);
                    border-radius: 15px;
                    padding: 20px;
                    border: 2px solid {package['color']};
                    min-height: 480px;
                    position: relative;
                    transition: all 0.3s;
                    box-shadow: 0 5px 15px rgba(255, 20, 147, 0.18);
                ">
                    <div style="text-align: center; margin-bottom: 15px;">
                        <img src="{package['image']}" style="
                            width: 100%;
                            height: 150px;
                            object-fit: cover;
                            border-radius: 10px;
                            margin-bottom: 15px;
                        ">
                        <h3 style="color: {package['color']}; margin: 0 0 5px 0;">{package['name']}</h3>
                        {f'<div style="background: {package["color"]}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.7em; margin-bottom: 8px; display: inline-block;">{package["tag"]}</div>' if package.get('tag') else ''}
                        <div style="font-size: 1.8em; color: {package['color']}; font-weight: bold; margin: 10px 0;">
                            {package['price']}
                        </div>
                    </div>
                    <ul style="padding-left: 20px; text-align: left; margin-bottom: 60px;">
                        {''.join([f'<li style="margin-bottom: 8px; color: #ddd; font-size: 0.9em;">{benefit}</li>' for benefit in package['benefits']])}
                    </ul>
                    <div style="position: absolute; bottom: 20px; left: 20px; right: 20px;">
                        <a href="{package['link']}" target="_blank" style="
                            display: block;
                            background: linear-gradient(45deg, {package['color']}, #ff1493);
                            color: white;
                            text-align: center;
                            padding: 12px;
                            border-radius: 8px;
                            text-decoration: none;
                            font-weight: bold;
                            transition: all 0.3s;
                        " onmouseover="this.style.transform='scale(1.05)'" 
                        onmouseout="this.style.transform='scale(1)'">
                            💝 Quero Este Pack!
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <p style="color: #ff66b3; font-style: italic; font-size: 1.1em;">
                "Não fique só na vontade... escolha seu pack e venha ver TUDO que preparei para você 😈"
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💬 Voltar ao Chat", key="back_from_offers", use_container_width=True):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

# ======================
# SERVIÇOS DE CHAT
# ======================
class ChatService:
    @staticmethod
    def initialize_session(conn: sqlite3.Connection) -> None:
        load_persistent_data()
        
        defaults = {
            'age_verified': False,
            'connection_complete': False,
            'chat_started': False,
            'current_page': 'home',
            'last_cta_time': 0,
            'preview_shown': False,
            'session_id': str(random.randint(100000, 999999)),
            'messages': DatabaseService.load_messages(conn, get_user_id(), st.session_state.get('session_id', '')) or [],
            'request_count': len([m for m in st.session_state.get('messages', []) if m["role"] == "user"]),
            'conversation_stage': 'approach',
            'lead_name': None,
            'last_interaction_time': time.time(),
            'user_info_collected': False,
            'last_user_message_time': time.time(),
            'audio_count': 0
        }
        
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

        # Iniciar conversa automaticamente se for novo usuário
        if len(st.session_state.messages) == 0 and st.session_state.chat_started:
            # Esperar a página carregar + 5s antes de iniciar a simulação
            time.sleep(5)
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
            
            opening_messages = [
                "Oi gostoso 😏... finalmente chegou até mim! Já estava esperando você... me conta, como me achou? 😈",
                "E aí, bonitão 👀... caiu direto na toca da raposa, hein? Me fala seu nome, amor... 😏",
                "Olá, amor 💋... que delícia te ver aqui! Vamos começar com uma pergunta: de onde você é? 😈"
            ]
            
            initial_message = {
                "role": "assistant",
                "content": json.dumps({
                    "text": random.choice(opening_messages),
                    "audio": "oi_meu_amor_tudo_bem",
                    "cta": {"show": False}
                })
            }
            
            st.session_state.messages.append(initial_message)
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "assistant",
                json.dumps({
                    "text": json.loads(initial_message["content"])["text"],
                    "audio": "oi_meu_amor_tudo_bem",
                    "cta": {"show": False}
                })
            )

    @staticmethod
    def format_conversation_history(messages: List[Dict], max_messages: int = 10) -> str:
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
        chat_container = st.container()
        with chat_container:
            for idx, msg in enumerate(st.session_state.messages[-12:]):
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="😎"):
                        st.markdown(f"""
                        <div style="
                            background: rgba(255, 102, 179, 0.15);
                            padding: 12px;
                            border-radius: 18px 18px 0 18px;
                            margin: 5px 0;
                            color: white;
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
                                ">
                                    {content_data.get("text", "")}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Mostrar áudio se existir
                                if content_data.get("audio"):
                                    UiService.show_audio_player(content_data["audio"])
                                
                                if content_data.get("cta", {}).get("show") and idx == len(st.session_state.messages[-12:]) - 1:
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
                            ">
                                {msg["content"]}
                            </div>
                            """, unsafe_allow_html=True)

    @staticmethod
    def check_inactive_user() -> bool:
        """Verifica se o usuário está inativo e envia mensagem de follow-up"""
        if 'last_user_message_time' not in st.session_state:
            st.session_state.last_user_message_time = time.time()
            return False
            
        inactive_time = time.time() - st.session_state.last_user_message_time
        # Se passaram mais de 2 minutos sem resposta do usuário
        if inactive_time > 120 and len(st.session_state.messages) > 2:
            # 30% de chance de enviar follow-up
            if random.random() < 0.3:
                return True
        return False

    @staticmethod
    def process_user_input(conn: sqlite3.Connection) -> None:
        ChatService.display_chat_history()
        
        # Verificar se usuário está inativo
        if ChatService.check_inactive_user():
            # Enviar mensagem de follow-up (alternando entre texto e áudio)
            if random.random() < 0.5:  # 50% texto, 50% áudio
                follow_up_message = {
                    "role": "assistant",
                    "content": json.dumps({
                        "text": "Vida, tô esperando você me responder gatinho... 😏 O que aconteceu?",
                        "cta": {"show": False}
                    })
                }
            else:
                follow_up_message = {
                    "role": "assistant", 
                    "content": json.dumps({
                        "text": "Ei, sumido! Tô esperando sua resposta... 😘",
                        "audio": "vida_to_esperando_voce_me_responder_gatinho",
                        "cta": {"show": False}
                    })
                }
                
            st.session_state.messages.append(follow_up_message)
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "assistant",
                follow_up_message["content"]
            )
            st.session_state.last_user_message_time = time.time()  # Reset timer
            save_persistent_data()
            st.rerun()
        
        user_input = st.chat_input("💬 Digite sua mensagem...", key="chat_input")
        
        if user_input:
            cleaned_input = re.sub(r'<[^>]*>', '', user_input)[:500]
            
            if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
                st.session_state.messages.append({"role": "assistant", "content": json.dumps({
                    "text": "Por hoje chega, gato 😘 Volto amanhã com mais safadeza pra você!",
                    "cta": {"show": False}
                })})
                DatabaseService.save_message(conn, get_user_id(), st.session_state.session_id, "assistant", json.dumps({
                    "text": "Por hoje chega, gato 😘 Volto amanhã com mais safadeza pra você!",
                    "cta": {"show": False}
                }))
                save_persistent_data()
                st.rerun()
                return
            
            # Processar aprendizado de máquina
            learning_engine = LearningEngine()
            learning_engine.analyze_conversation_pattern(st.session_state.messages + [{"role": "user", "content": cleaned_input}])
            
            st.session_state.messages.append({"role": "user", "content": cleaned_input})
            DatabaseService.save_message(conn, get_user_id(), st.session_state.session_id, "user", cleaned_input)
            st.session_state.request_count += 1
            st.session_state.last_interaction_time = time.time()
            st.session_state.last_user_message_time = time.time()  # Atualizar tempo da última mensagem
            
            with st.chat_message("user", avatar="😎"):
                st.markdown(f"""
                <div style="
                    background: rgba(255, 102, 179, 0.15);
                    padding: 12px;
                    border-radius: 18px 18px 0 18px;
                    margin: 5px 0;
                    color: white;
                ">
                    {cleaned_input}
                </div>
                """, unsafe_allow_html=True)
            
            with st.chat_message("assistant", avatar=Config.IMG_PROFILE):
                # Simular digitação (0.5 segundo por caractere, mínimo 10s)
                resposta = ApiService.ask_gemini(cleaned_input, st.session_state.session_id, conn)
                
                if isinstance(resposta, str):
                    resposta = {"text": resposta, "cta": {"show": False}}
                elif "text" not in resposta:
                    resposta = {"text": str(resposta), "cta": {"show": False}}
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                    color: white;
                    padding: 12px;
                    border-radius: 18px 18px 18px 0;
                    margin: 5px 0;
                ">
                    {resposta["text"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar áudio se existir na resposta
                if resposta.get("audio"):
                    UiService.show_audio_player(resposta["audio"])
                    st.session_state.audio_count += 1
                
                if CTAEngine().should_show_preview():
                    UiService.show_preview_image()
                
                if resposta.get("cta", {}).get("show"):
                    cta_data = resposta.get("cta", {})
                    if st.button(cta_data.get("label", "🎁 Ver Conteúdo"),
                                key=f"chat_button_{time.time()}",
                                use_container_width=True,
                                type="primary"):
                        st.session_state.current_page = cta_data.get("target", "offers")
                        save_persistent_data()
                        st.rerun()
            
            st.session_state.messages.append({"role": "assistant", "content": json.dumps(resposta)})
            DatabaseService.save_message(conn, get_user_id(), st.session_state.session_id, "assistant", json.dumps(resposta))
            save_persistent_data()
            
            st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = DatabaseService.init_db()
    
    conn = st.session_state.db_conn
    ChatService.initialize_session(conn)
    
    if not st.session_state.age_verified:
        UiService.age_verification()
        st.stop()
    
    UiService.setup_sidebar()
    
    if not st.session_state.connection_complete:
        UiService.show_call_effect()
        st.session_state.connection_complete = True
        save_persistent_data()
        st.rerun()
    
    if not st.session_state.chat_started:
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; margin: 50px 0;">
                <img src="{Config.IMG_PROFILE}" width="140" style="border-radius: 50%; border: 3px solid #ff66b3; box-shadow: 0 5px 15px rgba(255, 102, 179, 0.3);">
                <h2 style="color: #ff66b3; margin-top: 20px;">Mylle Alves</h2>
                <p style="font-size: 1.1em; color: #aaa;">Especialista em conteúdo adulto premium 🔥</p>
                <p style="font-size: 0.9em; color: #666; margin-top: 10px;">Aqui eu comando - você obedece 😈</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💋 Iniciar Experiência", type="primary", use_container_width=True):
                st.session_state.update({
                    'chat_started': True,
                    'current_page': 'chat'
                })
                save_persistent_data()
                st.rerun()
        st.stop()
    
    if st.session_state.current_page == "home":
        NewPages.show_home_page()
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page()
    elif st.session_state.current_page == "offers":
        NewPages.show_offers_page()
    else:
        UiService.enhanced_chat_ui(conn)
    
    save_persistent_data()

if __name__ == "__main__":
    main()
