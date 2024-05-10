import os
from google.cloud import pubsub_v1

# get the credentials path
credentials_path = "houseplant-privatekey.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# create a publisher itself
publisher = pubsub_v1.PublisherClient()
topic_path = "projects/pubsub-422710/topics/environmental-sensor"


data = "Hello"
data = data.encode("utf-8")

json_data = {
    'sensor_name': 'DHT11',
    'temp': '23.0',
    'humidity': '65.5'
}

# publish message
future = publisher.publish(topic=topic_path, data=data, **json_data)
print(f"Publish message id {future.result()}")
