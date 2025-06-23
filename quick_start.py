import subprocess
import webbrowser
import time
import os
import sys
import signal

def main():
    print("=" * 60)
    print("       房源数据分析与价格预测系统 - 快速启动")
    print("=" * 60)
    print("正在启动系统...")

    # 使用直接调用而不是分离的方式启动
    print("正在启动Web服务器...")

    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 尝试多种启动方式
    try:
        if os.name == 'nt':  # Windows
            # 尝试执行常规的Django服务器启动
            try:
                # 方法1: 直接使用manage.py启动
                server_process = subprocess.Popen(
                    ["python", "manage.py", "runserver", "0.0.0.0:8127"],
                    cwd=current_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except:
                # 方法2: 使用runserver直接启动
                print("尝试备用启动方式...")
                server_process = subprocess.Popen(
                    [sys.executable, "-c",
                     "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Python租房房源数据可视化分析.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8127'])"],
                    cwd=current_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
        else:  # 非Windows系统
            try:
                # 方法1: 直接使用manage.py启动
                server_process = subprocess.Popen(
                    ["python", "manage.py", "runserver", "0.0.0.0:8127"],
                    cwd=current_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except:
                # 方法2: 使用runserver直接启动
                print("尝试备用启动方式...")
                server_process = subprocess.Popen(
                    [sys.executable, "-c",
                     "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Python租房房源数据可视化分析.settings'); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8127'])"],
                    cwd=current_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
    except Exception as e:
        print(f"启动失败: {e}")
        print("尝试最简单的方式...")
        # 最后备用方法 - 直接启动 python -m http.server
        if os.name == 'nt':
            server_process = subprocess.Popen(
                ["python", "-m", "http.server", "8127"],
                cwd=current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            server_process = subprocess.Popen(
                ["python", "-m", "http.server", "8127"],
                cwd=current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)

    # 打开浏览器
    print("正在打开浏览器...")
    webbrowser.open("http://localhost:8127/app/login/")

    print("\n系统启动成功!")
    print("=" * 60)
    print("* 访问地址: http://localhost:8127/app/login/")
    print("* 服务器进程ID:", server_process.pid)
    print("=" * 60)
    print("\n按回车键关闭服务器并退出...")

    # 等待用户按回车
    input()

    # 停止服务器进程
    print("正在关闭服务器...")
    try:
        if os.name == 'nt':
            server_process.terminate()
        else:
            os.kill(server_process.pid, signal.SIGTERM)

        server_process.wait(timeout=5)
        print("服务器已关闭。")
    except:
        print("服务器未正常关闭，强制结束进程...")
        if os.name == 'nt':
            server_process.kill()
        else:
            os.kill(server_process.pid, signal.SIGKILL)

    print("系统已退出。")

if __name__ == "__main__":
    main() 