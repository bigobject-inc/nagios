from kafka import KafkaProducer, KafkaConsumer
import sys

NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

MONITOR_TOPIC="bo_watch"
CONSUMER_GROUP="bo_watch"

# python kafka_monitor.py ${HOST} ${PORT}
def main():
    # verify input
    args = sys.argv
    if len(args)<3:
        print("lack of argument")
        sys.exit(NAGIOS_CRITICAL)

    # setup input
    host = sys.argv[1]
    port = sys.argv[2]
    kafka_server = "{:s}:{:s}".format(host,port)
    topic = MONITOR_TOPIC
    consumer_group = CONSUMER_GROUP

    # setup producer, consumer
    producer = KafkaProducer(bootstrap_servers=kafka_server)
    consumer = KafkaConsumer(
        bootstrap_servers=kafka_server,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=consumer_group,
    )


    # send message via producer
    try:
        producer.send(topic, value="ACK".encode())
        producer.flush()
        producer.close()
    except Exception as e:
        print("Kafka send failed")
        sys.exit(NAGIOS_CRITICAL)


    # receive message
    try:
        consumer.subscribe([topic])
        data = consumer.poll(timeout_ms=3000,max_records=1)
        consumer.close()
    except Exception as e:
        print("Kafka read failed")
        sys.exit(NAGIOS_CRITICAL)

    # return result
    print("OK for read/write")
    sys.exit(NAGIOS_OK)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(NAGIOS_UNKNOWN)
