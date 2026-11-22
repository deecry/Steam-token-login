🔐 Steam Token Login
A lightweight Windows GUI tool to sign into Steam using an account username and a refresh token. It automatically closes running Steam processes, injects the session data, and launches Steam again ⚡

✨ How It Works
📝 Enter your Steam username (if an email is entered, the @... part is stripped automatically) and refresh token in the GUI window.

🛑 Terminates active steam.exe and steamwebhelper.exe processes and removes %LOCALAPPDATA%\Steam\local.vdf.

🧩 Extracts the SteamID from the token payload and protects the token using Windows DPAPI (CryptProtectData) with the account name as entropy.

⚙️ Updates Steam registry auto-login settings and writes config.vdf, loginusers.vdf, and local.vdf.

🚀 Starts steam.exe automatically.

🛠️ Usage
Run the Python script directly to open the graphical interface:


📋 Requirements
🪟 Windows (uses Windows DPAPI via ctypes and the Windows Registry)

🎮 Steam installed (auto-detected from the Registry, falling back to C:\Program Files (x86)\Steam)

🐍 Python 3.x (uses built-in standard library modules only, including tkinter)

⚠️ Security & Disclaimer
🔒 Keep your token private: Treat your refresh token like a password. Never share it in screenshots, logs, or commits.

⚖️ Unofficial tool — not affiliated with or endorsed by Valve or Steam. Use at your own risk.

📄 License
