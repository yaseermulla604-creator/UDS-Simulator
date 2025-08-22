from typing import Callable, Dict, List

class EventManager:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)

    def publish(self, event_type: str, data: any = None):
        # Check if there are subscribers for the event
        if event_type in self.subscribers and self.subscribers[event_type]:
            for callback in self.subscribers[event_type]:
                callback(data)
        else:
            print(f"No subscribers for event: {event_type}")

    def subscriber_count(self, event_type: str) -> int:
        return len(self.subscribers.get(event_type, []))
