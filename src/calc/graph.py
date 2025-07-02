import math
import tkinter as tk
from tkinter import ttk, messagebox
from itertools import repeat
from typing import Final

from .core import (
    fight_prob as default_fight_prob,
    fights_needed as default_fights_needed,
    cumulative as default_cumulative,
)
from .models import GameVersion

class DropCalc(tk.Tk):
    def __init__(
        self,
        fight_prob=default_fight_prob,
        fights_needed=default_fights_needed,
        cumulative=default_cumulative,
    ):
        super().__init__()
        self.configure(bg=BG)

        self.group_prob = fight_prob
        self.fights_needed = fights_needed
        self.cumulative = cumulative
        self.title("Dofus Rétro – Calculateur de Drop")
        self.minsize(560, 420)

        # Cl\xe9 = nom affich\xe9 ; Valeur = tuple(taux_decimal, lock_PP)
        self.resources: dict[str, tuple[float | None, int]] = {
            "Vulbis\xa0(0,001\u202f%)":    (0.00001, 800),
            "Turquoise\xa0(0,02\u202f%)":  (0.0002,  800),
            "Personnalisé":                (None,    0),   # sera g\xe9r\xe9 \xe0 part
        }

        self._style_ttk()
        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_calc = ttk.Frame(notebook)
        notebook.add(self.tab_calc, text="Calcul")

        try:
            import matplotlib  # noqa: F401
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self._Figure = Figure
            self._FigureCanvas = FigureCanvasTkAgg
            self.tab_graph = ttk.Frame(notebook)
            notebook.add(self.tab_graph, text="Graphique")
            self._graph_ready = True
        except ModuleNotFoundError:
            self._graph_ready = False

        self._inputs_section(self.tab_calc)
        self._outputs_section(self.tab_calc)

        if self._graph_ready:
            self._build_graph(self.tab_graph)

    def _style_ttk(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=BG, foreground=FG_TXT, font=FONT)
        style.configure("TLabelFrame", background=BG, foreground=FG_TXT)
        style.configure("TEntry", fieldbackground="#303030", foreground=FG_TXT)
        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", background="#282828", foreground=FG_TXT)
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#2e2e2e")],
            foreground=[("selected", FG_TXT)],
        )

        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="white",
            relief="flat",
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#ff6b58")],
            foreground=[("disabled", "#777777")],
        )

    def _inputs_section(self, parent):
        f = ttk.LabelFrame(parent, text="Paramètres", padding=15)
        f.pack(side="left", fill="y", padx=(0, 10), pady=5)

        ttk.Label(f, text="Dofus\xa0:").grid(row=0, column=0, sticky="w")
        self.dofus_var = tk.StringVar(value=list(self.resources)[0])
        menu = ttk.OptionMenu(
            f,
            self.dofus_var,
            self.dofus_var.get(),
            *self.resources.keys(),
            command=lambda *_: self._on_dofus_change(),
        )
        self.option_menu_ref = menu
        menu.grid(row=0, column=1, sticky="ew")
        self._create_tooltip(menu, "Sélectionne un Dofus ou 'Personnalisé'.")

        add_btn = ttk.Button(
            f,
            text="+",
            width=3,
            style="Accent.TButton",
            command=self._open_add_resource_dialog,
        )
        add_btn.grid(row=0, column=2, padx=(4, 0))
        self._create_tooltip(add_btn, "Ajouter une nouvelle ressource")

        ttk.Label(f, text="Taux base\u202f(%)\u202f:").grid(row=1, column=0, sticky="w")
        self.base_entry = ttk.Entry(f, width=10)
        self.base_entry.grid(row=1, column=1, sticky="ew")

        self.version_var = tk.StringVar(value="RETRO")
        rb_retro = ttk.Radiobutton(
            f, text="Rétro", variable=self.version_var, value="RETRO"
        )
        rb_v2 = ttk.Radiobutton(
            f, text="2.x", variable=self.version_var, value="V2"
        )
        rb_retro.grid(row=1, column=2, sticky="w", padx=(8, 0))
        rb_v2.grid(row=2, column=2, sticky="w", padx=(8, 0))

        self.mode_var = tk.StringVar(value="total")
        rb_tot = ttk.Radiobutton(
            f,
            text="PP totale",
            variable=self.mode_var,
            value="total",
            command=self._toggle_pp_mode,
        )
        rb_list = ttk.Radiobutton(
            f,
            text="PP par perso",
            variable=self.mode_var,
            value="list",
            command=self._toggle_pp_mode,
        )
        rb_tot.grid(row=2, column=0, sticky="w")
        rb_list.grid(row=2, column=1, sticky="w")

        self.pp_total_entry = ttk.Entry(f)
        self.pp_total_entry.insert(0, "800")
        self.pp_total_entry.grid(row=3, column=0, columnspan=2, sticky="ew")
        self._create_tooltip(self.pp_total_entry, "Somme\u202fPP du groupe.")

        self.pp_list_entry = ttk.Entry(f)
        self._create_tooltip(
            self.pp_list_entry,
            "Exemple\u202f: 150, 200, 100, 120… jusqu'\xe0 8 valeurs.",
        )

        ttk.Label(f, text="Nb persos\xa0:").grid(row=4, column=0, sticky="w")
        self.group_entry = ttk.Entry(f, width=5)
        self.group_entry.insert(0, "8")
        self.group_entry.grid(row=4, column=1, sticky="w")

        ttk.Label(f, text="Proba cible\u202f(%)\u202f:").grid(row=5, column=0, sticky="w")
        self.target_entry = ttk.Entry(f, width=7)
        self.target_entry.insert(0, "50")
        self.target_entry.grid(row=5, column=1, sticky="w")

        ttk.Label(f, text="Combats simulés\xa0:").grid(row=6, column=0, sticky="w")
        self.n_entry = ttk.Entry(f, width=7)
        self.n_entry.insert(0, "100")
        self.n_entry.grid(row=6, column=1, sticky="w")

        calc_btn = ttk.Button(
            f,
            text="Calculer",
            style="Accent.TButton",
            command=self._calculate,
        )
        calc_btn.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        parent.columnconfigure(0, weight=1)

        self._on_dofus_change()

    def _outputs_section(self, parent):
        g = ttk.LabelFrame(parent, text="Résultats", padding=15)
        g.pack(side="right", fill="both", expand=True, pady=5)

        self.res = {}
        labels = (
            "Chance par combat\u202f: ",
            "Combats nécessaires\u202f: ",
            "Proba après N\u202f: ",
        )
        for r, txt in enumerate(labels):
            ttk.Label(g, text=txt).grid(row=r, column=0, sticky="w", padx=5, pady=4)
            self.res[r] = ttk.Label(g, text="—")
            self.res[r].grid(row=r, column=1, sticky="w")

    def _build_graph(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="Courbe de probabilité cumulée",
            background=BG,
            foreground=FG_TXT,
        ).pack(pady=6)

        self.fig = self._Figure(figsize=(5.5, 3), tight_layout=True)
        self.fig.patch.set_facecolor(BG)
        self.ax = self.fig.add_subplot(111, facecolor=AX_BG)

        self.canvas = self._FigureCanvas(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=4)

    def _toggle_pp_mode(self):
        mode = self.mode_var.get()
        if mode == "total":
            self.pp_total_entry.grid()
            self.pp_list_entry.grid_remove()
            self.group_entry.config(state="normal")
        else:
            self.pp_total_entry.grid_remove()
            self.pp_list_entry.grid(row=3, column=0, columnspan=2, sticky="ew")
            self.group_entry.config(state="disabled")

    def _on_dofus_change(self) -> None:
        rate, _lock = self.resources.get(self.dofus_var.get(), (None, 0))
        self.base_entry.config(state="normal")
        self.base_entry.delete(0, tk.END)
        if rate is not None:
            self.base_entry.insert(0, f"{rate * 100:.6f}")
            self.base_entry.config(state="disabled")
        else:
            # « Personnalisé » → l’utilisateur saisit la valeur
            self.base_entry.config(state="normal")

    def _parse_pp(self):
        if self.mode_var.get() == "total":
            pp_total = float(self.pp_total_entry.get())
            n = int(self.group_entry.get())
            if n <= 0 or n > 8:
                raise ValueError("Nombre de personnages\u202f: 1\u202f–\u202f8.")
            return list(repeat(pp_total / n, n))
        vals = [float(v.strip()) for v in self.pp_list_entry.get().split(",") if v.strip()]
        if not 1 <= len(vals) <= 8:
            raise ValueError("Saisir 1 \xc3\xa0 8 valeurs PP.")
        return vals

    def _calculate(self, *_):
        try:
            base_pct = float(self.base_entry.get())
            if not 0 < base_pct < 100:
                raise ValueError("Taux de base hors bornes.")
            base_rate = base_pct / 100

            pp_values = self._parse_pp()
            target_p = float(self.target_entry.get()) / 100
            if not 0 < target_p < 1:
                raise ValueError("Proba cible 0\u202f<\u202fx\u202f<\u202f100.")
            n_sim = int(self.n_entry.get())
            if n_sim < 1:
                raise ValueError("Combats simulés \u2265\u202f1.")

            # -- probabilité par combat --
            rate, lock_pp = self.resources[self.dofus_var.get()]
            if rate is None:            # cas « Personnalisé »
                rate = base_rate        # déjà saisi dans base_entry
            total_pp = sum(pp_values)
            version = GameVersion[self.version_var.get()]

            # Si le total de PP est inférieur au lock → probabilité 0
            p_fight = (
                0.0
                if total_pp < lock_pp
                else self.group_prob(rate, pp_values, monsters=1, version=version)
            )
            need = self.fights_needed(target_p, p_fight)
            cumu = self.cumulative(p_fight, n_sim)

            self.res[0].config(text=f"{p_fight * 100:.6f}\u202f%")
            self.res[1].config(text="\u221e" if need == math.inf else f"{need:,}")
            self.res[2].config(text=f"{cumu * 100:.2f}\u202f%")

            if self._graph_ready:
                self._update_graph(p_fight)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _cumulative(self, p_fight: float, n: int) -> float:
        """Wrapper around the provided cumulative function."""
        return self.cumulative(p_fight, n)

    def _update_graph(self, p_fight: float) -> None:
        self.ax.clear()

        # Données
        x_vals = range(1, 501)
        y_vals = [self._cumulative(p_fight, n) * 100 for n in x_vals]

        # Courbe rouge
        self.ax.plot(x_vals, y_vals, color=ACCENT, linewidth=2)

        # Axes / ticks
        self.ax.set_xlabel("Combats", color=FG_TXT)
        self.ax.set_ylabel("Probabilité cumulée (%)", color=FG_TXT)
        self.ax.tick_params(colors=FG_TXT)
        for spine in self.ax.spines.values():
            spine.set_color(FG_TXT)

        # Fond / grille
        self.ax.set_facecolor(AX_BG)
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, color=GRID, linestyle="--", linewidth=0.5)

        self.canvas.draw()

    def _create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.config(bg="#2b2b2b", padx=4, pady=2)
        ttk.Label(
            tooltip,
            text=text,
            background="#2b2b2b",
            foreground=FG_TXT,
            font=FONT,
        ).pack()

        def enter(_):
            tooltip.deiconify()
            self._move_tip(widget, tooltip)

        def leave(_):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _move_tip(self, w, tip):
        x = w.winfo_rootx() + 20
        y = w.winfo_rooty() + w.winfo_height() + 2
        tip.geometry(f"+{x}+{y}")

    def _refresh_resource_menu(self) -> None:
        """Reconstruit le OptionMenu après ajout / suppression."""
        menu = self.option_menu_ref
        menu["menu"].delete(0, "end")
        for res in self.resources:
            menu["menu"].add_command(
                label=res,
                command=tk._setit(self.dofus_var, res, self._on_dofus_change),
            )

    def _open_add_resource_dialog(self) -> None:
        dlg = tk.Toplevel(self)
        dlg.title("Ajouter une ressource")
        dlg.grab_set()
        dlg.configure(bg=BG)

        ttk.Label(dlg, text="Nom :", background=BG, foreground=FG_TXT).grid(row=0, column=0, sticky="e", pady=4, padx=4)
        name_entry = ttk.Entry(dlg, width=25)
        name_entry.grid(row=0, column=1, pady=4, padx=4)

        ttk.Label(dlg, text="Taux de base (%) :", background=BG, foreground=FG_TXT).grid(row=1, column=0, sticky="e", pady=4, padx=4)
        rate_entry = ttk.Entry(dlg, width=10)
        rate_entry.grid(row=1, column=1, pady=4, padx=4)

        ttk.Label(dlg, text="PP‑lock (≥) :", background=BG, foreground=FG_TXT).grid(row=2, column=0, sticky="e", pady=4, padx=4)
        lock_entry = ttk.Entry(dlg, width=10)
        lock_entry.grid(row=2, column=1, pady=4, padx=4)

        def save() -> None:
            try:
                name = name_entry.get().strip()
                if not name:
                    raise ValueError("Nom vide.")
                if name in self.resources:
                    raise ValueError("Cette ressource existe déjà.")
                rate_pct = float(rate_entry.get())
                if not 0 < rate_pct < 100:
                    raise ValueError("Taux hors bornes 0‑100.")
                lock_pp = int(lock_entry.get())
                if lock_pp < 0:
                    raise ValueError("Lock négatif interdit.")
            except Exception as err:
                messagebox.showerror("Erreur", str(err), parent=dlg)
                return

            self.resources[name] = (rate_pct / 100.0, lock_pp)
            self._refresh_resource_menu()
            dlg.destroy()

        ttk.Button(dlg, text="Enregistrer", style="Accent.TButton", command=save)\
           .grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

# ---------------------------------------------------------------------------
#  Couleurs (dark / rouge)
# ---------------------------------------------------------------------------
BG: Final[str] = "#1a1a1a"   # fond fenêtre
FG_TXT: Final[str] = "#f0f0f0"   # texte général
ACCENT: Final[str] = "#e74c3c"   # rouge accent (boutons + courbe)
AX_BG: Final[str] = "#212121"   # fond du graphique
GRID: Final[str] = "#444444"   # grille claire
FONT: Final[tuple[str, int]] = ("Segoe UI", 10)

__all__ = ["DropCalc"]
