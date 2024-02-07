from datetime import datetime
import re
import json


class LuckyIoc():
    date: datetime
    indicator: str

    def __init__(self, date: datetime, indicator: str) -> None:
        self.date: datetime = date
        self.indicator: str = indicator

    def __str__(self) -> str:
        return json.dumps(self.asdict())

    def is_ip_address(self):
        """
        Check if the given text is an IP address.
        """
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        return re.match(ip_pattern, self.indicator) is not None

    def asdict(self) -> dict:
        if self.is_ip_address():
            # print(f"{ioc.indicator} was an ip!")
            return {
                "@timestamp": self.date.isoformat(),
                "message": self.indicator,
                "threat": {
                    "indicator": {
                        "type": "ipv4-addr",
                        "ip": self.indicator
                    }
                },
                "event": {
                    "type": "indicator",
                    "category": "threat"
                }
            }
        else:
            # print(f"{self.indicator} was a url!")
            return {
                "@timestamp": self.date.isoformat(),
                "message": self.indicator,
                "threat": {
                    "indicator": {
                        "type": "url",
                        "url": {
                            "domain": self.indicator
                        }
                    }
                },
                "event": {
                    "type": "indicator",
                    "category": "threat"
                }
            }
