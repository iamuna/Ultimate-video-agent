from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from video_agent.models import ProductionRequest
from video_agent.producer import produce_video


class UltimateVideoAgentApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Ultimate Video Agent - v0.1")
        self.geometry("1000x780")
        self.minsize(900, 700)

        self.video_var = ctk.StringVar()
        self.count_var = ctk.StringVar(value="5")
        self.focus_var = ctk.StringVar(value="Auto")
        self.vertical_var = ctk.BooleanVar(value=True)
        self.reframe_var = ctk.BooleanVar(value=True)
        self.captions_var = ctk.BooleanVar(value=True)
        self.force_var = ctk.BooleanVar(value=False)
        self.last_output: Path | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        title = ctk.CTkLabel(
            self,
            text="ULTIMATE VIDEO AGENT",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.grid(row=0, column=0, padx=24, pady=(22, 8), sticky="w")

        subtitle = ctk.CTkLabel(
            self,
            text="Video Production Agent • v0.1 Autonomous Clipping Producer",
        )
        subtitle.grid(row=1, column=0, padx=24, pady=(0, 14), sticky="w")

        source = ctk.CTkFrame(self)
        source.grid(row=2, column=0, padx=24, pady=8, sticky="ew")
        source.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(source, text="Source video").grid(
            row=0, column=0, padx=(16, 8), pady=14
        )
        ctk.CTkEntry(source, textvariable=self.video_var).grid(
            row=0, column=1, padx=8, pady=14, sticky="ew"
        )
        ctk.CTkButton(source, text="Browse", width=100, command=self._browse).grid(
            row=0, column=2, padx=(8, 16), pady=14
        )

        controls = ctk.CTkFrame(self)
        controls.grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        controls.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            controls,
            text="Production objective",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(14, 6), sticky="w")

        self.goal = ctk.CTkTextbox(controls, height=96)
        self.goal.grid(row=1, column=0, columnspan=6, padx=16, pady=(0, 12), sticky="ew")
        self.goal.insert(
            "1.0",
            "Find the strongest important, interesting, controversial, or emotional "
            "moments. Keep enough context to make each clip understandable and honest.",
        )

        ctk.CTkLabel(controls, text="Clips").grid(row=2, column=0, padx=(16, 6), pady=10)
        ctk.CTkOptionMenu(
            controls,
            values=[str(i) for i in range(1, 11)],
            variable=self.count_var,
            width=90,
        ).grid(row=2, column=1, padx=6, pady=10)

        ctk.CTkLabel(controls, text="Focus").grid(row=2, column=2, padx=(16, 6), pady=10)
        ctk.CTkOptionMenu(
            controls,
            values=["Auto", "Balanced", "Important", "Controversial", "Interesting", "Emotional"],
            variable=self.focus_var,
            width=150,
        ).grid(row=2, column=3, padx=6, pady=10)

        ctk.CTkCheckBox(
            controls, text="9:16 vertical", variable=self.vertical_var
        ).grid(row=3, column=0, columnspan=2, padx=16, pady=(4, 12), sticky="w")
        ctk.CTkCheckBox(
            controls, text="Smart reframe", variable=self.reframe_var
        ).grid(row=3, column=2, padx=8, pady=(4, 12), sticky="w")
        ctk.CTkCheckBox(
            controls, text="Captions", variable=self.captions_var
        ).grid(row=3, column=3, padx=8, pady=(4, 12), sticky="w")
        ctk.CTkCheckBox(
            controls, text="Re-analyze", variable=self.force_var
        ).grid(row=3, column=4, padx=8, pady=(4, 12), sticky="w")

        action = ctk.CTkFrame(self)
        action.grid(row=4, column=0, padx=24, pady=8, sticky="ew")
        action.grid_columnconfigure(2, weight=1)
        self.produce_button = ctk.CTkButton(
            action,
            text="PRODUCE CLIPS",
            width=180,
            height=42,
            command=self._start,
        )
        self.produce_button.grid(row=0, column=0, padx=14, pady=14)
        self.open_button = ctk.CTkButton(
            action,
            text="Open output",
            width=130,
            state="disabled",
            command=self._open_output,
        )
        self.open_button.grid(row=0, column=1, padx=(0, 14), pady=14)
        self.status = ctk.CTkLabel(action, text="Ready")
        self.status.grid(row=0, column=2, padx=14, pady=14, sticky="w")

        self.log = ctk.CTkTextbox(self)
        self.log.grid(row=5, column=0, padx=24, pady=(8, 24), sticky="nsew")
        self._append("Ready. Choose a video, describe what you want, then click PRODUCE CLIPS.")

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose a source video",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.mkv *.webm *.m4v"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.video_var.set(path)

    def _append(self, message: str) -> None:
        self.log.insert("end", message.rstrip() + "\n")
        self.log.see("end")

    def _thread_log(self, message: str) -> None:
        self.after(0, self._append, message)

    def _start(self) -> None:
        source = Path(self.video_var.get().strip())
        if not source.is_file():
            self._append("ERROR: choose a valid source video.")
            return

        goal = self.goal.get("1.0", "end").strip()
        self.produce_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.status.configure(text="Working...")
        self._append("")
        self._append("=== New production job ===")

        request = ProductionRequest(
            source_video=source,
            goal=goal,
            output_count=int(self.count_var.get()),
            focus=self.focus_var.get(),
            vertical=bool(self.vertical_var.get()),
            smart_reframe=bool(self.reframe_var.get()),
            burn_captions=bool(self.captions_var.get()),
            force_analysis=bool(self.force_var.get()),
        )
        threading.Thread(
            target=self._worker,
            args=(request,),
            daemon=True,
        ).start()

    def _worker(self, request: ProductionRequest) -> None:
        try:
            result = produce_video(request, progress=self._thread_log)
        except Exception as exc:
            self.after(0, self._failed, str(exc))
            return
        self.after(0, self._finished, result)

    def _failed(self, message: str) -> None:
        self._append(f"ERROR: {message}")
        self.status.configure(text="Failed")
        self.produce_button.configure(state="normal")

    def _finished(self, result) -> None:
        self.last_output = Path(result.output_dir)
        self._append("")
        self._append(f"Director strategy: {result.plan.strategy}")
        for clip in result.clips:
            qc = "PASS" if clip.qc.passed else "CHECK"
            self._append(
                f"[{qc}] {clip.title} • {clip.final_score:.1f}/100 • "
                f"{Path(clip.output_path).name}"
            )
            if clip.qc.issues:
                self._append("  QC: " + "; ".join(clip.qc.issues))
            if clip.qc.warnings:
                self._append("  Notes: " + "; ".join(clip.qc.warnings))
        self._append(f"Manifest: {result.manifest_path}")
        self.status.configure(text=f"Done • {len(result.clips)} clips")
        self.produce_button.configure(state="normal")
        self.open_button.configure(state="normal")

    def _open_output(self) -> None:
        if not self.last_output or not self.last_output.exists():
            return
        path = str(self.last_output)
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    app = UltimateVideoAgentApp()
    app.mainloop()
