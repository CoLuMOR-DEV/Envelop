import math
import random
import time
import tkinter as tk
from tkinter import font as tkfont


class EnvelopeApp:
    """Fullscreen monthsary envelope scene with smooth animations and transparent background support."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Monthsary Envelope")

        # Keep this as a normal top-level window so it appears in Alt+Tab.
        self.root.attributes("-fullscreen", True)

        self.transparent_key = "#00ff00"
        self.transparent_supported = False
        self._enable_transparent_background()

        self.canvas = tk.Canvas(
            self.root,
            bg=self.transparent_key if self.transparent_supported else "#100b19",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.is_open = False
        self.open_start_time = 0.0
        self.letter_start_time = 0.0
        self.hearts_started = False
        self.heart_state: list[dict] = []

        self.flap_open_ratio = 0.0
        self.letter_ratio = 0.0

        self.envelope_tag = "envelope"
        self.hint_tag = "hint"
        self.bg_tag = "bg"
        self.heart_tag = "heart"

        self.envelope_items: dict[str, int] = {}
        self.letter_items: dict[str, int] = {}

        self.palette = {
            "bg_top": "#140e22",
            "bg_bottom": "#28163a",
            "glow_hot": "#ff7aac",
            "glow_soft": "#ffbfd9",
            "env_base": "#ffd4e7",
            "env_mid": "#ffc0da",
            "env_dark": "#ee8fb8",
            "paper": "#fff9ef",
            "paper_edge": "#f1ddbd",
            "ink": "#563246",
            "ink_soft": "#a05a7d",
            "accent": "#ff4f93",
        }

        self.title_font_family = self.pick_first_font(["Segoe Script", "Lucida Handwriting", "Georgia", "Times New Roman"])
        self.body_font_family = self.pick_first_font(["Georgia", "Palatino Linotype", "Cambria", "Segoe UI"])

        self.bind_events()
        self.rebuild_scene()

    def _enable_transparent_background(self) -> None:
        self.root.configure(bg=self.transparent_key)
        try:
            self.root.wm_attributes("-transparentcolor", self.transparent_key)
            self.transparent_supported = True
        except tk.TclError:
            self.transparent_supported = False

    def bind_events(self) -> None:
        self.root.bind("<Escape>", lambda _e: self.root.destroy())
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.handle_click)

    def toggle_fullscreen(self, _event=None) -> None:
        current = bool(self.root.attributes("-fullscreen"))
        self.root.attributes("-fullscreen", not current)

    def on_resize(self, _event=None) -> None:
        new_w = self.root.winfo_width()
        new_h = self.root.winfo_height()
        if new_w <= 1 or new_h <= 1:
            return
        if (new_w, new_h) == (self.width, self.height):
            return

        self.width, self.height = new_w, new_h
        self.rebuild_scene()

    def rebuild_scene(self) -> None:
        self.canvas.delete("all")
        self.compute_layout()
        self.draw_background_layers()
        self.draw_envelope()

        if self.is_open:
            self.update_flap(1.0)
            self.draw_letter(1.0, show_text=True)

        self.draw_corner_hint()

        if self.hearts_started:
            self.redraw_hearts()

    def compute_layout(self) -> None:
        self.cx = self.width * 0.5
        self.cy = self.height * 0.54

        self.env_w = min(max(self.width * 0.34, 360), 760)
        self.env_h = self.env_w * 0.58

        self.left = self.cx - self.env_w * 0.5
        self.right = self.cx + self.env_w * 0.5
        self.top = self.cy - self.env_h * 0.5
        self.bottom = self.cy + self.env_h * 0.5

        self.letter_w = self.env_w * 0.87
        self.letter_h = self.env_h * 1.17

    def draw_background_layers(self) -> None:
        if self.transparent_supported:
            return

        self.draw_vertical_gradient(self.palette["bg_top"], self.palette["bg_bottom"], steps=70)

        glow_r = min(self.width, self.height)
        for i in range(10):
            r = glow_r * (0.10 + i * 0.043)
            color = self.mix_hex(self.palette["glow_hot"], self.palette["bg_top"], 0.20 - i * 0.015)
            self.canvas.create_oval(
                self.cx - r,
                self.cy - r * 0.85,
                self.cx + r,
                self.cy + r * 0.85,
                fill=color,
                outline="",
                tags=self.bg_tag,
            )

    def draw_vertical_gradient(self, top_hex: str, bottom_hex: str, steps: int = 60) -> None:
        r1, g1, b1 = self.hex_to_rgb(top_hex)
        r2, g2, b2 = self.hex_to_rgb(bottom_hex)

        for i in range(steps):
            t = i / max(steps - 1, 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            y0 = self.height * i / steps
            y1 = self.height * (i + 1) / steps
            self.canvas.create_rectangle(0, y0, self.width, y1, fill=f"#{r:02x}{g:02x}{b:02x}", outline="", tags=self.bg_tag)

    def draw_envelope(self) -> None:
        self.envelope_items.clear()
        shadow = max(8, self.env_w * 0.015)

        self.canvas.create_oval(
            self.left - self.env_w * 0.08,
            self.bottom - self.env_h * 0.10,
            self.right + self.env_w * 0.08,
            self.bottom + self.env_h * 0.20,
            fill="#120b19",
            outline="",
            stipple="gray25",
        )

        self.canvas.create_polygon(
            self.left + shadow,
            self.top + shadow,
            self.right + shadow,
            self.top + shadow,
            self.right + shadow,
            self.bottom + shadow,
            self.left + shadow,
            self.bottom + shadow,
            fill="#120a1b",
            outline="",
        )

        self.envelope_items["back"] = self.canvas.create_rectangle(
            self.left,
            self.top,
            self.right,
            self.bottom,
            fill=self.palette["env_base"],
            outline=self.palette["env_dark"],
            width=3,
            tags=self.envelope_tag,
        )

        self.envelope_items["left_fold"] = self.canvas.create_polygon(
            self.left,
            self.top,
            self.cx,
            self.cy + self.env_h * 0.12,
            self.left,
            self.bottom,
            fill=self.palette["env_mid"],
            outline=self.palette["env_dark"],
            width=2,
            tags=self.envelope_tag,
        )

        self.envelope_items["right_fold"] = self.canvas.create_polygon(
            self.right,
            self.top,
            self.cx,
            self.cy + self.env_h * 0.12,
            self.right,
            self.bottom,
            fill=self.palette["env_mid"],
            outline=self.palette["env_dark"],
            width=2,
            tags=self.envelope_tag,
        )

        self.envelope_items["bottom_fold"] = self.canvas.create_polygon(
            self.left,
            self.bottom,
            self.cx,
            self.cy + self.env_h * 0.14,
            self.right,
            self.bottom,
            fill="#ffafd0",
            outline=self.palette["env_dark"],
            width=2,
            tags=self.envelope_tag,
        )

        self.envelope_items["flap"] = self.canvas.create_polygon(
            self.left,
            self.top,
            self.cx,
            self.top - self.env_h * 0.46,
            self.right,
            self.top,
            fill="#ffadd0",
            outline=self.palette["env_dark"],
            width=2,
            tags=self.envelope_tag,
        )

        seal_size = int(max(30, self.env_w * 0.10))
        self.envelope_items["seal"] = self.canvas.create_text(
            self.cx,
            self.cy + self.env_h * 0.01,
            text="❤",
            fill=self.palette["accent"],
            font=("Segoe UI Emoji", seal_size, "bold"),
            tags=self.envelope_tag,
        )

        if not self.is_open:
            hint_size = int(max(16, min(self.width, self.height) * 0.022))
            self.canvas.create_text(
                self.cx,
                self.bottom + max(44, self.env_h * 0.20),
                text="Click envelope to open your letter",
                fill="#ffe0ef",
                font=("Segoe UI", hint_size, "bold"),
                tags=self.hint_tag,
            )

    def draw_corner_hint(self) -> None:
        text_color = "#efd4e5" if not self.transparent_supported else "#ffd3e8"
        self.canvas.create_text(
            self.width - 24,
            24,
            anchor="ne",
            text="Esc: close    F11: toggle fullscreen",
            fill=text_color,
            font=("Segoe UI", 11, "bold"),
        )

    def handle_click(self, event: tk.Event) -> None:
        if self.is_open:
            return

        if self.left <= event.x <= self.right and self.top <= event.y <= self.bottom:
            self.is_open = True
            self.canvas.delete(self.hint_tag)
            self.open_start_time = time.perf_counter()
            self.animate_opening()
            self.root.after(220, self.start_hearts)

    def animate_opening(self) -> None:
        elapsed = time.perf_counter() - self.open_start_time
        flap_duration = 0.70
        letter_duration = 0.85

        flap_t = self.ease_in_out_cubic(min(elapsed / flap_duration, 1.0))
        self.flap_open_ratio = flap_t
        self.update_flap(flap_t)

        if elapsed > 0.18:
            letter_elapsed = elapsed - 0.18
            letter_t = self.ease_out_back(min(letter_elapsed / letter_duration, 1.0))
            self.letter_ratio = max(0.0, min(letter_t, 1.0))
            self.draw_letter(self.letter_ratio, show_text=self.letter_ratio >= 0.99)

        if flap_t < 1.0 or self.letter_ratio < 1.0:
            self.root.after(16, self.animate_opening)

    def update_flap(self, progress: float) -> None:
        inset = self.env_w * 0.24 * progress
        tip_high = self.env_h * (0.46 + 0.72 * progress)
        tip_y = self.top - tip_high

        self.canvas.coords(
            self.envelope_items["flap"],
            self.left + inset,
            self.top,
            self.cx,
            tip_y,
            self.right - inset,
            self.top,
        )

        flap_color = self.mix_hex("#ffadd0", "#f58ab5", progress * 0.55)
        self.canvas.itemconfigure(self.envelope_items["flap"], fill=flap_color)

        if "seal" in self.envelope_items:
            seal_fade = max(0.0, 1.0 - progress * 1.35)
            seal_color = self.mix_hex(self.palette["accent"], self.palette["env_base"], 1.0 - seal_fade)
            self.canvas.itemconfigure(self.envelope_items["seal"], fill=seal_color)

    def draw_letter(self, progress: float, show_text: bool = False) -> None:
        left = self.cx - self.letter_w * 0.5
        right = self.cx + self.letter_w * 0.5
        bottom = self.bottom - self.env_h * 0.08
        top = bottom - self.letter_h * progress

        paper_edge = max(3, int(self.env_w * 0.0046))

        if "shadow" not in self.letter_items:
            self.letter_items["shadow"] = self.canvas.create_rectangle(
                left + 6,
                top + 6,
                right + 6,
                bottom + 6,
                fill="#0f0815",
                outline="",
                stipple="gray25",
            )
            self.letter_items["paper"] = self.canvas.create_rectangle(
                left,
                top,
                right,
                bottom,
                fill=self.palette["paper"],
                outline=self.palette["paper_edge"],
                width=paper_edge,
            )
            self.letter_items["line_1"] = self.canvas.create_line(left + 24, top + 56, right - 24, top + 56, fill="#f7ecd7", width=2)
            self.letter_items["line_2"] = self.canvas.create_line(left + 24, top + 96, right - 24, top + 96, fill="#f7ecd7", width=2)
        else:
            self.canvas.coords(self.letter_items["shadow"], left + 6, top + 6, right + 6, bottom + 6)
            self.canvas.coords(self.letter_items["paper"], left, top, right, bottom)
            self.canvas.coords(self.letter_items["line_1"], left + 24, top + 56, right - 24, top + 56)
            self.canvas.coords(self.letter_items["line_2"], left + 24, top + 96, right - 24, top + 96)

        if show_text:
            self.draw_letter_text(left, top, right, bottom)

    def draw_letter_text(self, left: float, top: float, right: float, bottom: float) -> None:
        w = right - left
        h = bottom - top

        heading_size = int(max(20, w * 0.050))
        body_size = int(max(13, min(25, w * 0.033)))

        heading_font = (self.title_font_family, heading_size, "bold")
        body_font = (self.body_font_family, body_size, "normal")

        heading = "Happy Monthsary"
        body = (
            "My love,\n\n"
            "Another month with you is another month\n"
            "of comfort, laughter, and sweet little moments\n"
            "I never want to lose.\n\n"
            "Thank you for being my calm, my home,\n"
            "and my favorite part of every day.\n\n"
            "I love you always. ❤"
        )

        content_width = w * 0.78

        if "heading" not in self.letter_items:
            self.letter_items["heading"] = self.canvas.create_text(
                self.cx,
                top + h * 0.12,
                text=heading,
                fill=self.palette["ink_soft"],
                font=heading_font,
            )
            self.letter_items["body"] = self.canvas.create_text(
                self.cx,
                top + h * 0.56,
                text=body,
                fill=self.palette["ink"],
                width=content_width,
                justify="center",
                font=body_font,
                spacing1=3,
                spacing2=4,
                spacing3=6,
            )
        else:
            self.canvas.coords(self.letter_items["heading"], self.cx, top + h * 0.12)
            self.canvas.coords(self.letter_items["body"], self.cx, top + h * 0.56)
            self.canvas.itemconfigure(self.letter_items["heading"], font=heading_font)
            self.canvas.itemconfigure(self.letter_items["body"], font=body_font, width=content_width)

    def start_hearts(self) -> None:
        if self.hearts_started:
            return
        self.hearts_started = True
        self.spawn_heart_loop()
        self.animate_hearts()

    def spawn_heart_loop(self) -> None:
        if not self.hearts_started:
            return

        x = random.uniform(12, self.width - 12)
        y = -30
        size = random.randint(max(11, int(self.width * 0.0068)), max(19, int(self.width * 0.012)))
        speed = random.uniform(0.9, 1.9)
        phase = random.uniform(0, math.pi * 2)
        amplitude = random.uniform(8.0, 20.0)
        drift = random.uniform(-0.24, 0.24)
        color = random.choice(["#ff85b8", "#ff6ea8", "#ffd3e9", "#ff4f93"])

        heart_id = self.canvas.create_text(x, y, text="❤", fill=color, font=("Segoe UI Emoji", size), tags=self.heart_tag)
        self.heart_state.append(
            {
                "id": heart_id,
                "x": x,
                "y": y,
                "speed": speed,
                "phase": phase,
                "amp": amplitude,
                "drift": drift,
                "step": random.uniform(0.05, 0.11),
            }
        )

        self.root.after(random.randint(220, 500), self.spawn_heart_loop)

    def animate_hearts(self) -> None:
        if not self.hearts_started:
            return

        alive = []
        for heart in self.heart_state:
            heart["y"] += heart["speed"]
            heart["phase"] += heart["step"]
            heart["x"] += heart["drift"]
            draw_x = heart["x"] + math.sin(heart["phase"]) * heart["amp"] * 0.06
            self.canvas.coords(heart["id"], draw_x, heart["y"])

            if heart["y"] <= self.height + 40:
                alive.append(heart)
            else:
                self.canvas.delete(heart["id"])

        self.heart_state = alive
        self.root.after(16, self.animate_hearts)

    def redraw_hearts(self) -> None:
        # On resize rebuild, existing hearts are removed with canvas; keep motion by clearing stale ids.
        self.heart_state.clear()

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def ease_out_back(t: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

    @staticmethod
    def hex_to_rgb(value: str) -> tuple[int, int, int]:
        value = value.strip().lstrip("#")
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    def mix_hex(self, fg: str, bg: str, ratio: float) -> str:
        ratio = max(0.0, min(1.0, ratio))
        fr, fg_c, fb = self.hex_to_rgb(fg)
        br, bg_c, bb = self.hex_to_rgb(bg)

        r = int(fr * ratio + br * (1 - ratio))
        g = int(fg_c * ratio + bg_c * (1 - ratio))
        b = int(fb * ratio + bb * (1 - ratio))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def pick_first_font(candidates: list[str]) -> str:
        try:
            available = set(tkfont.families())
        except tk.TclError:
            return "TkDefaultFont"

        for item in candidates:
            if item in available:
                return item
        return "TkDefaultFont"

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    EnvelopeApp().run()
