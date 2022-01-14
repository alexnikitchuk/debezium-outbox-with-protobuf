FROM confluentinc/cp-kafka-connect:6.1.4


# isntall connectors
RUN confluent-hub install --no-prompt debezium/debezium-connector-postgresql:1.7.1 \
    && confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:10.2.6
