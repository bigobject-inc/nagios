from kafka import KafkaConsumer, TopicPartition
from datetime import datetime as DateTime
import sys
import fcntl
import json

NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

METRIC_LOGDIR='/opt/metric/kafka/'
KAFKA_CONSUMER="bo_watch"

# python ...py ${HOST} ${PORT}
def main():
    # verify input
    args = sys.argv
    if len(args)<6:
        print("lack of argument")
        sys.exit(NAGIOS_CRITICAL)

    # setup input
    host_name = sys.argv[1]
    kafka_host = sys.argv[2]
    kafka_port = sys.argv[3]
    kafka_topic = sys.argv[4]
    expire_minute = int(sys.argv[5])
    log_file = METRIC_LOGDIR + "{!s}-{!s}.json".format(host_name,kafka_topic)
    
    # setup Kafka consumer connection
    kafka_server = "{:s}:{:s}".format(kafka_host,kafka_port)
    try:
        kf_consumer = KafkaConsumer(
            group_id=KAFKA_CONSUMER,
            bootstrap_servers=kafka_server,
            auto_offset_reset='latest'
        )
    except Exception as e:
        print("Kafka connection error: {!s}".format(e))
        sys.exit(NAGIOS_WARNING)

    # get offset of all partitons
    partnum_offset = {}
    for part_num in kf_consumer.partitions_for_topic(kafka_topic): 
        info = kf_consumer.end_offsets( [TopicPartition(kafka_topic, part_num)] )
        offset = next( iter(info.values()) )
        partnum_offset = { part_num: offset }
    # :iterate over each partition
    
    # get record in storage
    try:
        record_fd = open(log_file, 'w+', encoding='utf-8')
        fcntl.flock(record_fd, fcntl.LOCK_EX )
    except Exception as e:
        print('Error when fetch record file at {!s}: {!s}'.format(log_file, e))
        sys.exit(NAGIOS_WARNING)
    
    record_txt = record_fd.read()
    record = json.loads(record_txt) if len(record_txt) else {}

    errors = []
    for partnum, offset in partnum_offset.items():
        upsert_row = None
        
        # query record in DB
        row = record.get(partnum,None)
        
        if row is None:
            # no history found, just write new record
            upsert_row = True
            
        elif row is not None and row['offset'] != offset:
            # history found but having different offset, just update DB
            upsert_row = True
        
        elif row is not None and row['offset'] == offset:
            # history found and having the same offset
            upsert_row = False # don't update table to hold the old data
                
            # verify expire or not
            now_ts = DateTime.utcnow().timestamp()
            diff_seconds = int(now_ts) - int(row['last_ts'])
            diff_minute = int(diff_seconds/60)
            if diff_seconds < 0 or diff_seconds > expire_minute*60:
                # append error if expired
                errors.append(
                    "topic:{!s} partiton:{!s} expired by {!s} minutes, alert at {!s} minutes "\
                    .format( kafka_topic, partnum, diff_minute, expire_minute )
                )
            
        if upsert_row is None:
            errors.append("upsert_row logic error on topic/partition: {!s}/{!s} ".format(kafka_topic, partition))
        elif upsert_row is True:
            # update new status into log_file
            record[partnum] = {
                "topic": kafka_topic,
                "partition": part_num,
                "offset": offset,
                "last_ts": DateTime.utcnow().timestamp()
            }
    # :iterate over each topic/partiton
    
    # write results into log
    record_fd.seek(0)
    record_fd.truncate()
        # clean all existent content
    record_fd.write(json.dumps(record))
        # write
    fcntl.flock(record_fd, fcntl.LOCK_UN)
    record_fd.close()
        # close file
    
    if errors :
        print(errors)
        sys.exit(NAGIOS_WARNING)
    
    print('OK on topic:{!s} (alert threshold at {!s} mintute delay) '.format(kafka_topic, expire_minute))
    sys.exit(NAGIOS_OK)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(NAGIOS_UNKNOWN)
