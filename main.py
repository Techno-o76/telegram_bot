import os
import uuid
import logging
import tempfile
import urllib.request
from fpdf import FPDF
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

# Font setup: DejaVuSans for Unicode support
FONT_PATH = "DejaVuSans.ttf"
if not os.path.exists(FONT_PATH):
    logger.info("Downloading DejaVuSans.ttf font...")
    url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
    urllib.request.urlretrieve(url, FONT_PATH)
    logger.info("Font downloaded successfully.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! 👋 Send me text with emojis or special characters, and I'll convert it to PDF."
    )

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if not text.strip():
        await update.message.reply_text("Please send some text to convert.")
        return

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    filename = tmp.name
    tmp.close()

    try:
        # Create PDF with Unicode font
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.set_font("DejaVu", size=12)

        # Preserve paragraphs
        for line in text.splitlines():
            if line.strip():
                pdf.multi_cell(0, 6, line)
            else:
                pdf.ln(6)

        pdf.output(filename)

        # Send PDF
        with open(filename, "rb") as doc:
            nice_name = f"telegram_text_{uuid.uuid4().hex[:8]}.pdf"
            await update.message.reply_document(document=doc, filename=nice_name)

    except Exception as e:
        logger.exception("Error creating/sending PDF")
        await update.message.reply_text("⚠️ Something went wrong while creating the PDF.")
    finally:
        try:
            os.remove(filename)
        except Exception:
            pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_pdf))

    logger.info("Bot starting (polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()
