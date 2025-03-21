import os
import pyautogui
import tkinter as tk
from tkinter import font, ttk
from openai import OpenAI
import asyncio
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import keyboard
import json

version = "1.0.0"
name = "LeoTrans"

config_file = "leotrans_config.json"
GROK_API_MODEL = "grok-2-latest"  # Grok-এর মডেল নাম
GROK_API_BASE_URL = "https://api.x.ai/v1"  # xAI-এর API Base URL

LANGUAGE_OPTIONS = [
    "Afrikaans", "Albanian", "Amharic", "Arabic", "Arabic (Gulf)", "Armenian", "Assamese", "Azerbaijani",
    "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Burmese", "Cantonese",
    "Catalan", "Cebuano", "Chichewa", "Chinese", "Chinese (Traditional)", "Corsican", "Croatian", "Czech",
    "Danish", "Dutch",
    "English (US)", "English (UK)", "English (Normal)", "Esperanto", "Estonian",
    "Filipino", "Finnish", "French", "Frisian",
    "Galician", "Georgian", "German", "Greek", "Gujarati",
    "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hinglish", "Hmong", "Hungarian",
    "Icelandic", "Igbo", "Indonesian", "Irish", "Italian",
    "Japanese", "Javanese",
    "Kannada", "Kazakh", "Khmer", "Kinyarwanda", "Korean", "Kurdish", "Kyrgyz",
    "Lao", "Latin", "Latvian", "Lithuanian", "Luxembourgish",
    "Macedonian", "Malagasy", "Malay", "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian",
    "Nepali", "Norwegian",
    "Pashto", "Persian", "Polish", "Portuguese", "Punjabi",
    "Romanian", "Russian",
    "Samoan", "Scots Gaelic", "Serbian", "Sesotho", "Shona", "Sindhi", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", "Sundanese", "Swahili", "Swedish",
    "Tajik", "Tamil", "Tatar", "Telugu", "Thai", "Turkish", "Turkmen",
    "Ukrainian", "Urdu", "Uzbek",
    "Vietnamese",
    "Welsh", "Western Frisian",
    "Xhosa",
    "Yiddish", "Yoruba",
    "Zulu"
]

def load_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f)
    return {"api_key": "", "model": GROK_API_MODEL, **{f"language_{i+1}": "English (US)" for i in range(12)}}

def save_config():
    config = {f"language_{i+1}": lang_vars[i].get() for i in range(12)}
    config["api_key"] = api_key_var.get()
    config["model"] = model_var.get()
    with open(config_file, "w") as f:
        json.dump(config, f)

def get_prompt_for_language(language):
    if language == "Hinglish":
        return "Translate the following Hindi text to Hinglish (Hindi words written in English script) in a natural, fluent, and respectful tone, as if speaking to a senior person. Use 'Aap' instead of 'Tu' to show respect."
    else:
        return f"Translate the following text to {language} in a natural, fluent, and respectful tone, as if speaking to a senior person."
    
def custom_popup(title, message, fg_color):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("500x300+150+100")
    popup.configure(bg="#f5f5f5")
    popup.attributes("-topmost", True)
    text_widget = tk.Text(popup, wrap="word", font=("Helvetica", 12), bg="#f5f5f5", fg=fg_color, borderwidth=0)
    text_widget.insert("1.0", message)
    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both", padx=20, pady=20)

def update_status(message):
    status_label.config(text=f"LeoTrans - {message}")
    status_label.update()

async def translate_text(index, show_popup=False):
    update_status("Translating...")
    pyautogui.hotkey('ctrl', 'c')
    await asyncio.sleep(0.5)
    try:
        selected_text = root.clipboard_get()
        language = lang_vars[index].get()
        prompt = get_prompt_for_language(language)
        
        # Grok API ক্লায়েন্ট সেটআপ
        client = OpenAI(
            api_key=api_key_var.get(),
            base_url=GROK_API_BASE_URL,
        )
        
        # API কল
        completion = client.chat.completions.create(
            model=model_var.get(),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": selected_text}
            ]
        )
        
        # ট্রান্সলেটেড টেক্সট পাওয়া
        translated_text = completion.choices[0].message.content
        
        if show_popup:
            custom_popup("Translation", translated_text, "#000000")
        else:
            root.clipboard_clear()
            root.clipboard_append(translated_text)
            root.update()
            await asyncio.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
    except Exception as e:
        custom_popup("Error", f"Translation failed: {str(e)}", "red")
    finally:
        update_status("Ready")

root = tk.Tk()
root.title("LeoTrans")
root.geometry("250x700+100+50")
root.config(bg="#f5f5f5")
custom_font = font.Font(family="Helvetica", size=12)

config = load_config()

status_label = tk.Label(root, text="LeoTrans - Ready", font=custom_font, bg="#f5f5f5", fg="#333")
status_label.pack(pady=10)

api_key_var = tk.StringVar(value=config.get("api_key", ""))
tk.Label(root, text="xAI API Key:", font=custom_font, bg="#f5f5f5").pack()
tk.Entry(root, textvariable=api_key_var, show="*", font=custom_font, width=50).pack(pady=5, padx=50)

model_var = tk.StringVar(value=config.get("model", GROK_API_MODEL))
tk.Label(root, text="Grok Model:", font=custom_font, bg="#f5f5f5").pack()
tk.Entry(root, textvariable=model_var, font=custom_font, width=50).pack(pady=5, padx=50)

frame = tk.Frame(root, bg="#f5f5f5")
frame.pack(pady=20)

lang_vars = [tk.StringVar(value=config.get(f"language_{i+1}", "English (US)")) for i in range(12)]

for i in range(12):
    row = i
    tk.Label(frame, text=f"CTRL+F{i+1}", font=custom_font, bg="#f5f5f5").grid(row=row, column=0, padx=10, pady=5, sticky="w")
    opt = ttk.Combobox(frame, values=LANGUAGE_OPTIONS, textvariable=lang_vars[i], width=12, height=10)
    opt.grid(row=row, column=1, padx=10, pady=5)

save_btn = tk.Button(root, text="Save", command=save_config, font=custom_font, bg="#4CAF50", fg="white", padx=20, pady=10)
save_btn.pack(pady=20)

for i in range(12):
    if i < 11:
        keyboard.add_hotkey(f'ctrl+f{i+1}', lambda i=i: asyncio.run(translate_text(i)))
    else:
        keyboard.add_hotkey(f'ctrl+f{i+1}', lambda i=i: asyncio.run(translate_text(i, show_popup=True)))

def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(image)
    draw.rectangle((width // 2, 0, width, height), fill=color2)
    return image

def quit_app(icon, item):
    icon.stop()
    root.quit()
    root.destroy()
    os._exit(0)

menu = [item("Quit", quit_app)]
icon = pystray.Icon("LeoTrans", create_image(20, 20, "#FFFFFF", "#000000"), "LeoTrans", menu=pystray.Menu(*menu))
threading.Thread(target=icon.run, daemon=True).start()

root.mainloop()
