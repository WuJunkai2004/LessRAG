import argparse
import os
from cmath import e
from pathlib import Path
from typing import Any, Dict

# 处理 toml 解析器的版本兼容性
try:
    import tomllib  # Python 3.11+ 内置支持, # type: ignore
except ImportError:
    import tomli as tomllib  # Python 3.10 需要安装 tomli


from server.utils.logger import log


class Config:
    _instance = None
    config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        parser = argparse.ArgumentParser(
            prog="lessrag", description="LessRAG 命令行工具"
        )
        subparsers = parser.add_subparsers(dest="command", help="可用命令")

        # config 命令
        subparsers.add_parser("config", help="创建默认配置文件")

        # server 命令
        server_parser = subparsers.add_parser(
            "server", help="启动服务器", add_help=False
        )
        server_parser.add_argument(
            "-p", "--port", type=int, help="端口号 (默认: 15000 或配置文件指定)"
        )
        server_parser.add_argument(
            "-h", "--host", type=str, help="绑定地址 (默认: 0.0.0.0 或配置文件指定)"
        )
        server_parser.add_argument("-c", "--config", type=str, help="指定配置文件路径")
        server_parser.add_argument("--help", action="help", help="显示此帮助信息并退出")

        self.args = parser.parse_args()
        self.help = parser.print_help
        self.config_path = getattr(self.args, "config", None) or os.environ.get(
            "LESSRAG_CONFIG", "config.toml"
        )
        self.config = self.load(self.config_path)

    def load(self, path):
        """从文件加载配置，允许在程序运行期间更新配置路径"""
        config_path = Path(path).resolve()

        if not config_path.exists():
            log("config").warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return {}

        try:
            with config_path.open("rb") as f:
                return tomllib.load(f)
        except Exception:
            log("config").error(f"加载配置文件失败: {e}")
            return {}

    @property
    def command(self) -> str:
        return self.args.command

    def get(self, key: str, default: Any = None) -> Any:
        """支持点号分隔的层级访问，如 config.get('llm.model')"""
        keys = key.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def _required(self, keys: tuple) -> bool:
        """检查一组配置项是否都存在"""
        return all(self.get(k) is not None for k in keys)

    @property
    def all_required(self) -> bool:
        """检查所有必需的配置项是否都存在"""
        required_keys = (
            # model configuration
            "model.model",
            "model.api_url",
            # embedding configuration
            "embedding.model",
            "embedding.api_url",
        )
        return self._required(required_keys)


# 单例导出
config = Config()
