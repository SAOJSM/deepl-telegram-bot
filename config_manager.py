"""
設定檔管理模組 (config_manager.py)
讀取並驗證 config.ini 中的所有設定項目
"""

import os
import sys
import configparser
from typing import List, Optional

class Config:
    def __init__(self, config_path: str = "config.ini"):
        self.config_path = config_path
        self.parser = configparser.ConfigParser()
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"找不到設定檔: {config_path}！請參考 config.ini.example 建立並填寫設定。"
            )
            
        # 使用 utf-8 讀取設定檔
        self.parser.read(config_path, encoding="utf-8")
        
        # 讀取 Telegram 設定
        self.bot_token: str = self.get_str("telegram", "bot_token", required=True)
        raw_allowed_ids = self.get_str("telegram", "allowed_user_ids", default="")
        self.allowed_user_ids: List[int] = []
        if raw_allowed_ids.strip():
            for uid in raw_allowed_ids.split(","):
                clean_uid = uid.strip()
                if clean_uid.isdigit():
                    self.allowed_user_ids.append(int(clean_uid))

        # 讀取 DeepL 設定
        self.deepl_api_key: str = self.get_str("deepl", "api_key", required=True)
        self.deepl_server_url: Optional[str] = self.get_str("deepl", "server_url", default=None)
        if self.deepl_server_url and not self.deepl_server_url.strip():
            self.deepl_server_url = None

        # 每月額度保護設定 (預設上限 490,000 字元，留 1 萬字安全緩衝；90% 提示預警)
        self.monthly_limit: int = self.get_int("deepl", "monthly_limit", default=490000)
        self.warning_percent: int = self.get_int("deepl", "warning_percent", default=90)

        # 讀取 翻譯設定
        raw_source = self.get_str("translation", "source_lang", default="AUTO").strip().upper()
        # AUTO 或空字串均視為 None (DeepL 自動偵測)
        self.source_lang: Optional[str] = None if raw_source in ("", "AUTO", "NONE") else raw_source

        # 目標語言，預設為繁體中文 ZH-HANT
        self.target_lang: str = self.get_str("translation", "target_lang", default="ZH-HANT").strip().upper()
        # DeepL 官方標準: 繁體中文為 ZH-HANT, 簡體中文為 ZH 或 ZH-HANS
        if self.target_lang in ("ZH-TW", "ZH-HK", "TRADITIONAL CHINESE"):
            self.target_lang = "ZH-HANT"
        elif self.target_lang in ("ZH-CN", "SIMPLIFIED CHINESE"):
            self.target_lang = "ZH-HANS"

        # 顯示設定
        self.show_detected_lang: bool = self.get_bool("translation", "show_detected_lang", default=True)

    def get_str(self, section: str, key: str, default: Optional[str] = None, required: bool = False) -> str:
        try:
            val = self.parser.get(section, key).strip()
            if required and not val:
                raise ValueError(f"設定檔中 [{section}] -> {key} 不可為空！")
            return val
        except (configparser.NoSectionError, configparser.NoOptionError):
            if required:
                raise ValueError(f"設定檔缺少必要區塊或選項: [{section}] -> {key}")
            return default if default is not None else ""

    def get_int(self, section: str, key: str, default: int = 0) -> int:
        try:
            val = self.parser.get(section, key).strip()
            if not val:
                return default
            return int(val)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

    def get_bool(self, section: str, key: str, default: bool = False) -> bool:
        try:
            return self.parser.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

    def is_user_allowed(self, user_id: int) -> bool:
        """檢查該使用者是否有權限使用機器人 (若名單為空則允許所有人)"""
        if not self.allowed_user_ids:
            return True
        return user_id in self.allowed_user_ids


def load_config(config_path: str = "config.ini") -> Config:
    return Config(config_path)
