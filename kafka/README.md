### Start Kafka and Zookeeper
```
docker-compose up
```

### Create Topic
```
kafka-topics.sh --create \
--bootstrap-server 127.0.0.1:9092 \
--replication-factor 1 \
--partitions 1 \
--topic kafka-new-topic
```

### Start Producer
```
kafka-console-producer.sh \
--bootstrap-server localhost:9092 \
--topic kafka-new-topic
```

### Start Consumer
```
kafka-console-consumer.sh \
--bootstrap-server localhost:9092 \
--topic kafka-new-topic \
--from-beginning
```

#### Ref
[bitnami-kafka](https://hub.docker.com/r/bitnami/kafka)


### Starting Kafka with Kraft mode

Generate a random UUID using kafka-storage for the cluster
```
/opt/bitnami/kafka/bin/kafka-storage.sh random-uuid
```

Format storage directory
```
/opt/bitnami/kafka/bin/kafka-storage.sh format -t V-WzUhSASGO-TS48iP4nRw -c ~/opt/bitnami/kafka/config/kraft/server.properties
```

Start broker
```
/opt/bitnami/kafka/bin/kafka-server-start.sh ~/opt/bitnami/kafka/config/kraft/server.properties
```
