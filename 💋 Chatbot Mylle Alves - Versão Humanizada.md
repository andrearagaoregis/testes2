# 💋 Chatbot Mylle Alves - Versão Humanizada

## 🚀 Sobre o Projeto

Este é um chatbot premium totalmente humanizado para conteúdo adulto, desenvolvido com Streamlit e IA avançada. O sistema oferece uma experiência de conversa natural e envolvente com múltiplas funcionalidades.

## ✨ Funcionalidades Principais

### 🤖 IA Humanizada
- **Personalidade Dinâmica**: Diferentes personas baseadas no horário do dia
- **Análise Emocional**: Detecção de sentimentos nas mensagens do usuário
- **Respostas Contextuais**: IA treinada para conversas naturais e envolventes
- **Sistema de Aprendizado**: Perfil do usuário evolui com as interações

### 🎨 Interface Premium
- **Design Moderno**: Gradientes roxo/rosa com animações suaves
- **Responsivo**: Funciona perfeitamente em desktop e mobile
- **Navegação Intuitiva**: Sidebar com acesso rápido a todas as funcionalidades
- **Efeitos Visuais**: Animações e transições profissionais

### 💬 Sistema de Chat Avançado
- **Mensagens de Áudio**: Player integrado para mensagens de voz
- **Chat Inteligente**: Respostas baseadas no contexto da conversa
- **Estatísticas em Tempo Real**: Contador de mensagens, áudios e interações
- **Follow-up Automático**: Sistema detecta usuários inativos

### 🛍️ E-commerce Integrado
- **3 Packs VIP**: TARADINHA, MOLHADINHA, SAFADINHA
- **Sistema de Ofertas**: Descontos dinâmicos e promoções especiais
- **Galeria Preview**: Amostras do conteúdo exclusivo
- **Checkout Integrado**: Links diretos para pagamento

### 🔒 Segurança e Privacidade
- **Verificação de Idade**: Tela obrigatória para maiores de 18 anos
- **Banco de Dados Local**: SQLite para armazenamento seguro
- **Sessões Isoladas**: Cada usuário tem sua própria sessão
- **Rate Limiting**: Controle de spam e uso excessivo

## 🛠️ Instalação e Uso

### Pré-requisitos
- Python 3.11+
- pip

### Instalação
```bash
# Clone o repositório
git clone [seu-repositorio]
cd chatbot-mylle

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run chatbot_humanized.py
```

### Configuração
1. A aplicação roda na porta 8501 por padrão
2. O banco de dados SQLite é criado automaticamente
3. Acesse via navegador: `http://localhost:8501`

## 📁 Estrutura do Projeto

```
chatbot-mylle/
├── chatbot_humanized.py    # Código principal da aplicação
├── requirements.txt        # Dependências do projeto
├── README.md              # Documentação
├── test_results.md        # Relatório de testes
└── database/              # Banco de dados SQLite (criado automaticamente)
```

## 🎯 Funcionalidades Técnicas

### Classes Principais
- **Config**: Configurações e constantes
- **DatabaseService**: Gerenciamento do banco de dados
- **ApiService**: Integração com IA (Gemini)
- **DynamicPersonality**: Sistema de personalidades
- **EmotionalIntelligence**: Análise de sentimentos
- **LearningEngine**: Aprendizado do usuário
- **CTAEngine**: Sistema de call-to-action
- **UiService**: Interface do usuário
- **ChatService**: Lógica do chat
- **NewPages**: Páginas da aplicação

### Banco de Dados
- **Tabela messages**: Histórico de conversas
- **Tabela user_profiles**: Perfis dos usuários
- **Tabela user_interactions**: Estatísticas de uso

## 🚀 Deploy

### Streamlit Cloud
1. Faça upload do código para GitHub
2. Conecte com Streamlit Cloud
3. Configure as variáveis de ambiente se necessário

### Servidor Local
```bash
streamlit run chatbot_humanized.py --server.port 8501 --server.address 0.0.0.0
```

## 🔧 Personalização

### Modificar Personalidades
Edite a classe `DynamicPersonality` para adicionar novas personas:

```python
def get_current_persona(self):
    # Adicione suas próprias personas aqui
    pass
```

### Alterar Respostas da IA
Modifique o método `get_intelligent_response` na classe `ApiService`:

```python
def get_intelligent_response(self, user_input, user_id, conversation_history):
    # Customize as respostas aqui
    pass
```

### Configurar Pagamentos
Atualize os links de checkout na classe `Config`:

```python
CHECKOUT_TARADINHA = "seu-link-de-pagamento"
CHECKOUT_MOLHADINHA = "seu-link-de-pagamento"
CHECKOUT_SAFADINHA = "seu-link-de-pagamento"
```

## 📊 Monitoramento

O sistema inclui:
- Logs automáticos de todas as interações
- Estatísticas de uso em tempo real
- Análise de sentimentos dos usuários
- Métricas de conversão

## 🆘 Suporte

Para suporte técnico ou dúvidas:
1. Verifique os logs do Streamlit
2. Consulte a documentação do código
3. Teste em ambiente local primeiro

## 📝 Licença

Este projeto é proprietário e destinado apenas para uso autorizado.

---

**Desenvolvido com 💜 para uma experiência premium de chat adulto**

