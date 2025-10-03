import os
import uuid
import logging
import tempfile
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! Send me some text and I'll return it as a PDF file."
    )

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if not text.strip():
        await update.message.reply_text("Please send some text to convert.")
        return

    # Create a unique temporary filename
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    filename = tmp.name
    tmp.close()  # FPDF will write to this path

    try:
        # Build PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Use multi_cell to wrap text
        pdf.multi_cell(0, 6, text)

        # Save to disk
        pdf.output(filename)

        # Send as document
        with open(filename, "rb") as doc:
            # Set a nicer filename for the user
            nice_name = f"telegram_text_{uuid.uuid4().hex[:8]}.pdf"
            await update.message.reply_document(document=doc, filename=nice_name)
    except Exception as e:
        logger.exception("Error creating/sending PDF")
        await update.message.reply_text("Sorry, something went wrong while making the PDF.")
    finally:
        # cleanup
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
