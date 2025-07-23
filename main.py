import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, font, scrolledtext, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import google.generativeai as genai
import os
import textwrap
import json
from threading import Thread
import re
import tempfile

try:
    from fontTools.ttLib import TTFont
except ImportError:
    TTFont = None

# API Anahtarını harici dosyadan oku
try:
    from api_key import API_KEY
except ImportError:
    API_KEY = None

# API Modelini yapılandır
if API_KEY and API_KEY != "BURAYA_KENDİ_GERÇEK_API_ANAHTARINIZI_YAPIŞTIRIN":
    genai.configure(api_key=API_KEY)
    AI_MODEL_CONFIGURED = True
else:
    AI_MODEL_CONFIGURED = False

class CollapsiblePane(ttk.Frame):
    def __init__(self, parent, text=""):
        super().__init__(parent, style='Collapsible.TFrame')
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self._text = text
        self._is_open = False

        self.toggle_button = ttk.Button(self, text=f'► {self._text}', command=self.toggle, style='Toolbutton')
        self.toggle_button.grid(row=0, column=0, sticky='ew')
        
        self.content_frame = ttk.Frame(self)

    def toggle(self):
        if self._is_open:
            self.content_frame.grid_forget()
            self.toggle_button.configure(text=f'► {self._text}')
            self._is_open = False
        else:
            self.content_frame.grid(row=1, column=0, sticky='nsew')
            self.toggle_button.configure(text=f'▼ {self._text}')
            self._is_open = True

# --- YARDIMCI SINIF: Font Tarayıcı ---
class FontBrowser(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent); self.title("Font Tarayıcı"); self.geometry("400x500"); self.result = None; self.protocol("WM_DELETE_WINDOW", self.on_cancel); self.configure(bg='#2E2E2E')
        self.status_label = ttk.Label(self, text="Sistem fontları taranıyor..."); self.status_label.pack(pady=10, fill='x', padx=10)
        list_frame = ttk.Frame(self); list_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5); scrollbar = ttk.Scrollbar(list_frame); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget = tk.Text(list_frame, yscrollcommand=scrollbar.set, cursor="arrow", state=tk.DISABLED, bg="#3C3C3C", fg="#DCDCDC", relief='flat', highlightthickness=0); self.text_widget.pack(expand=True, fill=tk.BOTH)
        scrollbar.config(command=self.text_widget.yview); button_frame = ttk.Frame(self); button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Seç", command=self.on_select).pack(side=tk.LEFT, padx=10); ttk.Button(button_frame, text="İptal", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        self.fonts = {}; Thread(target=self.populate_font_list, daemon=True).start()
    def get_system_fonts(self):
        font_paths = {};
        if os.name == 'nt': paths = [os.path.join(os.environ['WINDIR'], 'Fonts')]
        elif os.name == 'posix': paths = ['/System/Library/Fonts', '/Library/Fonts', '~/Library/Fonts', '/usr/share/fonts', '~/.local/share/fonts', '/usr/X11R6/lib/X11/fonts/TTF/']
        else: return {}
        for path in paths:
            path = os.path.expanduser(path)
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            full_path = os.path.join(root, file)
                            try:
                                font = TTFont(full_path, 0); name = font['name'].getBestFamilyName()
                                if name not in font_paths: font_paths[name] = full_path
                            except Exception: continue
        return font_paths
    def populate_font_list(self):
        self.fonts = self.get_system_fonts(); sorted_fonts = sorted(self.fonts.keys())
        self.text_widget.config(state=tk.NORMAL); self.text_widget.delete("1.0", tk.END)
        for name in sorted_fonts:
            try:
                font_obj = font.Font(family=name, size=14); tag_name = f"font_{name.replace(' ', '_').replace('-', '_')}"
                self.text_widget.tag_configure(tag_name, font=font_obj, foreground="#DCDCDC")
                self.text_widget.insert(tk.END, f"{name}\n", tag_name)
            except Exception: continue
        self.text_widget.config(state=tk.DISABLED); self.status_label.config(text=f"{len(sorted_fonts)} adet font bulundu.")
    def on_select(self):
        try:
            index = self.text_widget.index(tk.CURRENT); selected_line_index = index.split('.')[0]
            selected_font_name = self.text_widget.get(f"{selected_line_index}.0", f"{selected_line_index}.end").strip()
            if selected_font_name in self.fonts: self.result = self.fonts[selected_font_name]; self.destroy()
        except Exception: messagebox.showerror("Hata", "Lütfen listeden bir font seçin.")
    def on_cancel(self): self.result = None; self.destroy()

# --- ANA UYGULAMA SINIFI ---
class InstaMaticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InstaMatic v3.0 - Final Sürümü")
        self.root.geometry("1200x800")
        
        # Tema ve Stil Ayarları
        self.bg_color = '#2E2E2E'; self.frame_bg_color = '#3C3C3C'; self.text_color_light = '#DCDCDC'; self.accent_color = '#007ACC'
        self.root.configure(bg=self.bg_color)
        style = ttk.Style(self.root); style.theme_use('clam')
        style.configure('.', background=self.frame_bg_color, foreground=self.text_color_light, fieldbackground='#555555', lightcolor=self.frame_bg_color, darkcolor=self.bg_color, bordercolor=self.accent_color)
        style.configure('TButton', padding=6, relief='flat', font=('Helvetica', 9, 'bold'), foreground='white', background=self.accent_color)
        style.map('TButton', background=[('active', '#005f9e'), ('disabled', '#555555')])
        style.configure('Toolbutton', padding=6, relief='flat', font=('Helvetica', 9), background='#555555')
        style.configure('TLabel', foreground=self.text_color_light, background=self.frame_bg_color)
        style.configure('Collapsible.TFrame', background=self.bg_color)
        style.configure('TRadiobutton', foreground=self.text_color_light, background=self.frame_bg_color)
        style.configure('TCheckbutton', foreground=self.text_color_light, background=self.frame_bg_color)
        
        # Değişkenler
        self.original_image = None; self.processed_images = {}; self.photo_image = None; self.display_img_info = {}
        self.crop_rect_id = None; self.rect_start_x = 0; self.rect_start_y = 0; self.base_cropped_image = None
        self.guide_h = None; self.guide_v = None; self.guide_center_x = 0; self.guide_center_y = 0
        self.drag_axis_lock = None; self.style_examples = None
        
        # Ayarlanabilir Değişkenler
        self.font_path = tk.StringVar(value="arial.ttf"); self.logo_path = tk.StringVar()
        self.font_size = tk.IntVar(value=72); self.text_padding = tk.IntVar(value=90); self.bg_opacity = tk.IntVar(value=50)
        self.text_color_on_img = tk.StringVar(value="#FFFFFF"); self.bg_color_rgb_on_img = (0, 0, 0)
        self.add_stroke = tk.BooleanVar(value=False); self.text_position = tk.StringVar(value="bottom")
        self.logo_position = tk.StringVar(value="br"); self.logo_opacity = tk.IntVar(value=70)
        self.ai_tone = tk.StringVar(value="Haber / Bilgilendirici"); self.ai_analyze_image = tk.BooleanVar(value=False)
        self.logo_image = None; self.is_ai_running = False
        
        self.model = genai.GenerativeModel('gemini-1.5-pro') if AI_MODEL_CONFIGURED else None
        
        self.create_widgets()
        self.load_config(); self.load_style_examples()

    def create_widgets(self):
        main_paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL); main_paned_window.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.Frame(main_paned_window, width=420); main_paned_window.add(control_frame, weight=1)
        self.canvas = tk.Canvas(main_paned_window, bg="#505050", highlightthickness=0); main_paned_window.add(self.canvas, weight=3)
        self.canvas.bind("<ButtonPress-1>", self.on_press); self.canvas.bind("<B1-Motion>", self.on_drag); self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        ttk.Label(control_frame, text="InstaMatic", font=("Helvetica", 18, "bold")).pack(pady=10); ttk.Separator(control_frame, orient='horizontal').pack(fill='x', padx=10, pady=5)
        ttk.Button(control_frame, text="1. Resim Seç", command=self.load_image).pack(fill=tk.X, padx=10, pady=5)
        
        style_pane = CollapsiblePane(control_frame, text="Stil Ayarları"); style_pane.pack(fill=tk.X, padx=10, pady=5, anchor='n')
        font_frame = ttk.Frame(style_pane.content_frame); font_frame.pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(font_frame, text="Font Seç", command=self.select_font).pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.font_label = ttk.Label(font_frame, text="Varsayılan: Arial", style='Toolbutton', anchor='center'); self.font_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))
        spin_frame = ttk.Frame(style_pane.content_frame); spin_frame.pack(fill=tk.X, pady=4, padx=5); spin_frame.columnconfigure(1, weight=1)
        ttk.Label(spin_frame, text="Font Boyutu:").grid(row=0, column=0, sticky='w', pady=2)
        self.font_size_spinbox = ttk.Spinbox(spin_frame, from_=30, to=150, increment=1, textvariable=self.font_size); self.font_size_spinbox.grid(row=0, column=1, sticky='ew')
        ttk.Label(spin_frame, text="Metin Genişliği (%):").grid(row=1, column=0, sticky='w', pady=2)
        self.padding_spinbox = ttk.Spinbox(spin_frame, from_=80, to=100, increment=1, textvariable=self.text_padding); self.padding_spinbox.grid(row=1, column=1, sticky='ew')
        ttk.Label(spin_frame, text="Arka Plan Yoğunluğu (%):").grid(row=2, column=0, sticky='w', pady=2)
        self.opacity_spinbox = ttk.Spinbox(spin_frame, from_=0, to=100, increment=5, textvariable=self.bg_opacity); self.opacity_spinbox.grid(row=2, column=1, sticky='ew')
        color_frame = ttk.Frame(style_pane.content_frame); color_frame.pack(fill=tk.X, pady=4, padx=5)
        ttk.Button(color_frame, text="Metin Rengi", command=lambda: self.choose_color('text')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
        ttk.Button(color_frame, text="Arka Plan Rengi", command=lambda: self.choose_color('bg')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2,0))
        ttk.Checkbutton(style_pane.content_frame, text="Metne Dış Çizgi Ekle", variable=self.add_stroke, style='TCheckbutton').pack(anchor='w', padx=5)
        pos_frame = ttk.Frame(style_pane.content_frame); pos_frame.pack(fill=tk.X, padx=5)
        ttk.Label(pos_frame, text="Metin Konumu:").pack(side=tk.LEFT); ttk.Radiobutton(pos_frame, text="Aşağıda", variable=self.text_position, value="bottom").pack(side=tk.LEFT, expand=True); ttk.Radiobutton(pos_frame, text="Yukarıda", variable=self.text_position, value="top").pack(side=tk.LEFT, expand=True)
        
        logo_pane = CollapsiblePane(control_frame, text="Logo / Filigran Ayarları"); logo_pane.pack(fill=tk.X, padx=10, pady=5, anchor='n')
        logo_button_frame = ttk.Frame(logo_pane.content_frame); logo_button_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(logo_button_frame, text="Logo Seç (.png)", command=self.select_logo).pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.logo_label = ttk.Label(logo_button_frame, text="Logo Seçilmedi", style='Toolbutton', anchor='center'); self.logo_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))
        logo_spin_frame = ttk.Frame(logo_pane.content_frame); logo_spin_frame.pack(fill=tk.X, pady=4, padx=5); logo_spin_frame.columnconfigure(1, weight=1)
        ttk.Label(logo_spin_frame, text="Logo Yoğunluğu (%):").grid(row=0, column=0, sticky='w', pady=2)
        self.logo_opacity_spinbox = ttk.Spinbox(logo_spin_frame, from_=0, to=100, increment=5, textvariable=self.logo_opacity); self.logo_opacity_spinbox.grid(row=0, column=1, sticky='ew')
        logo_pos_frame = ttk.Frame(logo_pane.content_frame); logo_pos_frame.pack(fill=tk.X, padx=5)
        ttk.Label(logo_pos_frame, text="Konum:").pack(side=tk.LEFT); ttk.Radiobutton(logo_pos_frame, text="Sağ Alt", variable=self.logo_position, value="br").pack(side=tk.LEFT, expand=True); ttk.Radiobutton(logo_pos_frame, text="Sol Alt", variable=self.logo_position, value="bl").pack(side=tk.LEFT, expand=True); ttk.Radiobutton(logo_pos_frame, text="Sağ Üst", variable=self.logo_position, value="tr").pack(side=tk.LEFT, expand=True); ttk.Radiobutton(logo_pos_frame, text="Sol Üst (Sıfır)", variable=self.logo_position, value="tl").pack(side=tk.LEFT, expand=True)

        text_pane = CollapsiblePane(control_frame, text="Metin Girişi"); text_pane.pack(fill=tk.X, padx=10, pady=5, anchor='n')
        tk.Label(text_pane.content_frame, text="Türkçe Metin:", bg=self.frame_bg_color, fg=self.text_color_light).pack(anchor='w', padx=5); tr_frame = ttk.Frame(text_pane.content_frame); tr_frame.pack(fill=tk.X, expand=True, padx=5, pady=2); tr_frame.columnconfigure(0, weight=1); tr_frame.columnconfigure(1, weight=0)
        self.text_entry_tr = tk.Text(tr_frame, height=4, wrap=tk.WORD, bg='#555555', fg=self.text_color_light, insertbackground=self.text_color_light, relief='flat', borderwidth=2); self.text_entry_tr.grid(row=0, column=0, sticky="nsew")
        ttk.Button(tr_frame, text="-> EN", command=lambda: self.translate_text('tr', 'en')).grid(row=0, column=1, sticky="ns", padx=(5,0))
        tk.Label(text_pane.content_frame, text="İngilizce Metin:", bg=self.frame_bg_color, fg=self.text_color_light).pack(anchor='w', padx=5); en_frame = ttk.Frame(text_pane.content_frame); en_frame.pack(fill=tk.X, expand=True, padx=5, pady=2); en_frame.columnconfigure(0, weight=1); en_frame.columnconfigure(1, weight=0)
        self.text_entry_en = tk.Text(en_frame, height=4, wrap=tk.WORD, bg='#555555', fg=self.text_color_light, insertbackground=self.text_color_light, relief='flat', borderwidth=2); self.text_entry_en.grid(row=0, column=0, sticky="nsew")
        ttk.Button(en_frame, text="-> TR", command=lambda: self.translate_text('en', 'tr')).grid(row=0, column=1, sticky="ns", padx=(5,0))
        
        action_frame = ttk.Frame(control_frame); action_frame.pack(fill=tk.X, padx=10, pady=5)
        self.btn_crop = ttk.Button(action_frame, text="2. Alanı Kırp ve Hazırla", command=self.crop_and_prepare); self.btn_crop.pack(fill=tk.X, pady=2)
        self.btn_update_text = ttk.Button(action_frame, text="Stil Değişikliklerini Uygula", state=tk.DISABLED, command=self.update_text_styles); self.btn_update_text.pack(fill=tk.X, pady=2)
        
        ai_pane = CollapsiblePane(control_frame, text="Yapay Zeka Asistanı"); ai_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, anchor='n')
        tk.Label(ai_pane.content_frame, text="Korunacak Terimler (virgülle ayırın):", bg=self.frame_bg_color, fg=self.text_color_light).pack(anchor='w', padx=5)
        self.protected_terms_entry = ttk.Entry(ai_pane.content_frame); self.protected_terms_entry.pack(fill=tk.X, pady=(0,5), padx=5)
        ai_top_frame = ttk.Frame(ai_pane.content_frame); ai_top_frame.pack(fill=tk.X, padx=5)
        ttk.Label(ai_top_frame, text="Ton:").pack(side=tk.LEFT)
        tones = ["Haber / Bilgilendirici", "Samimi", "Profesyonel", "Esprili", "Satış Odaklı"]; self.ai_tone_menu = ttk.OptionMenu(ai_top_frame, self.ai_tone, self.ai_tone.get(), *tones); self.ai_tone_menu.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Checkbutton(ai_pane.content_frame, text="Resmi de Analiz Et", variable=self.ai_analyze_image, style='TCheckbutton').pack(anchor='w', padx=5, pady=2)
        self.btn_ai_generate_all = ttk.Button(ai_pane.content_frame, text="AI Asistanı Çalıştır", state=tk.DISABLED, command=self.run_full_ai_assistant)
        self.btn_ai_generate_all.pack(fill=tk.X, pady=5, padx=5)
        self.ai_output_text = scrolledtext.ScrolledText(ai_pane.content_frame, height=5, wrap=tk.WORD, state=tk.DISABLED, bg='#555555', fg=self.text_color_light, relief='flat'); self.ai_output_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.style_label = ttk.Label(ai_pane.content_frame, text="Stil Örnekleri: Bulunamadı", style='Toolbutton', anchor='center'); self.style_label.pack(fill=tk.X, padx=5)
        
        self.btn_save = ttk.Button(control_frame, text="4. Hazırlanan Resimleri Kaydet", state=tk.DISABLED, command=self.save_image); self.btn_save.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)

    def on_press(self, event):
        self.rect_start_x, self.rect_start_y = event.x, event.y
        if event.state & 0x1: self.drag_axis_lock = 'undetermined'
        else: self.drag_axis_lock = None
        if event.state & 0x4: self.show_guides()

    def on_release(self, event):
        self.hide_guides()

    def on_drag(self, event):
        if not self.crop_rect_id: return
        dx, dy = event.x - self.rect_start_x, event.y - self.rect_start_y
        if self.drag_axis_lock:
            if self.drag_axis_lock == 'undetermined':
                if abs(dx) > abs(dy): self.drag_axis_lock = 'h'
                else: self.drag_axis_lock = 'v'
            if self.drag_axis_lock == 'h': dy = 0
            elif self.drag_axis_lock == 'v': dx = 0
        is_ctrl_only = (event.state & 0x4) and not (event.state & 0x1)
        if is_ctrl_only and self.guide_h:
            snap_tolerance = 10; x1, y1, x2, y2 = self.canvas.coords(self.crop_rect_id)
            rect_center_x, rect_center_y = (x1 + x2) / 2, (y1 + y2) / 2
            new_center_x, new_center_y = rect_center_x + dx, rect_center_y + dy
            if abs(new_center_x - self.guide_center_x) < snap_tolerance: dx = self.guide_center_x - rect_center_x
            if abs(new_center_y - self.guide_center_y) < snap_tolerance: dy = self.guide_center_y - rect_center_y
        self.canvas.move(self.crop_rect_id, dx, dy)
        self.rect_start_x, self.rect_start_y = event.x, event.y
    
    def show_guides(self, event=None):
        if not self.original_image or not self.display_img_info or self.guide_h: return
        info = self.display_img_info; self.guide_center_x = info['x'] + info['width'] / 2; self.guide_center_y = info['y'] + info['height'] / 2
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.guide_v = self.canvas.create_line(self.guide_center_x, 0, self.guide_center_x, canvas_height, fill="#E53935", dash=(5, 3), width=1.5)
        self.guide_h = self.canvas.create_line(0, self.guide_center_y, canvas_width, self.guide_center_y, fill="#E53935", dash=(5, 3), width=1.5)

    def hide_guides(self, event=None):
        if self.guide_h: self.canvas.delete(self.guide_h); self.guide_h = None
        if self.guide_v: self.canvas.delete(self.guide_v); self.guide_v = None

    def choose_color(self, target):
        color_code = colorchooser.askcolor(title=f"{target} Rengi Seç", color=self.text_color_on_img.get() if target == 'text' else None)
        if color_code and color_code[1]:
            if target == 'text': self.text_color_on_img.set(color_code[1])
            elif target == 'bg': self.bg_color_rgb_on_img = tuple(int(c) for c in color_code[0])

    def _add_logo(self, image):
        if not self.logo_image: return image
        logo = self.logo_image.copy(); opacity = self.logo_opacity.get()
        if opacity < 100:
            alpha = logo.split()[3]; alpha = alpha.point(lambda p: p * opacity / 100.0); logo.putalpha(alpha)
        image_w, image_h = image.size; logo.thumbnail((image_w * 0.20, image_h * 0.20), Image.Resampling.LANCZOS); logo_w, logo_h = logo.size
        padding = int(image_w * 0.03); pos = self.logo_position.get()
        if pos == "tl": x, y = 0, 0
        elif pos == "br": x, y = image_w - logo_w - padding, image_h - logo_h - padding
        elif pos == "bl": x, y = padding, image_h - logo_h - padding
        elif pos == "tr": x, y = image_w - logo_w - padding, padding
        else: x, y = padding, padding
        image.paste(logo, (x, y), logo)
        return image

    def _add_text_to_image(self, image, text):
        draw = ImageDraw.Draw(image, "RGBA"); font_size = self.font_size.get(); text_area_width_ratio = self.text_padding.get() / 100.0
        opacity_percent = self.bg_opacity.get(); alpha_value = int((opacity_percent / 100.0) * 255)
        final_bg_color = self.bg_color_rgb_on_img + (alpha_value,)
        try: image_font = ImageFont.truetype(self.font_path.get(), font_size)
        except IOError: image_font = ImageFont.load_default()
        char_width_ratio = 0.55; max_chars_per_line = int((image.width * text_area_width_ratio) / (font_size * char_width_ratio)) if font_size > 0 else 50
        final_lines = [line for user_line in text.split('\n') for line in (textwrap.wrap(user_line, width=max_chars_per_line, break_long_words=True) or [''])]
        wrapped_text = "\n".join(final_lines)
        stroke_width = 2 if self.add_stroke.get() else 0
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=image_font, align="center", stroke_width=stroke_width)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        padding_y = 25; rect_height = text_height + (padding_y * 2)
        if self.text_position.get() == "bottom": rect_y_pos = image.height - rect_height
        else: rect_y_pos = 0
        draw.rectangle([(0, rect_y_pos), (image.width, rect_y_pos + rect_height)], fill=final_bg_color)
        text_x, text_y = (image.width - text_width) / 2, rect_y_pos + padding_y
        draw.text((text_x, text_y), wrapped_text, font=image_font, fill=self.text_color_on_img.get(), align="center", stroke_width=stroke_width, stroke_fill="black")
        image = self._add_logo(image)
        return image
    
    def crop_and_prepare(self):
        if not self.original_image: messagebox.showerror("Hata", "Lütfen önce bir resim seçin!"); return
        if not self.crop_rect_id: messagebox.showerror("Hata", "Lütfen resim üzerinde bir kırpma alanı seçin."); return
        self.hide_guides()
        coords = self.canvas.coords(self.crop_rect_id); info = self.display_img_info; scale = info['scale_factor']
        x1, y1, x2, y2 = (coords[0] - info['x']) * scale, (coords[1] - info['y']) * scale, (coords[2] - info['x']) * scale, (coords[3] - info['y']) * scale
        cropped_piece = self.original_image.crop((x1, y1, x2, y2))
        self.base_cropped_image = cropped_piece.resize((1080, 1350), Image.Resampling.LANCZOS)
        self.canvas.delete(self.crop_rect_id); self.crop_rect_id = None
        self.btn_crop.config(state=tk.DISABLED); self.btn_update_text.config(state=tk.NORMAL); self.update_text_styles()

    def update_text_styles(self):
        if not self.base_cropped_image: messagebox.showerror("Hata", "Önce bir alanı kırpmanız gerekiyor."); return
        text_tr, text_en = self.text_entry_tr.get("1.0", tk.END).strip(), self.text_entry_en.get("1.0", tk.END).strip()
        if not text_tr and not text_en: messagebox.showerror("Hata", "Lütfen en az bir dilde metin girin!"); return
        self.processed_images.clear()
        if text_tr: self.processed_images['tr'] = self._add_text_to_image(self.base_cropped_image.copy(), text_tr)
        if text_en: self.processed_images['en'] = self._add_text_to_image(self.base_cropped_image.copy(), text_en)
        display_img = self.processed_images.get('tr') or self.processed_images.get('en')
        if display_img:
            self.display_image(display_img, is_processed=True)
            self.btn_save.config(state=tk.NORMAL); self.btn_ai_generate_all.config(state=tk.NORMAL)
            self.save_config()
    
    def _check_api_key(self):
        if not self.model: messagebox.showerror("API Hatası", "API Anahtarı bulunamadı veya yanlış.\nLütfen 'api_key.py' dosyasını ve içeriğini kontrol edin."); return False
        return True
        
    def reset_state(self):
        self.btn_save.config(state=tk.DISABLED); self.btn_ai_generate_all.config(state=tk.DISABLED)
        self.btn_crop.config(state=tk.NORMAL); self.btn_update_text.config(state=tk.DISABLED)
        self.ai_output_text.config(state=tk.NORMAL); self.ai_output_text.delete("1.0", tk.END); self.ai_output_text.config(state=tk.DISABLED)
        self.processed_images.clear(); self.text_entry_tr.delete("1.0", tk.END); self.text_entry_en.delete("1.0", tk.END)
        self.base_cropped_image = None
        
    def load_image(self):
        self.hide_guides()
        image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")]);
        if not image_path: return
        self.original_image = Image.open(image_path)
        self.display_image(self.original_image); self.reset_state()

    def display_image(self, img, is_processed=False):
        self.canvas.delete("all"); self.root.update_idletasks()
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        display_img = img.copy(); display_img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(display_img)
        img_x, img_y = (canvas_width - self.photo_image.width()) / 2, (canvas_height - self.photo_image.height()) / 2
        self.canvas.create_image(img_x, img_y, anchor=tk.NW, image=self.photo_image)
        if not is_processed:
            self.display_img_info = {'x': img_x, 'y': img_y, 'width': self.photo_image.width(), 'height': self.photo_image.height(), 'scale_factor': self.original_image.width / self.photo_image.width()}
            self.draw_crop_rectangle()
            
    def draw_crop_rectangle(self):
        if self.crop_rect_id: self.canvas.delete(self.crop_rect_id)
        info = self.display_img_info;
        if info['width'] == 0 or info['height'] == 0: return
        target_ratio = 4 / 5
        if info['width'] / info['height'] > target_ratio: crop_width, crop_height = info['width'] * 0.8, (info['width'] * 0.8) / target_ratio
        else: crop_height, crop_width = info['height'] * 0.8, (info['height'] * 0.8) * target_ratio
        x1, y1 = info['x'] + (info['width'] - crop_width) / 2, info['y'] + (info['height'] - crop_height) / 2
        x2, y2 = x1 + crop_width, y1 + crop_height
        self.crop_rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
        
    def select_font(self):
        if TTFont is None: messagebox.showerror("Eksik Kütüphane", "Lütfen 'fonttools' kütüphanesini kurun."); return
        browser = FontBrowser(self.root); self.root.wait_window(browser)
        if browser.result:
            self.font_path.set(browser.result); self.font_label.config(text=os.path.basename(self.font_path.get())); self.save_config()
            
    def select_logo(self):
        logo_path = filedialog.askopenfilename(title="Logo Dosyası Seçin", filetypes=[("PNG Files", "*.png")])
        if not logo_path: return
        try:
            self.logo_image = Image.open(logo_path).convert("RGBA"); self.logo_path.set(logo_path)
            self.logo_label.config(text=os.path.basename(logo_path)); self.save_config()
        except Exception as e: messagebox.showerror("Hata", f"Logo dosyası yüklenemedi: {e}")
            
    def save_config(self):
        config_data = {"font_path": self.font_path.get(), "logo_path": self.logo_path.get(), "font_size": self.font_size.get(), "text_padding": self.text_padding.get(), "bg_opacity": self.bg_opacity.get(), "text_color": self.text_color_on_img.get(), "bg_color_rgb": self.bg_color_rgb_on_img, "add_stroke": self.add_stroke.get(), "text_position": self.text_position.get(), "logo_position": self.logo_position.get(), "logo_opacity": self.logo_opacity.get(), "ai_tone": self.ai_tone.get()}
        try:
            with open("config.json", "w") as f: json.dump(config_data, f, indent=4)
        except Exception as e: print(f"Ayarlar kaydedilirken hata oluştu: {e}")
        
    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f: data = json.load(f)
                self.font_path.set(data.get("font_path", "arial.ttf")); self.font_label.config(text=os.path.basename(self.font_path.get()))
                logo_path = data.get("logo_path")
                if logo_path and os.path.exists(logo_path):
                    self.logo_path.set(logo_path); self.logo_image = Image.open(logo_path).convert("RGBA"); self.logo_label.config(text=os.path.basename(logo_path))
                self.font_size.set(data.get("font_size", 72)); self.text_padding.set(data.get("text_padding", 90)); self.bg_opacity.set(data.get("bg_opacity", 50))
                self.text_color_on_img.set(data.get("text_color", "#FFFFFF")); self.bg_color_rgb_on_img = tuple(data.get("bg_color_rgb", (0, 0, 0)))
                self.add_stroke.set(data.get("add_stroke", False)); self.text_position.set(data.get("text_position", "bottom"))
                self.logo_position.set(data.get("logo_position", "br")); self.logo_opacity.set(data.get("logo_opacity", 70))
                self.ai_tone.set(data.get("ai_tone", "Haber / Bilgilendirici"))
        except Exception as e: print(f"Ayarlar yüklenirken hata oluştu: {e}")
        
    def load_style_examples(self):
        if os.path.exists("style_examples.txt"):
            try:
                with open("style_examples.txt", "r", encoding="utf-8") as f: self.style_examples = f.read()
                self.style_label.config(text="Stil Örnekleri: Yüklendi", foreground="#4CAF50")
            except Exception as e: self.style_label.config(text="Stil Dosyası Okunamadı!", foreground="#F44336")
        else: self.style_label.config(text="Stil Örnekleri: Bulunamadı", foreground="#FFC107")

    def _clean_api_response(self, text):
        cleaned_text = text.strip();
        if cleaned_text.startswith("```json"): cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"): cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"): cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        if cleaned_text.startswith('"') and cleaned_text.endswith('"'): cleaned_text = cleaned_text[1:-1]
        if cleaned_text.startswith("'") and cleaned_text.endswith("'"): cleaned_text = cleaned_text[1:-1]
        return cleaned_text
    
    def _handle_api_error(self, e, context_widget=None):
        error_str = str(e)
        if "429" in error_str:
            retry_seconds = "60"; match = re.search(r"retry_delay: seconds: (\d+)", error_str)
            if match: retry_seconds = match.group(1)
            messagebox.showwarning("API Kullanım Limiti Aşıldı!", f"Google'ın ücretsiz kullanım limitine ulaştınız.\n\nLütfen devam etmeden önce yaklaşık {retry_seconds} saniye bekleyin.")
        else: messagebox.showerror("API Hatası", f"Beklenmedik bir API hatası oluştu:\n\n{error_str}")
        if context_widget: context_widget.config(state=tk.DISABLED)

    def translate_text(self, source_lang, target_lang):
        if not self._check_api_key() or self.is_ai_running: return
        self.is_ai_running = True
        Thread(target=self._execute_translation, args=(source_lang, target_lang), daemon=True).start()

    def _execute_translation(self, source_lang, target_lang):
        try:
            if source_lang == 'tr': source_box, target_box, prompt_text = self.text_entry_tr, self.text_entry_en, "Aşağıdaki Türkçe metni İngilizce'ye çevir."
            else: source_box, target_box, prompt_text = self.text_entry_en, self.text_entry_tr, "Aşağıdaki İngilizce metni Türkçe'ye çevir."
            source_text = source_box.get("1.0", tk.END).strip()
            if not source_text: messagebox.showwarning("Uyarı", "Lütfen çevrilecek bir metin girin."); return
            protected_terms = self.protected_terms_entry.get().strip()
            protection_instruction = f"\nÖNEMLİ KURAL: Şu terimleri asla çevirme, orijinal halleriyle bırak: '{protected_terms}'." if protected_terms else ""
            full_prompt = f"{prompt_text}{protection_instruction}\n\nÇevrilecek Metin: '{source_text}'"
            original_target_text = target_box.get("1.0", tk.END).strip()
            target_box.delete("1.0", tk.END); target_box.insert("1.0", "Çevriliyor...")
            response = self.model.generate_content(full_prompt)
            cleaned_translation = self._clean_api_response(response.text)
            target_box.delete("1.0", tk.END); target_box.insert("1.0", cleaned_translation)
        except Exception as e:
            self._handle_api_error(e)
            target_box.delete("1.0", tk.END); target_box.insert("1.0", original_target_text)
        finally:
            self.is_ai_running = False

    def run_full_ai_assistant(self):
        if not self._check_api_key() or self.is_ai_running: return
        base_text = self.text_entry_tr.get("1.0", tk.END).strip(); analyze_image = self.ai_analyze_image.get()
        if not base_text and not analyze_image: messagebox.showerror("Hata", "Lütfen bir ana metin girin veya 'Resmi Analiz Et' seçeneğini işaretleyin."); return
        if analyze_image and not self.base_cropped_image: messagebox.showerror("Hata", "Resmi analiz edebilmek için önce bir alanı kırpmanız gerekiyor."); return
        self.is_ai_running = True; self.btn_ai_generate_all.config(state=tk.DISABLED)
        self.ai_output_text.config(state=tk.NORMAL); self.ai_output_text.delete("1.0", tk.END); self.ai_output_text.insert("1.0", "Gemini düşünüyor (tek istek)...")
        self.root.update_idletasks()
        Thread(target=self._execute_full_ai_assistant, daemon=True).start()

    def _execute_full_ai_assistant(self):
        base_text = self.text_entry_tr.get("1.0", tk.END).strip(); analyze_image = self.ai_analyze_image.get()
        style_prompt_prefix = f"Sen bir anime ve manga haberleri editörüsün. Yazım stilin aşağıdaki örneklere benzemeli.\n\n---ÖRNEKLER---\n{self.style_examples}\n---ÖRNEKLER SONU---\n\nBu stili kullanarak" if self.style_examples else "Şimdi,"
        protected_terms = self.protected_terms_entry.get().strip()
        protection_instruction = f"ÖNEMLİ KURAL: Şu terimleri asla çevirme veya değiştirme: '{protected_terms}'." if protected_terms else ""
        prompt_parts = []
        if analyze_image:
            prompt_parts.append("Aşağıdaki resme ve metne bakarak şu görevleri yerine getir ve sonucu tek bir geçerli JSON objesi olarak döndür:")
            prompt_parts.append(self.base_cropped_image)
        else:
            prompt_parts.append("Aşağıdaki metne bakarak şu görevleri yerine getir ve sonucu tek bir geçerli JSON objesi olarak döndür:")
        
        prompt_parts.append(f"""
JSON objesi şu anahtarları içermelidir: "generated_caption", "english_translation".

1.  **generated_caption:** {style_prompt_prefix} 'Ton Seçimi' olarak '{self.ai_tone.get()}' seçildi. Bu tonu dikkate alarak bir Instagram gönderi açıklaması yaz. {protection_instruction} Açıklamanın sonuna uygun emojiler ve 3-5 adet popüler hashtag ekle.
2.  **english_translation:** Ana metni İngilizce'ye çevir. {protection_instruction}

Ana Metin: '{base_text if base_text else "Yok"}'
""")
        try:
            response = self.model.generate_content(prompt_parts)
            json_text = self._clean_api_response(response.text)
            ai_results = json.loads(json_text)
            self.ai_output_text.delete("1.0", tk.END)
            self.ai_output_text.insert("1.0", ai_results.get("generated_caption", "Açıklama üretilemedi."))
            if base_text: # Sadece ana metin varsa çevirisini ekle
                self.text_entry_en.delete("1.0", tk.END)
                self.text_entry_en.insert("1.0", ai_results.get("english_translation", ""))
        except Exception as e:
            self._handle_api_error(e, self.ai_output_text)
        finally:
            self.is_ai_running = False
            self.btn_ai_generate_all.config(state=tk.NORMAL)
            self.ai_output_text.config(state=tk.DISABLED)

    def save_image(self):
        if not self.processed_images: return
        base_path = filedialog.asksaveasfilename(title="Kaydedilecek dosya adını ve yerini seçin", filetypes=[("JPEG Image", "*.jpg")])
        if not base_path: return
        base_name, _ = os.path.splitext(base_path)
        saved_files = []
        try:
            if 'tr' in self.processed_images: self.processed_images['tr'].convert("RGB").save(f"{base_name}_tr.jpg", "JPEG"); saved_files.append(f"{base_name}_tr.jpg")
            if 'en' in self.processed_images: self.processed_images['en'].convert("RGB").save(f"{base_name}_en.jpg", "JPEG"); saved_files.append(f"{base_name}_en.jpg")
            messagebox.showinfo("Başarılı", "Resimler başarıyla kaydedildi:\n\n" + "\n".join(saved_files))
        except Exception as e: messagebox.showerror("Kayıt Hatası", f"Dosyalar kaydedilirken bir hata oluştu: {e}")

if __name__ == "__main__":
    if TTFont is None:
        if messagebox.askyesno("Eksik Kütüphane", "'fonttools' kütüphanesi gerekli.\nKurulsun mu?"):
            import subprocess; import sys
            try: subprocess.check_call([sys.executable, "-m", "pip", "install", "fonttools"]); messagebox.showinfo("Başarılı", "Kütüphane kuruldu. Lütfen programı yeniden başlatın.")
            except Exception as e: messagebox.showerror("Hata", f"Kurulum hatası: {e}")
        exit()
    if not AI_MODEL_CONFIGURED: messagebox.showwarning("API Anahtarı Eksik", "'api_key.py' dosyası bulunamadı veya anahtar geçersiz.\n\nYapay zeka özellikleri çalışmayacaktır.")
    root = tk.Tk()
    app = InstaMaticApp(root)
    root.mainloop()