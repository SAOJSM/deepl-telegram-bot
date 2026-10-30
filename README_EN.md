# DeepL Telegram Smart Translation Bot 🤖🌐

[English](README_EN.md) | [繁體中文](README.md)

> **Telegram translation bot powered by DeepL API with auto language detection and Traditional Chinese support.**

A Telegram automatic translation bot capable of running on all Linux distributions (minimum requirement: **Ubuntu 20.04 LTS+**). Powered by the official **DeepL API** and **Telegram Bot API**, it delivers high-accuracy, fluent, and context-aware translations. Simply send any text in any language to the bot, and it will automatically detect the source language and translate it into **Traditional Chinese (`ZH-HANT`)** (or any configured target language) in real time.

---

## ✨ Key Features

- 🔍 **Automatic Source Language Detection**: Powered by DeepL's neural network engine; no manual language selection is required.
- 🇹🇼 **Native Traditional Chinese Support (`ZH-HANT`)**: Leverages DeepL's official `ZH-HANT` target code for authentic phrasing.
- ⚙️ **Modular Configuration (`config.ini`)**: Easily configure Bot Token, API Key, source/target languages, and safety limits.
- ✂️ **Smart Long Message Splitting**: Automatically splits long articles exceeding Telegram's 4,096-character limit by paragraph, delivering seamless multi-part replies.
- 📊 **Quota & Status Tracking**: Built-in `/status` command allows checking real-time consumption against DeepL's 500,000 free monthly characters directly inside Telegram.
- 🛡️ **User Whitelist Protection**: Option to specify `allowed_user_ids` to keep your bot private and prevent unauthorized consumption of your DeepL quota.
- 🐧 **Broad Linux Compatibility (Minimum Ubuntu 20.04 LTS+)**: Built with lightweight dependencies, compatible with Python 3.8 ~ 3.12+ without deprecation issues.
- 🔄 **24/7 Background Reliability**: Provides both native `systemd` service integration and Docker container deployment with auto-restart on failure.

---

## 📁 Project Structure

```text
.
├── config.ini            # Actual configuration file with your secrets (excluded by .gitignore)
├── config.ini.example    # Configuration template
├── config_manager.py     # Configuration loader & validator
├── translator.py         # DeepL API wrapper (long-text splitting, quota checks)
├── bot.py                # Main Telegram Bot application
├── requirements.txt      # Python dependencies (compatible with Python 3.8+)
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose deployment configuration
├── .gitignore            # Git ignore rules (prevents secret leaks)
├── .dockerignore          # Docker ignore rules (prevents secrets in build context)
├── deploy/
│   ├── install.sh        # One-click Linux / Ubuntu deployment script
│   └── deepl-bot.service # systemd service unit file
├── README.md             # Documentation (繁體中文)
└── README_EN.md          # Documentation (English)
```

---

## 🔑 Prerequisites: Getting API Credentials

### 1. Obtain a Telegram Bot Token
1. Open Telegram, search for [@BotFather](https://t.me/BotFather), and start a chat.
2. Send `/newbot`, then follow the prompts to choose a bot name and username (must end in `bot`).
3. BotFather will provide an **HTTP API Token** (e.g., `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

### 2. Obtain a DeepL API Key
1. Go to the [DeepL API Official Website](https://www.deepl.com/pro-api) and create an account.
2. Subscribe to the **DeepL API Free** plan (grants 500,000 characters/month for free).
3. In your account dashboard under "Account", copy your **Authentication Key for DeepL API** (Free keys typically end with `:fx`).

---

## 🚀 Deployment Guide (All Linux Distributions, Min Ubuntu 20.04 LTS+)

### Option A: One-Click Installation Script (Native Python venv + systemd)

An automated script is provided for Ubuntu / Debian and compatible Linux distributions. It installs `python3-venv`, sets up an isolated virtual environment, installs dependencies, and registers a systemd service.

1. **Clone or transfer the project to your Linux server**:
   ```bash
   cd /opt
   # Assuming the project is placed in /opt/deepl-telegram-bot
   cd deepl-telegram-bot
   ```

2. **Execute the installation script**:
   ```bash
   chmod +x deploy/install.sh
   ./deploy/install.sh
   ```

3. **Edit the configuration file**:
   ```bash
   nano config.ini
   ```
   Paste your `bot_token` and DeepL `api_key`, then save (`Ctrl+O` -> `Enter` -> `Ctrl+X`).

4. **Start the bot**:
   ```bash
   sudo systemctl start deepl-bot
   ```

5. **Verify status & view live logs**:
   ```bash
   # Check service status
   sudo systemctl status deepl-bot

   # Tail logs in real time
   journalctl -u deepl-bot -f
   ```

---

### Option B: Deploy with Docker Compose (Cross-Platform)

If you prefer containerization, you can run the bot on any Linux, macOS, or Windows environment with Docker:

1. **Create and edit `config.ini`**:
   ```bash
   cp config.ini.example config.ini
   nano config.ini
   ```

2. **Start the container**:
   ```bash
   docker compose up -d --build
   ```

3. **View logs**:
   ```bash
   docker compose logs -f
   ```

---

## ⚙️ `config.ini` Configuration Reference

```ini
[telegram]
# Telegram Bot Token from @BotFather
bot_token = 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ

# Allowed Telegram User IDs (Optional)
# Enter your personal Telegram ID to prevent unauthorized usage and protect your quota.
# You can check your ID by sending /myid to the bot.
# Leave blank to allow anyone to use the bot.
allowed_user_ids = 12345678

[deepl]
# DeepL API Key (Free tier keys typically end with :fx)
api_key = your-deepl-api-key:fx

# Custom API endpoint (leave empty for automatic selection between Free/Pro)
server_url = 

# Monthly character safety limit
# When monthly usage reaches this number, translation stops to preserve safety margin.
# Recommended: 490000 (leaves 10,000 buffer characters; set to 0 for no limit).
monthly_limit = 490000

# Quota warning threshold percentage (e.g., 90 adds a warning header when reaching 90%; 0 disables)
warning_percent = 90

[translation]
# Source language: AUTO or leave blank for automatic detection
source_lang = AUTO

# Target language: Defaults to Traditional Chinese (ZH-HANT)
# Other options include: EN-US, EN-GB, JA, KO, DE, FR, etc.
target_lang = ZH-HANT

# Show detected source language at top of reply (e.g., [EN ➔ ZH-HANT])
show_detected_lang = true
```

> **Applying configuration changes**:
> - systemd: `sudo systemctl restart deepl-bot`
> - Docker: `docker compose restart`

---

## 💬 Bot Commands & Menu Integration

The bot automatically registers command shortcuts with Telegram's server:
1. **Menu Button (bottom left)**: An interactive `[/]` or `[Menu]` button appears next to the chat input field.
2. **Inline Action Buttons**: `/start`, `/status`, and `/help` include interactive buttons for one-tap actions on mobile and desktop.

| Command | Telegram Menu Description | Function |
| :--- | :--- | :--- |
| `/start` | 🚀 Start the bot and view current settings | Shows welcome message, current language settings, and quick buttons |
| `/status` | 📊 Check DeepL quota usage & status | Displays **DeepL 500,000 free quota usage**, percentages, and safety threshold |
| `/myid` | 🆔 Check your Telegram User ID | Helps find your ID for the `allowed_user_ids` whitelist |
| `/help` | 📖 Help guide & instructions | Displays instructions and operational details |

---

## 🛠️ Common Maintenance Commands (Linux systemd)

```bash
# Start service
sudo systemctl start deepl-bot

# Stop service
sudo systemctl stop deepl-bot

# Restart service
sudo systemctl restart deepl-bot

# Check status
sudo systemctl status deepl-bot

# Enable start at boot (enabled by default in install script)
sudo systemctl enable deepl-bot

# View live logs (last 50 lines)
journalctl -u deepl-bot -f -n 50
```

---

## ❓ Frequently Asked Questions (FAQ)

**Q1: Why choose `pyTelegramBotAPI` over `python-telegram-bot 20+`?**  
A: Ubuntu 20.04 ships with Python 3.8 by default, whereas `python-telegram-bot v21+` strictly requires Python 3.9+. `pyTelegramBotAPI` runs reliably on Python 3.8+, has a tiny dependency footprint, uses minimal memory (~30MB), and features built-in reconnect and threading mechanisms—making it ideal for lightweight VPS deployments.

**Q2: What is the official DeepL language code for Traditional Chinese?**  
A: DeepL officially introduced Traditional Chinese support with the code `ZH-HANT`. Setting `target_lang = ZH-HANT` ensures high-quality Traditional Chinese translation adapted for Taiwan, Hong Kong, and Macau.

**Q3: Can the bot translate forwarded messages with images or files?**  
A: Currently, the bot focuses on text and dialogue translations. If you forward any text-based message, the bot will translate it immediately.

**Q4: How does DeepL count and reset the 500,000 monthly characters? Does it require manual reset?**  
A: **No manual reset is needed!** DeepL tracks quota based on your account's monthly billing cycle (e.g., from the 15th of each month to the 15th of the next). DeepL's servers reset the counter to zero automatically on your billing date. Every time the bot queries the API, DeepL returns the authoritative count.

**Q5: How can I prevent exceeding the 500,000 free character limit?**  
A: The project includes built-in budget and quota guards:
1. **Safety Cutoff (`monthly_limit = 490000`)**: If usage reaches 490,000 characters (leaving a 10,000-character safety buffer), the bot stops translating and warns you, avoiding unexpected charges or quota exhaustion.
2. **Warning Alerts (`warning_percent = 90`)**: When usage reaches 90% (450,000 characters), replies will include an alert header reminding you of the remaining balance.
3. **On-Demand Inspection (`/status`)**: Send or tap `/status` at any time to inspect real-time usage and remaining characters.

