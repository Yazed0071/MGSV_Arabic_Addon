import tkinter as tk
from tkinter import ttk, messagebox

import re
try:
    from arabic_reshaper import ArabicReshaper
    from bidi.algorithm import get_display
except Exception:
    ArabicReshaper = None
    get_display = None

# --- Arabic handling ---
arabic_re = re.compile(r"[؀-ۿ]")


def make_reshaper(delete_harakat: bool):
    if ArabicReshaper is None or get_display is None:
        raise ImportError(
            "This app needs 'arabic-reshaper' and 'python-bidi'."
            "Install with: pip install arabic-reshaper python-bidi"
        )
    return ArabicReshaper({"delete_harakat": delete_harakat})


def fix_arabic_text(text: str, reshaper: "ArabicReshaper") -> str:
    if not text or not arabic_re.search(text):
        return text
    reshaped = reshaper.reshape(text)
    return get_display(reshaped)


class TextApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arabic Text Reshaper")
        self.geometry("980x720")
        self.minsize(820, 560)

        # State
        self.var_delete_harakat = tk.BooleanVar(value=False)  # False = keep diacritics
        self.var_live = tk.BooleanVar(value=True)
        self._reshaper = None

        self._build_ui()
        if ArabicReshaper is None or get_display is None:
            self.after(200, self._warn_missing_deps)

    # ---------------- UI -----------------
    def _build_ui(self):
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        # Controls row
        controls = ttk.Frame(outer)
        controls.pack(fill=tk.X)

        ttk.Checkbutton(
            controls,
            text="Delete Harakat",
            variable=self.var_delete_harakat,
            command=self._maybe_reprocess,
        ).pack(side=tk.LEFT)

        ttk.Checkbutton(
            controls,
            text="Live processing",
            variable=self.var_live,
        ).pack(side=tk.LEFT, padx=(12, 0))

        ttk.Button(controls, text="Process now", command=self.process_once).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Button(controls, text="Copy output", command=self.copy_output).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(controls, text="Swap", command=self.swap_io).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(controls, text="Clear", command=self.clear_both).pack(side=tk.LEFT, padx=(6, 0))

        # Paned layout for Input / Output
        paned = ttk.PanedWindow(outer, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        # Input
        in_frame = ttk.LabelFrame(paned, text="Input (plain text)", padding=8)
        self.txt_in = tk.Text(in_frame, wrap=tk.WORD, undo=True)
        self.txt_in.pack(fill=tk.BOTH, expand=True)
        self.txt_in.bind("<KeyRelease>", self._on_input_changed)
        paned.add(in_frame, weight=1)

        # Output
        out_frame = ttk.LabelFrame(paned, text="Output (reshaped for correct Arabic display)", padding=8)
        self.txt_out = tk.Text(out_frame, wrap=tk.WORD)
        self.txt_out.pack(fill=tk.BOTH, expand=True)
        self.txt_out.config(state=tk.DISABLED)
        paned.add(out_frame, weight=1)

        # Status bar
        self.status = ttk.Label(outer, text="Ready", anchor="w")
        self.status.pack(fill=tk.X, pady=(8, 0))

    # ------------- Actions --------------
    def _ensure_reshaper(self):
        if self._reshaper is None:
            self._reshaper = make_reshaper(self.var_delete_harakat.get())
        return self._reshaper

    def _recreate_reshaper_if_needed(self):
        # Always recreate when toggle changes to keep behavior explicit
        self._reshaper = make_reshaper(self.var_delete_harakat.get())

    def process_once(self, *_):
        try:
            self._recreate_reshaper_if_needed()
            text = self.txt_in.get("1.0", tk.END)
            out = self._process_text_block(text)
            self._set_output(out)
            self._set_status("Processed")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._set_status("Error")

    def _process_text_block(self, text: str) -> str:
        reshaper = self._ensure_reshaper()
        # Process line-by-line so paragraph breaks remain identical
        lines = text.splitlines()
        fixed_lines = [fix_arabic_text(line, reshaper) for line in lines]
        return "".join(fixed_lines)

    def _set_output(self, text: str):
        self.txt_out.config(state=tk.NORMAL)
        self.txt_out.delete("1.0", tk.END)
        self.txt_out.insert("1.0", text)
        self.txt_out.config(state=tk.DISABLED)

    def copy_output(self):
        out = self.txt_out.get("1.0", tk.END).strip("")
        self.clipboard_clear()
        self.clipboard_append(out)
        self._set_status("Output copied to clipboard")

    def swap_io(self):
        inp = self.txt_in.get("1.0", tk.END)
        out = self.txt_out.get("1.0", tk.END)
        self.txt_in.delete("1.0", tk.END)
        self.txt_in.insert("1.0", out)
        self._set_output(inp)
        self._set_status("Swapped input/output")

    def clear_both(self):
        self.txt_in.delete("1.0", tk.END)
        self._set_output("")
        self._set_status("Cleared")

    # ------------- Event hooks ----------
    def _on_input_changed(self, event):
        if not self.var_live.get():
            return
        try:
            # Only recreate reshaper when checkbox actually toggled, but in live mode
            # we still need a reshaper.
            self._ensure_reshaper()
            text = self.txt_in.get("1.0", tk.END)
            out = self._process_text_block(text)
            self._set_output(out)
            self._set_status("Live")
        except Exception as e:
            self._set_status(f"Error: {e}")

    def _maybe_reprocess(self):
        # Called when harakat checkbox toggles
        if self.var_live.get():
            self.process_once()

    # ------------- Utils ----------------
    def _set_status(self, msg: str):
        self.status.config(text=msg)

    def _warn_missing_deps(self):
        messagebox.showwarning(
            "Missing dependencies",
            (
                "This app needs 'arabic-reshaper' and 'python-bidi'"
                "Install them with:"
                "  pip install arabic-reshaper python-bidi"
                "Then restart the app."
            ), 
        )


if __name__ == "__main__":
    app = TextApp()
    app.mainloop()
