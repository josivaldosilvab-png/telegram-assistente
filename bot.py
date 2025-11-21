import os
import logging
import requests
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis de ambiente corretas
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise RuntimeError(
        "Você precisa definir TELEGRAM_TOKEN e GROQ_API_KEY no Render!"
    )

# Função para gerar respostas usando Groq (gratuito)
def gerar_resposta(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.1-8b-instant",  # modelo 100% gratuito
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Erro na API Groq: {e}")
        return "⚠️ Erro ao gerar resposta. Tente novamente."

# /start
def start(update, context):
    update.message.reply_text(
        "Olá! Sou seu assistente baseado no estilo Napoleon Hill. Como posso ajudar?"
    )

# /foco
def foco(update, context):
    update.message.reply_text("⏳ Iniciando ciclo de foco de 25 minutos...")
    time.sleep(1500)
    update.message.reply_text("🔔 Tempo concluído! Hora da pausa.")
    time.sleep(300)
    update.message.reply_text("💪 Retornando ao foco!")

# Resposta normal
def responder(update, context):
    mensagem = update.message.text
    resposta = gerar_resposta(mensagem)
    update.message.reply_text(resposta)

def main():
    logger.info("Iniciando o bot...")

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("foco", foco))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, responder))

    updater.start_polling()
    logger.info("Bot rodando!")
    updater.idle()

if __name__ == "__main__":
    main()
