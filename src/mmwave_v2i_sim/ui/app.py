"""PySide6 desktop app — mmWave V2I Simulator GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mmwave_v2i_sim.config.schema import SimConfig
from mmwave_v2i_sim.sim_engine.constants import N_VEHICLE_OPTIONS
from mmwave_v2i_sim.sim_engine.engine import SimSession, StepSnapshot
from mmwave_v2i_sim.sim_engine.packing import ALGORITHMS
from mmwave_v2i_sim.sim_engine.session_export import (
    build_workspace,
    save_workspace_zip,
    snapshot_to_dict,
)
from mmwave_v2i_sim.sim_engine.trim_plot import (
    TrimPlotSeries,
    draw_trim_trend_panel,
    style_for_series_index,
)
from mmwave_v2i_sim.sim_engine.visualize import draw_figure1_map, draw_figure2_packing

_RUN_COUNT_OPTIONS = [1, 5, 20, 50]

_HEADER_STYLE = "font-weight: bold; font-size: 11px; padding: 2px 0; letter-spacing: 1px;"
_CAPTION_STYLE = "color: #FFFFFF; font-size: 10px; font-weight: 600;"


_ALGO_LABELS = {
    "guillotine": "Guillotine  (best short-side fit, simplest)",
    "shelf": "Shelf  (row by row, fastest)",
    "max_rects": "Max Rects  (best area fit, tightest)",
}

_ROUTE_LABELS = {
    "full": "On  (full route visible)",
    "off": "Off  (hide routes)",
}


def run_desktop_app(config: SimConfig) -> None:
    try:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        from matplotlib.gridspec import GridSpec
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtWidgets import (
            QApplication,
            QButtonGroup,
            QComboBox,
            QDoubleSpinBox,
            QFileDialog,
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QPushButton,
            QSizePolicy,
            QSlider,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install GUI deps: pip install '.[gui]'") from exc

    def _sel_label(text: str, *, bold: bool = False, caption: bool = False) -> QLabel:
        lbl = QLabel(text)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if caption:
            lbl.setStyleSheet(_CAPTION_STYLE)
        elif bold:
            lbl.setStyleSheet("font-weight: bold;")
        return lbl

    def _section(title: str, body: QWidget) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Plain)
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(8, 4, 8, 6)
        outer.setSpacing(4)
        header = _sel_label(title)
        header.setStyleSheet(_HEADER_STYLE)
        outer.addWidget(header)
        outer.addWidget(body)
        return frame

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("mmWave V2I Simulator")
            self.resize(1600, 900)

            self._n_vehicle: int = config.n_vehicle
            self._base_seed: int = config.seed
            self._p_los_thresh: float = config.p_los_thresh
            self._packing_algo: str = config.packing_algorithm
            initial_route = config.route_display
            if initial_route == "active_segment":
                initial_route = "full"
            self._route_display: str = initial_route
            self._n_runs_target: int = 1
            self._runs_completed: int = 0

            self._trim_series: list[TrimPlotSeries] = []
            self._series_styles: dict[tuple[int, str, float], tuple[str, str]] = {}
            self._completed_run_logs: list[list[dict[str, Any]]] = []
            self._current_run_steps: list[dict[str, Any]] = []
            self._params_locked: bool = False

            self._session = self._make_session()
            self._snap = self._session.reset()
            self._record_step(self._snap)
            self._playing = False
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._on_timer_step)
            self._build_ui()
            self._refresh_all()

        def _param_key(self) -> tuple[int, str, float]:
            return (self._n_vehicle, self._packing_algo, self._p_los_thresh)

        def _run_seed(self) -> int:
            return self._base_seed + self._runs_completed

        def _make_session(self) -> SimSession:
            return SimSession(
                n_vehicle=self._n_vehicle,
                seed=self._run_seed(),
                packing_algorithm=self._packing_algo,
                p_los_thresh=self._p_los_thresh,
            )

        def _build_ui(self) -> None:
            root = QWidget(self)
            self.setCentralWidget(root)
            outer = QHBoxLayout(root)

            left = QVBoxLayout()
            outer.addLayout(left, stretch=62)

            self._fig_map = Figure(figsize=(9, 5.5), dpi=100)
            self._ax_map = self._fig_map.add_subplot(1, 1, 1)
            self._canvas_map = FigureCanvasQTAgg(self._fig_map)
            left.addWidget(self._canvas_map, stretch=1)
            left.addWidget(_section("PLAYBACK", self._build_controls()))
            params_row = QWidget()
            params_hbox = QHBoxLayout(params_row)
            params_hbox.setContentsMargins(0, 0, 0, 0)
            params_hbox.setSpacing(8)
            params_hbox.addWidget(_section("SIMULATION PARAMETERS", self._build_params()), stretch=3)
            params_hbox.addWidget(_section("SESSION DATA", self._build_export_panel()), stretch=1)
            left.addWidget(params_row)

            right = QVBoxLayout()
            outer.addLayout(right, stretch=38)

            self._fig_pack = Figure(figsize=(6, 6.5), dpi=100)
            gs = GridSpec(2, 1, figure=self._fig_pack, height_ratios=[3.2, 1.4], hspace=0.08)
            self._ax_pack = self._fig_pack.add_subplot(gs[0, 0])
            self._ax_text = self._fig_pack.add_subplot(gs[1, 0])
            self._canvas_pack = FigureCanvasQTAgg(self._fig_pack)
            self._canvas_pack.setMinimumHeight(420)
            right.addWidget(self._canvas_pack)

            self._fig_trim = Figure(figsize=(6, 3), dpi=100, tight_layout=True)
            self._ax_trim = self._fig_trim.add_subplot(1, 1, 1)
            self._canvas_trim = FigureCanvasQTAgg(self._fig_trim)
            self._canvas_trim.setMinimumHeight(260)
            right.addWidget(self._canvas_trim)

        def _build_controls(self) -> QWidget:
            box = QWidget()
            col = QVBoxLayout(box)
            col.setContentsMargins(0, 0, 0, 0)
            col.setSpacing(4)

            row1 = QHBoxLayout()
            row1.addStretch()
            self.play_pause_btn = QPushButton("\u25B6  Play")
            self.play_pause_btn.setCheckable(True)
            self.play_pause_btn.setMinimumWidth(90)
            self.play_pause_btn.toggled.connect(self._on_play_pause_toggled)
            row1.addWidget(self.play_pause_btn)

            self._step_btn = QPushButton()
            self._step_btn.clicked.connect(self._on_step_clicked)
            row1.addWidget(self._step_btn)

            self._step_dir_btn = QPushButton("Fwd/Back")
            self._step_dir_btn.setCheckable(True)
            self._step_dir_btn.setToolTip("Unchecked = forward; checked = backward")
            self._step_dir_btn.toggled.connect(self._update_step_btn_label)
            row1.addWidget(self._step_dir_btn)
            self._update_step_btn_label()

            terminate_btn = QPushButton("Terminate")
            terminate_btn.setToolTip("Stop playback and wipe all session run data")
            terminate_btn.clicked.connect(self._on_terminate)
            row1.addWidget(terminate_btn)
            row1.addStretch()
            col.addLayout(row1)

            row2 = QHBoxLayout()
            row2.addStretch()
            row2.addWidget(_sel_label("Playback interval:"))
            self._speed_slider = QSlider(Qt.Horizontal)
            self._speed_slider.setRange(1, 10)
            self._speed_slider.setValue(5)
            self._speed_slider.setMinimumWidth(220)
            self._speed_slider.valueChanged.connect(self._on_speed_changed)
            row2.addWidget(self._speed_slider)
            self._speed_label = _sel_label(self._speed_text())
            self._speed_label.setMinimumWidth(80)
            row2.addWidget(self._speed_label)

            row2.addSpacing(24)
            row2.addWidget(_sel_label("Vehicles:"))
            self._nveh_group = QButtonGroup(box)
            for n in N_VEHICLE_OPTIONS:
                btn = QPushButton(str(n))
                btn.setCheckable(True)
                btn.setMaximumWidth(36)
                btn.setChecked(n == self._n_vehicle)
                self._nveh_group.addButton(btn, n)
                row2.addWidget(btn)
            self._nveh_group.idClicked.connect(self._on_nvehicle_clicked)
            row2.addStretch()
            col.addLayout(row2)

            speed_cap = _sel_label(
                "Animation speed only - vehicles advance one route sample per step.",
                caption=True,
            )
            speed_cap.setAlignment(Qt.AlignCenter)
            col.addWidget(speed_cap)
            return box

        def _build_params(self) -> QWidget:
            box = QWidget()
            grid = QGridLayout(box)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(10)
            grid.setVerticalSpacing(4)
            grid.setColumnStretch(0, 0)
            grid.setColumnStretch(1, 1)

            row = 0
            grid.addWidget(_sel_label("Packing:", bold=True), row, 0, Qt.AlignLeft)
            self._algo_combo = QComboBox()
            self._algo_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            for algo in ALGORITHMS:
                self._algo_combo.addItem(_ALGO_LABELS.get(algo, algo), algo)
            idx = ALGORITHMS.index(self._packing_algo) if self._packing_algo in ALGORITHMS else 0
            self._algo_combo.setCurrentIndex(idx)
            self._algo_combo.currentIndexChanged.connect(self._on_algo_changed)
            grid.addWidget(self._algo_combo, row, 1, Qt.AlignLeft)
            row += 1

            grid.addWidget(_sel_label("Runs:", bold=True), row, 0, Qt.AlignLeft)
            runs_row = QHBoxLayout()
            runs_row.setContentsMargins(0, 0, 0, 0)
            self._runs_combo = QComboBox()
            for n in _RUN_COUNT_OPTIONS:
                self._runs_combo.addItem(str(n), n)
            self._runs_combo.currentIndexChanged.connect(self._on_runs_changed)
            runs_row.addWidget(self._runs_combo)
            runs_cap = _sel_label(
                "Play button runs this many times with the selected parameters..",
                caption=True,
            )
            runs_cap.setWordWrap(False)
            runs_row.addWidget(runs_cap)
            runs_row.addStretch()
            runs_wrap = QWidget()
            runs_wrap.setLayout(runs_row)
            grid.addWidget(runs_wrap, row, 1)
            row += 1

            grid.addWidget(_sel_label("LoS threshold:", bold=True), row, 0, Qt.AlignLeft)
            los_row = QHBoxLayout()
            los_row.setContentsMargins(0, 0, 0, 0)
            self._los_spin = QDoubleSpinBox()
            self._los_spin.setRange(0.0, 1.0)
            self._los_spin.setSingleStep(0.1)
            self._los_spin.setDecimals(1)
            self._los_spin.setValue(self._p_los_thresh)
            self._los_spin.valueChanged.connect(self._on_los_changed)
            los_row.addWidget(self._los_spin)
            los_row.addWidget(_sel_label(
                "Vehicles with P(LoS) >= threshold join the packing.", caption=True
            ))
            los_row.addStretch()
            los_wrap = QWidget()
            los_wrap.setLayout(los_row)
            grid.addWidget(los_wrap, row, 1)
            row += 1

            grid.addWidget(_sel_label("Route display:", bold=True), row, 0, Qt.AlignLeft)
            route_row = QHBoxLayout()
            route_row.setContentsMargins(0, 0, 0, 0)
            self._route_combo = QComboBox()
            self._route_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            for mode, label in _ROUTE_LABELS.items():
                self._route_combo.addItem(label, mode)
            if self._route_display not in _ROUTE_LABELS:
                self._route_display = "full"
            cur_label = _ROUTE_LABELS[self._route_display]
            ridx = self._route_combo.findText(cur_label)
            if ridx >= 0:
                self._route_combo.setCurrentIndex(ridx)
            self._route_combo.currentIndexChanged.connect(self._on_route_display_changed)
            route_row.addWidget(self._route_combo)
            route_row.addWidget(_sel_label(
                "Show or hide each vehicle's full path.", caption=True
            ))
            route_row.addStretch()
            route_wrap = QWidget()
            route_wrap.setLayout(route_row)
            grid.addWidget(route_wrap, row, 1)

            self._param_widgets = [
                self._algo_combo,
                self._runs_combo,
                self._los_spin,
                self._route_combo,
            ]
            for btn in self._nveh_group.buttons():
                self._param_widgets.append(btn)
            return box

        def _build_export_panel(self) -> QWidget:
            box = QWidget()
            col = QVBoxLayout(box)
            col.setContentsMargins(0, 0, 0, 0)
            export_cap = _sel_label(
                "Export trim histories, parameters, and per-step snapshots from all runs in this session.",
                caption=True,
            )
            export_cap.setWordWrap(False)
            col.addWidget(export_cap)
            col.addStretch(1)
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            self._download_btn = QPushButton("Download simulation data")
            self._download_btn.setSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Fixed,
            )
            self._download_btn.clicked.connect(self._on_download_session)
            btn_row.addWidget(self._download_btn)
            btn_row.addStretch()
            col.addLayout(btn_row)
            col.addStretch(1)
            self._update_download_enabled()
            return box

        def _apply_params_lock(self, locked: bool) -> None:
            for w in self._param_widgets:
                w.setEnabled(not locked)

        def _speed_ms(self) -> int:
            v = self._speed_slider.value()
            return int(500 - (v - 1) * 50)

        def _speed_text(self) -> str:
            return f"{self._speed_ms()} ms/step"

        def _run_progress_text(self) -> str:
            cur = self._runs_completed + 1 if self._playing else self._runs_completed
            return f"{cur}/{self._n_runs_target} runs"

        def _update_step_btn_label(self, *_args: object) -> None:
            arrow = "\u25C0" if self._step_dir_btn.isChecked() else "\u25B6"
            self._step_btn.setText(f"Step {arrow}")

        def _has_exportable_data(self) -> bool:
            if self._completed_run_logs:
                return True
            return any(s.runs for s in self._trim_series)

        def _update_download_enabled(self) -> None:
            self._download_btn.setEnabled(self._has_exportable_data())

        def _record_step(self, snap: object) -> None:
            if isinstance(snap, StepSnapshot):
                self._current_run_steps.append(snapshot_to_dict(snap))

        def _find_or_create_series(self, key: tuple[int, str, float]) -> TrimPlotSeries:
            for s in self._trim_series:
                if (s.n_vehicle == key[0]
                        and s.algorithm == key[1]
                        and abs(s.los_thresh - key[2]) < 1e-9):
                    return s
            s = TrimPlotSeries(
                n_vehicle=key[0], algorithm=key[1], los_thresh=key[2]
            )
            self._trim_series.append(s)
            self._series_styles[key] = style_for_series_index(len(self._trim_series) - 1)
            return s

        def _save_completed_run(self) -> None:
            history = list(self._session.trim_history)
            if not history:
                return
            key = self._param_key()
            series = self._find_or_create_series(key)
            series.runs.append(history)
            if self._current_run_steps:
                self._completed_run_logs.append(list(self._current_run_steps))
            self._current_run_steps = []

        def _start_next_run(self) -> None:
            self._session = self._make_session()
            self._snap = self._session.reset()
            self._current_run_steps = []
            self._record_step(self._snap)

        def _finish_run_batch_or_continue(self) -> None:
            self._save_completed_run()
            self._runs_completed += 1
            self._update_download_enabled()
            if self._runs_completed >= self._n_runs_target:
                self.play_pause_btn.setChecked(False)
                self._params_locked = False
                self._apply_params_lock(False)
                self._refresh_all()
            else:
                self._start_next_run()
                self._refresh_all()

        def _on_play_pause_toggled(self, checked: bool) -> None:
            self._playing = checked
            if checked:
                self.play_pause_btn.setText("\u23F8  Pause")
                self._runs_completed = 0
                self._params_locked = True
                self._apply_params_lock(True)
                self._start_next_run()
                self._timer.start(self._speed_ms())
            else:
                self.play_pause_btn.setText("\u25B6  Play")
                self._timer.stop()

        def _on_speed_changed(self) -> None:
            self._speed_label.setText(self._speed_text())
            if self._playing:
                self._timer.setInterval(self._speed_ms())

        def _on_step_clicked(self) -> None:
            if self._playing:
                self.play_pause_btn.setChecked(False)
            if self._step_dir_btn.isChecked():
                self._step_backward()
            else:
                if not self._advance_step():
                    self._finish_run_batch_or_continue()

        def _on_timer_step(self) -> None:
            if self._step_dir_btn.isChecked():
                if not self._step_backward():
                    self.play_pause_btn.setChecked(False)
            else:
                if not self._advance_step():
                    self._finish_run_batch_or_continue()

        def _step_backward(self) -> bool:
            target = max(0, self._session.current_i_num - 2)
            if target == self._session.current_i_num - 1:
                return False
            self._start_next_run()
            for _ in range(target):
                nxt = self._session.step()
                if nxt:
                    self._snap = nxt
                    self._record_step(self._snap)
            self._refresh_all()
            return True

        def _advance_step(self) -> bool:
            nxt = self._session.step()
            if nxt is None:
                return False
            self._snap = nxt
            self._record_step(self._snap)
            self._refresh_all()
            return True

        def _on_terminate(self) -> None:
            if self._playing:
                self.play_pause_btn.setChecked(False)
            self._trim_series.clear()
            self._series_styles.clear()
            self._completed_run_logs.clear()
            self._current_run_steps.clear()
            self._runs_completed = 0
            self._params_locked = False
            self._apply_params_lock(False)
            self._start_next_run()
            self._update_download_enabled()
            self._refresh_all()

        def _reset_session_only(self) -> None:
            if self._playing:
                self.play_pause_btn.setChecked(False)
            self._runs_completed = 0
            self._current_run_steps.clear()
            self._start_next_run()
            self._refresh_all()

        def _on_nvehicle_clicked(self, n: int) -> None:
            if self._params_locked:
                for btn in self._nveh_group.buttons():
                    btn.setChecked(self._nveh_group.id(btn) == self._n_vehicle)
                return
            if n == self._n_vehicle:
                return
            self._n_vehicle = n
            self._reset_session_only()

        def _on_algo_changed(self) -> None:
            if self._params_locked:
                idx = ALGORITHMS.index(self._packing_algo) if self._packing_algo in ALGORITHMS else 0
                self._algo_combo.blockSignals(True)
                self._algo_combo.setCurrentIndex(idx)
                self._algo_combo.blockSignals(False)
                return
            new_algo = self._algo_combo.currentData()
            if new_algo == self._packing_algo:
                return
            self._packing_algo = new_algo
            self._reset_session_only()

        def _on_runs_changed(self) -> None:
            if self._params_locked:
                idx = _RUN_COUNT_OPTIONS.index(self._n_runs_target)
                self._runs_combo.blockSignals(True)
                self._runs_combo.setCurrentIndex(idx)
                self._runs_combo.blockSignals(False)
                return
            self._n_runs_target = int(self._runs_combo.currentData())

        def _on_los_changed(self, value: float) -> None:
            if self._params_locked:
                self._los_spin.blockSignals(True)
                self._los_spin.setValue(self._p_los_thresh)
                self._los_spin.blockSignals(False)
                return
            if abs(value - self._p_los_thresh) < 1e-9:
                return
            self._p_los_thresh = float(value)
            self._reset_session_only()

        def _on_route_display_changed(self) -> None:
            if self._params_locked:
                cur_label = _ROUTE_LABELS.get(self._route_display, "")
                idx_r = self._route_combo.findText(cur_label)
                if idx_r >= 0:
                    self._route_combo.blockSignals(True)
                    self._route_combo.setCurrentIndex(idx_r)
                    self._route_combo.blockSignals(False)
                return
            self._route_display = self._route_combo.currentData()
            self._refresh_all()

        def _on_download_session(self) -> None:
            if not self._has_exportable_data():
                return
            path_str, _ = QFileDialog.getSaveFileName(
                self,
                "Download simulation data",
                "mmwave_sim_session.zip",
                "ZIP archive (*.zip)",
            )
            if not path_str:
                return
            path = Path(path_str)
            if path.suffix.lower() != ".zip":
                path = path.with_suffix(".zip")
            workspace = build_workspace(
                n_vehicle=self._n_vehicle,
                packing_algorithm=self._packing_algo,
                p_los_thresh=self._p_los_thresh,
                route_display=self._route_display,
                n_runs_target=self._n_runs_target,
                base_seed=self._base_seed,
                trim_series=self._trim_series,
                completed_run_logs=self._completed_run_logs,
                current_session_trim=list(self._session.trim_history)
                if self._session.trim_history
                else None,
            )
            save_workspace_zip(path, workspace)

        def _refresh_all(self) -> None:
            draw_figure1_map(
                self._ax_map,
                self._snap,
                route_display=self._route_display,
                run_progress=self._run_progress_text(),
            )
            draw_figure2_packing(self._ax_pack, self._ax_text, self._snap)
            self._fig_map.subplots_adjust(
                left=0.08, right=0.98, top=0.94, bottom=0.10
            )
            self._fig_pack.subplots_adjust(
                left=0.14, right=0.96, top=0.88, bottom=0.06, hspace=0.35
            )
            draw_trim_trend_panel(
                self._ax_trim, self._trim_series, series_styles=self._series_styles
            )
            self._fig_trim.subplots_adjust(left=0.12, right=0.98, top=0.88, bottom=0.18)
            self._update_download_enabled()
            self._canvas_map.draw_idle()
            self._canvas_pack.draw_idle()
            self._canvas_trim.draw_idle()

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
