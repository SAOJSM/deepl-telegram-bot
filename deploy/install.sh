#!/usr/bin/env bash
# ==============================================================
# DeepL Telegram Bot - Ubuntu 20.04+ 一鍵安裝與部屬腳本
# ==============================================================

set -e

echo "=========================================================="
echo "  DeepL Telegram Bot 一鍵安裝程式 (Ubuntu 20.04 LTS+)"
echo "=========================================================="

# 確保以具備 sudo 權限執行或一般使用者執行
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CURRENT_USER="$(whoami)"

echo "專案路徑: ${PROJECT_DIR}"
echo "執行使用者: ${CURRENT_USER}"

# 1. 安裝系統依賴
echo ""
echo "[1/4] 更新套件清單並安裝 Python 3 虛擬環境套件..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv

# 2. 建立 Python 虛擬環境
echo ""
echo "[2/4] 建立專屬 Python 虛擬環境 (.venv)..."
if [ ! -d "${PROJECT_DIR}/.venv" ]; then
    python3 -m venv "${PROJECT_DIR}/.venv"
    echo "虛擬環境已建立。"
else
    echo "虛擬環境已存在，跳過建立步驟。"
fi

# 3. 安裝 Python 依賴
echo ""
echo "[3/4] 安裝專案依賴套件 (requirements.txt)..."
"${PROJECT_DIR}/.venv/bin/pip" install --upgrade pip
"${PROJECT_DIR}/.venv/bin/pip" install -r "${PROJECT_DIR}/requirements.txt"

# 檢查設定檔
if [ ! -f "${PROJECT_DIR}/config.ini" ]; then
    echo "未發現 config.ini，從 config.ini.example 複製..."
    cp "${PROJECT_DIR}/config.ini.example" "${PROJECT_DIR}/config.ini"
fi

# 4. 註冊 systemd 服務
echo ""
echo "[4/4] 設定 systemd 系統背景守護服務 (deepl-bot.service)..."

SERVICE_FILE="/etc/systemd/system/deepl-bot.service"

sudo bash -c "cat <<EOF > ${SERVICE_FILE}
[Unit]
Description=DeepL Telegram Translation Bot Service
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/.venv/bin/python3 ${PROJECT_DIR}/bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable deepl-bot.service

echo ""
echo "=========================================================="
echo "✅ 安裝完成！"
echo ""
echo "⚠️  下一步操作："
echo "1. 請編輯設定檔填寫 Token 與 DeepL Key："
echo "   nano ${PROJECT_DIR}/config.ini"
echo ""
echo "2. 啟動機器人背景服務："
echo "   sudo systemctl start deepl-bot"
echo ""
echo "3. 檢查服務狀態與即時日誌："
echo "   sudo systemctl status deepl-bot"
echo "   journalctl -u deepl-bot -f"
echo "=========================================================="
