import firebase_admin
from firebase_admin import credentials, messaging


class SendNotification:
    def __init__(self, topic):
        self.topic = topic

    def get_recent_value(self, items):
        items.sort(key = lambda x:x['created_at'])
        return items[-1]

    def message(self, items, recent_value):
        if len(items) == 1:
            notification_message = f'{recent_value} is available to read'
        else:
            notification_message = f'{recent_value[:80]}... and {len(items)-1} more are available to read!'
        return notification_message
    
    def notification_push(self,title, body):
        cred = credentials.Certificate(
            f"firebase2/gov-glance-firebase-adminsdk-3osxk-6fc6be7677.json")
        firebase_admin.initialize_app(cred)

        topic = f'{self.topic}News'
        # topic = 'test'

        message = messaging.Message(
            notification=messaging.Notification(
                title=title, body=body),
            topic=topic,
        )
        print(message)
        # messaging.send(message)