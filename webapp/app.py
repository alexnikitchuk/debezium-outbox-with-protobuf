import os
from uuid import uuid4

import psycopg2
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from faker import Faker
from flask import Flask

from customer_pb2 import Customer

app = Flask(__name__)

schema_registry_url = os.environ['SCHEMA_REGISTRY_URL']
kafka_topic = os.environ['KAFKA_TOPIC']

postgres_user = os.environ['POSTGRES_USER']
postgres_password = os.environ['POSTGRES_PASSWORD']
postgres_hots = os.environ['POSTGRES_HOST']
postgres_port = os.environ['POSTGRES_PORT']
postgres_database = os.environ['POSTGRES_DATABASE']


@app.route('/add_new_customer')
def add_new_customer():
    schema_registry_conf = {'url': schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    protobuf_serializer = ProtobufSerializer(Customer, schema_registry_client, {'use.deprecated.format': True})

    # generate random Customer
    fake = Faker()
    customer = Customer(first_name=fake.first_name(), last_name=fake.last_name(), email=fake.email())

    # inventory.customer table
    customer_insert_query = """INSERT INTO inventory.customers
    (first_name, last_name, email)
    VALUES (%s, %s, %s)"""
    customer_insert_values = (customer.first_name, customer.last_name, customer.email)

    record_id = str(uuid4())
    aggregate_id = str(uuid4())
    ctx = SerializationContext(kafka_topic, MessageField.VALUE)
    payload = protobuf_serializer(customer, ctx)
    outbox_insert_values = (record_id, kafka_topic, aggregate_id, payload)

    # public.outboxevent table
    outbox_insert_query = """INSERT INTO public.outboxevent
    (id, aggregatetype, aggregateid, payload)
    VALUES (%s, %s, %s, %s)"""

    # cleanup outbox table
    cleanup_outbox_table = "DELETE FROM public.outboxevent"

    with psycopg2.connect(user=postgres_user,
                          password=postgres_password,
                          host=postgres_hots,
                          port=postgres_port,
                          database=postgres_database) as connection:
        with connection.cursor() as cursor:
            cursor.execute(customer_insert_query, customer_insert_values)
            cursor.execute(outbox_insert_query, outbox_insert_values)
            cursor.execute(cleanup_outbox_table)
            connection.commit()

    return f'New customer: <br> {customer}'
