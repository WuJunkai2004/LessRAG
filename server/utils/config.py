import os
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
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.reload(False)
        return cls._instance

    def reload(self, log_on=True):
        """重新从文件加载配置，允许在程序运行期间更新配置路径"""
        # 优先级：环境变量 LESSRAG_CONFIG > 当前目录 config.toml
        config_path_str = os.environ.get("LESSRAG_CONFIG", "config.toml")
        config_path = Path(config_path_str).resolve()

        if not config_path.exists():
            if "LESSRAG_CONFIG" in os.environ:
                if log_on:
                    log("config").error(f"指定的配置文件未找到: {config_path}")
            else:
                if log_on:
                    log("config").debug(f"默认配置文件未找到: {config_path}")
            self._config = {}
            return self

        try:
            with open(config_path, "rb") as f:
                self._config = tomllib.load(f)
            if log_on:
                log("config").info(f"成功加载配置文件: {config_path}")
        except Exception as e:
            if log_on:
                log("config").error(f"解析配置文件失败 {config_path}: {e}")
            self._config = {}

        return self

    def get(self, key: str, default: Any = None) -> Any:
        """支持点号分隔的层级访问，如 config.get('llm.model')"""
        keys = key.split(".")
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def all(self) -> Dict[str, Any]:
        return self._config


# 单例导出
config = Config()
