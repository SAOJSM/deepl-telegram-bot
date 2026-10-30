"""
Telegram 翻譯機器人主程式 (bot.py)
整合 Telegram Bot API 與 DeepL 翻譯服務，支援自動語言偵測與長訊息切分。
相容 Ubuntu 20.04+ (Python 3.8+)。
"""

import sys
import time
import logging
import signal
import telebot
from telebot import types
import deepl

from config_manager import load_config, Config
from translator import DeepLTranslator

# 設定日誌格式
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DeepLBot")


def main():
    logger.info("啟動 DeepL Telegram 翻譯機器人...")

    # 1. 載入設定檔
    try:
        config: Config = load_config("config.ini")
        logger.info(f"設定檔載入成功。目標語言: {config.target_lang}, 源語言: {config.source_lang or '自動偵測 (AUTO)'}")
    except Exception as e:
        logger.critical(f"無法載入 config.ini: {e}")
        sys.exit(1)

    # 2. 初始化 DeepL Translator
    try:
        translator = DeepLTranslator(config)
    except Exception as e:
        logger.critical(f"無法初始化 DeepL 翻譯服務: {e}")
        sys.exit(1)

    # 3. 初始化 Telegram Bot
    try:
        # 使用多執行緒 (threaded=True) 提升訊息處理吞吐量
        bot = telebot.TeleBot(config.bot_token, parse_mode=None, threaded=True)
        bot_info = bot.get_me()
        logger.info(f"Telegram Bot 連線成功！機器人名稱: @{bot_info.username} (ID: {bot_info.id})")

        # 向 Telegram 官方註冊常用指令清單（聊天視窗左下角會出現 [/] 或 [Menu] 選單按鈕，點擊即可發送）
        try:
            bot_commands = [
                types.BotCommand("start", "🚀 啟動機器人並查看設定"),
                types.BotCommand("status", "📊 查詢 DeepL 額度用量與狀態"),
                types.BotCommand("myid", "🆔 查詢個人 Telegram User ID"),
                types.BotCommand("help", "📖 使用說明與功能介紹")
            ]
            bot.set_my_commands(bot_commands)
            logger.info("已成功向 Telegram 註冊常用指令選單！")
        except Exception as e:
            logger.warning(f"註冊指令選單時發生警告 (非致命): {e}")

    except Exception as e:
        logger.critical(f"無法連線至 Telegram Bot API: {e}")
        sys.exit(1)

    # 快捷內聯按鈕鍵盤
    def get_quick_buttons():
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_status = types.InlineKeyboardButton("📊 查詢額度 (/status)", callback_data="cmd_status")
        btn_myid = types.InlineKeyboardButton("🆔 我的 ID (/myid)", callback_data="cmd_myid")
        btn_help = types.InlineKeyboardButton("📖 使用說明 (/help)", callback_data="cmd_help")
        markup.add(btn_status, btn_myid)
        markup.add(btn_help)
        return markup

    # ------------------ 指令處理 ------------------

    @bot.message_handler(commands=["start"])
    def handle_start(message: types.Message):
        if not config.is_user_allowed(message.from_user.id):
            bot.reply_to(message, "⛔ 抱歉，您沒有使用此機器人的權限。")
            return

        welcome_text = (
            f"👋 您好，{message.from_user.first_name}！\n\n"
            "我是 **DeepL 智能翻譯機器人**。\n"
            "只要直接傳送任何文字或轉傳訊息給我，我將自動為您翻譯！\n\n"
            f"📌 **目前翻譯設定：**\n"
            f"• 來源語言：`{config.source_lang or '自動偵測 (AUTO)'}`\n"
            f"• 目標語言：`{config.target_lang}` (預設繁體中文)\n\n"
            "💡 **您可以直接點擊下方按鈕或透過左下角 [/] 選單發送指令：**"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=get_quick_buttons())

    @bot.message_handler(commands=["help"])
    def handle_help(message: types.Message):
        if not config.is_user_allowed(message.from_user.id):
            return

        help_text = (
            "📖 **使用說明**\n\n"
            "1. **直接翻譯**：傳送單字、句子、長文章，甚至程式註解或外語對話。\n"
            "2. **轉傳翻譯**：直接將其他群組或頻道的訊息轉傳至此，機器人會擷取文字自動翻譯。\n"
            "3. **自動切分**：若文章長度超過 Telegram 的 4096 字元限制，機器人會智慧分段依序回傳。\n"
            "4. **語言設定**：如需變更目標語言（例如改為簡體中文或日文），可直接修改 `config.ini` 中的 `target_lang` 並重啟服務。\n\n"
            "點擊下方按鈕或輸入 /status 可隨時查看 DeepL 當月翻譯用量！"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown", reply_markup=get_quick_buttons())

    @bot.message_handler(commands=["status"])
    def handle_status(message: types.Message):
        if not config.is_user_allowed(message.from_user.id):
            return

        bot.send_chat_action(message.chat.id, "typing")
        usage_info = translator.get_usage()
        status_text = (
            f"⚙️ **機器人運作狀態**：正常\n"
            f"🌐 **源語言設定**：`{config.source_lang or '自動偵測 (AUTO)'}`\n"
            f"🎯 **目標語言設定**：`{config.target_lang}`\n\n"
            f"{usage_info}"
        )
        bot.reply_to(message, status_text, parse_mode="Markdown", reply_markup=get_quick_buttons())

    @bot.message_handler(commands=["myid"])
    def handle_myid(message: types.Message):
        user_id = message.from_user.id
        reply = (
            f"您的 Telegram User ID 為：`{user_id}`\n\n"
            f"若需將此機器人設定為私人專用，可在 `config.ini` 的 `allowed_user_ids` 加入此 ID。"
        )
        bot.reply_to(message, reply, parse_mode="Markdown", reply_markup=get_quick_buttons())

    # ------------------ 內聯按鈕回調處理 ------------------

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call: types.CallbackQuery):
        user_id = call.from_user.id
        if not config.is_user_allowed(user_id):
            bot.answer_callback_query(call.id, "⛔ 您沒有使用權限。", show_alert=True)
            return

        if call.data == "cmd_status":
            bot.answer_callback_query(call.id, "正在查詢額度...")
            usage_info = translator.get_usage()
            status_text = (
                f"⚙️ **機器人運作狀態**：正常\n"
                f"🌐 **源語言設定**：`{config.source_lang or '自動偵測 (AUTO)'}`\n"
                f"🎯 **目標語言設定**：`{config.target_lang}`\n\n"
                f"{usage_info}"
            )
            bot.send_message(call.message.chat.id, status_text, parse_mode="Markdown", reply_markup=get_quick_buttons())

        elif call.data == "cmd_myid":
            bot.answer_callback_query(call.id)
            reply = (
                f"您的 Telegram User ID 為：`{user_id}`\n\n"
                f"若需將此機器人設定為私人專用，可在 `config.ini` 的 `allowed_user_ids` 加入此 ID。"
            )
            bot.send_message(call.message.chat.id, reply, parse_mode="Markdown", reply_markup=get_quick_buttons())

        elif call.data == "cmd_help":
            bot.answer_callback_query(call.id)
            help_text = (
                "📖 **使用說明**\n\n"
                "1. **直接翻譯**：傳送單字、句子、長文章，甚至程式註解或外語對話。\n"
                "2. **轉傳翻譯**：直接將其他群組或頻道的訊息轉傳至此，機器人會擷取文字自動翻譯。\n"
                "3. **自動切分**：長文章會智慧分段依序回傳。\n"
                "4. **語言設定**：可在 `config.ini` 更改目標語言設定。"
            )
            bot.send_message(call.message.chat.id, help_text, parse_mode="Markdown", reply_markup=get_quick_buttons())

    # ------------------ 訊息翻譯處理 ------------------

    @bot.message_handler(content_types=["text"])
    def handle_translation(message: types.Message):
        user_id = message.from_user.id

        # 權限檢查
        if not config.is_user_allowed(user_id):
            logger.warning(f"拒絕未授權使用者請求: {user_id} (@{message.from_user.username})")
            bot.reply_to(message, "⛔ 您沒有使用此機器人的權限。")
            return

        text = message.text.strip()
        if not text:
            return

        # 忽視以 / 開頭的無效指令
        if text.startswith("/"):
            return

        # 檢查每月額度安全保護線
        can_proceed, stop_reason, warning_note = translator.check_quota(len(text))
        if not can_proceed:
            logger.warning(f"使用者 [{user_id}] 觸發每月安全額度上限，已停止翻譯。")
            bot.reply_to(message, stop_reason, parse_mode="Markdown", reply_markup=get_quick_buttons())
            return

        # 顯示正在輸入狀態 (Typing...)
        try:
            bot.send_chat_action(message.chat.id, "typing")
        except Exception:
            pass

        start_time = time.time()
        logger.info(f"收到來自 [{user_id}] 的翻譯請求 (長度: {len(text)} 字元)")

        try:
            # 進行 DeepL 翻譯
            translated_text, detected_lang = translator.translate(text)
            elapsed = time.time() - start_time

            if not translated_text:
                bot.reply_to(message, "⚠️ 翻譯結果為空。")
                return

            # 是否顯示預警或語言提示
            prefix = f"{warning_note}\n\n" if warning_note else ""
            header = f"🌐 [{detected_lang} ➔ {config.target_lang}]\n\n" if (config.show_detected_lang and detected_lang) else ""

            full_reply = f"{prefix}{header}{translated_text}"

            # 切分超出長度限制的訊息
            chunks = translator.split_message(full_reply, max_length=4000)
            for idx, chunk in enumerate(chunks):
                if idx == 0:
                    bot.reply_to(message, chunk)
                else:
                    bot.send_message(message.chat.id, chunk)

            logger.info(f"翻譯完成 (耗時: {elapsed:.2f}s, 偵測語言: {detected_lang})")

        except deepl.QuotaExceededException:
            logger.error("DeepL 翻譯額度已用盡！")
            bot.reply_to(message, "⚠️ DeepL API 額度已用盡，請至 DeepL 官方控制台檢查用量。")
        except deepl.AuthorizationException:
            logger.error("DeepL API Key 認證失敗！")
            bot.reply_to(message, "❌ DeepL API Key 無效，請檢查伺服器 config.ini 設定。")
        except deepl.TooManyRequestsException:
            logger.warning("DeepL API 頻率過高 (Rate Limit)！")
            bot.reply_to(message, "⏳ 請求過於頻繁，請稍候片刻再試。")
        except Exception as e:
            logger.error(f"翻譯過程發生錯誤: {e}", exc_info=True)
            bot.reply_to(message, f"❌ 翻譯時發生錯誤：{str(e)}")

    # 4. 優雅終止訊號處理
    def shutdown_handler(signum, frame):
        logger.info("接收到終止訊號，準備安全停止 Telegram Bot...")
        bot.stop_polling()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # 5. 啟動無窮輪詢 (自動重連機制)
    logger.info("機器人啟動成功，開始監聽 Telegram 訊息...")
    bot.infinity_polling(timeout=20, long_polling_timeout=20)


if __name__ == "__main__":
    main()
