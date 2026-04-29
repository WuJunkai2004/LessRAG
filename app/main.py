import argparse
import os
import shutil
from pathlib import Path

import uvicorn


def handle_config(args):
    """处理 config 命令：从包目录复制 config.example.toml 到当前工作目录下的 config.toml"""
    # 源文件：现在与本文件在同一目录下
    src = Path(__file__).resolve().parent / "config.example.toml"

    # 目标文件：用户当前所在的目录
    dst = Path.cwd() / "config.toml"

    if not src.exists():
        print(f"[-] 错误: 找不到模板文件 {src}")
        exit(1)

    if dst.exists():
        try:
            choice = input(
                f"[!] 当前目录下 {dst.name} 已存在，是否覆盖？(y/N): "
            ).lower()
            if choice != "y":
                print("[*] 操作已取消")
                return
        except KeyboardInterrupt:
            print("\n[*] 操作已取消")
            return

    try:
        # 记录是否为覆盖操作
        is_update = dst.exists()

        # 使用临时文件进行原子性操作
        tmp_dst = dst.with_suffix(".tmp")
        try:
            shutil.copy2(src, tmp_dst)
            tmp_dst.replace(dst)
            print(f"[+] 成功{'覆盖' if is_update else '创建'}配置文件: {dst.resolve()}")
        finally:
            # 如果 replace 失败（例如目标文件被锁定），清理临时文件
            if tmp_dst.exists():
                tmp_dst.unlink()
    except PermissionError:
        print(f"[-] 错误: 没有权限在当前目录写入文件 {dst}")
        exit(1)
    except Exception as e:
        print(f"[-] 创建配置文件失败: {e}")
        exit(1)


def handle_server(args):
    """处理 server 命令：启动 uvicorn 服务器"""
    # 如果指定了配置文件，可以在这里进行额外的逻辑（目前 LessRAG 内部可能通过环境变量或默认路径读取）
    if args.config:
        os.environ["LESSRAG_CONFIG"] = args.config

    print(f"正在启动 LessRAG 服务器于 {args.host}:{args.port}...")
    uvicorn.run("server.main:app", host=args.host, port=args.port)


def main():
    parser = argparse.ArgumentParser(prog="lessrag", description="LessRAG 命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # config 命令
    subparsers.add_parser("config", help="创建默认配置文件")

    # server 命令
    server_parser = subparsers.add_parser("server", help="启动服务器", add_help=False)
    server_parser.add_argument(
        "-p", "--port", type=int, default=15000, help="端口号 (默认: 15000)"
    )
    server_parser.add_argument(
        "-h", "--host", type=str, default="0.0.0.0", help="绑定地址 (默认: 0.0.0.0)"
    )
    server_parser.add_argument("-c", "--config", type=str, help="指定配置文件路径")
    server_parser.add_argument("--help", action="help", help="显示此帮助信息并退出")

    args = parser.parse_args()

    if args.command == "config":
        handle_config(args)
    elif args.command == "server":
        handle_server(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
