import tkinter as tk
from typing import Optional

from InfoPanel.gui.validator import validate, StartupFormData


class StartupDialog:
    def __init__(self) -> None:
        self._result: Optional[StartupFormData] = None

        self._root = tk.Tk()
        self._root.title("Настройки")
        self._root.geometry("360x250")
        self._root.resizable(False, False)
        self._root.attributes("-topmost", True)

        self._entry_com: tk.Entry
        self._entry_api_key: tk.Entry
        self._entry_city: tk.Entry
        self._error_label: tk.Label

        self._build_ui()

    def _build_ui(self) -> None:
        root = self._root
        root.columnconfigure(1, weight=1)

        fields = [
            ("COM порт:",         "_entry_com",     False),
            ("Город (на англ.):", "_entry_city",    False),
            ("API key:",          "_entry_api_key", True),
        ]

        for row, (label_text, attr, secret) in enumerate(fields):
            tk.Label(root, text=label_text, font=("Arial", 11)).grid(
                row=row, column=0, padx=10, pady=(20 if row == 0 else 5, 5), sticky="w"
            )
            entry = tk.Entry(root, font=("Arial", 12), show="*" if secret else "")
            entry.grid(row=row, column=1, padx=10, pady=(20 if row == 0 else 5, 5), sticky="ew")
            setattr(self, attr, entry)

        self._entry_com.focus_set()

        self._error_label = tk.Label(root, text="", fg="red", font=("Arial", 10))
        self._error_label.grid(row=3, column=0, columnspan=2, pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        tk.Button(btn_frame, text="OK",      width=10, command=self._on_ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Отмена", width=10, command=root.destroy).pack(side="left", padx=5)

        root.bind("<Return>", lambda _: self._on_ok())
        root.bind("<Escape>", lambda _: root.destroy())

    def _on_ok(self) -> None:
        data, error = validate(
            self._entry_com.get(),
            self._entry_api_key.get(),
            self._entry_city.get(),
        )
        if error:
            self._error_label.config(text=error)
            return

        self._result = data
        self._root.destroy()

    def ask(self) -> Optional[StartupFormData]:
        self._root.mainloop()
        return self._result