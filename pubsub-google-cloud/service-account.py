from google.oauth2 import service_account
from google.cloud import pubsub_v1

cred = service_account.Credentials.from_service_account_file(
    filename="esp8266-private-key.json",
    scopes=["https://www.googleapis.com/auth/pubsub"],
)

subscriber = pubsub_v1.SubscriberClient(credentials=cred)
subscription_path = "projects/pubsub-422710/subscriptions/environmental-sensor-sub"

print(f"Listening on {subscription_path}")

with subscriber:
    # Pull -> response
    response = subscriber.pull(
        request={
            "subscription": subscription_path,
            "max_messages": 1277,
        }
    )

    if len(response.received_messages) > 0:
        ack_ids = []
        for message in response.received_messages:
            if message.message.attributes:
                for attr_key, attr_value in message.message.attributes.items():
                    print(f"{attr_key}: {attr_value}")

            print(f"Data: {message.message.data.decode('utf-8')}")
            ack_ids.append(message.ack_id)

        # send ACK -> Done
        subscriber.acknowledge(
            request={
                "subscription": subscription_path,
                "ack_ids": ack_ids,
            }
        )

        print(
            f"Received and ACK {len(response.received_messages)} messages from {subscription_path}"
        )
    else:
        pass
