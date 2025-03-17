import pandas as pd
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler,
    filters
)

# تحميل ملفات البحث
file_path = 'مدينة الزهراء طوارئ.xlsx'
df = pd.read_excel(file_path)

previous_beneficiaries_file = 'كشف المستلمين الإجمالي.xlsx'
df_previous = pd.read_excel(previous_beneficiaries_file)

# تعريف حالات المحادثة
CHOOSING, ID_SEARCH, LIMIT_ID_SEARCH, PREVIOUS_BENEFICIARY_SEARCH = range(4)

# تحديد نطاق البحث داخل الكشف
START_ROW = 10
END_ROW = 50

# دالة البحث في جميع الصفوف
def search_identity(id_number, data):
    id_number = str(id_number).strip()
    data['رقم هوية المقيم'] = data['رقم هوية المقيم'].astype(str).str.strip()
    result = data[data['رقم هوية المقيم'] == id_number]
    
    if not result.empty:
        result_text = f"*نتيجة البحث عن رقم الهوية:* \n\n"
        result_text += f"*رقم الهوية:* {result['رقم هوية المقيم'].values[0]}\n"
        result_text += f"*الاسم:* {result['اسم المقيم الحالي'].values[0]}\n"
        result_text += f"*جوال:* {result['جوال'].values[0]}\n"
        result_text += f"*اسم الزوجة رباعي :* {result['اسم الزوجة تم رباعي '].values[0]}\n"
        result_text += f"*عدد افراد الاسرة:* {result['عدد افراد الاسرة'].values[0]}\n\n"
        result_text += f"*عنوان النزوح الحالي :* {result['عنوان النزوح الحالي'].values[0]}\n\n"
    else:
        result_text = "*لم يتم العثور على رقم الهوية في الكشف.*"

    return result_text


# دالة البحث في نطاق محدد
def search_identity_in_range(id_number):
    id_number = str(id_number).strip()
    df['رقم هوية المقيم'] = df['رقم هوية المقيم'].astype(str).str.strip()
    limited_df = df.iloc[START_ROW-1:END_ROW]
    result = limited_df[limited_df['رقم هوية المقيم'] == id_number]
    
    if not result.empty:
        result_text = f"*نتيجة البحث عن رقم الهوية ضمن المستفيدين* \n\n"
        result_text += f"*رقم الهوية:* {result['رقم هوية المقيم'].values[0]}\n"
        result_text += f"*الاسم:* {result['اسم المقيم الحالي'].values[0]}\n"
        result_text += f"*جوال:* {result['جوال'].values[0]}\n"
        result_text += f"*اسم الزوجة رباعي :* {result['اسم الزوجة تم رباعي '].values[0]}\n"
        result_text += f"*عدد افراد الاسرة:* {result['عدد افراد الاسرة'].values[0]}\n\n"
        result_text += f"*عنوان النزوح الحالي :* {result['عنوان النزوح الحالي'].values[0]}\n\n"
    else:
        result_text = "*نأسف، لست مدرجًا في كشف الدورة الحالية. انتظرنا في الأيام القادمة لتستفيد.*"

    return result_text


# دالة البحث في كشف المستفيدين سابقًا
def search_previous_beneficiaries(id_number):
    id_number = str(id_number).strip()
    df_previous['رقم الهوية'] = df_previous['رقم الهوية'].astype(str).str.strip()
    result = df_previous[df_previous['رقم الهوية'] == id_number]
    result = result[result['التوقيع'].astype(str).str.strip() != "nan"]
    
    if not result.empty:
        result_text = f"*نتيجة البحث في كشف المستفيدين سابقًا:* \n\n"
        result_text += f"*رقم الهوية:* {result['رقم الهوية'].values[0]}\n"
        result_text += f"*الاسم:* {result['الاسم'].values[0]}\n"
        result_text += f"*جوال:* {result['رقم الجوال'].values[0]}\n"
        result_text += f"*اسم الطرد :* {result['التوقيع'].values[0]}\n\n"
        result_text += f"*لقد استفدت بطرد في دورة شهر 3*\n"
    else:
        result_text = "*لم يتم العثور على رقم الهوية في كشف المستفيدين سابقًا.*"



async def show_options(update: Update):
    """إعادة عرض الخيارات بعد البحث"""
    await update.message.reply_text(
        "\nاختر إحدى الخيارات التالية:\n"
        "1️⃣ للاستعلام عن اسمك في الكشف العام\n"
        "2️⃣ للاستعلام عن إمكانية الاستفادة قريبًا\n"
        "3️⃣ للاستعلام عن اسمك في كشف المستفيدين سابقًا\n"
        "🔄 أرسل الرقم المناسب:"
    )


async def start(update: Update, context: CallbackContext) -> int:
    await show_options(update)
    return CHOOSING


async def choose_option(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text.strip()
    if user_choice == '1':
        await update.message.reply_text("أرسل لي رقم الهوية للبحث عنه في الكشف العام.")
        return ID_SEARCH
    elif user_choice == '2':
        await update.message.reply_text("أرسل لي رقم الهوية للبحث عنه مستفيد الآن أم لا.")
        return LIMIT_ID_SEARCH
    elif user_choice == '3':
        await update.message.reply_text("أرسل لي رقم الهوية للبحث عنه في كشف المستفيدين سابقًا.")
        return PREVIOUS_BENEFICIARY_SEARCH
    else:
        await update.message.reply_text("خيار غير صالح. اختر 1 أو 2 أو 3.")
        return CHOOSING


async def handle_id_search(update: Update, context: CallbackContext) -> int:
    id_number = update.message.text.strip()
    result = search_identity(id_number, df)
    await update.message.reply_text(result, parse_mode='Markdown')
    await show_options(update)
    return CHOOSING


async def handle_limit_id_search(update: Update, context: CallbackContext) -> int:
    id_number = update.message.text.strip()
    result = search_identity_in_range(id_number)
    await update.message.reply_text(result, parse_mode='Markdown')
    await show_options(update)
    return CHOOSING


async def handle_previous_beneficiary_search(update: Update, context: CallbackContext) -> int:
    id_number = update.message.text.strip()
    result = search_previous_beneficiaries(id_number)
    await update.message.reply_text(result, parse_mode='Markdown')
    await show_options(update)
    return CHOOSING


def main():
    TOKEN = '7781667291:AAE7tEbFB4qbP28Fm1RCSoLEV3XnShHADkE'
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_option)],
            ID_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id_search)],
            LIMIT_ID_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_limit_id_search)],
            PREVIOUS_BENEFICIARY_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_previous_beneficiary_search)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
