import shutil
from pathlib import Path

import uvicorn

from server.utils.config import config
from server.utils.logger import log


def handle_config():
    """处理 config 命令：从包目录复制 config.example.toml 到当前工作目录下的 config.toml"""
    # 源文件：现在与本文件在同一目录下
    src = Path(__file__).resolve().parent / "config.example.toml"

    # 目标文件：用户当前所在的目录
    dst = Path.cwd() / "config.toml"

    if not src.exists():
        log("config").error(f"找不到模板文件 {src}")
        exit(1)

    if dst.exists():
        try:
            choice = input(f"当前目录下 {dst.name} 已存在，是否覆盖？(y/N): ").lower()
            if choice != "y":
                log("config").info("用户选择不覆盖现有配置文件")
                return
        except KeyboardInterrupt:
            log("config").info("用户取消了操作")
            return

    try:
        # 记录是否为覆盖操作
        is_update = dst.exists()

        # 使用临时文件进行原子性操作
        tmp_dst = dst.with_suffix(".tmp")
        try:
            shutil.copy2(src, tmp_dst)
            tmp_dst.replace(dst)
            log("config").info(
                f"成功{'覆盖' if is_update else '创建'}配置文件: {dst.resolve()}"
            )
        finally:
            # 如果 replace 失败（例如目标文件被锁定），清理临时文件
            if tmp_dst.exists():
                tmp_dst.unlink()
    except PermissionError:
        log("config").error(f"没有权限在当前目录写入文件 {dst}")
        exit(1)
    except Exception as e:
        log("config").error(f"创建配置文件失败: {e}")
        exit(1)


def handle_server():
    # 优先级：命令行参数 > 配置文件 > 硬编码默认值
    host = config.args.host or config.get("host") or "0.0.0.0"
    port = config.args.port or config.get("port") or 15000

    uvicorn.run("server.main:app", host=host, port=port, reload=True)


def main():
    if config.command == "config":
        handle_config()
    elif config.command == "server":
        handle_server()
    else:
        config.help()


if __name__ == "__main__":
    main()
