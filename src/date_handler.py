from datetime import datetime, timedelta
from dateutil import parser
from zoneinfo import ZoneInfo


class DateHandler:
    # 默认时区设置为北京时间
    DEFAULT_TZ = "Asia/Shanghai"

    @classmethod
    def now(cls) -> datetime:
        """
        获取当前时间，带有时区信息（默认为北京时间）
        :return: aware datetime
        """
        return datetime.now(ZoneInfo(cls.DEFAULT_TZ))

    @classmethod
    def get_recent_time(cls, days: int) -> datetime:
        """
        获取当前时间往前推若干天的时间点（带时区）
        :param days: 向前推的天数
        :return: aware datetime
        """
        return cls.now() - timedelta(days=days)

    @classmethod
    def parse(cls, date_str: str) -> datetime:
        """
        将时间字符串解析为 datetime 对象（自动识别是否包含时区）
        如果没有时区信息，统一添加默认时区
        :param date_str: 字符串形式的时间（如 ISO 8601）
        :return: aware datetime
        """
        dt = parser.isoparse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(cls.DEFAULT_TZ))
        return dt

    @classmethod
    def is_within_days(cls, date_str: str, days: int) -> bool:
        """
        判断一个时间字符串是否在最近 X 天之内
        :param date_str: 提交或更新时间的字符串
        :param days: 向前推多少天
        :return: 如果在这段时间范围内，返回 True；否则 False
        """
        target_time = cls.parse(date_str)
        recent_time = cls.get_recent_time(days)
        return target_time > recent_time

    @classmethod
    def is_after_recent_time(cls, target_time: datetime, days: int) -> bool:
        """
        判断一个 datetime 是否晚于当前时间减去 days 天的时间点
        :param target_time: 目标时间（可以是 naive 或 aware datetime）
        :param days: 天数范围
        :return: 如果在范围内（晚于 recent_time），返回 True
        """
        recent_time = cls.get_recent_time(days)
        target_time = cls.to_aware(target_time)
        return target_time > recent_time

    @classmethod
    def is_after_recent_time_str(cls, date_str: str, days: int) -> bool:
        """
        同 is_after_recent_time，但接收字符串类型的时间
        :param date_str: 时间字符串（支持 ISO 格式）
        :param days: 向前推的天数
        :return: 是否在范围内
        """
        target_time = cls.parse(date_str)
        return cls.is_after_recent_time(target_time, days)

    @classmethod
    def to_naive(cls, dt: datetime) -> datetime:
        """
        将带时区的 datetime 对象转换为 naive（无时区）对象
        :param dt: datetime 对象
        :return: naive datetime
        """
        return dt.replace(tzinfo=None)

    @classmethod
    def to_aware(cls, dt: datetime) -> datetime:
        """
        将 naive（无时区）的 datetime 对象转换为带默认时区的 aware 对象
        :param dt: datetime 对象
        :return: aware datetime
        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=ZoneInfo(cls.DEFAULT_TZ))
        return dt
