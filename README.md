# ESP32 Menu 中文转换工具

这是一个用于将 ESP-IDF 菜单选项转换为中文的工具。它可以帮助中文用户更方便地理解和使用 ESP-IDF 的配置选项。

## 功能特点

- 将 ESP-IDF 的 Kconfig 菜单选项转换为中文
- 支持多种 ESP-IDF 版本
- 提供简单的命令行界面
- 支持清理屏幕、显示帮助信息等功能

## 使用方法

1. 双击运行 `esp32-menu_ZH.bat` 文件
2. 在菜单中选择以下操作之一:
   - 将菜单转换为中文
   - 恢复为英文菜单
   - 显示帮助信息
   - 检查更新

## 目录结构

```
esp32-menu-zh/
├── app/                  # 主程序文件
│   ├── Kconfig_copy.py   # Kconfig 文件处理工具
│   └── menu_covert.py    # 主程序，实现菜单转换功能
├── resource/             # 资源文件
│   ├── ESP-IDF_v5.4/     # ESP-IDF v5.4 的 Kconfig 文件
│   ├── ESP-IDF_v5.5/     # ESP-IDF v5.5 的 Kconfig 文件
│   └── managed_components/ # 管理组件的 Kconfig 文件
└── esp32-menu_ZH.bat     # Windows 启动脚本
```

## 技术细节

- 使用 Python 编写，支持 Python 3.13
- 利用面向对象编程实现功能
- 包含颜色输出支持，提高可读性
- 处理文件路径规范化，确保跨平台兼容性

## 注意事项

- 请确保在使用前备份您的原始 Kconfig 文件
- 该工具不会修改原始文件，而是生成新的中文版本
- 如果遇到任何问题，可以尝试重新启动工具或检查文件路径

## 版权信息

该项目基于 ESP-IDF 框架，遵循 ESP-IDF 的许可协议。

ESP-IDF 是乐鑫科技开发的物联网开发框架，包含丰富的组件和驱动程序，支持 ESP32 系列芯片的开发。