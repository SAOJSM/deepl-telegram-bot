"""
DeepL 翻譯服務封裝模組 (translator.py)
整合官方 deepl SDK，處理翻譯請求、語言代碼、用量統計、每月額度保護與長文字分割。
"""

import time
import logging
from typing import Optional, Tuple, List
import deepl
from config_manager import Config

logger = logging.getLogger(__name__)

class DeepLTranslator:
    def __init__(self, config: Config):
        self.config = config
        self.cached_count: int = 0
        self.cached_limit: int = 500000
        self.last_usage_sync: float = 0.0
        self.sync_interval: float = 60.0  # 每 60 秒同步一次官方 API 最新用量
        self._init_translator()
        # 啟動時先同步一次用量
        self.sync_usage(force=True)

    def _init_translator(self):
        """初始化 DeepL Translator 實例"""
        kwargs = {}
        if self.config.deepl_server_url:
            kwargs["server_url"] = self.config.deepl_server_url

        try:
            self.translator = deepl.Translator(
                auth_key=self.config.deepl_api_key,
                **kwargs
            )
            logger.info("DeepL Translator 實例初始化成功。")
        except Exception as e:
            logger.error(f"初始化 DeepL Translator 失敗: {e}")
            raise

    def sync_usage(self, force: bool = False):
        """與 DeepL 官方伺服器同步目前帳單週期的使用量 (此 API 完全免費不扣字數)"""
        now = time.time()
        if not force and (now - self.last_usage_sync < self.sync_interval):
            return

        try:
            usage = self.translator.get_usage()
            if usage.character:
                self.cached_count = usage.character.count
                if usage.character.limit:
                    self.cached_limit = usage.character.limit
            self.last_usage_sync = now
            logger.debug(f"已同步 DeepL 用量: {self.cached_count}/{self.cached_limit}")
        except Exception as e:
            logger.warning(f"同步 DeepL 用量時發生警告: {e}")

    def check_quota(self, text_len: int) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        檢查額度是否允許本次翻譯。
        回傳: (是否允許翻譯, 停止原因訊息, 預警提示文字)
        """
        # 定期同步官方最新數據
        self.sync_usage()

        # 1. 檢查是否超出使用者設定的每月安全上限
        if self.config.monthly_limit > 0:
            effective_limit = self.config.monthly_limit
            if (self.cached_count + text_len) > effective_limit:
                reason = (
                    f"🛑 **已觸發每月安全上限保護，暫停翻譯！**\n\n"
                    f"• 當前已使用：`{self.cached_count:,}` 字\n"
                    f"• 本次欲翻譯：`{text_len:,}` 字\n"
                    f"• 安全停止線：`{effective_limit:,}` 字\n"
                    f"• 官方總上限：`{self.cached_limit:,}` 字\n\n"
                    f"💡 為保留字數緩衝，系統已自動攔截請求。"
                    f"如需繼續使用，可在伺服器 `config.ini` 調高 `monthly_limit` 並重啟服務。"
                )
                return False, reason, None

        # 2. 檢查官方硬性上限
        if self.cached_limit and (self.cached_count + text_len) > self.cached_limit:
            reason = (
                f"⚠️ **DeepL 官方每月額度已耗盡！**\n"
                f"• 已使用：`{self.cached_count:,}` / `{self.cached_limit:,}` 字\n\n"
                f"請等待下個帳單週期自動重置，或至 DeepL 官網升級方案。"
            )
            return False, reason, None

        # 3. 檢查預警提醒
        warning_note = None
        if self.config.warning_percent > 0 and self.cached_limit:
            pct = (self.cached_count / self.cached_limit) * 100
            if pct >= self.config.warning_percent:
                warning_note = f"⚠️ [用量提醒：已達 {pct:.1f}% ({self.cached_count:,}/{self.cached_limit:,} 字)]"

        return True, None, warning_note

    def translate(self, text: str) -> Tuple[str, Optional[str]]:
        """
        翻譯文字。
        回傳: (翻譯後的文字, 偵測到的來源語言代碼)
        """
        if not text or not text.strip():
            return "", None

        # 呼叫 DeepL API 進行翻譯
        result = self.translator.translate_text(
            text=text,
            source_lang=self.config.source_lang,
            target_lang=self.config.target_lang
        )

        detected_source_lang = result.detected_source_lang
        translated_text = result.text

        # 成功翻譯後，本地累加字數快取，保證高頻訊息時保護依然即時精確
        self.cached_count += len(text)

        return translated_text, detected_source_lang

    def get_usage(self, force_refresh: bool = True) -> str:
        """
        查詢 DeepL API 目前的額度使用情況與保護狀態
        """
        try:
            if force_refresh:
                self.sync_usage(force=True)

            limit_str = f"`{self.cached_limit:,}` 字" if self.cached_limit else "無上限"
            pct = (self.cached_count / self.cached_limit) * 100 if self.cached_limit else 0

            safe_limit_info = ""
            if self.config.monthly_limit > 0:
                remaining_safe = max(0, self.config.monthly_limit - self.cached_count)
                safe_limit_info = (
                    f"• 安全上限門檻：`{self.config.monthly_limit:,}` 字\n"
                    f"• 剩餘安全額度：`{remaining_safe:,}` 字\n"
                )

            return (
                f"📊 **DeepL 字數額度使用情況**\n"
                f"• 當月已使用：`{self.cached_count:,}` 字\n"
                f"• 官方總額度：{limit_str}\n"
                f"• 目前使用率：`{pct:.2f}%`\n"
                f"{safe_limit_info}"
                f"\nℹ️ *DeepL 伺服器會於每月的註冊帳單週期自動重置，無需手動重置。*"
            )
        except deepl.AuthorizationException:
            return "❌ DeepL API Key 無效，請檢查 config.ini 設定。"
        except Exception as e:
            logger.error(f"查詢 DeepL 用量失敗: {e}")
            return f"❌ 查詢額度失敗: {str(e)}"

    @staticmethod
    def split_message(text: str, max_length: int = 4000) -> List[str]:
        """
        將超出 Telegram 限制 (4096 字元) 的訊息分段切分
        以換行符號為優先斷點，避免截斷句子
        """
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = []
        current_len = 0

        lines = text.split("\n")
        for line in lines:
            line_len = len(line) + 1  # 包含 \n
            if current_len + line_len > max_length:
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_len = 0

                # 若單行即超過 max_length，則進行強制硬切
                while len(line) > max_length:
                    chunks.append(line[:max_length])
                    line = line[max_length:]

                if line:
                    current_chunk.append(line)
                    current_len = len(line) + 1
            else:
                current_chunk.append(line)
                current_len += line_len

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks
