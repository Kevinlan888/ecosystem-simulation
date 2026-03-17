"""
抽象接口定义模块

定义生态系统中所有可扩展接口的抽象基类：
- EnvironmentalFactor: 环境因素接口
- ReproductionStrategy: 繁殖策略接口
- EventListener: 事件监听接口
"""

from abc import ABC, abstractmethod


class EnvironmentalFactor(ABC):
    """
    环境因素抽象接口。

    所有环境因素（温度、食物、水、光照、疾病等）都应继承此类，
    实现 apply() 和 update() 方法。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """环境因素名称，用于标识和查找。"""

    @abstractmethod
    def apply(self, organism, ecosystem) -> None:
        """
        对单个生物施加影响。

        Args:
            organism: 被影响的生物实例
            ecosystem: 当前生态系统实例
        """

    @abstractmethod
    def update(self, ecosystem) -> None:
        """
        每个时间步更新因素自身状态（如季节变化、食物再生等）。

        Args:
            ecosystem: 当前生态系统实例
        """


class ReproductionStrategy(ABC):
    """
    繁殖策略抽象接口。

    有性繁殖和无性繁殖都继承此类，实现 can_reproduce() 和 reproduce() 方法。
    """

    @abstractmethod
    def can_reproduce(self, organism) -> bool:
        """
        判断给定生物是否满足繁殖条件。

        Args:
            organism: 待判断的生物实例

        Returns:
            bool: 是否可以繁殖
        """

    @abstractmethod
    def reproduce(self, organism, ecosystem) -> list:
        """
        执行繁殖逻辑，返回新生生物列表。

        Args:
            organism: 执行繁殖的生物实例
            ecosystem: 当前生态系统实例

        Returns:
            list: 新生生物实例列表
        """


class EventListener(ABC):
    """
    事件监听抽象接口。

    实现此接口以订阅和响应生态系统事件。
    """

    @abstractmethod
    def on_event(self, event_name: str, data: dict) -> None:
        """
        处理接收到的事件。

        Args:
            event_name: 事件名称（如 'tick_end', 'organism_born' 等）
            data: 事件附带的数据字典
        """
