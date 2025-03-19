import pandas as pd
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler,
    filters
)

# تحميل ملفات البحث
main_file_path = 'NewBene.xlsx'
df_main = pd.read_excel(main_file_path)

# تعريف حالات المحادثة
ID_SEARCH = 1


def search_identity(id_number, data):
    id_number = str(id_number).strip()
    data['رقم هوية المقيم'] = data['رقم هوية المقيم'].astype(str).str.strip()
    result = data[data['رقم هوية المقيم'] == id_number]
    
    if not result.empty:
        result_text = f"*نتيجة البحث عن رقم الهوية:* \n\n"
        result_text += f"*رقم الهوية:* {result['رقم هوية المقيم'].values[0]}\n"
        result_text += f"*الاسم:* {result['اسم المقيم الحالي'].values[0]}\n"
        result_text += f"*جوال:* {result['جوال'].values[0]}\n"
        result_text += f"*عدد افراد الاسرة:* {result['عدد الأفراد'].values[0]}\n\n\n\n\n"
        result_text += f'''
        *
        السيد/ة {result['اسم المقيم الحالي'].values[0]} التوجه غدا الخميس من س9ص وحتى س 1م لاستلام طرد غذائي من بيت أبو عبد الله المشارفة (شرق ملعب الدرة ب100 متر  بدير البلح).
        إحضار الهوية و3 ش بدل مواصلات وكيس فارغ.
        ملاحظة : التسليم ليوم واحد فقط.
        *
        '''

    else:
        result_text = "*لست مستفيد الأن...انتظرنا بالأيام القادمة*"

    return result_text


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("أرسل لي رقم الهوية للبحث عنه هل انت مستفيد الأن")
    return ID_SEARCH


async def handle_id_search(update: Update, context: CallbackContext) -> int:
    id_number = update.message.text.strip()
    result = search_identity(id_number, df_main)
    
    # إرسال النتيجة للمستخدم
    await update.message.reply_text(result, parse_mode='Markdown')

    # إعادة طلب رقم الهوية
    await update.message.reply_text("أرسل لي رقم الهوية أخر للبحث عنه")
    return ID_SEARCH


def main():
    TOKEN = '7781667291:AAE7tEbFB4qbP28Fm1RCSoLEV3XnShHADkE'
    application = Application.builder().token(TOKEN).build()
    
    # تعريف المحادثة بحيث يكون خيار البحث عن رقم الهوية فقط
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ID_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id_search)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
