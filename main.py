#!/usr/bin/env python3
"""
Pomodoro Timer - 桌面番茄钟应用
基于番茄工作法的时间管理工具
"""

from controller import PomodoroController
from ui import PomodoroUI


def main():
    controller = PomodoroController()
    app = PomodoroUI(controller)
    app.run()


if __name__ == "__main__":
    main()