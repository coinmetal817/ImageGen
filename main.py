import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from diffusers import StableDiffusionXLPipeline
import torch
import threading
import traceback
import os, re
from pathlib import Path

# Theme
BG_COLOR = "#0f2c38"
FG_COLOR = "#aefeff"
BTN_COLOR = "#16798a"
ENTRY_BG = "#174953"
HIGHLIGHT = "#30f0ff"

class CrystalCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔷 Crystal Canvas")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("720x860")
        self.root.resizable(True, True)

        # App state
        self.pipe = self.load_model()
        self.selected_size = 512
        self.animating = False
        self.dot_state = 0

        # Widgets
        self.size_buttons = {}
        self.steps_entry = None
        self.step_status = None
        self.prompt_entry = None
        self.status_label = None
        self.image_label = None
        self.generate_btn = None

        self.setup_ui()

    def load_model(self):
        model_path = os.path.abspath(os.path.join("sdxl-turbo"))
        pipe = StableDiffusionXLPipeline.from_pretrained(model_path, torch_dtype=torch.float32, local_files_only=True )
        pipe.to("cpu")
        return pipe

    def setup_ui(self):
        tk.Label(self.root, text="🔷 Crystal Canvas", font=("Segoe UI", 24, "bold"),
                 fg=HIGHLIGHT, bg=BG_COLOR).pack(pady=20)

        # Prompt
        prompt_frame = tk.Frame(self.root, bg=BG_COLOR)
        prompt_frame.pack(pady=15)
        tk.Label(prompt_frame, text="Describe Your Vision:", font=("Segoe UI", 12),
                 fg=FG_COLOR, bg=BG_COLOR).pack(anchor="w", padx=10)
        self.prompt_entry = tk.Entry(prompt_frame, font=("Segoe UI", 12),
                                     bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
                                     width=60, relief="flat", highlightthickness=1,
                                     highlightbackground=HIGHLIGHT)
        self.prompt_entry.pack(pady=5, padx=10)

        # Size
        size_frame = tk.LabelFrame(self.root, text="Image Size", font=("Segoe UI", 11, "bold"),
                                   fg=HIGHLIGHT, bg=BG_COLOR, padx=10, pady=10)
        size_frame.pack(pady=10)
        for size in [256, 512, 1024]:
            btn = tk.Button(size_frame, text=f"{size}×{size}", font=("Segoe UI", 10),
                            bg=BTN_COLOR, fg=FG_COLOR, activebackground=HIGHLIGHT,
                            activeforeground=BG_COLOR, padx=12, pady=6, relief="flat",
                            highlightbackground=HIGHLIGHT,
                            command=lambda s=size: self.set_image_size(s))
            btn.pack(side="left", padx=8)
            self.size_buttons[size] = btn
        self.update_size_buttons()

        # Inference Steps
        step_frame = tk.Frame(self.root, bg=BG_COLOR)
        step_frame.pack(pady=10)
        tk.Label(step_frame, text="Inference Steps (1–50):", font=("Segoe UI", 12),
                 fg=FG_COLOR, bg=BG_COLOR).pack()
        self.step_status = tk.Label(step_frame, text="", font=("Segoe UI", 9),
                                    fg="#FF8C00", bg=BG_COLOR)
        self.step_status.pack(pady=(0, 5))
        vcmd = (self.root.register(self.validate_steps_input), "%P")
        self.steps_entry = tk.Entry(step_frame, font=("Segoe UI", 10), width=12, justify="center",
                                    bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
                                    relief="solid", highlightbackground=HIGHLIGHT,
                                    validate="key", validatecommand=vcmd)
        self.steps_entry.insert(0, "50")
        self.steps_entry.pack()
        self.steps_entry.bind("<FocusOut>", lambda event: self.get_validated_steps())

        # Generate button
        self.generate_btn = tk.Button(self.root, text="Generate Image", font=("Segoe UI", 12, "bold"),
                                      bg=BTN_COLOR, fg=FG_COLOR, activebackground=HIGHLIGHT,
                                      activeforeground=BG_COLOR, padx=12, pady=8, relief="flat",
                                      highlightbackground=HIGHLIGHT,
                                      command=self.generate)
        self.generate_btn.pack(pady=20)

        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Segoe UI", 12),
                                     fg=FG_COLOR, bg=BG_COLOR)
        self.status_label.pack()

        # Image preview
        self.image_label = tk.Label(self.root, bg=BG_COLOR)
        self.image_label.pack(pady=10)

        # Footer
        tk.Label(self.root, text="Powered by SDXL-Turbo • CPU Mode", font=("Segoe UI", 9),
                 fg=FG_COLOR, bg=BG_COLOR).pack(side="bottom", pady=10)

    def set_image_size(self, new_size):
        self.selected_size = new_size
        self.update_size_buttons()

    def update_size_buttons(self):
        for size, btn in self.size_buttons.items():
            btn.config(bg=HIGHLIGHT if size == self.selected_size else BTN_COLOR,
                       relief="sunken" if size == self.selected_size else "raised")

    def validate_steps_input(self, new_value):
        if new_value == "":
            self.step_status.config(text="")
            return True
        if new_value.isdigit():
            val = int(new_value)
            if 1 <= val <= 50:
                self.step_status.config(text="")
                return True
            else:
                self.step_status.config(text="Must be between 1 and 50")
                return False
        self.step_status.config(text="Only numbers 1–50 allowed")
        return False

    def get_validated_steps(self):
        raw = self.steps_entry.get()
        try:
            steps = int(raw)
            if 1 <= steps <= 50:
                self.step_status.config(text="")
                return steps
            clamped = max(1, min(steps, 50))
            self.steps_entry.delete(0, tk.END)
            self.steps_entry.insert(0, str(clamped))
            self.step_status.config(text=f"Out of range — reset to {clamped}")
            return clamped
        except ValueError:
            self.steps_entry.delete(0, tk.END)
            self.steps_entry.insert(0, "50")
            self.step_status.config(text="Invalid input — reset to 50")
            return 50

    def get_next_image_number(self, folder="outputs"):
        Path(folder).mkdir(exist_ok=True)
        existing = [f.name for f in Path(folder).glob("image*.png")]
        nums = [int(re.match(r"image(\d+)\.png", f).group(1)) for f in existing if re.match(r"image(\d+)\.png", f)]
        return max(nums) + 1 if nums else 1

    def generate(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showerror("Missing Prompt", "Please enter a text prompt to generate.")
            return

        steps = self.get_validated_steps()
        self.generate_btn.config(state="disabled")
        self.status_label.config(text="Generating, please wait")
        self.animating = True
        self.dot_state = 0
        self.animate_dots()

        threading.Thread(target=self.run_generation, args=(prompt, steps), daemon=True).start()

    def animate_dots(self):
        if not self.animating:
            return
        dots = "." * (self.dot_state % 4)
        self.status_label.config(text=f"Generating, please wait{dots}")
        self.dot_state += 1
        self.root.after(500, self.animate_dots)

    def run_generation(self, prompt, steps):
        try:
            image = self.pipe(prompt,
                              num_inference_steps=steps,
                              height=self.selected_size,
                              width=self.selected_size).images[0]

            image_num = self.get_next_image_number()
            filename = f"outputs/image{image_num}.png"
            image.save(filename)

            img_resized = image.resize((512, 512))
            tk_img = ImageTk.PhotoImage(img_resized)
            self.root.after(0, self.display_image, tk_img)

        except Exception:
            traceback_str = traceback.format_exc()
            self.root.after(0, messagebox.showerror, "Generation Error", "Image generation failed. See error_log.txt.")
            with open("error_log.txt", "w", encoding="utf-8") as log:
                log.write(traceback_str)
        finally:
            self.root.after(0, self.finish_generation)

    def display_image(self, tk_img):
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img

    def finish_generation(self):
        self.animating = False
        self.status_label.config(text="Completed!")
        self.generate_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CrystalCanvasApp(root)
    root.mainloop()