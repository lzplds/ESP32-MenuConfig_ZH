#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kconfig文件拷贝脚本
功能：
1. 读取build文件夹下的kconfigs.in和kconfigs_projbuild.in文件
2. 解析每行source后的文件路径
3. 根据路径中的版本信息将文件拷贝到app/resource相应文件夹
4. 重命名文件为其内容中首个"menu"后面的内容
跨平台兼容：支持Windows、Linux和macOS
"""

import os
import re
import shutil
import sys
from pathlib import Path

# 跨平台兼容的彩色输出实现
class Colors:
    # ANSI转义序列颜色常量
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

# 跨平台检测终端颜色支持
def supports_color():
    """检查终端是否支持彩色输出（跨平台兼容）"""
    plat = sys.platform
    # 检查操作系统平台
    supported_platform = plat not in ('Pocket PC', 'cli')
    
    # Windows 10 版本 1607 及以上原生支持 ANSI 序列
    if plat == 'win32':
        try:
            if sys.getwindowsversion().major >= 10 and sys.getwindowsversion().build >= 10586:
                supported_platform = True
        except AttributeError:
            # 旧版Windows可能没有getwindowsversion方法
            pass
    
    # 检查是否为交互终端
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    # 检查环境变量（常见于CI/CD环境或特定终端）
    if os.environ.get('NO_COLOR') is not None:
        return False
    
    return supported_platform and is_a_tty

# 启用 Windows 命令提示符的 ANSI 支持（Windows 10+）
def enable_windows_ansi_support():
    """启用 Windows 命令提示符的 ANSI 转义序列支持"""
    if sys.platform == 'win32':
        try:
            # 尝试修改控制台模式以支持 ANSI 序列
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            # 忽略任何错误，继续使用默认设置
            pass

# 初始化环境（针对不同平台进行优化）
def init_environment():
    """初始化跨平台环境"""
    # 针对Windows平台特殊处理
    if sys.platform == 'win32':
        enable_windows_ansi_support()
    
    # 检查并尝试导入colorama库作为备选
    has_colorama = False
    try:
        import colorama
        colorama.init(autoreset=True)
        has_colorama = True
    except ImportError:
        pass
    
    return has_colorama

# 初始化环境
HAS_COLORAMA = init_environment()

# 跨平台的彩色输出函数
def colored_print(text, color=None):
    """打印带颜色的文本（跨平台兼容）"""
    # 如果不支持彩色输出，直接返回原始文本
    if not supports_color():
        return text
    
    # 使用colorama库（如果可用）
    if HAS_COLORAMA:
        from colorama import Fore, Style
        color_map = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'cyan': Fore.CYAN,
            'magenta': Fore.MAGENTA
        }
        color_code = color_map.get(color, '')
        return f"{color_code}{text}{Style.RESET_ALL}"
    
    # 使用ANSI转义序列（默认方案）
    color_map = {
        'red': Colors.RED,
        'green': Colors.GREEN,
        'yellow': Colors.YELLOW,
        'blue': Colors.BLUE,
        'cyan': Colors.CYAN,
        'magenta': Colors.MAGENTA
    }
    color_code = color_map.get(color, '')
    return f"{color_code}{text}{Colors.RESET}"

# 首次运行时的环境信息提示
if HAS_COLORAMA:
    print(colored_print("使用 colorama 库进行彩色输出", 'green'))
else:
    print(colored_print("使用标准 ANSI 转义序列进行彩色输出", 'blue'))
    # 提供安装提示（仅在Windows平台）
    if sys.platform == 'win32':
        print("若彩色输出不正常，建议在 PowerShell 中运行脚本，或安装 colorama 库：")
        print("pip install colorama")

# 跨平台的路径标准化函数
def normalize_path(path):
    """标准化路径以确保跨平台兼容性"""
    return Path(path).resolve()

# 从Kconfig文件中提取第一个menu后面的内容作为文件名
def extract_menu_name(file_path):
    """
    从Kconfig文件中提取第一个menu后面的内容作为文件名
    """
    try:
        # 确保文件路径标准化
        file_path = normalize_path(file_path)
        
        # 使用utf-8编码读取文件，兼容各种平台
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                # 匹配menu "内容"格式
                match = re.search(r'menu\s+"([^"]+)"', line.strip())
                if match:
                    menu_name = match.group(1)
                    # 清理文件名中的非法字符（跨平台兼容）
                    menu_name = re.sub(r'[<>:"/\\|?*]', '_', menu_name)
                    return menu_name
        # 如果没有找到menu，使用原文件名（不含扩展名）
        return Path(file_path).stem
    except Exception as e:
        print(colored_print(f"读取文件 {file_path} 时出错: {e}", 'red'))
        return Path(file_path).stem

# 根据文件路径确定目标目录
def get_target_directory(file_path):
    """
    根据文件路径确定目标目录
    - 如果路径中有esp-idf-vX.Y.Z，则返回ESP-IDF_vX.Y（提取主版本号）
    - 如果路径中有managed_components，则返回managed_components
    - 否则返回None表示跳过
    """
    file_path_str = str(file_path)
    
    # 首先检查是否包含esp-idf-v版本号模式（忽略大小写）
    match = re.search(r'esp-idf-(v\d+\.\d+)', file_path_str, re.IGNORECASE)
    if match:
        # 提取主版本号（如v5.4.2提取为v5.4）
        main_version = match.group(1)
        return f"ESP-IDF_{main_version}"
    
    # 检查是否包含managed_components
    elif 'managed_components' in file_path_str:
        return "managed_components"
    
    else:
        return None

# 主处理函数
def process_kconfig_files():
    """
    处理kconfig文件（跨平台兼容实现）
    """
    try:
        # 获取脚本文件所在目录的路径（跨平台方式）
        script_dir = Path(__file__).parent.resolve()
        
        # 工作区路径确定 - 更灵活的方式
        # 从脚本目录向上查找，直到找到build目录
        current_dir = script_dir
        max_levels = 5  # 最大向上查找层级
        found_build = False
        
        while max_levels > 0 and not found_build:
            parent_dir = current_dir.parent
            if parent_dir == current_dir:  # 到达根目录
                break
            
            build_dir = parent_dir / "build"
            if build_dir.is_dir():
                workspace_path = parent_dir
                found_build = True
                break
            
            current_dir = parent_dir
            max_levels -= 1
        
        # 如果没有找到build目录，使用原有逻辑作为备选
        if not found_build:
            workspace_path = script_dir.parent.parent
            print(colored_print("警告：未找到build目录，使用默认路径逻辑", 'yellow'))
        
        # 确定build路径
        build_path = workspace_path / "build"
        
        # 确定resource目录路径
        # 从脚本目录向上查找ESP32-menu_ZH目录
        current_dir = script_dir
        max_levels = 3
        found_app_dir = False
        
        while max_levels > 0 and not found_app_dir:
            parent_dir = current_dir.parent
            if parent_dir == current_dir:  # 到达根目录
                break
            
            if parent_dir.name.lower() == "esp32-menu_zh":
                app_resource_path = parent_dir / "resource"
                found_app_dir = True
                break
            
            current_dir = parent_dir
            max_levels -= 1
        
        # 如果没有找到ESP32-menu_ZH目录，使用原有逻辑
        if not found_app_dir:
            app_resource_path = script_dir.parent / "resource"
        
        # 确保resource目录存在
        app_resource_path.mkdir(parents=True, exist_ok=True)
        
        # 要处理的配置文件
        config_files = [
            build_path / "kconfigs.in",
            build_path / "kconfigs_projbuild.in"
        ]
        
        processed_files = []
        failed_files = []
        skipped_files = []
        
        for config_file in config_files:
            if not config_file.exists():
                print(colored_print(f"配置文件不存在: {config_file}", 'red'))
                continue
                
            print(colored_print(f"\n处理配置文件: {config_file}", 'blue'))
            
            try:
                with open(config_file, 'r', encoding='utf-8', errors='replace') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line or not line.startswith('source'):
                            continue
                        
                        # 提取source后面的文件路径（去掉引号）
                        match = re.search(r'source\s+"([^"]+)"', line)
                        if not match:
                            continue
                        
                        source_file_path = match.group(1)
                        
                        # 标准化源文件路径
                        # 处理相对路径情况
                        if not Path(source_file_path).is_absolute():
                            # 假设相对路径是相对于build目录
                            source_file = build_path / source_file_path
                            source_file = source_file.resolve()
                        else:
                            source_file = Path(source_file_path)
                        
                        if not source_file.exists():
                            print(colored_print(f"  源文件不存在: {source_file_path}", 'red'))
                            failed_files.append({
                                'source': source_file_path,
                                'reason': '源文件不存在'
                            })
                            continue
                        
                        # 获取目标目录
                        target_dir_name = get_target_directory(source_file_path)
                        if target_dir_name is None:
                            skipped_files.append({
                                'source': source_file_path,
                                'reason': '路径中不包含esp-idf-v版本号或managed_components'
                            })
                            print(colored_print(f"  跳过文件: {source_file_path}", 'yellow'))
                            continue
                        
                        # 创建目标目录
                        target_dir = app_resource_path / target_dir_name
                        target_dir.mkdir(parents=True, exist_ok=True)
                        
                        # 提取menu名称作为新文件名
                        menu_name = extract_menu_name(source_file_path)
                        new_filename = f"{menu_name}.kconfig"
                        
                        # 目标文件路径
                        target_file = target_dir / new_filename
                        
                        # 拷贝文件（使用shutil.copy2保持元数据）
                        try:
                            shutil.copy2(source_file, target_file)
                            processed_files.append({
                                'source': source_file_path,
                                'target': str(target_file),
                                'menu_name': menu_name,
                                'version': target_dir_name
                            })
                            print(colored_print(f"  拷贝成功: {source_file.name} -> {target_file}", 'green'))
                            print(colored_print(f"    菜单名: {menu_name}", 'cyan'))
                            print(colored_print(f"    目标目录: {target_dir_name}", 'cyan'))
                        except Exception as e:
                            print(colored_print(f"  拷贝失败 {source_file_path}: {e}", 'red'))
                            failed_files.append({
                                'source': source_file_path,
                                'reason': f'拷贝失败: {e}'
                            })
                    
            except Exception as e:
                print(colored_print(f"处理配置文件 {config_file} 时出错: {e}", 'red'))
        
        # 输出处理结果统计
        print(colored_print(f"\n\n=== 处理完成 ===", 'magenta'))
        print(colored_print(f"成功处理: {len(processed_files)} 个文件", 'green'))
        print(colored_print(f"失败处理: {len(failed_files)} 个文件", 'red'))
        print(colored_print(f"跳过处理: {len(skipped_files)} 个文件", 'yellow'))
        print(colored_print(f"总计: {len(processed_files) + len(failed_files) + len(skipped_files)} 个文件", 'blue'))
        
        # 如果有失败的文件，显示失败详情
        if failed_files:
            print(colored_print(f"\n失败文件详情:", 'red'))
            for failed in failed_files:
                print(colored_print(f"  {Path(failed['source']).name}: {failed['reason']}", 'red'))
        
        # 如果有跳过的文件，显示跳过详情
        if skipped_files:
            print(colored_print(f"\n跳过文件详情:", 'yellow'))
            for skipped in skipped_files:
                print(colored_print(f"  {Path(skipped['source']).name}: {skipped['reason']}", 'yellow'))
        
    except Exception as e:
        # 捕获并显示所有未处理的异常
        print(colored_print(f"处理过程中出现错误: {e}", 'red'))
        import traceback
        traceback.print_exc()

# 主程序入口
if __name__ == "__main__":
    try:
        process_kconfig_files()
    except KeyboardInterrupt:
        print(colored_print("\n用户中断操作", 'yellow'))
    except Exception as e:
        print(colored_print(f"程序执行出错: {e}", 'red'))
        import traceback
        traceback.print_exc()