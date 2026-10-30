# DeepL Telegram 繁體中文智慧翻譯機器人 🤖🌐

[English](README_EN.md) | [繁體中文](README.md)

可在所有 Linux 系統中執行（最低配置需求 **Ubuntu 20.04 LTS+**）的 Telegram 自動翻譯機器人。基於官方 **DeepL API** 與 **Telegram Bot API**，提供高精準度、語意自然的翻譯服務。傳送任意語言的文字給機器人，即可自動偵測源語言並即時翻譯為**繁體中文 (Traditional Chinese)**。

---

## ✨ 核心特色

- 🔍 **源語言自動偵測 (Auto-Detect)**：無需手動切換來源，由 DeepL 神經網路模型自動辨識。
- 🇹🇼 **完美支援繁體中文 (`ZH-HANT`)**：採用 DeepL 官方標準繁體中文代碼，符合台灣/港澳閱讀習慣。
- ⚙️ **獨立設定檔 (`config.ini`)**：Bot Token、API Key、來源語言、目標語言完全模組化，隨改即用。
- ✂️ **智慧長文切分**：自動處理超過 Telegram 4096 字元上限的長篇文章，依段落無縫分批送達。
- 📊 **額度與狀態查詢**：內建 `/status` 指令，可直接在 Telegram 中檢視 DeepL 每月 50 萬字免費額度剩餘情況。
- 🛡️ **使用者白名單防護**：支援設定 `allowed_user_ids`，避免公開機器人被他人濫用消耗您的 DeepL 額度。
- 🐧 **廣泛相容所有 Linux 系統（最低需求 Ubuntu 20.04 LTS+）**：依賴套件輕量純淨，支援 Python 3.8 ~ 3.12+，永不產生依賴淘汰過舊問題。
- 🔄 **24/7 背景穩定運行**：提供 `systemd` 服務設定與 Docker 容器化兩種部署方案，具備故障自動重連與開機自啟。

---

## 📁 專案檔案結構

```text
.
├── config.ini            # 實際運行的設定檔 (需填入您的金鑰，已由 .gitignore 排除上傳)
├── config.ini.example    # 設定檔範本
├── config_manager.py     # 設定檔解析與驗證模組
├── translator.py         # DeepL API 封裝 (含長文分割、額度查詢)
├── bot.py                # Telegram Bot 主邏輯程式
├── requirements.txt      # 輕量相容依賴清單 (相容 Python 3.8+)
├── Dockerfile            # Docker 映像檔構建設定
├── docker-compose.yml    # Docker Compose 一鍵啟動設定
├── .gitignore            # Git 忽略設定 (保護敏感金鑰不上傳)
├── .dockerignore          # Docker 忽略設定 (避免敏感檔案打包進映像檔)
├── deploy/
│   ├── install.sh        # Linux / Ubuntu 一鍵自動化安裝腳本
│   └── deepl-bot.service # systemd 背景服務守護設定檔
├── README.md             # 說明文件 (繁體中文)
└── README_EN.md          # 說明文件 (English)
```

---

## 🔑 前置準備：獲取 API 金鑰

### 1. 取得 Telegram Bot Token
1. 在 Telegram 搜尋官方機器人 [@BotFather](https://t.me/BotFather) 並開始對話。
2. 發送 `/newbot`，依提示依序輸入機器人暱稱（Name）與使用者名稱（Username，必須以 `bot` 結尾）。
3. 成功後，BotFather 會給出一串 **HTTP API Token**（格式例如 `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`）。

### 2. 取得 DeepL API Key
1. 前往 [DeepL API 官方網站](https://www.deepl.com/pro-api) 註冊帳號。
2. 申請 **DeepL API Free** 方案（每月享有 500,000 字元免費翻譯額度）。
3. 進入帳號後台的「Account」頁面，複製 **Authentication Key for DeepL API**（Free 版金鑰通常以 `:fx` 結尾）。

---

## 🚀 部署指南 (支援所有 Linux 系統，最低需求 Ubuntu 20.04 LTS+)

### 方案 A：使用一鍵安裝腳本 (原生 Python 虛擬環境 + systemd)

本專案提供自動化腳本，適用於 Ubuntu / Debian 及相容的 Linux 發行版。腳本會自動安裝 `python3-venv`、建立專屬虛擬環境、安裝相依套件並註冊 systemd 服務。

1. **上傳或 Clone 專案至 Linux 伺服器**：
   ```bash
   cd /opt
   # 假設您將專案放置於 /opt/deepl-telegram-bot
   cd deepl-telegram-bot
   ```

2. **執行一鍵安裝腳本**：
   ```bash
   chmod +x deploy/install.sh
   ./deploy/install.sh
   ```

3. **編輯設定檔**：
   ```bash
   nano config.ini
   ```
   將您的 `bot_token` 與 `api_key` 貼上後儲存（Ctrl+O -> Enter -> Ctrl+X）。

4. **啟動機器人**：
   ```bash
   sudo systemctl start deepl-bot
   ```

5. **檢查運作狀態與即時日誌**：
   ```bash
   # 檢查運行狀態
   sudo systemctl status deepl-bot

   # 即時查看日誌
   journalctl -u deepl-bot -f
   ```

---

### 方案 B：使用 Docker Compose 部署 (跨平台通用)

如果您偏好使用 Docker，可以在任何支援 Docker 的 Linux、macOS 或 Windows 環境中運行，只需兩行指令即可啟動：

1. **建立並填寫 `config.ini`**：
   ```bash
   cp config.ini.example config.ini
   nano config.ini
   ```

2. **啟動容器**：
   ```bash
   docker compose up -d --build
   ```

3. **查看日誌**：
   ```bash
   docker compose logs -f
   ```

---

## ⚙️ `config.ini` 設定說明

```ini
[telegram]
# Telegram 機器人金鑰
bot_token = 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ

# 允許使用的 Telegram User ID（選填）
# 填寫您自己的 Telegram ID 可防止被他人盜用額度
# 可先在 Telegram 發送 /myid 查詢自己的 ID
# 留空則代表所有人皆可使用
allowed_user_ids = 12345678

[deepl]
# DeepL API 金鑰 (Free 版通常以 :fx 結尾)
api_key = your-deepl-api-key:fx

# 自訂 API 網址 (一般留空即可，程式會自動判斷 Free/Pro)
server_url = 

# 每月字數安全上限閾值（達到此字數時暫停翻譯，保留緩衝空間）
# 建議設定為 490000（預留 1 萬字作為安全緩衝，設為 0 則不限制）
monthly_limit = 490000

# 即將超過限額的警告百分比 (例如 90 代表達到 90% 時會在翻譯回覆中加入用量提醒；0 則不提醒)
warning_percent = 90

[translation]
# 源語言：AUTO 或留空表示自動偵測
source_lang = AUTO

# 目標語言：預設為繁體中文 (ZH-HANT)
# 若日後想翻譯成其他語言，可直接在此更換 (例如：EN-US, JA, KO)
target_lang = ZH-HANT

# 是否在回覆文字頂部標註偵測到的語言 (例如 [EN ➔ ZH-HANT])
show_detected_lang = true
```

> **修改設定後套用方法**：
> - systemd: `sudo systemctl restart deepl-bot`
> - Docker: `docker compose restart`

---

## 💬 機器人可用指令與點擊選單

本專案會自動向 Telegram 官方伺服器註冊指令選單，使用者進入聊天室後：
1. **左下角選單按鈕**：聊天輸入框左側會出現 `[/]` 或 `[Menu]` 按鈕，點擊即可彈出指令清單一鍵發送。
2. **訊息內聯快捷按鈕**：發送 `/start`、`/status` 或 `/help` 時，訊息下方均附帶互動按鈕，可直接在手機或電腦螢幕上點擊查詢。

| 指令 | 官方選單說明 | 功能效果 |
| :--- | :--- | :--- |
| `/start` | 🚀 啟動機器人並查看設定 | 顯示歡迎訊息、當前語言設定與快捷按鈕 |
| `/status` | 📊 查詢 DeepL 額度用量與狀態 | 即時查詢 **DeepL 50 萬字免費額度消耗比例**與安全保護線 |
| `/myid` | 🆔 查詢個人 Telegram User ID | 取得自己的 Telegram ID，便於設定白名單 |
| `/help` | 📖 使用說明與功能介紹 | 顯示功能介紹與使用指南 |

---

## 🛠️ 常用維護指令 (Linux systemd)

```bash
# 啟動服務
sudo systemctl start deepl-bot

# 停止服務
sudo systemctl stop deepl-bot

# 重啟服務
sudo systemctl restart deepl-bot

# 查看狀態
sudo systemctl status deepl-bot

# 開機自動啟動 (已預設啟用)
sudo systemctl enable deepl-bot

# 查看即時日誌
journalctl -u deepl-bot -f -n 50
```

---

## ❓ 常見問題 FAQ

**Q1：為什麼選擇 `pyTelegramBotAPI` 而不是 `python-telegram-bot 20+`？**  
A：Ubuntu 20.04 預設自帶 Python 3.8，而 `python-telegram-bot v21+` 強制要求 Python 3.9+。使用 `pyTelegramBotAPI` 不僅能在 Python 3.8 環境完美運行，且相依套件極小、記憶體占用極低（約 30MB），並內建自動重連與執行緒池，非常適合部署在 Ubuntu 20.04 輕量 VPS 上。

**Q2：DeepL 的繁體中文代碼是什麼？**  
A：DeepL 官方在 2024 年正式推出繁體中文支援，標準代碼為 `ZH-HANT`。在 `config.ini` 中設定 `target_lang = ZH-HANT` 即可獲得高質量的繁體中文翻譯。

**Q3：轉傳包含圖片或檔案的訊息可以翻譯嗎？**  
A：目前機器人專注於文字與訊息對話翻譯。若轉傳包含純文字的訊息，機器人均會即時翻譯。

**Q4：DeepL 每月 50 萬字額度是如何計算與重置的？需要手動設定重置嗎？**  
A：**不需要手動重置！** DeepL API 的用量是綁定在官方帳號的**帳單月週期**（例如您在 10 月 15 日註冊，則週期為每月 15 日到次月 15 日）。當達到您的重置日，DeepL 伺服器會**自動歸零**字數。每次機器人查詢 API，DeepL 都會回傳當前週期最新的真實字數，不會跨月錯亂。

**Q5：如何避免翻譯過量超過 50 萬字免費上限？**  
A：專案內建防超額保護機制：
1. **安全上限暫停 (`monthly_limit = 490000`)**：在達到 490,000 字（預留 10,000 字緩衝）時，機器人會主動攔截翻譯請求並傳送通知，防止額度見底或產生意外費用。
2. **用量預警提示 (`warning_percent = 90`)**：當達到 90%（450,000 字）時，回覆文字頂部會自動加上預警標籤，提醒您額度即將用盡。
3. **隨時查閱 (`/status`)**：點擊選單的 `/status` 即可隨時查看官方已用字數與剩餘安全額度。
