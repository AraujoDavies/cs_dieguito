#pip install pyrogram
#pip install tgcrypto 
from pyrogram import Client, enums # para aceitar HTML
from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = Client(getenv('TELEGRAM_CLIENT'))
chat_id = getenv('TELEGRAM_CHAT_ID')

def enviar_no_telegram(chat_id, msg):
    " Enviando mensagem e salva o ID no banco"
    app.start() 
    app.send_message(chat_id, (f'{msg}'), parse_mode=enums.ParseMode.HTML)
    for message in app.get_chat_history(chat_id):
        id = message.id
        break
    app.stop()
    return id
# enviar_no_telegram(chat_id, msg)

async def resultado_da_entrada(chat_id, reply_msg_id, msg):
    """
        responde a msg de entrada com o resultado(green/red)
    """
    await app.start() 
    await app.send_message(chat_id, f'{msg}', reply_to_message_id=reply_msg_id)
    await app.stop()
# app.run(resultado_da_entrada(chat_id, reply_msg_id, msg))

# função assíncrona - informmações da msg
@app.on_message() # quando receber uma mensagem...
async def resposta(client, message): 
    print(message)

# app.run() # executa

def telegram_validation():
    app = Client(getenv('TELEGRAM_CLIENT'))
    id_cs = enviar_no_telegram(getenv('TELEGRAM_CHAT_ID'), 'Mensagem_test')
    app.run(resultado_da_entrada(getenv('TELEGRAM_CHAT_ID'), id_cs, 'TESTADO'))
    assert type(id_cs) == int
