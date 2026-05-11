import time
import threading
from enum import Enum


class TimerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


class TimerType(Enum):
    POMODORO = "pomodoro"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class PomodoroTimer:
    def __init__(self, settings):
        self.settings = settings
        self.state = TimerState.IDLE
        self.timer_type = TimerType.POMODORO
        self.remaining_seconds = 0
        self.pomodoro_count = 0

        self._thread = None
        self._stop_event = threading.Event()

        # Callbacks
        self.on_tick = None
        self.on_complete = None
        self.on_state_change = None

    def start_pomodoro(self):
        self.timer_type = TimerType.POMODORO
        self._start_timer(self.settings.pomodoro_duration * 60)

    def start_short_break(self):
        self.timer_type = TimerType.SHORT_BREAK
        self._start_timer(self.settings.short_break_duration * 60)

    def start_long_break(self):
        self.timer_type = TimerType.LONG_BREAK
        self._start_timer(self.settings.long_break_duration * 60)

    def _start_timer(self, seconds):
        if self.state == TimerState.RUNNING:
            return

        self.remaining_seconds = seconds
        self.state = TimerState.RUNNING
        self._stop_event.clear()

        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

        self._notify_state_change()

    def _run(self):
        while self.remaining_seconds > 0 and not self._stop_event.is_set():
            time.sleep(1)
            if not self._stop_event.is_set():
                self.remaining_seconds -= 1
                if self.on_tick:
                    self.on_tick(self.remaining_seconds)

        if self.remaining_seconds <= 0:
            self._on_timer_complete()

    def _on_timer_complete(self):
        if self.timer_type == TimerType.POMODORO:
            self.pomodoro_count += 1

        self.state = TimerState.IDLE
        self._notify_state_change()

        if self.on_complete:
            self.on_complete(self.timer_type)

    def pause(self):
        if self.state == TimerState.RUNNING:
            self._stop_event.set()
            self.state = TimerState.PAUSED
            if self._thread:
                self._thread.join(timeout=1)
            self._notify_state_change()

    def resume(self):
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()
            self._notify_state_change()

    def reset(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
        self.state = TimerState.IDLE

        if self.timer_type == TimerType.POMODORO:
            self.remaining_seconds = self.settings.pomodoro_duration * 60
        elif self.timer_type == TimerType.SHORT_BREAK:
            self.remaining_seconds = self.settings.short_break_duration * 60
        else:
            self.remaining_seconds = self.settings.long_break_duration * 60

        self._notify_state_change()

    def skip(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
        self._on_timer_complete()

    def _notify_state_change(self):
        if self.on_state_change:
            self.on_state_change(self.state, self.timer_type)

    def get_time_string(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def should_take_long_break(self):
        return self.pomodoro_count > 0 and self.pomodoro_count % self.settings.long_break_interval == 0

    def is_running(self):
        return self.state == TimerState.RUNNING

    def is_paused(self):
        return self.state == TimerState.PAUSED

    def is_idle(self):
        return self.state == TimerState.IDLE