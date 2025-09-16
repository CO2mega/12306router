import os
import subprocess
import sys

def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("运行 SQLite 性能测试覆盖率测试...")
    
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建命令
    cmd = [
        sys.executable,
        "-m", "pytest",
        "tests/test_sqlite_performance.py",
        "--cov=sqlite_performance_test",
        "--cov-report=term",
        "--cov-report=html",
        "-v"
    ]
    
    # 执行测试命令
    try:
        subprocess.run(cmd, cwd=current_dir, check=True)
        print("\n测试完成！")
        print(f"HTML 覆盖率报告生成在: {os.path.join(current_dir, 'htmlcov')}")
        print("打开 index.html 文件查看详细报告。")
    except subprocess.CalledProcessError as e:
        print(f"测试执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests_with_coverage()