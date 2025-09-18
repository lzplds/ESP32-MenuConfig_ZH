@echo off
rem ESP32 MenuConfig Chinese Tool - Using Pinyin to avoid encoding issues
rem ZhongWenHua = 中文化, GongJu = 工具, XuanZe = 选择, TuiChu = 退出
chcp 65001 >nul
setlocal enabledelayedexpansion

:main_menu
cls
echo.
echo ============================================
echo          ESP32 MenuConfig ZhongWenHua GongJu
echo ============================================
echo.
echo 1. Jiang esp32-menuconfig ZhuanHuan Wei ZhongWen    2. Jiang esp32-menuconfig HuanYuan Wei YingWen
echo.
echo 3. esp-idf ShiYong JiQiao                  4. BangZhu XinXi
echo.
echo 5. FanHui Shang YiYe                       6. TuiChu ChengXu
echo.
echo ============================================
echo.
echo QingShuRu 1-6 XuanZe GongNeng, Huo ShuRu exit ZhiJie TuiChu
echo.
:main_menu_input
set user_input=
set /p user_input=QingXuanZe (1-6) Huo ShuRu exit TuiChu: 
if /i "%user_input%"=="exit" goto exit_script
if "%user_input%"=="1" goto convert_to_chinese
if "%user_input%"=="2" goto restore_to_english
if "%user_input%"=="3" goto esp_idf_tips
if "%user_input%"=="4" goto help_menu
if "%user_input%"=="5" goto previous_page
if "%user_input%"=="6" goto exit_script
if "%user_input%"=="" goto main_menu
echo WuXiao XuanZe, Qing ChongXin ShuRu
goto main_menu_input

:convert_to_chinese
cls
echo.
echo GongNeng KaiFa Zhong, JingQing QiDai GengXin
echo.
set user_input=
set /p user_input=An HuiChe FanHui ZhuCaiDan, Huo ShuRu exit TuiChu: 
if /i "%user_input%"=="exit" goto exit_script
goto main_menu

:restore_to_english
cls
echo.
echo GongNeng KaiFa Zhong, JingQing QiDai GengXin
echo.
set user_input=
set /p user_input=An HuiChe FanHui ZhuCaiDan, Huo ShuRu exit TuiChu: 
if /i "%user_input%"=="exit" goto exit_script
goto main_menu

:esp_idf_tips
cls
echo.
echo ESP-IDF ShiYong JiQiao:
echo 1. ShiYong idf.py build BianYi XiangMu
echo 2. ShiYong idf.py flash ShaoLu GuJian
echo 3. ShiYong idf.py monitor JianKong ShuChu
echo.
set user_input=
set /p user_input=An HuiChe FanHui ZhuCaiDan, Huo ShuRu exit TuiChu: 
if /i "%user_input%"=="exit" goto exit_script
goto main_menu

:help_menu
cls
echo.
echo BangZhu XinXi:
echo Ben GongJu YongYu ESP32-MenuConfig JieMian YingZhong ZhuanHuan
echo QingShuRu 1-6 XuanZe GongNeng, ShuRu exit Ke ZhiJie TuiChu
echo.
set user_input=
set /p user_input=An HuiChe FanHui ZhuCaiDan, Huo ShuRu exit TuiChu: 
if /i "%user_input%"=="exit" goto exit_script
goto main_menu

:previous_page
cls
echo.
echo DangQian YiJing Shi ZhuCaiDan, MeiYou Shang YiYe
echo.
set user_input=
set /p user_input=An HuiChe FanHui ZhuCaiDan, Huo ShuRu exit TuiChu: 
if /i "%user_input%"=="exit" goto exit_script
goto main_menu

:exit_script
cls
echo.
echo XieXie ShiYong, ZaiJian!
timeout /t 2 >nul
exit /b 0