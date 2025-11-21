import os
import logging
import requests
import time

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Correto: pegar variáveis de ambiente pelo nome
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPINFRA_KEY = os.getenv("DEEPINFRA_API_KEY")

if not TELEGRAM_TOKEN or not DEEPINFRA_KEY:
    raise RuntimeError("Você precisa definir TELEGRAM_TOKEN e DEEPINFRA_API_KEY no Render!")

def gerar_resposta(prompt):
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPINFRA_KEY}"}

    data = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Erro na API DeepInfra: {e}")
        return "⚠️ Erro ao gerar resposta. Tente novamente."

def start(update, context):
    update.message.reply_text("Olá! Sou seu assistente baseado em Napoleon Hill. Como posso te ajudar hoje?")

def foco(update, context):
    update.message.reply_text("⏳ Iniciando ciclo de foco de 25 minutos...")
    time.sleep(1500)
    update.message.reply_text("🔔 Tempo concluído! Hora da pausa.")
    time.sleep(300)
    update.message.reply_text("💪 Retornando ao foco!")

def responder(update, context):
    pergunta = update.message.text
    resposta = gerar_resposta(pergunta)
    update.message.reply_text(resposta)

def main():
    logger.info("Iniciando o bot...")

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("foco", foco))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, responder))

    updater.start_polling()
    logger.info("Bot rodando com sucesso!")
    updater.idle()

if __name__ == "__main__":
    main()
