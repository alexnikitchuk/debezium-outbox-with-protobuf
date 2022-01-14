Start all services
```bash
docker-compose -f docker-compose.yaml up
```

Open terminal and connect to app database container
```bash
docker exec -it debezium-outbox-with-protobuf_app-db_1 psql -h localhost -p 5432 -U postgres postgres
```

Create outbox table in app database using query
```sql
CREATE TABLE public.outboxevent
(
    id uuid PRIMARY KEY,
    aggregatetype VARCHAR(75),
    aggregateid VARCHAR(50) NOT NULL,
    payload BYTEA NOT NULL
);
```

Open another terminal and deploy source and sink connectors to Kafka Connect
```bash
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @./connectors/outbox-connector.json
```
```bash
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @./connectors/target-db-sink-connector.json
```

Connect to target database container
```bash
docker exec -it debezium-outbox-with-protobuf_target-db_1 psql -h localhost -p 5432 -U postgres postgres
```

Open browser and go to URL to add new customer (can be done multiple times)
```
http://localhost:5000/add_new_customer
```

Switch back to target database terminal and check produced records appear in destination table
```sql
SELECT * FROM public.customers_topic;
```
