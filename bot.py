import os
import json
import time
import requests
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Pegando as credenciais das variáveis de ambiente
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPINFRA_API_KEY = os.environ.get("DEEPINFRA_API_KEY")
TASKS_FILE = "tasks.json"

if not TELEGRAM_TOKEN or not DEEPINFRA_API_KEY:
    raise RuntimeError("Defina as variáveis de ambiente TELEGRAM_TOKEN e DEEPINFRA_API_KEY")

# Utilities para tarefas locais (simples JSON)
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# Função que chama a API da DeepInfra
def ask_ai(prompt):
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPINFRA_API_KEY}"}
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 500
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # proteger caso o formato retorne diferente
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return str(data)

# Handlers de comandos
def start(update, context):
    update.message.reply_text(
        "Olá! Sou seu assistente diário.\n"
        "Use /hoje /tarefas /prioridades /resumo /nova <tarefa> /foco /meta"
    )

def hoje(update, context):
    tasks = load_tasks()
    prompt = f"Organize meu dia com base nessas tarefas: {tasks}"
    resposta = ask_ai(prompt)
    update.message.reply_text(resposta)

def resumo(update, context):
    tasks = load_tasks()
    resposta = ask_ai(f"Gere um resumo do meu dia considerando: {tasks}")
    update.message.reply_text(resposta)

def prioridades(update, context):
    tasks = load_tasks()
    resposta = ask_ai(f"Liste prioridades do dia com base nas tarefas: {tasks}")
    update.message.reply_text(resposta)

def nova(update, context):
    tarefa = " ".join(context.args)
    if not tarefa:
        update.message.reply_text("Use /nova <tarefa> para adicionar.")
        return
    tasks = load_tasks()
    tasks.append({"tarefa": tarefa, "feita": False, "criacao": datetime.utcnow().isoformat()})
    save_tasks(tasks)
    update.message.reply_text(f"Tarefa adicionada: {tarefa}")

def tarefas(update, context):
    tasks = load_tasks()
    if not tasks:
        update.message.reply_text("Nenhuma tarefa registrada.")
        return
    msg = "📋 Suas tarefas:\n"
    for i, t in enumerate(tasks):
        status = "✔️" if t.get("feita") else "❌"
        msg += f"{i+1}. {status} {t['tarefa']}\n"
    update.message.reply_text(msg)

def foco(update, context):
    update.message.reply_text("⏳ Modo foco Pomodoro iniciado: 25 minutos.")
    # Nota: sleep bloqueia; em deploy real, seria melhor agendar notificação
    time.sleep(1500)
    update.message.reply_text("🚨 Tempo de foco concluído! Faça uma pausa de 5 minutos.")

def meta(update, context):
    objetivo = " ".join(context.args)
    if not objetivo:
        update.message.reply_text("Use /meta <objetivo> para registrar uma meta.")
        return
    resposta = ask_ai(f"Divida esta meta em etapas: {objetivo}")
    update.message.reply_text(resposta)

def mensagem(update, context):
    pergunta = update.message.text
    resposta = ask_ai(pergunta)
    update.message.reply_text(resposta)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("hoje", hoje))
    dp.add_handler(CommandHandler("resumo", resumo))
    dp.add_handler(CommandHandler("prioridades", prioridades))
    dp.add_handler(CommandHandler("nova", nova))
    dp.add_handler(CommandHandler("tarefas", tarefas))
    dp.add_handler(CommandHandler("foco", foco))
    dp.add_handler(CommandHandler("meta", meta))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, mensagem))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

requirements.txt
python-telegram-bot==13.15
requests
