import json
import os


DEFAULT_SETTINGS = {
    "pomodoro_duration": 25,      # 专注时长（分钟）
    "short_break_duration": 5,    # 短休息时长（分钟）
    "long_break_duration": 15,    # 长休息时长（分钟）
    "long_break_interval": 4,     # 几个番茄钟后长休息
    "auto_start_breaks": False,   # 自动开始休息
    "auto_start_pomodoros": False,# 自动开始下一个番茄钟
    "sound_enabled": True,        # 启用声音提示
    "notification_enabled": True, # 启用系统通知
}


class Settings:
    def __init__(self):
        self.settings_file = os.path.join(
            os.path.expanduser("~"),
            ".pomodoro-timer",
            "settings.json"
        )
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        self.settings = self._load_settings()

    def _load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    # 合并默认设置和新设置
                    settings = DEFAULT_SETTINGS.copy()
                    settings.update(saved)
                    return settings
            except (json.JSONDecodeError, IOError):
                return DEFAULT_SETTINGS.copy()
        return DEFAULT_SETTINGS.copy()

    def _save_settings(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self._save_settings()

    def get_all(self):
        return self.settings.copy()

    def reset(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self._save_settings()

    @property
    def pomodoro_duration(self):
        return self.settings["pomodoro_duration"]

    @property
    def short_break_duration(self):
        return self.settings["short_break_duration"]

    @property
    def long_break_duration(self):
        return self.settings["long_break_duration"]

    @property
    def long_break_interval(self):
        return self.settings["long_break_interval"]

    @property
    def auto_start_breaks(self):
        return self.settings["auto_start_breaks"]

    @property
    def auto_start_pomodoros(self):
        return self.settings["auto_start_pomodoros"]

    @property
    def sound_enabled(self):
        return self.settings["sound_enabled"]

    @property
    def notification_enabled(self):
        return self.settings["notification_enabled"]