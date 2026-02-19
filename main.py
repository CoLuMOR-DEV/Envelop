import random
import tkinter as tk


class EnvelopeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.width = 900
        self.height = 600
        self.bg_color = "#00FF00"  # transparent key color for supported platforms

        self.root.title("Monthsary Envelope")
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Transparency works differently per platform, so fail softly.
        try:
            self.root.wm_attributes("-transparentcolor", self.bg_color)
        except tk.TclError:
            pass
        try:
            self.root.wm_attributes("-alpha", 0.98)
        except tk.TclError:
            pass

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.bg_color,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.envelope_center = (self.width // 2, self.height // 2 + 20)
        self.envelope_width = 360
        self.envelope_height = 220

        self.is_open = False
        self.hearts_started = False
        self.heart_ids = []
        self.letter_id = None
        self.letter_text_id = None
        self.letter_shadow = None

        self.draw_closed_envelope()
        self.canvas.tag_bind("envelope", "<Button-1>", self.open_envelope)

        self.root.bind("<Escape>", lambda _event: self.root.destroy())

    def draw_closed_envelope(self) -> None:
        cx, cy = self.envelope_center
        w, h = self.envelope_width, self.envelope_height
        left, right = cx - w // 2, cx + w // 2
        top, bottom = cy - h // 2, cy + h // 2

        self.envelope_back = self.canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="#ffe4ec",
            outline="#f5b8c8",
            width=3,
            tags="envelope",
        )

        self.left_fold = self.canvas.create_polygon(
            left,
            top,
            cx,
            cy + 20,
            left,
            bottom,
            fill="#ffd5e2",
            outline="#f5b8c8",
            width=2,
            tags="envelope",
        )
        self.right_fold = self.canvas.create_polygon(
            right,
            top,
            cx,
            cy + 20,
            right,
            bottom,
            fill="#ffd5e2",
            outline="#f5b8c8",
            width=2,
            tags="envelope",
        )

        self.bottom_fold = self.canvas.create_polygon(
            left,
            bottom,
            cx,
            cy + 20,
            right,
            bottom,
            fill="#ffc7da",
            outline="#f5b8c8",
            width=2,
            tags="envelope",
        )

        self.flap = self.canvas.create_polygon(
            left,
            top,
            cx,
            cy - 35,
            right,
            top,
            fill="#ffbfd6",
            outline="#f5b8c8",
            width=2,
            tags="envelope",
        )

        self.seal = self.canvas.create_text(
            cx,
            cy + 5,
            text="❤",
            fill="#ff5c8a",
            font=("Segoe UI Emoji", 34, "bold"),
            tags="envelope",
        )

        self.hint = self.canvas.create_text(
            cx,
            bottom + 34,
            text="Click the envelope",
            fill="#ffffff",
            font=("Segoe UI", 16, "italic"),
            tags="hint",
        )

    def open_envelope(self, _event=None) -> None:
        if self.is_open:
            return
        self.is_open = True
        self.canvas.delete("hint")
        self.animate_flap(0)
        self.root.after(300, self.animate_letter_rise, 0)
        self.root.after(350, self.start_hearts)

    def animate_flap(self, step: int) -> None:
        cx, cy = self.envelope_center
        w, h = self.envelope_width, self.envelope_height
        left, right = cx - w // 2, cx + w // 2
        top = cy - h // 2

        # Animate the flap "opening" by pulling tip upward and slightly narrowing.
        max_steps = 18
        progress = min(step / max_steps, 1.0)
        tip_y = cy - 35 - int(175 * progress)
        inset = int(90 * progress)

        self.canvas.coords(
            self.flap,
            left + inset,
            top,
            cx,
            tip_y,
            right - inset,
            top,
        )

        if step < max_steps:
            self.root.after(20, self.animate_flap, step + 1)

    def animate_letter_rise(self, step: int) -> None:
        cx, cy = self.envelope_center
        w, h = self.envelope_width, self.envelope_height
        left = cx - (w // 2) + 25
        right = cx + (w // 2) - 25
        bottom = cy + (h // 2) - 16

        max_steps = 22
        progress = min(step / max_steps, 1.0)
        letter_height = 225
        top = bottom - int(letter_height * progress)

        if self.letter_id is None:
            self.letter_shadow = self.canvas.create_rectangle(
                left + 4,
                top + 4,
                right + 4,
                bottom + 4,
                fill="#000000",
                outline="",
                stipple="gray25",
            )
            self.letter_id = self.canvas.create_rectangle(
                left,
                top,
                right,
                bottom,
                fill="#fffaf2",
                outline="#f7d9a8",
                width=2,
            )
        else:
            self.canvas.coords(self.letter_shadow, left + 4, top + 4, right + 4, bottom + 4)
            self.canvas.coords(self.letter_id, left, top, right, bottom)

        if step >= max_steps and self.letter_text_id is None:
            message = (
                "Happy Monthsary, my love 💌\n\n"
                "Another month with you means\n"
                "more smiles, warm hugs,\n"
                "and tiny moments that feel\n"
                "like magic.\n\n"
                "Thank you for being my safe place.\n"
                "I love you so much. ❤"
            )
            self.letter_text_id = self.canvas.create_text(
                cx,
                top + 105,
                text=message,
                fill="#7a2f45",
                width=(right - left) - 28,
                justify="center",
                font=("Segoe UI", 14, "bold"),
            )

        if step < max_steps:
            self.root.after(20, self.animate_letter_rise, step + 1)

    def start_hearts(self) -> None:
        if self.hearts_started:
            return
        self.hearts_started = True
        self.spawn_heart()
        self.animate_hearts()

    def spawn_heart(self) -> None:
        if not self.hearts_started:
            return

        x = random.randint(10, self.width - 10)
        y = -15
        size = random.randint(12, 20)
        drift = random.uniform(-0.8, 0.8)
        speed = random.uniform(1.2, 2.2)
        color = random.choice(["#ff6b9d", "#ff8fb5", "#ffc0d7", "#ff4f8b"])

        heart_id = self.canvas.create_text(
            x,
            y,
            text="❤",
            fill=color,
            font=("Segoe UI Emoji", size),
        )

        self.heart_ids.append(
            {
                "id": heart_id,
                "x": float(x),
                "y": float(y),
                "speed": speed,
                "drift": drift,
                "phase": random.uniform(0, 6.28),
            }
        )

        # Low-density snowfall feel.
        delay = random.randint(220, 480)
        self.root.after(delay, self.spawn_heart)

    def animate_hearts(self) -> None:
        if not self.hearts_started:
            return

        alive = []
        for heart in self.heart_ids:
            heart["y"] += heart["speed"]
            heart["phase"] += 0.06
            heart["x"] += heart["drift"] + (0.7 * random.uniform(-0.4, 0.4))
            sway = 2.2 * (random.uniform(-0.5, 0.5))
            self.canvas.coords(heart["id"], heart["x"] + sway, heart["y"])

            if heart["y"] < self.height + 40:
                alive.append(heart)
            else:
                self.canvas.delete(heart["id"])

        self.heart_ids = alive
        self.root.after(30, self.animate_hearts)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = EnvelopeApp()
    app.run()
