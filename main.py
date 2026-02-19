import random
import tkinter as tk
from tkinter import font as tkfont


class EnvelopeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Monthsary Envelope")

        # Fullscreen keeps the app visible in Alt+Tab while hiding normal window chrome.
        self.root.attributes("-fullscreen", True)
        self.root.minsize(900, 600)

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.is_open = False
        self.hearts_started = False
        self.hearts: list[dict] = []
        self.envelope_items: dict[str, int] = {}
        self.letter_items: dict[str, int] = {}

        self.palette = {
            "bg_top": "#171224",
            "bg_bottom": "#2a1730",
            "glow": "#ff7fb0",
            "env_back": "#ffd9e8",
            "env_fold": "#ffc3dc",
            "env_shadow": "#ee9fbe",
            "paper": "#fffaf3",
            "paper_border": "#f3dcb1",
            "ink": "#5a2d41",
            "accent": "#ff5f98",
        }

        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<Button-1>", self.handle_click)
        self.root.bind("<Configure>", self.on_resize)

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.build_scene()

    def on_resize(self, _event=None) -> None:
        new_w = self.root.winfo_width()
        new_h = self.root.winfo_height()
        if new_w <= 1 or new_h <= 1:
            return
        if (new_w, new_h) == (self.width, self.height):
            return
        self.width, self.height = new_w, new_h
        self.build_scene(redraw_only=True)

    def build_scene(self, redraw_only: bool = False) -> None:
        self.canvas.delete("all")

        self.draw_gradient_background()
        self.draw_center_glow()
        self.compute_layout()
        self.draw_envelope_closed()

        if self.is_open:
            self.draw_envelope_open_static()
            self.draw_letter(progress=1.0, show_text=True)

        if not redraw_only:
            self.hearts.clear()

    def compute_layout(self) -> None:
        self.cx = self.width / 2
        self.cy = self.height / 2 + self.height * 0.02

        self.env_w = max(340, min(self.width * 0.34, 720))
        self.env_h = self.env_w * 0.56

        self.left = self.cx - self.env_w / 2
        self.right = self.cx + self.env_w / 2
        self.top = self.cy - self.env_h / 2
        self.bottom = self.cy + self.env_h / 2

        self.letter_w = self.env_w * 0.86
        self.letter_h = self.env_h * 1.16

    def draw_gradient_background(self) -> None:
        steps = 80
        r1, g1, b1 = self.hex_to_rgb(self.palette["bg_top"])
        r2, g2, b2 = self.hex_to_rgb(self.palette["bg_bottom"])

        for i in range(steps):
            t = i / (steps - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            y0 = int((self.height / steps) * i)
            y1 = int((self.height / steps) * (i + 1))
            self.canvas.create_rectangle(0, y0, self.width, y1, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    def draw_center_glow(self) -> None:
        for i in range(7):
            radius = min(self.width, self.height) * (0.10 + i * 0.05)
            alpha_blend = max(0, 38 - i * 5)
            color = self.fade_to_bg(self.palette["glow"], alpha_blend / 100)
            self.canvas.create_oval(
                self.cx - radius,
                self.cy - radius * 0.84,
                self.cx + radius,
                self.cy + radius * 0.84,
                fill=color,
                outline="",
            )

    def draw_envelope_closed(self) -> None:
        shadow_offset = max(6, int(self.env_w * 0.014))
        self.canvas.create_polygon(
            self.left + shadow_offset,
            self.top + shadow_offset,
            self.right + shadow_offset,
            self.top + shadow_offset,
            self.right + shadow_offset,
            self.bottom + shadow_offset,
            self.left + shadow_offset,
            self.bottom + shadow_offset,
            fill="#140c1d",
            outline="",
        )

        self.envelope_items["back"] = self.canvas.create_rectangle(
            self.left,
            self.top,
            self.right,
            self.bottom,
            fill=self.palette["env_back"],
            outline=self.palette["env_shadow"],
            width=3,
            tags="envelope",
        )

        self.envelope_items["left_fold"] = self.canvas.create_polygon(
            self.left,
            self.top,
            self.cx,
            self.cy + self.env_h * 0.10,
            self.left,
            self.bottom,
            fill=self.palette["env_fold"],
            outline=self.palette["env_shadow"],
            width=2,
            tags="envelope",
        )

        self.envelope_items["right_fold"] = self.canvas.create_polygon(
            self.right,
            self.top,
            self.cx,
            self.cy + self.env_h * 0.10,
            self.right,
            self.bottom,
            fill=self.palette["env_fold"],
            outline=self.palette["env_shadow"],
            width=2,
            tags="envelope",
        )

        self.envelope_items["bottom_fold"] = self.canvas.create_polygon(
            self.left,
            self.bottom,
            self.cx,
            self.cy + self.env_h * 0.12,
            self.right,
            self.bottom,
            fill="#ffb4d3",
            outline=self.palette["env_shadow"],
            width=2,
            tags="envelope",
        )

        self.envelope_items["flap"] = self.canvas.create_polygon(
            self.left,
            self.top,
            self.cx,
            self.top - self.env_h * 0.42,
            self.right,
            self.top,
            fill="#ffb0d0",
            outline=self.palette["env_shadow"],
            width=2,
            tags="envelope",
        )

        seal_font_size = max(30, int(self.env_w * 0.10))
        self.envelope_items["seal"] = self.canvas.create_text(
            self.cx,
            self.cy + self.env_h * 0.02,
            text="❤",
            fill=self.palette["accent"],
            font=("Segoe UI Emoji", seal_font_size, "bold"),
            tags="envelope",
        )

        hint_size = max(16, int(min(self.width, self.height) * 0.022))
        self.canvas.create_text(
            self.cx,
            self.bottom + max(36, self.env_h * 0.18),
            text="Click the envelope to open your monthsary letter",
            fill="#ffd9ea",
            font=("Segoe UI", hint_size, "bold"),
            tags="hint",
        )

        self.canvas.create_text(
            self.width - 24,
            26,
            text="Press Esc to close",
            anchor="ne",
            fill="#ffe6f1",
            font=("Segoe UI", max(10, int(hint_size * 0.55)), "bold"),
        )

    def draw_envelope_open_static(self) -> None:
        inset = self.env_w * 0.24
        self.canvas.coords(
            self.envelope_items["flap"],
            self.left + inset,
            self.top,
            self.cx,
            self.top - self.env_h * 1.02,
            self.right - inset,
            self.top,
        )

    def handle_click(self, event: tk.Event) -> None:
        if self.is_open:
            return

        if self.left <= event.x <= self.right and self.top <= event.y <= self.bottom:
            self.is_open = True
            self.canvas.delete("hint")
            self.animate_flap(0)
            self.root.after(280, lambda: self.animate_letter_rise(0))
            self.root.after(320, self.start_hearts)

    def animate_flap(self, step: int) -> None:
        max_steps = 20
        progress = min(step / max_steps, 1.0)
        inset = self.env_w * 0.24 * progress
        tip_y = self.top - self.env_h * (0.42 + 0.60 * progress)

        self.canvas.coords(
            self.envelope_items["flap"],
            self.left + inset,
            self.top,
            self.cx,
            tip_y,
            self.right - inset,
            self.top,
        )

        if step < max_steps:
            self.root.after(18, lambda: self.animate_flap(step + 1))

    def draw_letter(self, progress: float, show_text: bool = False) -> None:
        rise = self.letter_h * progress
        letter_left = self.cx - self.letter_w / 2
        letter_right = self.cx + self.letter_w / 2
        letter_bottom = self.bottom - self.env_h * 0.08
        letter_top = letter_bottom - rise

        if "shadow" not in self.letter_items:
            self.letter_items["shadow"] = self.canvas.create_rectangle(
                letter_left + 5,
                letter_top + 5,
                letter_right + 5,
                letter_bottom + 5,
                fill="#1a0f25",
                outline="",
                stipple="gray25",
            )
            self.letter_items["paper"] = self.canvas.create_rectangle(
                letter_left,
                letter_top,
                letter_right,
                letter_bottom,
                fill=self.palette["paper"],
                outline=self.palette["paper_border"],
                width=3,
            )
        else:
            self.canvas.coords(self.letter_items["shadow"], letter_left + 5, letter_top + 5, letter_right + 5, letter_bottom + 5)
            self.canvas.coords(self.letter_items["paper"], letter_left, letter_top, letter_right, letter_bottom)

        if show_text:
            self.draw_letter_text(letter_left, letter_top, letter_right, letter_bottom)

    def draw_letter_text(self, letter_left: float, letter_top: float, letter_right: float, letter_bottom: float) -> None:
        content_w = letter_right - letter_left
        content_h = letter_bottom - letter_top

        title_size = max(19, int(content_w * 0.050))
        body_size = max(14, int(content_w * 0.032))

        title_font = self.pick_font(["Georgia", "Garamond", "Times New Roman", "Segoe UI"], title_size, "bold")
        body_font = self.pick_font(["Georgia", "Palatino Linotype", "Segoe UI"], body_size, "normal")

        msg = (
            "Happy Monthsary, my love ✨\n\n"
            "Every month with you feels like home.\n"
            "Thank you for the laughs, the comfort,\n"
            "and the little moments that become\n"
            "my favorite memories.\n\n"
            "I’m always grateful for you.\n"
            "I love you so much. ❤"
        )

        pad = content_w * 0.10
        text_y = letter_top + content_h * 0.52

        if "title" not in self.letter_items:
            self.letter_items["title"] = self.canvas.create_text(
                self.cx,
                letter_top + content_h * 0.15,
                text="To My Favorite Person",
                fill="#b45b7b",
                font=title_font,
            )
            self.letter_items["body"] = self.canvas.create_text(
                self.cx,
                text_y,
                text=msg,
                fill=self.palette["ink"],
                width=content_w - (2 * pad),
                justify="center",
                font=body_font,
                spacing1=5,
                spacing2=4,
                spacing3=6,
            )
        else:
            self.canvas.coords(self.letter_items["title"], self.cx, letter_top + content_h * 0.15)
            self.canvas.coords(self.letter_items["body"], self.cx, text_y)
            self.canvas.itemconfigure(self.letter_items["title"], font=title_font)
            self.canvas.itemconfigure(self.letter_items["body"], font=body_font, width=content_w - (2 * pad))

    def animate_letter_rise(self, step: int) -> None:
        max_steps = 26
        progress = min(step / max_steps, 1.0)
        self.draw_letter(progress=progress, show_text=progress >= 1.0)

        if step < max_steps:
            self.root.after(18, lambda: self.animate_letter_rise(step + 1))

    def start_hearts(self) -> None:
        if self.hearts_started:
            return
        self.hearts_started = True
        self.spawn_heart()
        self.animate_hearts()

    def spawn_heart(self) -> None:
        if not self.hearts_started:
            return

        x = random.uniform(16, self.width - 16)
        y = -20
        size = random.randint(max(12, int(self.width * 0.007)), max(18, int(self.width * 0.013)))
        color = random.choice(["#ff90be", "#ff74ad", "#ffd2e6", "#ff5f98"])
        speed = random.uniform(1.1, 2.2)
        drift = random.uniform(-0.7, 0.7)

        heart_id = self.canvas.create_text(x, y, text="❤", fill=color, font=("Segoe UI Emoji", size))
        self.hearts.append({"id": heart_id, "x": x, "y": y, "speed": speed, "drift": drift, "sway": random.uniform(0, 6.2)})

        self.root.after(random.randint(240, 520), self.spawn_heart)

    def animate_hearts(self) -> None:
        if not self.hearts_started:
            return

        alive = []
        for heart in self.hearts:
            heart["y"] += heart["speed"]
            heart["sway"] += 0.05
            heart["x"] += heart["drift"] + 0.35 * (random.uniform(-1, 1))
            sway_offset = 2.6 * random.uniform(-0.7, 0.7)
            self.canvas.coords(heart["id"], heart["x"] + sway_offset, heart["y"])

            if heart["y"] < self.height + 36:
                alive.append(heart)
            else:
                self.canvas.delete(heart["id"])

        self.hearts = alive
        self.root.after(30, self.animate_hearts)

    @staticmethod
    def hex_to_rgb(value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))

    def fade_to_bg(self, color: str, strength: float) -> str:
        r, g, b = self.hex_to_rgb(color)
        rb, gb, bb = self.hex_to_rgb(self.palette["bg_top"])
        fr = int((r * strength) + (rb * (1 - strength)))
        fg = int((g * strength) + (gb * (1 - strength)))
        fb = int((b * strength) + (bb * (1 - strength)))
        return f"#{fr:02x}{fg:02x}{fb:02x}"

    @staticmethod
    def pick_font(candidates: list[str], size: int, weight: str) -> tuple[str, int, str]:
        available = set(tkfont.families())
        for name in candidates:
            if name in available:
                return (name, size, weight)
        return ("TkDefaultFont", size, weight)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    EnvelopeApp().run()
