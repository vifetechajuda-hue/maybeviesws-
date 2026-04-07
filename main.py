import os
import logging
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Token do bot (obtido das variáveis de ambiente)
BOT_TOKEN = "8564521988:AAGparPmW-4cipZkhs2WT58HV_s8ylSsRPc"

# Função para gerar visualizações em um link
async def generate_views(url: str, count: int):
    """
    Gera visualizações reais em um URL usando múltiplas requisições.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = asyncio.create_task(session.get(url, headers=headers, ssl=False))
            tasks.append(task)
        
        # Executa todas as tarefas simultaneamente
        await asyncio.gather(*tasks)
        return True

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia mensagem de boas-vindas com botões de opções."""
    keyboard = [
        [
            InlineKeyboardButton("1000 Views", callback_data="1000"),
            InlineKeyboardButton("5000 Views", callback_data="5000"),
        ],
        [
            InlineKeyboardButton("10000 Views", callback_data="10000"),
            InlineKeyboardButton("50000 Views", callback_data="50000"),
        ],
        [
            InlineKeyboardButton("Inserir Link", callback_data="input_link"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Bem-vindo ao Gerador de Views! 🚀\n\n"
        "Escolha uma opção abaixo ou insira seu link personalizado:",
        reply_markup=reply_markup
    )

# Manipulador para botões
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manipula cliques nos botões."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "input_link":
        await query.edit_message_text(text="Por favor, envie o link que você quer promover usando o comando /link URL")
        return
    
    # Se o usuário já forneceu um link, processa a solicitação
    if 'user_url' in context.user_data:
        view_count = int(query.data)
        url = context.user_data['user_url']
        
        await query.edit_message_text(text=f"Gerando {view_count} visualizações para {url}... Isso pode levar alguns segundos.")
        
        # Gera as visualizações
        success = await generate_views(url, view_count)
        
        if success:
            await query.edit_message_text(text=f"✅ Concluído! Foram geradas {view_count} visualizações para {url}")
        else:
            await query.edit_message_text(text="❌ Ocorreu um erro ao gerar as visualizações. Tente novamente.")
    else:
        # Pede ao usuário para fornecer um link primeiro
        keyboard = [
            [
                InlineKeyboardButton("1000 Views", callback_data="1000"),
                InlineKeyboardButton("5000 Views", callback_data="5000"),
            ],
            [
                InlineKeyboardButton("10000 Views", callback_data="10000"),
                InlineKeyboardButton("50000 Views", callback_data="50000"),
            ],
            [
                InlineKeyboardButton("Inserir Link", callback_data="input_link"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Por favor, forneça um link primeiro usando o comando /link URL",
            reply_markup=reply_markup
        )

# Comando para definir o link
async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Define o URL para o qual as visualizações serão geradas."""
    if not context.args:
        await update.message.reply_text("Por favor, forneça um URL após o comando. Exemplo: /link https://example.com")
        return
    
    url = context.args[0]
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    
    context.user_data['user_url'] = url
    
    keyboard = [
        [
            InlineKeyboardButton("1000 Views", callback_data="1000"),
            InlineKeyboardButton("5000 Views", callback_data="5000"),
        ],
        [
            InlineKeyboardButton("10000 Views", callback_data="10000"),
            InlineKeyboardButton("50000 Views", callback_data="50000"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Link definido: {url}\n\nAgora escolha quantas visualizações você deseja gerar:",
        reply_markup=reply_markup
    )

# Comando de ajuda
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de ajuda."""
    await update.message.reply_text(
        "Como usar o bot:\n\n"
        "/start - Inicia o bot e mostra as opções\n"
        "/link URL - Define o URL para o qual as visualizações serão geradas\n"
        "/help - Mostra esta mensagem de ajuda\n\n"
        "Após definir um link, basta clicar nos botões para gerar visualizações."
    )

def main() -> None:
    """Inicia o bot."""
    # Cria a aplicação
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Adiciona os manipuladores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("link", set_link))
    application.add_handler(CallbackQueryHandler(button))
    
    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()
