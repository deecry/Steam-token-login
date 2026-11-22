import os
import json
import base64
import time
import subprocess
import winreg
import zlib
import ctypes
import tkinter as tk
from tkinter import messagebox


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def crypt_protect_data(data, entropy):
    data_in = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_ubyte)))
    entropy_in = DATA_BLOB(len(entropy), ctypes.cast(ctypes.create_string_buffer(entropy), ctypes.POINTER(ctypes.c_ubyte)))
    data_out = DATA_BLOB()
    if ctypes.windll.crypt32.CryptProtectData(ctypes.byref(data_in), None, ctypes.byref(entropy_in), None, None, 0, ctypes.byref(data_out)):
        result = ctypes.string_at(data_out.pbData, data_out.cbData)
        ctypes.windll.kernel32.LocalFree(data_out.pbData)
        return result.hex()
    return None


def vdf_dump(data, indent=0):
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append("\t" * indent + f'"{key}"')
            lines.append("\t" * indent + "{")
            lines.extend(vdf_dump(value, indent + 1))
            lines.append("\t" * indent + "}")
        else:
            lines.append("\t" * indent + f'"{key}"\t\t"{value}"')
    return lines if indent > 0 else "\n".join(lines)


def steam_session_inject(account_name, refresh_token, status_label):
    if "@" in account_name:
        account_name = account_name.split("@")[0]

    try:
        jwt_payload = refresh_token.split(".")[1]
        jwt_payload += "=" * (4 - len(jwt_payload) % 4)
        steam_id = json.loads(base64.b64decode(jwt_payload))["sub"]
    except:
        steam_id = "0"

    status_label.config(text="Killing Steam...")
    status_label.update()

    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam")
        install_dir, _ = winreg.QueryValueEx(reg_key, "InstallPath")
    except:
        install_dir = r"C:\Program Files (x86)\Steam"

    local_data_file = os.path.join(os.environ["LOCALAPPDATA"], "Steam", "local.vdf")

    for p in ["steam.exe", "steamwebhelper.exe"]:
        subprocess.run(["taskkill", "/F", "/IM", p], capture_output=True)
    time.sleep(2)

    if os.path.exists(local_data_file):
        os.remove(local_data_file)

    status_label.config(text="Injecting session...")
    status_label.update()

    user_reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(user_reg, "AutoLoginUser", 0, winreg.REG_SZ, account_name)
    winreg.SetValueEx(user_reg, "RememberPassword", 0, winreg.REG_DWORD, 1)

    cache_key = format(zlib.crc32(account_name.encode()) & 0xFFFFFFFF, "08x") + "1"
    protected_token = crypt_protect_data(refresh_token.encode(), account_name.encode())

    config_data = {"InstallConfigStore": {"Software": {"Valve": {"Steam": {"AutoUpdateWindowEnabled": "0", "Accounts": {account_name: {"SteamID": steam_id}}}}}}}
    login_users_data = {"users": {steam_id: {"AccountName": account_name, "PersonaName": account_name, "RememberPassword": "1", "AllowAutoLogin": "1", "MostRecent": "1", "Timestamp": str(int(time.time()))}}}
    local_machine_data = {"MachineUserConfigStore": {"Software": {"Valve": {"Steam": {"ConnectCache": {cache_key: protected_token}}}}}}

    os.makedirs(os.path.dirname(local_data_file), exist_ok=True)

    with open(os.path.join(install_dir, "config", "config.vdf"), "w") as f:
        f.write(vdf_dump(config_data))
    with open(os.path.join(install_dir, "config", "loginusers.vdf"), "w") as f:
        f.write(vdf_dump(login_users_data))
    with open(local_data_file, "w") as f:
        f.write(vdf_dump(local_machine_data))

    status_label.config(text="Starting Steam...")
    status_label.update()

    subprocess.Popen([os.path.join(install_dir, "steam.exe")])
    status_label.config(text="Done!")


def login():
    username = username_entry.get().strip()
    token = token_entry.get().strip()
    if not username or not token:
        messagebox.showerror("Error", "Enter both username and token")
        return
    try:
        steam_session_inject(username, token, status_label)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="")


root = tk.Tk()
root.title("Steam Login")
root.geometry("400x180")
root.resizable(False, False)

tk.Label(root, text="Username:").pack(anchor="w", padx=20, pady=(15, 0))
username_entry = tk.Entry(root, width=50)
username_entry.pack(padx=20)

tk.Label(root, text="Token:").pack(anchor="w", padx=20, pady=(10, 0))
token_entry = tk.Entry(root, width=50)
token_entry.pack(padx=20)

tk.Button(root, text="Login", command=login, width=15).pack(pady=15)
status_label = tk.Label(root, text="", fg="gray")
status_label.pack()

root.mainloop()
