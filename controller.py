from timer import PomodoroTimer, TimerState, TimerType
from database import Database
from settings import Settings


class PomodoroController:
    def __init__(self):
        self.settings = Settings()
        self.db = Database()
        self.timer = PomodoroTimer(self.settings)

        self.current_task_id = None

        # Callbacks (will be set by UI)
        self.on_timer_tick = None
        self.on_timer_complete = None
        self.on_state_change = None
        self.on_stats_update = None
        self.on_tasks_update = None

        # Setup timer callbacks
        self.timer.on_tick = self._handle_tick
        self.timer.on_complete = self._handle_complete
        self.timer.on_state_change = self._handle_state_change

    def load_data(self):
        self._refresh_tasks()
        self._refresh_stats()

    def _handle_tick(self, seconds):
        if self.on_timer_tick:
            self.on_timer_tick(seconds)

    def _handle_state_change(self, state, timer_type):
        if self.on_state_change:
            self.on_state_change(state, timer_type)

    def _handle_complete(self, timer_type):
        if self.on_timer_complete:
            self.on_timer_complete(timer_type)

        if timer_type == TimerType.POMODORO:
            # Record pomodoro if a task is selected
            if self.current_task_id:
                self.db.update_task_progress(self.current_task_id)
                self.db.add_pomodoro_record(
                    self.current_task_id,
                    self.settings.pomodoro_duration
                )
            else:
                self.db.add_pomodoro_record(
                    None,
                    self.settings.pomodoro_duration
                )

        self._refresh_stats()
        self._refresh_tasks()

        # Auto-start next phase
        if timer_type == TimerType.POMODORO:
            if self.settings.auto_start_breaks:
                if self.timer.should_take_long_break():
                    self.start_long_break()
                else:
                    self.start_short_break()
        else:
            if self.settings.auto_start_pomodoros:
                self.start_pomodoro()

    def _refresh_stats(self):
        today = self.db.get_today_pomodoro_count()
        week = self.db.get_week_pomodoro_count()
        if self.on_stats_update:
            self.on_stats_update(today, week)

    def _refresh_tasks(self):
        tasks = self.db.get_tasks()
        if self.on_tasks_update:
            self.on_tasks_update(tasks)

    # Timer controls
    def start(self):
        if self.timer.is_idle():
            self.timer.start_pomodoro()
        elif self.timer.is_paused():
            self.timer.resume()

    def pause(self):
        if self.timer.is_running():
            self.timer.pause()

    def reset(self):
        self.timer.reset()
        # Reset display
        if self.on_timer_tick:
            self.on_timer_tick(self.settings.pomodoro_duration * 60)

    def skip(self):
        self.timer.skip()

    def start_short_break(self):
        self.timer.start_short_break()

    def start_long_break(self):
        self.timer.start_long_break()

    # Task management
    def add_task(self, name, estimated_pomodoros):
        self.db.create_task(name, estimated_pomodoros)
        self._refresh_tasks()

    def complete_task(self, task_id):
        self.db.complete_task(task_id)
        if self.current_task_id == task_id:
            self.current_task_id = None
        self._refresh_tasks()

    def delete_task(self, task_id):
        self.db.delete_task(task_id)
        if self.current_task_id == task_id:
            self.current_task_id = None
        self._refresh_tasks()

    def select_task(self, task_id):
        self.current_task_id = task_id

    def get_task_id_at_index(self, index):
        tasks = self.db.get_tasks()
        if 0 <= index < len(tasks):
            return tasks[index][0]
        return None

    def get_current_timer_type(self):
        return self.timer.timer_type

    def get_pomodoro_count(self):
        return self.timer.pomodoro_count