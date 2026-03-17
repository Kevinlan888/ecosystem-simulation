"""
事件总线模块

实现观察者模式：发布者发布事件，订阅者通过回调函数接收通知。
预设事件名：tick_end, organism_born, organism_died, factor_added, factor_removed
"""

from __future__ import annotations
from collections import defaultdict
from typing import Callable


class EventBus:
    """
    事件总线（观察者模式）。

    支持多个订阅者监听同一事件，也支持订阅所有事件（通配符 '*'）。
    """

    def __init__(self):
        """初始化空的订阅字典。"""
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_name: str, listener: Callable) -> None:
        """
        订阅指定事件。

        Args:
            event_name: 事件名称，或 '*' 表示订阅所有事件
            listener: 可调用对象，签名为 (event_name: str, data: dict) -> None
        """
        self._subscribers[event_name].append(listener)

    def publish(self, event_name: str, data: dict) -> None:
        """
        发布事件，通知所有相关订阅者。

        Args:
            event_name: 事件名称
            data: 事件附带的数据字典
        """
        # 通知具体事件订阅者
        for listener in list(self._subscribers.get(event_name, [])):
            listener(event_name, data)
        # 通知通配符订阅者
        if event_name != "*":
            for listener in list(self._subscribers.get("*", [])):
                listener(event_name, data)

    def __repr__(self) -> str:
        return f"EventBus(subscriptions={dict(self._subscribers)})"
