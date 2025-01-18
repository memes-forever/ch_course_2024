from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from clickhouse_driver import Client

KAFKA_SERVERS = '192.168.1.232:9093'

def create_topic(topic_name):
    a = AdminClient({'bootstrap.servers': KAFKA_SERVERS})
    fs = a.create_topics([NewTopic(topic_name, num_partitions=3, replication_factor=1)])

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))


def produce_messages(messages, topic_name):
    p = Producer({'bootstrap.servers': KAFKA_SERVERS})

    def delivery_report(err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    for data in messages:
        p.poll(0)
        p.produce(topic_name, data.encode('utf-8'), callback=delivery_report)

    p.flush()


if __name__ == "__main__":
    topic_name = "test.click"
    messages = [
        '{"key_1": 1, "key_2": 2}',
        '{"key_1": 3, "key_2": 4}',
        '{"key_1": 5, "key_2": 6}',
    ]

    create_topic(topic_name)
    produce_messages(messages, topic_name)

    # To consume latest messages and auto-commit offsets
    c = Consumer({
        'bootstrap.servers': KAFKA_SERVERS,
        'group.id': 'mygroup',
        'auto.offset.reset': 'earliest',
    })

    c.subscribe([topic_name])

    client = Client(
        host='localhost',
        user='default',
    )

    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        m = msg.value().decode('utf-8')
        print(f'Received message: {m}')

        # execute query
        client.execute(f"insert into kafka_test_2 (message) values ('{m}')")

    c.close()
