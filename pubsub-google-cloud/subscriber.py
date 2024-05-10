import os
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from google.api_core import retry

# get the credentials path
credentials_path = "houseplant-privatekey.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

timeout = 5

subscriber = pubsub_v1.SubscriberClient()
subscription_path = "projects/pubsub-422710/subscriptions/environmental-sensor-sub"


# def callback(message):
#     print(f"Receive message {message}")
#     print(f"Data: {message.data.decode('utf-8')}")
#     if message.attributes:
#         for attr_key, attr_value in message.attributes.items():
#             print(f"{attr_key}: {attr_value}")

#     # delete from pubsub server (google cloud)
#     message.ack()


# streaming_pull_future = subscriber.subscribe(
#     subscription=subscription_path, callback=callback
# )
print(f"Listening for messages on {subscription_path}")

# StreamingPull
# with subscriber:
#     try:
#         streaming_pull_future.result()
#     except TimeoutError:
#         streaming_pull_future.cancel()
#         streaming_pull_future.result()


# Unary pull
with subscriber:
    response = subscriber.pull(
        request={"subscription": subscription_path, "max_messages": 1277},
        retry=retry.Retry(deadline=300),
    )

    if len(response.received_messages) > 0:
        ack_ids = []
        for message in response.received_messages:
            print(message.message.attributes)
            print(message.message.data.decode("utf-8"))
            ack_ids.append(message.ack_id)

        subscriber.acknowledge(
            request={"subscription": subscription_path, "ack_ids": ack_ids}
        )

        print(
            f"Received and ack {len(response.received_messages)} messages from {subscription_path}"
        )
    else:
        pass
