# ESP32 Menu Config 中文转换工具

## 📚 项目介绍

ESP32 Menu Config 中文转换工具是一个专为中文开发者设计的实用工具，旨在将ESP-IDF（Espressif IoT Development Framework）的menuconfig配置界面从英文转换为中文显示，降低中文开发者的语言障碍，提升开发体验。

## ✨ 功能特点

- 📝 **中文转换**：将ESP-IDF的menuconfig配置菜单从英文转换为中文显示
- 🔄 **英文还原**：可随时将中文配置菜单还原为英文原版
- 📚 **ESP-IDF使用指南**：提供ESP-IDF开发环境的使用技巧和最佳实践
- 🔍 **帮助文档**：包含工具使用说明和常见问题解答
- 🔄 **自动更新**：支持检测和更新到最新版本
- 🎯 **支持多版本ESP-IDF**：兼容ESP-IDF v5.1至v5.5版本
- 🔧 **支持managed_components**：可转换第三方组件的配置菜单

## 🚀 安装说明

### 前提条件

- 已安装ESP-IDF开发环境（v5.1至v5.5）
- 已编译至少一次项目（生成build文件夹）

### 快速安装

1. 克隆或下载本项目到本地
   ```bash
   git clone https://gitee.com/lzplds/esp32-menu-zh.git
   ```

2. 直接运行项目根目录下的批处理文件（Windows系统）
   ```
   esp32-menu_ZH.bat
   ```

3. 或通过Python直接运行脚本（所有系统）
   ```bash
   cd app
   python menu_covert.py
   ```

## 📖 使用方法

### 基本操作流程

1. **编译项目**：确保您的ESP-IDF项目已编译至少一次，生成了build文件夹
   ```bash
   idf.py build
   ```

2. **运行工具**：启动ESP32 Menu Config 中文转换工具

3. **选择功能**：在主菜单中选择您需要的功能：
   ```
   1. 将menu-config转换为中文
   2. 将menu-config还原为英文
   3. ESP-IDF使用tips
   4. 帮助
   5. 检测更新
   6. 退出
   ```

4. **执行操作**：根据提示完成相应操作

5. **重新配置**：转换完成后，重新运行menuconfig查看中文界面
   ```bash
   idf.py menuconfig
   ```

### 功能详解

#### 1. 将menu-config转换为中文

此功能会自动扫描您项目build目录中的配置文件，查找对应的中文翻译资源，并将配置菜单转换为中文显示。转换前会自动备份原始文件。

#### 2. 将menu-config还原为英文

如果您需要使用原始英文界面，可选择此功能将配置菜单还原为英文。此操作会使用之前备份的文件覆盖当前文件。

#### 3. ESP-IDF使用tips

提供ESP-IDF开发环境的使用技巧，包括环境设置、菜单配置、编译和烧录、调试技巧以及性能优化等方面的建议。

#### 4. 帮助

显示工具的详细使用说明、注意事项和技术支持信息。

#### 5. 检测更新

检查是否有工具的更新版本，如果有，可选择立即更新到最新版本。

## 📋 支持的ESP-IDF版本

- ESP-IDF v5.1
- ESP-IDF v5.2
- ESP-IDF v5.3
- ESP-IDF v5.4
- ESP-IDF v5.5

## 📁 项目结构

```
ESP32-menu_ZH/
├── app/                 # 应用程序代码
│   ├── menu_covert.py   # 主程序入口
│   └── Kconfig_copy.py  # 辅助工具
├── resource/            # 中文资源文件
│   ├── ESP-IDF_v5.1/    # ESP-IDF v5.1中文翻译
│   ├── ESP-IDF_v5.2/    # ESP-IDF v5.2中文翻译
│   ├── ESP-IDF_v5.3/    # ESP-IDF v5.3中文翻译
│   ├── ESP-IDF_v5.4/    # ESP-IDF v5.4中文翻译
│   ├── ESP-IDF_v5.5/    # ESP-IDF v5.5中文翻译
│   ├── managed_components/ # 第三方组件翻译
│   └── python_lib/      # Python依赖库
├── esp32-menu_ZH.bat    # Windows启动脚本
└── README.md            # 项目说明文档
```

## 💡 注意事项

1. 转换前请确保已编译项目，生成了build文件夹
2. 转换操作会备份原始文件，可随时还原
3. 转换后需要重新运行idf.py menuconfig才能看到中文界面
4. 如果遇到问题，可选择还原功能恢复原始状态
5. 建议在ESP-IDF环境下运行此工具
6. 工具更新后需要重新启动才能应用新的功能

## 🤝 贡献指南

欢迎对本项目进行贡献！如果您有任何建议或发现问题，请在项目的Issues页面提出。您也可以提交Pull Request来改进代码或添加新功能。

## 📜 许可证

本项目采用MIT许可证开源。详情请查看项目中的LICENSE文件。

## 📞 技术支持

- 项目地址：[https://gitee.com/lzplds/esp32-menu-zh.git](https://gitee.com/lzplds/esp32-menu-zh.git)
- 问题反馈：Issues 页面
- 文档更新：Wiki 页面

---

