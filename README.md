# 🍅 桌面番茄钟

基于 Python + tkinter 的番茄工作法计时器。

## 功能特性

- ⏱️ **计时功能**: 25分钟专注 + 5分钟短休息 + 15分钟长休息
- 📋 **任务管理**: 创建、标记完成、删除任务
- 📊 **统计面板**: 今日/本周番茄数统计
- ⚙️ **自定义设置**: 时长、通知、音效均可配置
- 🔔 **系统通知**: 计时结束自动提醒 (Linux notify-send)

## 运行方式

```bash
cd pomodoro-timer
python3 main.py
```

## 项目结构

```
pomodoro-timer/
├── main.py       # 入口文件
├── timer.py      # 计时器核心逻辑
├── ui.py         # GUI界面
├── controller.py # 控制器(MVC)
├── database.py   # SQLite数据持久化
├── settings.py   # 设置管理
└── requirements.txt
```

## 使用说明

1. 点击"开始"启动番茄钟计时
2. 每完成一个番茄钟会自动记录
3. 可以添加任务并跟踪完成进度
4. 在设置中可以自定义时长和通知选项