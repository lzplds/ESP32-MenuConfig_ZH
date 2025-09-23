#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Menu Config 中文转换客户端
使用简单的控制台界面实现
"""

import sys
import os
import signal

# 添加相对路径到Python搜索路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resource', 'python_lib'))

import re
import shutil
import requests
import zipfile
import tempfile
import subprocess
import time

# ANSI 颜色代码
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'  # 重置颜色

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    print(f"\n\n{Colors.CYAN}用户取消操作，程序退出{Colors.END}")
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)

class ESP32MenuConverter:
    """ESP32 菜单配置转换器主类"""
    
    def __init__(self):
        self.running = True
        self.version = "v0.0.3"  # 版本字段
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_header(self):
        """显示标题"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}" + "="*60 + f"{Colors.END}")
        print(f"{Colors.YELLOW}{Colors.BOLD}        ESP32 Menu Config 中文转换工具 {self.version}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}" + "="*60 + f"{Colors.END}\n")
        
    def find_chinese_resource_file(self, script_dir, source_file, menu_name, is_managed_component):
        """
        查找对应的中文资源文件
        """
        # 对于managed_components文件，在resource/managed_components中查找
        if is_managed_component:
            component_name = os.path.basename(source_file)
            managed_resource_dir = os.path.join(script_dir, "..", "resource", "managed_components")
            if os.path.exists(managed_resource_dir):
                config_file = os.path.join(managed_resource_dir, component_name)
                if os.path.exists(config_file):
                    return config_file
            return None
        
        # 对于ESP-IDF文件，从路径提取版本信息
        version_match = re.search(r'esp-idf-v(\d+\.\d+)', source_file)
        if not version_match:
            print(f"{Colors.YELLOW}  警告: 无法从路径中提取ESP-IDF版本信息，跳过转换: {source_file}{Colors.END}")
            return None
        
        idf_version = version_match.group(1)
        resource_dir = os.path.join(script_dir, "..", "resource", f"ESP-IDF_v{idf_version}")
        
        # 检查resource目录是否存在
        if not os.path.exists(resource_dir):
            print(f"{Colors.YELLOW}  警告: resource目录不存在: {resource_dir}，跳过转换{Colors.END}")
            return None
        
        # 1. 首先尝试直接匹配menu_name.kconfig
        config_filename = menu_name + '.kconfig'
        config_file = os.path.join(resource_dir, config_filename)
        if os.path.exists(config_file):
            return config_file
        
        # 2. 尝试将空格和特殊字符替换为下划线
        normalized_name = re.sub(r'[\s-]+', '_', menu_name)
        config_filename = normalized_name + '.kconfig'
        config_file = os.path.join(resource_dir, config_filename)
        if os.path.exists(config_file):
            return config_file
        
        # 3. 模糊匹配，查找包含menu_name的kconfig文件
        try:
            for file in os.listdir(resource_dir):
                if file.endswith('.kconfig'):
                    # 检查文件名是否包含menu_name的关键字
                    file_base = file.replace('.kconfig', '').lower()
                    menu_lower = menu_name.lower()
                    
                    # 直接匹配
                    if menu_lower in file_base or file_base in menu_lower:
                        config_file = os.path.join(resource_dir, file)
                        return config_file
                    
                    # 去除空格和特殊字符后匹配  
                    normalized_menu = re.sub(r'[\s-_]+', '', menu_lower)
                    normalized_file = re.sub(r'[\s-_]+', '', file_base)
                    if normalized_menu in normalized_file or normalized_file in normalized_menu:
                        config_file = os.path.join(resource_dir, file)
                        return config_file
        except OSError as e:
            print(f"{Colors.RED}  错误: 无法访问resource目录 {resource_dir}: {e}{Colors.END}")
            return None
        
        print(f"{Colors.YELLOW}  警告: 未找到对应的中文配置文件: {menu_name}.kconfig{Colors.END}")
        return None
        
    def convert_file_to_chinese(self, source_file, script_dir):
        """将源文件转换为中文显示"""
        try:
            # 检查文件路径是否包含managed_components
            is_managed_component = 'managed_components' in source_file
            
            # 读取源文件内容，找到第一个menu后面的字符
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                print(f"{Colors.RED}  错误: 无法读取源文件 {source_file}: {e}{Colors.END}")
                return
            
            # 查找第一个menu定义
            menu_match = re.search(r'menu\s+"([^"]+)"', content)
            if not menu_match:
                print(f"{Colors.YELLOW}  警告: 源文件中未找到menu定义，跳过转换: {source_file}{Colors.END}")
                return
            
            menu_name = menu_match.group(1)
            print(f"{Colors.BLUE}  检测到菜单: {menu_name}{Colors.END}")
            
            # 查找对应的中文资源文件
            config_file = self.find_chinese_resource_file(script_dir, source_file, menu_name, is_managed_component)
            if not config_file:
                return
            
            
            # 读取中文配置文件
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    chinese_content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                print(f"{Colors.RED}  错误: 无法读取中文配置文件 {config_file}: {e}{Colors.END}")
                return
            
            # 解析中文配置文件，提取子选项信息
            chinese_options = {}
            # 匹配config、menu、choice等子选项
            option_patterns = [
                r'(config|menu|choice|comment)\s+(\w+)\s+(?:bool|string|int|hex)\s+"([^"]+)"',
                r'(config|menu|choice|comment)\s+(\w+)\s+"([^"]+)"'
            ]
            
            for pattern in option_patterns:
                matches = re.finditer(pattern, chinese_content, re.MULTILINE)
                for match in matches:
                    option_type, option_name, option_text = match.groups()
                    chinese_options[option_name] = (option_type, option_text)
            
            # 6. 修改源文件内容
            modified_content = content
            modified_count = 0
            
            # 替换选项文本 - 改进的精确替换逻辑
            for option_name, (option_type, option_text) in chinese_options.items():
                # 不修改主menu，只修改子选项
                if option_type == 'menu' and option_name == menu_name:
                    continue
                
                # 构建精确匹配模式，考虑行首缩进
                patterns = [
                    # 匹配带类型的配置项
                    fr'(\s*{option_type}\s+{option_name}\s+(?:bool|string|int|hex)\s+)"([^"]*)"',
                    # 匹配不带类型的配置项  
                    fr'(\s*{option_type}\s+{option_name}\s+)"([^"]*)"'
                ]
                
                replaced = False
                for pattern in patterns:
                    matches = list(re.finditer(pattern, modified_content, re.MULTILINE))
                    if matches:
                        # 从后往前替换，避免位置偏移
                        for match in reversed(matches):
                            existing_text = match.group(2)
                            if existing_text != option_text:
                                start, end = match.span()
                                replacement = match.group(1) + f'"{option_text}"'
                                modified_content = modified_content[:start] + replacement + modified_content[end:]
                                modified_count += 1
                                replaced = True
                        break
                
                if not replaced:
                    print(f"{Colors.YELLOW}  警告: 在源文件中未找到选项: {option_name}{Colors.END}")

            # 7. 替换help文本
            # 先在中文配置中提取help信息
            help_pattern = r'(config|menu|choice|comment)\s+(\w+)[\s\S]*?help\s+([\s\S]*?)(?=\n\s*(?:config|menu|choice|comment|endmenu|endchoice|#))'
            chinese_helps = {}
            
            matches = re.finditer(help_pattern, chinese_content, re.MULTILINE)
            for match in matches:
                option_type, option_name, help_text = match.groups()
                chinese_helps[option_name] = help_text.strip()
            
            # 在源文件中替换help文本
            for option_name, help_text in chinese_helps.items():
                # 不修改主menu的help
                if option_name == menu_name:
                    continue
                
                # 查找源文件中的help部分
                source_help_pattern = fr'(config|menu|choice|comment)\s+{option_name}[\s\S]*?help\s+([\s\S]*?)(?=\n\s*(?:config|menu|choice|comment|endmenu|endchoice|#))'
                match = re.search(source_help_pattern, modified_content, re.MULTILINE)
                
                if match:
                    existing_help = match.group(2).strip()
                    # 对比文字是否相同，相同则不修改也不统计
                    if existing_help == help_text:
                        continue
                    # 进行替换
                    prefix = match.group(1)
                    modified_content = re.sub(source_help_pattern, fr'{prefix} {option_name}\s+help\n{help_text}', modified_content)
                    modified_count += 1
            
            # 8. 保存修改后的文件
            if modified_count > 0:
                with open(source_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print(f"{Colors.GREEN}  成功: 已将{source_file}转换为中文，修改了{modified_count}处{Colors.END}")
            else:
                print(f"{Colors.WHITE}  信息: 未在{source_file}中找到需要转换的内容{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}  错误: 转换文件失败{source_file}: {e}{Colors.END}")
            # 出现错误时保留备份文件，不删除
            pass
        
    def show_main_menu(self):
        """显示主菜单"""
        self.clear_screen()
        self.show_header()
        
        print(f"{Colors.GREEN}请选择操作：{Colors.END}")
        print()
        # 每行显示两列选项，使用Tab对齐
        print(f"{Colors.WHITE}1. 将menu-config转换为中文\t\t2. 将menu-config还原为英文{Colors.END}")
        print(f"{Colors.WHITE}3. ESP-IDF使用tips\t\t\t4. 帮助{Colors.END}")
        print(f"{Colors.WHITE}5. 检测更新\t\t\t\t6. 退出{Colors.END}")
        print()
        print(f"{Colors.CYAN}" + "-" * 60 + f"{Colors.END}")
        print(f"{Colors.MAGENTA}使用数字键选择，按回车确认{Colors.END}")
        
    def show_convert_to_chinese(self):
        """显示转换为中文的二级菜单"""
        self.clear_screen()
        self.show_header()
        print(f"{Colors.YELLOW}{Colors.BOLD}转换为中文{Colors.END}")
        print(f"{Colors.CYAN}" + "="*30 + f"{Colors.END}")
        print()
        
        # 检查build文件夹中的文件
        # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 从脚本目录向上两级到项目根目录，然后进入build文件夹
        build_path = os.path.join(script_dir, "..", "..", "build")
        build_path = os.path.abspath(build_path)  # 转换为绝对路径
        kconfigs_file = os.path.join(build_path, "kconfigs.in")
        kconfigs_projbuild_file = os.path.join(build_path, "kconfigs_projbuild.in")
        
        print(f"{Colors.BLUE}正在检查必要文件...{Colors.END}")
        print(f"{Colors.WHITE}当前工作目录: {os.getcwd()}{Colors.END}")
        print(f"{Colors.WHITE}脚本目录: {script_dir}{Colors.END}")
        print(f"{Colors.WHITE}检查路径: {build_path}{Colors.END}")
        print(f"{Colors.WHITE}目标文件: kconfigs.in, kconfigs_projbuild.in{Colors.END}")
        print()
        
        # 检查文件是否存在
        kconfigs_exists = os.path.exists(kconfigs_file)
        kconfigs_projbuild_exists = os.path.exists(kconfigs_projbuild_file)
        
        print(f"{Colors.WHITE}文件检查结果：{Colors.END}")
        print(f"{Colors.WHITE}• kconfigs.in: {'✓ 存在' if kconfigs_exists else '✗ 不存在'}{Colors.END}")
        print(f"{Colors.WHITE}• kconfigs_projbuild.in: {'✓ 存在' if kconfigs_projbuild_exists else '✗ 不存在'}{Colors.END}")
        print()
        
        if not kconfigs_exists or not kconfigs_projbuild_exists:
            print(f"{Colors.RED}工作区build文件夹无效，请先编译工程。{Colors.END}")
            print(f"{Colors.YELLOW}建议操作：{Colors.END}")
            print(f"{Colors.WHITE}• 运行 'idf.py build' 编译项目{Colors.END}")
            print(f"{Colors.WHITE}• 确认在正确的ESP-IDF项目目录中运行{Colors.END}")
            print()
            input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")
            return
        
        print(f"{Colors.GREEN}正在处理配置文件...{Colors.END}")
        print()
        
        # 处理两个文件
        files_to_process = [kconfigs_file, kconfigs_projbuild_file]
        
        for config_file in files_to_process:
            print(f"{Colors.BLUE}处理文件: {config_file}{Colors.END}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line.startswith('source'):
                        # 提取source后面的文件路径
                        parts = line.split(None, 1)  # 分割为'source'和路径部分
                        if len(parts) > 1:
                            source_path = parts[1].strip('"\'')
                            # 转换为相对路径
                            source_file = os.path.join(build_path, source_path)
                            
                            if os.path.exists(source_file):
                                backup_file = source_file + '.menu.covert.bak'
                                try:
                                    # 检查备份文件是否已存在
                                    if os.path.exists(backup_file):
                                        print(f"{Colors.YELLOW}  文件{line_num}: 备份文件已存在: {source_path}.menu.covert.bak，跳过备份{Colors.END}")
                                    else:
                                        # 复制文件并添加.menu.covert.bak后缀
                                        shutil.copy2(source_file, backup_file)
                                        print(f"{Colors.WHITE}  文件{line_num}: {source_path} -> {source_path}.menu.covert.bak{Colors.END}")
                                          
                                    # 检查文件是否需要转换
                                    # 首先检查是否是managed_components路径的文件
                                    is_managed_component = 'managed_components' in source_path
                                    
                                    # 检查resource目录下是否有对应的中文文件
                                    resource_zh_file = None
                                    
                                    # 优先处理managed_components路径的文件
                                    if is_managed_component:
                                        resource_zh_file = os.path.join(script_dir, '..', 'resource', 'managed_components', os.path.basename(source_file))
                                    elif 'esp-idf' in source_path.lower():
                                        # 尝试在resource目录下找到对应的中文文件
                                        resource_path = os.path.join(script_dir, '..', 'resource')
                                        # 提取esp-idf版本号
                                        version_match = re.search(r'esp-idf-v?(\d+\.\d+)', source_path.lower())
                                        if version_match:
                                            idf_version = version_match.group(1)
                                            # 构建resource目录下的对应路径
                                            # 找到esp-idf相关部分并替换
                                            for part in source_path.split(os.sep):
                                                if 'esp-idf' in part.lower():
                                                    relative_path = source_path.split(part)[1].lstrip(os.sep)
                                                    resource_zh_file = os.path.join(resource_path, f'ESP-IDF_v{idf_version}', relative_path)
                                                    break
                                            
                                            # 如果没有找到，尝试使用默认版本
                                            if not resource_zh_file or not os.path.exists(resource_zh_file):
                                                for version in ['v5.5', 'v5.4', 'v5.3', 'v5.2', 'v5.1']:
                                                    test_path = os.path.join(resource_path, version)
                                                    if os.path.exists(test_path):
                                                        # 尝试匹配路径中的组件名
                                                        component_name = os.path.basename(source_file)
                                                        test_zh_file = os.path.join(test_path, 'components', os.path.basename(os.path.dirname(source_file)), component_name)
                                                        if os.path.exists(test_zh_file):
                                                            resource_zh_file = test_zh_file
                                                            break
                                    
                                    # 确保resource_zh_file不为None，然后检查是否存在
                                    if resource_zh_file is not None and os.path.exists(resource_zh_file):
                                        # 存在中文文件，需要进行翻译转换
                                        self.convert_file_to_chinese(source_file, script_dir)
                                    else:
                                        print(f"{Colors.YELLOW}  文件{line_num}: 未找到对应的中文配置文件，跳过转换{Colors.END}")
                                except Exception as e:
                                    print(f"{Colors.RED}  文件{line_num}: 复制{source_path}失败: {e}{Colors.END}")
                            else:
                                print(f"{Colors.YELLOW}  文件{line_num}: 文件不存在: {source_path}{Colors.END}")
                        
            except Exception as e:
                print(f"{Colors.RED}读取文件{config_file}失败: {e}{Colors.END}")
            
            print()  # 空行分隔
        
        print(f"{Colors.GREEN}处理完成！{Colors.END}")
        print(f"{Colors.GREEN}须重新构建工程，配置才能生效{Colors.END}")
        print()
        input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")
    
    def show_restore_to_english(self):
        """显示还原为英文的二级菜单并恢复原始文件"""
        self.clear_screen()
        self.show_header()
        print(f"{Colors.YELLOW}{Colors.BOLD}即将还原配置菜单为英文{Colors.END}")
        print(f"{Colors.CYAN}" + "="*30 + f"{Colors.END}")
        print()
        
        # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 从脚本目录向上两级到项目根目录，然后进入build文件夹
        build_path = os.path.join(script_dir, "..", "..", "build")
        build_path = os.path.abspath(build_path)  # 转换为绝对路径
        kconfigs_file = os.path.join(build_path, "kconfigs.in")
        kconfigs_projbuild_file = os.path.join(build_path, "kconfigs_projbuild.in")
        
        print(f"{Colors.BLUE}正在检查必要文件...{Colors.END}")
        print(f"{Colors.WHITE}检查路径: {build_path}{Colors.END}")
        print()
        
        # 检查文件是否存在
        kconfigs_exists = os.path.exists(kconfigs_file)
        kconfigs_projbuild_exists = os.path.exists(kconfigs_projbuild_file)
        
        if not kconfigs_exists or not kconfigs_projbuild_exists:
            print(f"{Colors.RED}工作区build文件夹无效，请先编译工程。{Colors.END}")
            print()
            input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")
            return
        
        # 获取用户确认
        confirm = input(f"{Colors.YELLOW}确定要恢复原始文件吗？这将删除当前的源文件并使用备份文件替换。(y/n): {Colors.END}").strip().lower()
        if confirm != 'y':
            print(f"{Colors.WHITE}操作已取消{Colors.END}")
            print()
            input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")
            return
        
        print()
        print(f"{Colors.GREEN}正在查找并恢复原始文件...{Colors.END}")
        print()
        
        # 处理两个文件
        files_to_process = [kconfigs_file, kconfigs_projbuild_file]
        restored_count = 0
        
        for config_file in files_to_process:
            print(f"{Colors.BLUE}处理文件: {config_file}{Colors.END}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line.startswith('source'):
                        # 提取source后面的文件路径
                        parts = line.split(None, 1)  # 分割为'source'和路径部分
                        if len(parts) > 1:
                            source_path = parts[1].strip('"\'')
                            # 转换为相对路径
                            source_file = os.path.join(build_path, source_path)
                            
                            # 构建.menu.covert.bak文件路径
                            backup_file = source_file + '.menu.covert.bak'
                            
                            # 检查.menu.covert.bak文件是否存在
                            if os.path.exists(backup_file):
                                try:
                                    # 先删除源文件（如果存在）
                                    if os.path.exists(source_file):
                                        os.remove(source_file)
                                        
                                    # 将备份文件重命名为源文件
                                    os.rename(backup_file, source_file)
                                    print(f"{Colors.WHITE}  文件{line_num}: 已恢复 {source_path} (从.menu.covert.bak备份){Colors.END}")
                                    restored_count += 1
                                except Exception as e:
                                    print(f"{Colors.RED}  文件{line_num}: 恢复{source_path}失败: {e}{Colors.END}")
                            else:
                                print(f"{Colors.YELLOW}  文件{line_num}: 备份文件不存在: {source_path}.menu.covert.bak{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}读取文件{config_file}失败: {e}{Colors.END}")
            
            print()  # 空行分隔
        
        print(f"{Colors.GREEN}处理完成！共恢复了 {restored_count} 个文件{Colors.END}")
        print(f"{Colors.GREEN}还原后须重新构建工程，配置才能生效{Colors.END}")
        print()
        input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")
    
    def show_esp_idf_tips(self):
        """显示ESP-IDF使用tips"""
        self.clear_screen()
        self.show_header()
        print(f"{Colors.YELLOW}{Colors.BOLD}ESP-IDF 使用指南{Colors.END}")
        print(f"{Colors.CYAN}" + "="*30 + f"{Colors.END}")
        print()
        print(f"{Colors.GREEN}🔧 开发环境设置：{Colors.END}")
        print(f"{Colors.WHITE}• 使用 idf.py 命令行工具{Colors.END}")
        print(f"{Colors.WHITE}• 配置正确的工具链路径{Colors.END}")
        print(f"{Colors.WHITE}• 设置串口权限和波特率{Colors.END}")
        print()
        print(f"{Colors.BLUE}📝 菜单配置 (menuconfig)：{Colors.END}")
        print(f"{Colors.WHITE}• idf.py menuconfig - 打开配置菜单{Colors.END}")
        print(f"{Colors.WHITE}• 使用空格键选择/取消选择{Colors.END}")
        print(f"{Colors.WHITE}• 使用回车键进入子菜单{Colors.END}")
        print(f"{Colors.WHITE}• 按 '?' 查看帮助信息{Colors.END}")
        print()
        print(f"{Colors.MAGENTA}🚀 编译和烧录：{Colors.END}")
        print(f"{Colors.WHITE}• idf.py build - 编译项目{Colors.END}")
        print(f"{Colors.WHITE}• idf.py flash - 烧录到设备{Colors.END}")
        print(f"{Colors.WHITE}• idf.py monitor - 监控串口输出{Colors.END}")
        print(f"{Colors.WHITE}• idf.py flash monitor - 烧录并监控{Colors.END}")
        print()
        print(f"{Colors.RED}🐛 调试技巧：{Colors.END}")
        print(f"{Colors.WHITE}• 使用 ESP_LOGI/ESP_LOGE 宏打印日志{Colors.END}")
        print(f"{Colors.WHITE}• 配置适当的日志级别{Colors.END}")
        print(f"{Colors.WHITE}• 使用 idf.py monitor 查看运行状态{Colors.END}")
        print(f"{Colors.WHITE}• 利用 GDB 进行深度调试{Colors.END}")
        print()
        print(f"{Colors.YELLOW}⚡ 性能优化：{Colors.END}")
        print(f"{Colors.WHITE}• 合理配置 CPU 频率{Colors.END}")
        print(f"{Colors.WHITE}• 优化内存使用{Colors.END}")
        print(f"{Colors.WHITE}• 启用编译器优化选项{Colors.END}")
        print(f"{Colors.WHITE}• 使用分区表管理Flash存储{Colors.END}")
        print()
        input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")    
    
    def show_help(self):
        """显示帮助信息"""
        self.clear_screen()
        self.show_header()
        print(f"{Colors.YELLOW}{Colors.BOLD}帮助文档{Colors.END}")
        print(f"{Colors.CYAN}" + "="*30 + f"{Colors.END}")
        print()
        print(f"{Colors.GREEN}📖 工具介绍：{Colors.END}")
        print(f"{Colors.WHITE}本工具旨在帮助中文开发者更好地使用ESP-IDF开发环境，{Colors.END}")
        print(f"{Colors.WHITE}通过提供菜单配置的中英文转换功能，降低语言障碍。{Colors.END}")
        print()
        print(f"{Colors.BLUE}🎯 主要功能：{Colors.END}")
        print(f"{Colors.WHITE}1. 中文转换 - 将英文menuconfig转换为中文显示{Colors.END}")
        print(f"{Colors.WHITE}2. 英文还原 - 将中文menuconfig还原为英文{Colors.END}")
        print(f"{Colors.WHITE}3. ESP-IDF指南 - 提供开发技巧和最佳实践{Colors.END}")
        print(f"{Colors.WHITE}4. 在线帮助 - 获取使用说明和故障排除{Colors.END}")
        print()
        print(f"{Colors.MAGENTA}🔧 使用方法：{Colors.END}")
        print(f"{Colors.WHITE}• 输入数字 1-6 选择菜单项{Colors.END}")
        print(f"{Colors.WHITE}• 按下回车键确认选择{Colors.END}")
        print(f"{Colors.WHITE}• 在任何界面都可以使用 Ctrl+C 强制退出{Colors.END}")
        print()
        print(f"{Colors.RED}💡 注意事项：{Colors.END}")
        print(f"{Colors.WHITE}• 转换前请备份原始配置文件{Colors.END}")
        print(f"{Colors.WHITE}• 确保有足够的磁盘空间进行文件操作{Colors.END}")
        print(f"{Colors.WHITE}• 建议在ESP-IDF环境下运行此工具{Colors.END}")
        print(f"{Colors.WHITE}• 如遇问题请查看日志文件或联系技术支持{Colors.END}")
        print()
        print(f"{Colors.CYAN}📞 技术支持：{Colors.END}")
        print(f"{Colors.WHITE}• 项目地址：GitHub ESP32-menu_ZH{Colors.END}")
        print(f"{Colors.WHITE}• 问题反馈：Issues 页面{Colors.END}")
        print(f"{Colors.WHITE}• 文档更新：Wiki 页面{Colors.END}")
        print()
        print(f"{Colors.YELLOW}版本：{self.version}{Colors.END}")
        print()
        input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")
    
    def check_for_updates(self):
        """检测更新 - 从gitee项目获取最新版本信息，从github下载更新"""
        self.clear_screen()
        self.show_header()
        print(f"{Colors.YELLOW}{Colors.BOLD}检测更新{Colors.END}")
        print(f"{Colors.CYAN}" + "="*30 + f"{Colors.END}")
        print()
        
        # gitee项目信息（在try块外定义以避免在异常处理中未定义）
        gitee_repo_url = "https://gitee.com/lzplds/esp32-menuconfig_zh"
        api_url = "https://gitee.com/api/v5/repos/lzplds/esp32-menuconfig_zh/releases/latest"
        
        try:
            print(f"{Colors.BLUE}正在检查更新...{Colors.END}")
            print(f"{Colors.WHITE}当前版本：{self.version}{Colors.END}")
            print(f"{Colors.WHITE}检查更新源连接...{Colors.END}")
            
            # 发送请求获取最新版本信息
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()  # 抛出HTTP错误
            
            # 解析响应内容
            latest_release = response.json()
            latest_version = latest_release.get("tag_name", "v0.0.0")
            release_title = latest_release.get("name", "")
            release_description = latest_release.get("body", "")
            
            # 显示版本信息
            print(f"{Colors.WHITE}最新版本：{latest_version}{Colors.END}")
            print(f"{Colors.WHITE}版本标题：{release_title}{Colors.END}")
            
            # 版本比较
            if self.compare_versions(self.version, latest_version) < 0:
                print(f"\n{Colors.GREEN}🎉 发现新版本！{Colors.END}")
                print(f"{Colors.YELLOW}版本更新内容：{Colors.END}")
                # 显示更新描述（限制显示行数）
                description_lines = release_description.strip().split('\n')
                for i, line in enumerate(description_lines[:5]):
                    print(f"{Colors.WHITE}  {line.strip()}{Colors.END}")
                if len(description_lines) > 5:
                    print(f"{Colors.WHITE}  ... 更多更新内容请访问项目页面查看{Colors.END}")
                
                # 提示有新版本，并询问是否立即更新
                
                # 询问用户是否更新
                update_confirm = input(f"\n{Colors.MAGENTA}是否立即下载并更新到最新版本？更新完成后将自动重启 (y/n): {Colors.END}").strip().lower()
                if update_confirm == 'y':
                    # 构建GitHub下载URL
                    github_download_url = f"https://codeload.github.com/lzplds/ESP32-MenuConfig_ZH/zip/refs/tags/{latest_version}"
                    self.perform_update(github_download_url, latest_version)
                    return  # 更新过程中会自动重启，不需要继续
                else:
                    print(f"{Colors.WHITE}您选择暂不更新，可以随时通过主菜单选项5进行更新{Colors.END}")
            else:
                print(f"\n{Colors.GREEN}检查完成！{Colors.END}")
                print(f"{Colors.GREEN}🎉 您正在使用最新版本的ESP32 Menu Config 中文转换工具{Colors.END}")
                print(f"{Colors.WHITE}项目地址：{gitee_repo_url}{Colors.END}")
        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}\n检查更新失败: 网络连接错误 - {e}{Colors.END}")
            print(f"{Colors.YELLOW}可能是网络连接问题或Gitee API访问限制，请稍后重试{Colors.END}")
            print(f"{Colors.YELLOW}您也可以手动访问项目页面检查更新: {gitee_repo_url}/releases{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}\n检查更新失败: {str(e)}{Colors.END}")
            print(f"{Colors.YELLOW}请手动访问项目页面检查更新: https://gitee.com/lzplds/esp32-menuconfig_zh{Colors.END}")
        
        print()
        input(f"{Colors.MAGENTA}按回车键返回主菜单...{Colors.END}")
        
    def compare_versions(self, current_version, latest_version):
        """比较版本号，返回-1（当前版本旧）、0（相同）、1（当前版本新）"""
        # 移除版本号前缀v并分割成数字列表
        def parse_version(v):
            parts = v.lstrip('vV').split('.')
            return [int(part) if part.isdigit() else 0 for part in parts]
            
        current = parse_version(current_version)
        latest = parse_version(latest_version)
        
        # 比较版本号数字
        for c, l in zip(current, latest):
            if c < l:
                return -1
            if c > l:
                return 1
        
        # 如果前面的数字都相同，比较长度
        if len(current) < len(latest):
            return -1
        if len(current) > len(latest):
            return 1
        
        return 0
        
    def restart_tool(self):
        """自动重新启动工具"""
        try:
            # 获取脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(script_dir, "..")
            bat_file = os.path.join(project_root, "esp32-menu_ZH.bat")
            
            if os.path.exists(bat_file):
                print(f"{Colors.WHITE}正在重新启动工具...{Colors.END}")
                print(f"{Colors.YELLOW}3秒后自动重新启动...{Colors.END}")
                
                # 短暂延迟给用户时间阅读信息
                time.sleep(3)
                
                # 使用 subprocess 启动新进程
                subprocess.Popen([bat_file], cwd=project_root, shell=True)
                
                # 退出当前程序
                sys.exit(0)
            else:
                print(f"{Colors.RED}未找到 esp32-menu_ZH.bat 文件，无法自动重启{Colors.END}")
                print(f"{Colors.YELLOW}请手动重新运行 esp32-menu_ZH.bat{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}自动重启失败: {e}{Colors.END}")
            print(f"{Colors.YELLOW}请手动重新运行 esp32-menu_ZH.bat{Colors.END}")
    
    def perform_update(self, github_download_url, version):
        """执行更新操作 - 优先从GitHub下载，失败时提示从Gitee手动下载"""
        print(f"{Colors.BLUE}\n正在准备更新...{Colors.END}")
        
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, "..")
        
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "update.zip")
                
                # 尝试从GitHub下载更新包
                print(f"{Colors.WHITE}正在从GitHub下载更新包...{Colors.END}")
                print(f"{Colors.WHITE}下载地址: {github_download_url}{Colors.END}")
                
                try:
                    with requests.get(github_download_url, stream=True, timeout=30) as r:
                        r.raise_for_status()
                        total_length = int(r.headers.get('content-length', 0))
                        downloaded = 0
                        
                        with open(zip_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    if total_length > 0:
                                        percent = int(50 * downloaded / total_length)
                                        print(f"\r{Colors.WHITE}下载进度: [{'█' * percent}{'░' * (50-percent)}] {downloaded/1024/1024:.1f}MB{Colors.END}", end='', flush=True)
                        print()  # 换行
                        
                except requests.exceptions.RequestException as download_error:
                    print(f"\n{Colors.RED}GitHub下载失败: {download_error}{Colors.END}")
                    print(f"{Colors.YELLOW}请手动从Gitee仓库下载更新：{Colors.END}")
                    print(f"{Colors.WHITE}1. 访问: https://gitee.com/lzplds/esp32-menuconfig_zh/releases{Colors.END}")
                    print(f"{Colors.WHITE}2. 下载版本 {version} 的源码包{Colors.END}")
                    print(f"{Colors.WHITE}3. 解压并替换当前目录下的 app 和 resource 文件夹{Colors.END}")
                    print(f"{Colors.WHITE}4. 替换 esp32-menu_ZH.bat 文件{Colors.END}")
                    return
                
                # 验证下载的文件
                if not os.path.exists(zip_path) or os.path.getsize(zip_path) < 1024:
                    raise Exception("下载的文件无效或损坏")
                
                # 解压更新包
                print(f"{Colors.WHITE}解压更新包...{Colors.END}")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 找到解压后的目录（GitHub的zip包格式为：ESP32-MenuConfig_ZH-版本号）
                extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                if not extracted_dirs:
                    raise Exception("解压失败，未找到更新文件")
                
                # GitHub下载的包可能包含版本号后缀，寻找正确的目录
                update_source_dir = None
                for dir_name in extracted_dirs:
                    if 'ESP32-MenuConfig' in dir_name or 'esp32-menuconfig' in dir_name.lower():
                        update_source_dir = os.path.join(temp_dir, dir_name)
                        break
                
                if not update_source_dir:
                    update_source_dir = os.path.join(temp_dir, extracted_dirs[0])
                
                print(f"{Colors.WHITE}更新源目录: {update_source_dir}{Colors.END}")
                
                # 更新文件（仅更新app和resource目录）
                directories_to_update = ["app", "resource"]
                updated_dirs = []
                
                for dir_name in directories_to_update:
                    src_dir = os.path.join(update_source_dir, dir_name)
                    dst_dir = os.path.join(project_root, dir_name)
                    
                    if os.path.exists(src_dir):
                        print(f"{Colors.WHITE}更新{dir_name}目录...{Colors.END}")
                        
                        # 如果目标目录存在，先删除
                        if os.path.exists(dst_dir):
                            if os.name == 'nt':  # Windows
                                subprocess.run(["rmdir", "/s", "/q", dst_dir], shell=True)
                            else:  # Unix-like
                                shutil.rmtree(dst_dir)
                        
                        # 复制新文件
                        shutil.copytree(src_dir, dst_dir)
                        updated_dirs.append(dir_name)
                    else:
                        print(f"{Colors.YELLOW}警告: 源目录不存在 {src_dir}{Colors.END}")
                
                # 更新批处理文件
                bat_file = os.path.join(update_source_dir, "esp32-menu_ZH.bat")
                if os.path.exists(bat_file):
                    print(f"{Colors.WHITE}更新批处理文件...{Colors.END}")
                    shutil.copy2(bat_file, os.path.join(project_root, "esp32-menu_ZH.bat"))
                
                # 更新README文件（如果存在）
                readme_file = os.path.join(update_source_dir, "README.md")
                if os.path.exists(readme_file):
                    print(f"{Colors.WHITE}更新README文件...{Colors.END}")
                    shutil.copy2(readme_file, os.path.join(project_root, "README.md"))
                
                print(f"\n{Colors.GREEN}✅ 更新完成！{Colors.END}")
                print(f"{Colors.GREEN}已更新目录: {', '.join(updated_dirs)}{Colors.END}")
                print(f"{Colors.GREEN}更新版本: {self.version} -> {version}{Colors.END}")
                print(f"{Colors.YELLOW}即将自动重新启动工具...{Colors.END}")
                
                # 自动重新启动工具
                self.restart_tool()
                
        except Exception as e:
            print(f"{Colors.RED}\n更新失败: {str(e)}{Colors.END}")
            print(f"{Colors.YELLOW}请手动从Gitee仓库下载更新：{Colors.END}")
            print(f"{Colors.WHITE}1. 访问: https://gitee.com/lzplds/esp32-menuconfig_zh/releases{Colors.END}")
            print(f"{Colors.WHITE}2. 下载版本 {version} 的源码包{Colors.END}")
            print(f"{Colors.WHITE}3. 解压并替换当前目录下的 app 和 resource 文件夹{Colors.END}")
            print(f"{Colors.WHITE}4. 替换 esp32-menu_ZH.bat 文件{Colors.END}")
        
    def handle_choice(self, choice):
        """处理用户选择"""
        if choice == '1':
            self.show_convert_to_chinese()
        elif choice == '2':
            self.show_restore_to_english()
        elif choice == '3':
            self.show_esp_idf_tips()
        elif choice == '4':
            self.show_help()
        elif choice == '5':
            self.check_for_updates()
        elif choice == '6':
            self.running = False
            print(f"\n{Colors.GREEN}感谢使用 ESP32 Menu Config 转换工具！{Colors.END}")
        else:
            print(f"\n{Colors.RED}无效的选择，请输入 1-6 之间的数字{Colors.END}")
            # 移除 input() 调用，直接返回继续循环
    
    def run(self):
        """运行应用程序"""
        try:
            while self.running:
                self.show_main_menu()
                choice = input(f"\n{Colors.YELLOW}请输入选择 (1-6): {Colors.END}").strip()
                self.handle_choice(choice)
                
        except KeyboardInterrupt:
            # 这个异常处理现在不会被触发，因为信号处理器会直接退出
            pass
        except Exception as e:
            print(f"\n{Colors.RED}程序运行出错: {e}{Colors.END}")


def main():
    """主函数"""
    try:
        app = ESP32MenuConverter()
        # 检查是否有--check-update参数
        if len(sys.argv) > 1 and sys.argv[1] == "--check-update":
            app.check_for_updates()
        else:
            app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())