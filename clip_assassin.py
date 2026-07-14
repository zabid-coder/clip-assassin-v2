import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import threading
import sys
import os

# Import our backend engine
from resolve_core import ResolveConnection

class ClipAssassinApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.resolve_core = ResolveConnection()
        self.placeholder_text = "1m57-2m08\n3m10-3m22"
        
        # Window setup
        self.title("Clip Assassin — DaVinci Resolve Workflow Automator")
        self.geometry("900x750")
        self.minsize(800, 700)
        
        # Color Palette - Modern Purple Theme (Inspired by Inspiration Image)
        self.color_bg = "#1A1025"       # Deep dark purple background
        self.color_card = "#2A1B3D"     # Lighter purple for cards
        self.color_primary = "#6D28D9"  # Vibrant Purple (Primary buttons)
        self.color_secondary = "#4F46E5" # Indigo (Secondary buttons)
        self.color_warning = "#D946EF"  # Fuchsia/Pink instead of Amber
        self.color_error = "#F43F5E"    # Rose Red
        self.color_success = "#10B981"  # Emerald
        self.color_text = "#FFFFFF"     # Pure white text
        self.color_muted = "#A78BFA"    # Light lavender for muted text
        self.color_border = "#3B2859"   # Subtle purple border
        self.color_input = "#1F1330"    # Very dark purple for inputs
        self.color_text_dark = "#FFFFFF"
        
        self.font_sans = "Inter"
        self.font_mono = "JetBrains Mono"
        
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=self.color_bg)
        
        # Top connection bar
        self.create_connection_bar()
        
        # Tabs container
        self.tabview = ctk.CTkTabview(
            self, 
            corner_radius=20,
            fg_color=self.color_card,
            segmented_button_fg_color=self.color_bg,
            segmented_button_selected_color=self.color_primary,
            segmented_button_selected_hover_color=self.color_secondary
        )
        self.tabview.pack(padx=20, pady=(10, 10), fill="both", expand=True)
        
        self.tab_cut = self.tabview.add("✂️ Cut & Extract")
        self.tab_process = self.tabview.add("🔄 Process")
        self.tab_export = self.tabview.add("📤 Export")
        
        # Create UIs
        self.create_cut_tab()
        self.create_process_tab()
        self.create_export_tab()
        
        # Log Panel (Always visible at bottom)
        self.create_log_panel()

    def _get_font(self, size, weight="normal"):
        return ctk.CTkFont(family=self.font_sans, size=size, weight=weight)

    def create_connection_bar(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))
        
        self.status_dot = ctk.CTkLabel(header, text="●", text_color=self.color_error, font=self._get_font(24))
        self.status_dot.pack(side="left", padx=(0, 10))
        
        self.status_label = ctk.CTkLabel(header, text="Not Connected", text_color=self.color_error, font=self._get_font(16, "bold"))
        self.status_label.pack(side="left")
        
        self.connect_btn = ctk.CTkButton(
            header,
            text="Connect / Refresh",
            command=self.connect_to_resolve,
            fg_color=self.color_primary,
            hover_color=self.color_secondary,
            font=self._get_font(14, "bold"),
            height=36,
            corner_radius=18
        )
        self.connect_btn.pack(side="right")

    # ---------------------------------------------------------
    # TAB: CUT & EXTRACT
    # ---------------------------------------------------------
    def create_cut_tab(self):
        scrollable = ctk.CTkScrollableFrame(self.tab_cut, fg_color="transparent")
        scrollable.pack(fill="both", expand=True)

        # 1. Timecode Cutter
        f1 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f1.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f1, text="✂️ Timecode Cutter", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.timecodes_text = ctk.CTkTextbox(f1, height=100, fg_color=self.color_input, border_color=self.color_border, border_width=1)
        self.timecodes_text.pack(fill="x", padx=16, pady=5)
        self.timecodes_text.insert("0.0", self.placeholder_text)
        
        self.clip_name_entry = ctk.CTkEntry(f1, placeholder_text="Specific Clip Name Or Timeline Name (Optional)", fg_color=self.color_input)
        self.clip_name_entry.pack(fill="x", padx=16, pady=5)
        
        btn_frame1 = ctk.CTkFrame(f1, fg_color="transparent")
        btn_frame1.pack(fill="x", padx=16, pady=(5, 16))
        
        self.execute_btn = ctk.CTkButton(btn_frame1, text="Cut Inside Ranges", command=self.execute_cut_normal, fg_color=self.color_primary)
        self.execute_btn.pack(side="left", expand=True, padx=(0, 5))
        
        self.reverse_btn = ctk.CTkButton(btn_frame1, text="Cut Outside Ranges (Reverse)", command=self.execute_cut_reverse, fg_color=self.color_secondary)
        self.reverse_btn.pack(side="right", expand=True, padx=(5, 0))

        # 2. Clip Picker
        f2 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f2.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f2, text="🎯 Clip Picker", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.clip_numbers_entry = ctk.CTkEntry(f2, placeholder_text="8607-8610, 8804, 8813", fg_color=self.color_input)
        self.clip_numbers_entry.pack(fill="x", padx=16, pady=5)
        
        self.pick_btn = ctk.CTkButton(f2, text="Build Timeline from Clips", command=self.execute_clip_picking, fg_color=self.color_warning)
        self.pick_btn.pack(fill="x", padx=16, pady=(5, 16))

        # 3. Markers to Timeline
        f3 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f3.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f3, text="📍 Markers to Timeline", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.marker_color_var = ctk.StringVar(value="All")
        colors = ["All", "Blue", "Cyan", "Green", "Yellow", "Red", "Pink", "Purple", "Fuchsia", "Rose", "Lavender", "Sky", "Mint", "Lemon", "Sand", "Cocoa", "Cream"]
        self.marker_combo = ctk.CTkComboBox(f3, values=colors, variable=self.marker_color_var, fg_color=self.color_input)
        self.marker_combo.pack(fill="x", padx=16, pady=5)
        
        self.marker_btn = ctk.CTkButton(f3, text="Extract Marked Clips", command=self.execute_markers, fg_color=self.color_success)
        self.marker_btn.pack(fill="x", padx=16, pady=(5, 16))

        # 4. Flag Filter
        f4 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f4.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f4, text="🏳️ Flag Filter", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.flag_color_var = ctk.StringVar(value="Green")
        self.flag_combo = ctk.CTkComboBox(f4, values=colors, variable=self.flag_color_var, fg_color=self.color_input)
        self.flag_combo.pack(fill="x", padx=16, pady=5)
        
        self.flag_btn = ctk.CTkButton(f4, text="Extract Flagged Clips", command=self.execute_flags, fg_color=self.color_primary)
        self.flag_btn.pack(fill="x", padx=16, pady=(5, 16))

    # ---------------------------------------------------------
    # TAB: PROCESS
    # ---------------------------------------------------------
    def create_process_tab(self):
        scrollable = ctk.CTkScrollableFrame(self.tab_process, fg_color="transparent")
        scrollable.pack(fill="both", expand=True)

        # 1. Merge Timelines
        f1 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f1.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f1, text="🔀 Merge Timelines", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.merge_entry = ctk.CTkEntry(f1, placeholder_text="Timeline 1, Timeline 2, Day 3...", fg_color=self.color_input)
        self.merge_entry.pack(fill="x", padx=16, pady=5)
        
        self.merge_btn = ctk.CTkButton(f1, text="Merge into Single Timeline", command=self.execute_merge, fg_color=self.color_primary)
        self.merge_btn.pack(fill="x", padx=16, pady=(5, 16))

        # 2. Watermark
        f2 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f2.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f2, text="💧 Add Watermark Track", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.watermark_entry = ctk.CTkEntry(f2, placeholder_text="Absolute path to PNG image (e.g. /Users/.../logo.png)", fg_color=self.color_input)
        self.watermark_entry.pack(fill="x", padx=16, pady=5)
        
        self.watermark_btn = ctk.CTkButton(f2, text="Apply Watermark to Timeline", command=self.execute_watermark, fg_color=self.color_secondary)
        self.watermark_btn.pack(fill="x", padx=16, pady=(5, 16))

    # ---------------------------------------------------------
    # TAB: EXPORT
    # ---------------------------------------------------------
    def create_export_tab(self):
        scrollable = ctk.CTkScrollableFrame(self.tab_export, fg_color="transparent")
        scrollable.pack(fill="both", expand=True)

        # 1. Batch Render
        f1 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f1.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f1, text="📱 Multi-Platform Render", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        chk_frame = ctk.CTkFrame(f1, fg_color="transparent")
        chk_frame.pack(fill="x", padx=16, pady=5)
        
        self.var_169 = ctk.BooleanVar(value=True)
        self.var_916 = ctk.BooleanVar(value=True)
        self.var_11 = ctk.BooleanVar(value=False)
        
        ctk.CTkCheckBox(chk_frame, text="YouTube (16:9)", variable=self.var_169).pack(side="left", padx=10)
        ctk.CTkCheckBox(chk_frame, text="Shorts/Reels (9:16)", variable=self.var_916).pack(side="left", padx=10)
        ctk.CTkCheckBox(chk_frame, text="Square (1:1)", variable=self.var_11).pack(side="left", padx=10)
        
        self.render_dir_entry = ctk.CTkEntry(f1, placeholder_text="Output Directory (e.g. /Users/name/Desktop/Renders)", fg_color=self.color_input)
        self.render_dir_entry.pack(fill="x", padx=16, pady=5)
        
        self.render_btn = ctk.CTkButton(f1, text="Add to Render Queue", command=self.execute_batch_render, fg_color=self.color_success)
        self.render_btn.pack(fill="x", padx=16, pady=(5, 16))

        # 2. Thumbnails
        f2 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f2.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f2, text="🖼️ Thumbnail Extractor", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.thumb_mode_var = ctk.StringVar(value="Markers")
        ctk.CTkComboBox(f2, values=["Markers", "Timeline Center"], variable=self.thumb_mode_var, fg_color=self.color_input).pack(fill="x", padx=16, pady=5)
        
        self.thumb_dir_entry = ctk.CTkEntry(f2, placeholder_text="Output Directory", fg_color=self.color_input)
        self.thumb_dir_entry.pack(fill="x", padx=16, pady=5)
        
        self.thumb_btn = ctk.CTkButton(f2, text="Queue Still Exports", command=self.execute_thumbnails, fg_color=self.color_primary)
        self.thumb_btn.pack(fill="x", padx=16, pady=(5, 16))

        # 3. CSV Export
        f3 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f3.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f3, text="📋 Export CSV (Clip List)", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.csv_dir_entry = ctk.CTkEntry(f3, placeholder_text="Full file path (e.g. /Users/.../timeline.csv)", fg_color=self.color_input)
        self.csv_dir_entry.pack(fill="x", padx=16, pady=5)
        
        self.csv_btn = ctk.CTkButton(f3, text="Export CSV", command=self.execute_csv, fg_color=self.color_secondary)
        self.csv_btn.pack(fill="x", padx=16, pady=(5, 16))

        # 4. YouTube Chapters
        f4 = ctk.CTkFrame(scrollable, fg_color=self.color_bg, corner_radius=20)
        f4.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f4, text="🎬 Auto YouTube Chapters", font=self._get_font(16, "bold")).pack(anchor="w", padx=16, pady=(16, 5))
        
        self.yt_btn = ctk.CTkButton(f4, text="Generate Chapters from Markers", command=self.execute_yt_chapters, fg_color=self.color_error)
        self.yt_btn.pack(fill="x", padx=16, pady=(5, 16))


    # ---------------------------------------------------------
    # LOG PANEL
    # ---------------------------------------------------------
    def create_log_panel(self):
        log_frame = ctk.CTkFrame(self, fg_color=self.color_card, corner_radius=12)
        log_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        top = ctk.CTkFrame(log_frame, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(10, 0))
        ctk.CTkLabel(top, text="Mission Log", font=self._get_font(14, "bold")).pack(side="left")
        ctk.CTkButton(top, text="Clear", width=60, height=24, command=self.clear_log, fg_color=self.color_bg).pack(side="right")
        
        self.result_text = ctk.CTkTextbox(log_frame, height=120, font=ctk.CTkFont(family=self.font_mono, size=12), fg_color="transparent", border_width=0)
        self.result_text.pack(fill="both", expand=True, padx=16, pady=(5, 10))
        
        try:
            self.result_text.tag_config("success", foreground=self.color_success)
            self.result_text.tag_config("error", foreground=self.color_error)
            self.result_text.tag_config("warning", foreground=self.color_warning)
            self.result_text.tag_config("info", foreground=self.color_text)
        except Exception:
            pass

    # ---------------------------------------------------------
    # LOGIC & EVENT HANDLERS
    # ---------------------------------------------------------
    def clear_log(self):
        self.result_text.configure(state="normal")
        self.result_text.delete("0.0", "end")
        self.result_text.configure(state="disabled")

    def log_msg(self, msg, tag="info"):
        self.result_text.configure(state="normal")
        self.result_text.insert("end", msg + "\n", tag)
        self.result_text.see("end")
        self.result_text.configure(state="disabled")

    def update_status(self, message, color, dot_color):
        self.status_label.configure(text=message, text_color=color)
        self.status_dot.configure(text_color=dot_color)

    def connect_to_resolve(self):
        self.update_status("Connecting...", self.color_muted, self.color_muted)
        
        def attempt_connection():
            success, message = self.resolve_core.connect()
            if success:
                self.after(0, lambda: self.update_status("Connected to Resolve", self.color_success, self.color_success))
                self.after(0, lambda: self.log_msg("✓ Connection Established.", "success"))
            else:
                self.after(0, lambda: self.update_status("Connection Failed", self.color_error, self.color_error))
                self.after(0, lambda: self.log_msg(f"✗ Connection Failed: {message}", "error"))

        threading.Thread(target=attempt_connection, daemon=True).start()

    # Generic wrapper for threading tasks
    def run_task(self, task_func, success_msg, error_msg="Task failed"):
        def wrapper():
            self.after(0, lambda: self.log_msg("Running task...", "info"))
            try:
                success, msg = task_func()
                if success:
                    self.after(0, lambda: self.log_msg(msg, "success"))
                else:
                    self.after(0, lambda: self.log_msg(msg, "error"))
            except Exception as e:
                self.after(0, lambda: self.log_msg(f"{error_msg}: {str(e)}", "error"))
        
        threading.Thread(target=wrapper, daemon=True).start()

    # -- TAB 1 ACTIONS --
    def execute_cut_normal(self):
        timecodes = self.timecodes_text.get("0.0", "end-1c").strip()
        clip_name = self.clip_name_entry.get().strip()
        if timecodes == self.placeholder_text: timecodes = ""
        self.run_task(lambda: self.resolve_core.cut_video(timecodes, False, clip_name), "Cut success")

    def execute_cut_reverse(self):
        timecodes = self.timecodes_text.get("0.0", "end-1c").strip()
        clip_name = self.clip_name_entry.get().strip()
        if timecodes == self.placeholder_text: timecodes = ""
        self.run_task(lambda: self.resolve_core.cut_video(timecodes, True, clip_name), "Cut reverse success")

    def execute_clip_picking(self):
        names = self.clip_numbers_entry.get().strip()
        self.run_task(lambda: self.resolve_core.pick_clips_from_timeline(names), "Clip picking success")

    def execute_markers(self):
        color = self.marker_color_var.get()
        self.run_task(lambda: self.resolve_core.markers_to_timeline(color), "Marker extraction success")

    def execute_flags(self):
        color = self.flag_color_var.get()
        self.run_task(lambda: self.resolve_core.filter_by_flag(color), "Flag extraction success")

    # -- TAB 2 ACTIONS --
    def execute_merge(self):
        names = self.merge_entry.get().strip()
        self.run_task(lambda: self.resolve_core.merge_timelines(names), "Merge success")

    def execute_watermark(self):
        path = self.watermark_entry.get().strip()
        self.run_task(lambda: self.resolve_core.apply_watermark_track(path), "Watermark success")

    # -- TAB 3 ACTIONS --
    def execute_batch_render(self):
        d = self.render_dir_entry.get().strip()
        p = []
        if self.var_169.get(): p.append("16:9")
        if self.var_916.get(): p.append("9:16")
        if self.var_11.get(): p.append("1:1")
        self.run_task(lambda: self.resolve_core.batch_render(p, d), "Render queued")

    def execute_thumbnails(self):
        m = self.thumb_mode_var.get()
        d = self.thumb_dir_entry.get().strip()
        self.run_task(lambda: self.resolve_core.extract_thumbnails(m, d), "Thumbnails queued")

    def execute_csv(self):
        p = self.csv_dir_entry.get().strip()
        self.run_task(lambda: self.resolve_core.export_csv_data(p), "CSV export success")

    def execute_yt_chapters(self):
        self.run_task(lambda: self.resolve_core.generate_youtube_chapters(), "YT Chapters generated")

    def run(self):
        # Auto connect on start
        self.after(500, self.connect_to_resolve)
        self.mainloop()

if __name__ == "__main__":
    app = ClipAssassinApp()
    app.run()
