from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import calendar

# Estados de la conversación
NOMBRE, EQUIPO, UBICACION, DIA, MES, SEM, DESCRIPCION, MEDIA, MENU = range(9)

# Token del bot y el ID del canal
TOKEN = '6992363677:AAEVNtqFtz3wPyNE-_POwHqd6Rc2b0oP_lo'
CHANNEL_ID = '-1002217255637'

# Función de inicio que pregunta por el nombre del usuario
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Nuevo Reporte', 'Salir']]
    await update.message.reply_text(
        '¡Bienvenido!\n\nPulsa o escribe "Nuevo Reporte" para informar sobre un fallo en un equipo📝\n\nPulsa o escribe "Salir" para cerrar el chat❌\n\n¿Qué te gustaría hacer?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENU

# Función para manejar la selección del menú
async def menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Nuevo Reporte':
        await update.message.reply_text(
            'Por favor, dime tu nombre para registrar el reporte.👤',
            reply_markup=ReplyKeyboardRemove()
        )
        return NOMBRE
    elif update.message.text == 'Salir':
        return await cancel(update, context)
    else:
        await update.message.reply_text('Selecciona una opción válida.')
        return MENU

# Pregunta sobre el equipo
async def ask_equipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['nombre'] = update.message.text
    await update.message.reply_text('¿Qué equipo está presentando problemas?💻 \n\nIndica si es Computadora de escritorio, Laptop, Router, etc.')
    return EQUIPO

# Pregunta sobre la ubicación del equipo
async def ask_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['equipo'] = update.message.text
    await update.message.reply_text('¿En qué ubicación del colegio está el equipo?📌 \n\n(Oficina, biblioteca, laboratorio, etc.)')
    return UBICACION

# Comienza el proceso de selección de la fecha Dia de semana
async def ask_semana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ubicacion'] = update.message.text
    days_of_week = [['Lunes', 'Martes', 'Miércoles'], ['Jueves', 'Viernes', 'Sábado', 'Domingo']]
    await update.message.reply_text('¿Cuándo ocurrió o se detectó la falla?🗓️. \n\nSelecciona o escribe el día de la semana:', reply_markup=ReplyKeyboardMarkup(days_of_week, one_time_keyboard=True))
    return SEM

#Guarda el dia de la semana y pregunta fecha
async def ask_dia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['sem'] = update.message.text
    days = [[str(i) for i in range(1, 8)], [str(i) for i in range(8, 15)], [str(i) for i in range(15, 22)], [str(i) for i in range(22, 29)], [str(i) for i in range(29, 32)]]
    await update.message.reply_text('Selecciona el día:', reply_markup=ReplyKeyboardMarkup(days, one_time_keyboard=True))
    return DIA

# Guarda el día y pregunta por el mes
async def ask_mes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dia'] = update.message.text
    months = [['Enero', 'Febrero', 'Marzo'], ['Abril', 'Mayo', 'Junio'], ['Julio', 'Agosto', 'Septiembre'], ['Octubre', 'Noviembre', 'Diciembre']]
    await update.message.reply_text('Selecciona el mes:', reply_markup=ReplyKeyboardMarkup(months, one_time_keyboard=True))
    return MES

# Guarda el mes y avanza a la descripción
async def ask_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['mes'] = update.message.text
    dia = context.user_data['dia']
    mes = context.user_data['mes']
    sem = context.user_data['sem']
    context.user_data['fecha'] = f"{sem} {dia} de {mes}"
    await update.message.reply_text('Para atender el reporte es necesario saber que ocurrió.\n\nPor favor, describe detalladamente la falla. (por escrito)')
    return DESCRIPCION

# Pregunta si quiere añadir una imagen o video
async def ask_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['descripcion'] = update.message.text
    reply_keyboard = [['Sí\n📷', 'No\n➡️']]
    await update.message.reply_text(
        '¿Quieres adjuntar una imagen o video de la falla?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MEDIA

# Maneja la respuesta para adjuntar media
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Sí\n📷':
        await update.message.reply_text(
            'Por favor, envía  ahora a este chat la imagen o video. 📷',
            reply_markup=ReplyKeyboardRemove()
        )
        return MEDIA
    else:
        # Limpia cualquier media anterior almacenada en el contexto
        context.user_data.pop('media', None)
        return await finish_report(update, context)

# Almacena la imagen o video y finaliza el reporte
async def handle_media_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['media'] = update.message
    return await finish_report(update, context)

# Finaliza la conversación y envía el reporte al canal
async def finish_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Construye el reporte
    report = (
        f"Nuevo reporte recibido de ➡️\t {context.user_data['nombre']}:\n\n"
        f"Equipo: {context.user_data['equipo']}\n"
        f"Ubicación: {context.user_data['ubicacion']}\n\n"
        f"Fecha de la Falla: {context.user_data['fecha']}\n\n"
        f"Descripción: \n{context.user_data['descripcion']}\n"
    )

    # Envía el reporte al canal
    await context.bot.send_message(chat_id=CHANNEL_ID, text=report)
    
    # Envía la imagen o video si se adjuntó
    if 'media' in context.user_data:
        media_message = context.user_data['media']
        if media_message.photo:
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=media_message.photo[-1].file_id)
        elif media_message.video:
            await context.bot.send_video(chat_id=CHANNEL_ID, video=media_message.video.file_id)

    # Confirma al usuario que su reporte fue enviado
    await update.message.reply_text('Gracias por tu reporte. Será atendido a la brevedad.✅', reply_markup=ReplyKeyboardRemove())

    # Regresa al menú principal
    return await chao(update, context)

# Maneja el comando /cancel para terminar la conversación
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operación cancelada. Para iniciar pulsa aquí 👉👉 /start.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def chao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Para iniciar pulsa aquí 👉👉 /start.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    # Crea la aplicación del bot
    application = Application.builder().token(TOKEN).build()

    # Definir el manejador de conversaciones
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_selection)],
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_equipo)],
            EQUIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ubicacion)],
            UBICACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_semana)],
            SEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_dia)],
            DIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mes)],
            MES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_descripcion)],
            DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_media)],
            MEDIA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_media),
                MessageHandler(filters.PHOTO | filters.VIDEO, handle_media_file),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Añadir el manejador de conversaciones al dispatcher
    application.add_handler(conv_handler)

    # Inicia el bot
    application.run_polling()

if __name__ == '__main__':
    main()
