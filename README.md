# ESP32 MenuConfig 中文版

## 项目简介
ESP32 MenuConfig 中文版是一个为 ESP-IDF 提供中文菜单配置界面的工具。它允许开发者通过直观的中文界面来配置 ESP-IDF 项目，简化了配置过程并提升了用户体验。

## 功能特点
- 提供中文菜单界面，便于理解和操作。
- 支持将配置文件转换为中文，方便中文用户查看和编辑。
- 提供版本检查和更新功能，确保使用最新版本。
- 支持多种 ESP-IDF 版本（如 v5.4 和 v5.5）。

## 安装步骤
1. 下载项目代码：
   ```bash
   git clone https://gitee.com/lzplds/esp32-menuconfig_zh.git
   ```
2. 进入项目目录：
   ```bash
   cd esp32-menuconfig_zh
   ```
3. 安装依赖库：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法
1. 运行菜单配置工具：
   ```bash
   python app/menu_covert.py
   ```
2. 在中文菜单界面中选择所需的功能，如配置转换、恢复英文界面或查看帮助信息。

## 贡献指南
欢迎贡献代码和文档。请遵循以下步骤：
1. Fork 项目仓库。
2. 创建新分支并进行修改。
3. 提交 Pull Request 并描述更改内容。

## 许可证
本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 版本历史
- **v1.0.0** - 初始版本，支持基本的中文菜单配置功能。
- **v1.1.0** - 增加版本检查和更新功能。
- **v1.2.0** - 支持更多 ESP-IDF 版本，并优化了用户界面。

## 联系方式
如有任何问题或建议，请联系 [lzplds](https://gitee.com/lzplds)。