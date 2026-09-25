from app.db.course_data.helpers import make_lesson, make_question

# Course 3: Data Engineering & Distributed Systems
# Slug: data-engineering-distributed-systems

MODULE_1_LESSONS = [
    make_lesson(
        title="Fundamentals of Data Engineering",
        slug="fundamentals-of-data-engineering",
        order_index=1,
        duration_minutes=45,
        description="Introduction to data engineering lifecycles, data maturity models, storage hierarchies, and the distinction between data engineering, science, and analytics.",
        objectives=[
            "Understand the Data Engineering Lifecycle (generation, storage, ingestion, transformation, serving)",
            "Evaluate data architectures against enterprise business requirements",
            "Differentiate operational (OLTP) vs analytical (OLAP) systems"
        ],
        content_body="""Data Engineering is the discipline of designing, building, and operating data platforms and pipelines to ingest, store, process, and serve reliable data for analytics and machine learning.

### The Data Engineering Lifecycle
1. **Generation**: Source systems creating data (databases, IoT sensors, APIs, CDC logs).
2. **Storage**: Choosing the right storage layer (Object Storage, Relational DBs, Data Lakes).
3. **Ingestion**: Moving data from sources into storage (batch vs streaming).
4. **Transformation**: Cleaning, conforming, enriching, and aggregating data into business models.
5. **Serving**: Delivering data to consumers (BI dashboards, ML models, reverse ETL).

### Undercurrents of Data Engineering
Security, Data Management, DataOps, Data Architecture, Orchestration, and Software Engineering.""",
        key_concepts=[
            "The 5 stages of the Data Engineering Lifecycle",
            "OLTP (Row-oriented, high write concurrency) vs OLAP (Columnar, high read throughput)",
            "Data maturity curves in enterprise organizations",
            "The 6 core lifecycle undercurrents"
        ],
        practical_example="""```python
# Conceptual Data Engineering Pipeline Stage Definition
class PipelineStage:
    def __init__(self, name: str, stage_type: str):
        self.name = name
        self.stage_type = stage_type

lifecycle = [
    PipelineStage("Postgres CDC Source", "Generation"),
    PipelineStage("Kafka Event Stream", "Ingestion"),
    PipelineStage("S3 Data Lake (Parquet)", "Storage"),
    PipelineStage("dbt / Spark Transformations", "Transformation"),
    PipelineStage("Snowflake Data Warehouse", "Serving")
]
```""",
        completion_req="Review the stages and undercurrents of the Data Engineering Lifecycle.",
        is_free_preview=True
    ),
    make_lesson(
        title="Data Modeling for Analytics: Star and Snowflake Schemas",
        slug="data-modeling-for-analytics-star-snowflake-schemas",
        order_index=2,
        duration_minutes=55,
        description="Dimensional modeling concepts: Kimball methodology, Fact tables, Dimension tables, Star schemas, Snowflake schemas, and Slowly Changing Dimensions (SCD).",
        objectives=[
            "Design Star and Snowflake dimensional models for analytical workloads",
            "Distinguish Fact tables (additive, semi-additive) from Dimension tables",
            "Implement Slowly Changing Dimension (SCD Types 0, 1, 2, 3) strategies"
        ],
        content_body="""Dimensional modeling (pioneered by Ralph Kimball) structures data for query simplicity and high analytical performance.

### Core Elements
- **Fact Tables**: Contain numerical measurements, metrics, and foreign keys pointing to dimension tables (e.g., `fact_course_enrollments`, `fact_quiz_attempts`).
  - *Additive*: Can be summed across all dimensions (e.g., revenue, duration).
  - *Semi-Additive*: Can be summed across some dimensions but not others (e.g., account balance across time).
- **Dimension Tables**: Contain descriptive context, attributes, and hierarchies (e.g., `dim_students`, `dim_courses`, `dim_date`).

### Star Schema vs Snowflake Schema
- **Star Schema**: Dimensions are completely denormalized (flat). Simpler queries, faster analytical joins.
- **Snowflake Schema**: Dimensions are normalized into multiple related tables. Reduces storage redundancy but requires more multi-table joins.""",
        key_concepts=[
            "Fact vs Dimension table grain",
            "Star Schema denormalization vs Snowflake Schema normalization",
            "Surrogate keys vs Natural/Business keys",
            "SCD Type 1 (overwrite), SCD Type 2 (track history with valid_from/valid_to dates)"
        ],
        practical_example="""```sql
-- Dimensional Star Schema SQL DDL Example
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    day_name VARCHAR(15) NOT NULL
);

CREATE TABLE dim_student (
    student_key INT PRIMARY KEY,
    student_id UUID NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    is_active BOOLEAN,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP
);

CREATE TABLE fact_lesson_completions (
    completion_id BIGINT PRIMARY KEY,
    student_key INT REFERENCES dim_student(student_key),
    date_key INT REFERENCES dim_date(date_key),
    course_id UUID NOT NULL,
    lesson_id UUID NOT NULL,
    time_spent_seconds INT NOT NULL,
    score_percentage DECIMAL(5, 2)
);
```""",
        completion_req="Design a dimensional star schema with fact and dimension tables."
    ),
    make_lesson(
        title="Relational vs Non-Relational Databases for Analytics",
        slug="relational-vs-non-relational-databases-analytics",
        order_index=3,
        duration_minutes=50,
        description="Comparing database paradigms: Row-oriented RDBMS, Columnar Data Warehouses, Document stores, Key-Value stores, and Graph databases.",
        objectives=[
            "Compare Row-Oriented (PostgreSQL) vs Columnar (ClickHouse, Redshift) storage architectures",
            "Evaluate document stores (MongoDB) for semi-structured analytics",
            "Choose optimal storage engines based on read/write patterns and query complexity"
        ],
        content_body="""Storage format fundamentally dictates database I/O efficiency for different workload types.

### Row-Oriented vs Columnar Storage
- **Row-Oriented (OLTP - PostgreSQL, MySQL)**: Stores entire rows contiguously on disk. Ideal for fetching or updating single records by primary key (`SELECT * FROM users WHERE id = 123`). Inefficient for analytical aggregates because all columns must be read from disk.
- **Columnar (OLAP - ClickHouse, DuckDB, Snowflake, BigQuery)**: Stores each column contiguously. Only the requested columns are read from disk, achieving 10-100x query speedups and exceptional compression ratios (snappy, zstd, dictionary encoding).""",
        key_concepts=[
            "Row-oriented disk layout vs Columnar disk layout",
            "Vectorized query execution and SIMD processing",
            "Columnar compression algorithms (Run-Length, Dictionary, Delta)",
            "Semi-structured JSON querying (PostgreSQL JSONB vs MongoDB BSON)"
        ],
        practical_example="""```sql
-- Comparing Row-scan vs Column-scan performance in analytical queries
-- In Columnar DB: Only reads 'time_spent_seconds' column from disk, skipping other 20 columns
SELECT 
    course_id,
    AVG(time_spent_seconds) AS avg_duration_sec,
    COUNT(*) AS total_completions
FROM fact_lesson_completions
GROUP BY course_id;
```""",
        completion_req="Analyze the architectural differences between Row and Columnar stores."
    ),
    make_lesson(
        title="ETL vs ELT Pipeline Architectures",
        slug="etl-vs-elt-pipeline-architectures",
        order_index=4,
        duration_minutes=55,
        description="Evolution of data pipelines: traditional ETL (Extract, Transform, Load) vs modern ELT (Extract, Load, Transform) powered by cloud data warehouses and dbt.",
        objectives=[
            "Distinguish between ETL and ELT architectural philosophies",
            "Understand why cloud data warehouses enabled the shift to ELT",
            "Implement modern transformation layers using dbt (data build tool)"
        ],
        content_body="""Data integration patterns have transitioned from ETL to ELT due to the infinite compute and decoupled storage of modern cloud data warehouses.

### ETL (Extract, Transform, Load)
- Data is extracted from source, transformed on a separate dedicated compute server (e.g., Informatica, custom Python workers), and loaded into the destination warehouse.
- *Downside*: Compute bottlenecks on transformation servers, loss of raw source data.

### ELT (Extract, Load, Transform)
- Data is extracted and loaded directly into the destination warehouse/lakehouse in raw format. Transformations are executed *in-warehouse* using SQL and dbt.
- *Advantage*: Raw data preserved, massive warehouse parallel processing (MPP) utilized, modular transformation logic.""",
        key_concepts=[
            "Decoupled compute and storage",
            "The role of dbt (Data Build Tool) in the modern data stack",
            "Data lineage and transformation DAGs",
            "Idempotency and incremental models"
        ],
        practical_example="""```sql
-- Example dbt Model (models/marts/fct_student_engagement.sql)
{{ config(materialized='incremental', unique_key='engagement_id') }}

SELECT
    {{ dbt_utils.generate_surrogate_key(['student_id', 'date_day']) }} AS engagement_id,
    student_id,
    date_day,
    total_lessons_completed,
    total_quiz_score
FROM {{ ref('stg_student_activity') }}
{% if is_incremental() %}
  WHERE date_day > (SELECT MAX(date_day) FROM {{ this }})
{% endif %}
```""",
        completion_req="Understand ETL vs ELT tradeoffs and write a dbt transformation model."
    ),
    make_lesson(
        title="Batch Processing Principles and Tools",
        slug="batch-processing-principles-and-tools",
        order_index=5,
        duration_minutes=55,
        description="Batch data processing paradigms: chunking, partition strategies, MapReduce concepts, checkpointing, and backfilling.",
        objectives=[
            "Design scalable batch processing jobs handling large volumes of historical data",
            "Implement partition pruning and batch checkpointing mechanisms",
            "Execute automated backfills and handle schema evolution"
        ],
        content_body="""Batch processing processes high volumes of static, bounded data collected over a period of time (e.g., daily, hourly).

### Core Batch Principles
- **Bounded Datasets**: Processing begins when all data for a time window is available.
- **Partitioning**: Slicing datasets by date (`year=2026/month=09/day=23/`) allows processing engines to skip irrelevant files (Partition Pruning).
- **Idempotency**: Running a batch job multiple times on the same input partition must always yield the exact same result without duplicate rows.""",
        key_concepts=[
            "Bounded vs unbounded datasets",
            "Partition pruning and directory layout conventions",
            "Checkpointing, retries, and dead letter queues",
            "Backfilling strategies for historical data fixes"
        ],
        practical_example="""```python
# PySpark Batch Partition Processing Example
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("DailyBatchAggregator").getOrCreate()

# Read only specific date partition
raw_df = spark.read.parquet("s3://enterprise-data-lake/events/year=2026/month=09/day=23/")

aggregated_df = raw_df.groupBy("course_id") \\
    .agg({"student_id": "count", "time_spent": "sum"}) \\
    .withColumnRenamed("count(student_id)", "daily_active_students")

# Write idempotent output partition
aggregated_df.write.mode("overwrite").parquet("s3://enterprise-data-lake/analytics/daily_course_stats/date=2026-09-23/")
```""",
        completion_req="Implement an idempotent batch processing pipeline."
    ),
    make_lesson(
        title="Stream Processing Fundamentals",
        slug="stream-processing-fundamentals",
        order_index=6,
        duration_minutes=60,
        description="Real-time data streaming: unbounded datasets, event time vs processing time, windowing (tumbling, sliding, session), and watermarking.",
        objectives=[
            "Differentiate Event Time, Ingestion Time, and Processing Time",
            "Apply streaming window functions: Tumbling, Sliding, and Session windows",
            "Manage out-of-order data and late arrivals with Watermarks"
        ],
        content_body="""Stream processing handles continuous, unbounded streams of data in near real-time with millisecond-to-second latencies.

### Time Semantics
- **Event Time**: The timestamp when the event actually occurred on the client device.
- **Processing Time**: The timestamp when the stream processing engine processes the event.
- **Watermarks**: A mechanism in stream engines (Flink, Spark Streaming) that tracks progress in event time and determines when to close a time window for late-arriving events.

### Windowing Strategies
- **Tumbling Window**: Fixed, non-overlapping time intervals (e.g., every 5 minutes).
- **Sliding Window**: Fixed-length, overlapping intervals (e.g., 5-minute window sliding every 1 minute).
- **Session Window**: Dynamic gaps based on periods of inactivity.""",
        key_concepts=[
            "Unbounded continuous streaming vs micro-batching",
            "Event Time vs Ingestion Time vs Processing Time",
            "Watermarking thresholds for late data handling",
            "Tumbling, Sliding, and Session window aggregations"
        ],
        practical_example="""```python
# Spark Structured Streaming with Watermarking and Windowing
from pyspark.sql.functions import window, col

streaming_counts = event_stream \\
    .withWatermark("event_timestamp", "10 minutes") \\
    .groupBy(
        window(col("event_timestamp"), "5 minutes", "1 minute"),
        col("event_type")
    ) \\
    .count()
```""",
        completion_req="Understand streaming time semantics, windowing, and watermarks."
    ),
    make_lesson(
        title="Message Queues and Event Streaming with Kafka",
        slug="message-queues-and-event-streaming-kafka",
        order_index=7,
        duration_minutes=65,
        description="Apache Kafka internals: distributed commit log, topics, partitions, consumer groups, offsets, replication factor, and KRaft consensus.",
        objectives=[
            "Explain Apache Kafka's distributed append-only commit log architecture",
            "Design partition keys for even load distribution and strict message ordering",
            "Configure consumer groups, offset commits, and delivery guarantees (At-Least-Once, Exactly-Once)"
        ],
        content_body="""Apache Kafka is a distributed event streaming platform capable of handling trillions of events a day with high throughput and low latency.

### Kafka Core Architecture
- **Topics & Partitions**: A Topic is a logical stream of events. Topics are split into **Partitions** distributed across cluster brokers for horizontal scalability.
- **Append-Only Log**: Each partition is an immutable ordered sequence of records where new messages are continuously appended.
- **Consumer Groups**: Multiple consumers cooperatively read from a topic, where each partition is assigned to exactly one consumer in the group.""",
        key_concepts=[
            "Append-only commit log structure",
            "Partitions, message keys, and hashing for ordering guarantees",
            "Consumer Group rebalancing and offset management (`__consumer_offsets`)",
            "Delivery semantics: At-Most-Once, At-Least-Once, Exactly-Once (EOS with idempotent producers)"
        ],
        practical_example="""```python
from confluent_kafka import Producer, Consumer

# Kafka Producer with Idempotence Enabled
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'enable.idempotence': True,
    'acks': 'all'
})

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

producer.produce('lms.events.quiz_submitted', key='student-101', value='{"score": 95}', callback=delivery_report)
producer.flush()
```""",
        completion_req="Produce and consume messages using Kafka with delivery confirmation."
    ),
    make_lesson(
        title="Data Ingestion Patterns and Best Practices",
        slug="data-ingestion-patterns-and-best-practices",
        order_index=8,
        duration_minutes=50,
        description="Data ingestion strategies: Change Data Capture (CDC with Debezium), batch file ingestion, webhook receivers, API scraping, and schema registry validation.",
        objectives=[
            "Implement Change Data Capture (CDC) from operational databases using Debezium",
            "Validate event schemas with Apache Avro and Confluent Schema Registry",
            "Handle ingestion failure modes with Dead Letter Queues (DLQ)"
        ],
        content_body="""Data ingestion is the bridge connecting operational source systems to analytical storage.

### Ingestion Patterns
- **Change Data Capture (CDC)**: Reads database write-ahead logs (WAL) to capture every `INSERT`, `UPDATE`, and `DELETE` without polling the database or impacting transaction performance (e.g., Debezium + Kafka Connect).
- **Batch File Ingestion**: Scheduled pulls of CSV/JSON/Parquet files from SFTP, S3, or partner APIs.
- **Schema Enforcement**: Utilizing Apache Avro or Protobuf with a **Schema Registry** ensures producer applications cannot emit breaking schema changes into the pipeline.""",
        key_concepts=[
            "Write-Ahead Log (WAL) scraping for zero-impact CDC",
            "Schema Registry compatibility modes (Backward, Forward, Full)",
            "Handling schema drift and polymorphic event payloads",
            "Dead Letter Queues (DLQ) for unparseable poison pills"
        ],
        practical_example="""```json
// Example Debezium PostgreSQL CDC Event Envelope (Payload snippet)
{
  "before": { "id": 10, "status": "DRAFT" },
  "after": { "id": 10, "status": "PUBLISHED" },
  "source": { "version": "2.4.0", "db": "lms", "table": "courses", "lsn": 10849204 },
  "op": "u",
  "ts_ms": 1727078400000
}
```""",
        completion_req="Understand CDC log extraction and schema compatibility."
    ),
    make_lesson(
        title="Data Warehousing Concepts and Architecture",
        slug="data-warehousing-concepts-and-architecture",
        order_index=9,
        duration_minutes=55,
        description="Cloud Data Warehouses (Snowflake, BigQuery, Amazon Redshift): MPP query engines, micro-partitioning, virtual warehouses, and zero-copy cloning.",
        objectives=[
            "Analyze Massively Parallel Processing (MPP) query engine architectures",
            "Understand storage micro-partitioning and clustering keys in Snowflake/BigQuery",
            "Optimize query costs and performance via caching tiers"
        ],
        content_body="""Cloud Data Warehouses have revolutionized analytics by separating compute resources from centralized cloud storage, enabling instant elasticity.

### Modern Warehouse Architectures (e.g., Snowflake)
1. **Centralized Storage**: Immutable columnar micro-partitions stored in cloud object storage (S3/GCS/Azure Blob).
2. **Multi-Cluster Compute**: Independent compute virtual warehouses scale up/down dynamically and query the shared storage without contention.
3. **Cloud Services Layer**: Coordinates security, metadata management, transaction optimization, and query compilation.""",
        key_concepts=[
            "Massively Parallel Processing (MPP) compute clusters",
            "Micro-partitioning and automatic pruning",
            "Decoupled compute scaling without data re-sharding",
            "Zero-copy cloning and Time Travel data recovery"
        ],
        practical_example="""```sql
-- Snowflake Zero-Copy Cloning and Time Travel Query
-- Clone entire multi-terabyte production warehouse in seconds without duplicating storage
CREATE DATABASE lms_analytics_dev CLONE lms_analytics_prod;

-- Querying table state from 2 hours ago using Time Travel
SELECT * 
FROM lms_analytics_prod.public.fact_enrollments 
AT (OFFSET => -60*120);
```""",
        completion_req="Explore cloud data warehouse architectures and execute Time Travel queries."
    ),
    make_lesson(
        title="Data Quality, Validation, and Monitoring",
        slug="data-quality-validation-and-monitoring",
        order_index=10,
        duration_minutes=60,
        description="Data observability and quality frameworks: Great Expectations, Soda Core, dbt test assertions, anomaly detection, and data SLAs/SLIs.",
        objectives=[
            "Define the 5 pillars of Data Observability (Freshness, Volume, Schema, Quality, Lineage)",
            "Write declarative data tests using Great Expectations and dbt tests",
            "Implement automated alerting for data drift and volume anomalies"
        ],
        content_body="""Data downtime (bad, late, or missing data) breaks dashboards and machine learning models. Robust data teams treat data as a product with strict quality guarantees.

### The 5 Pillars of Data Observability
1. **Freshness**: Is the data up-to-date and landing within expected SLAs?
2. **Volume**: Did the expected number of records arrive, or was there an abnormal drop/spike?
3. **Schema**: Have columns changed, been deleted, or types drifted?
4. **Quality**: Do field values pass business constraints (nullability, uniqueness, allowed ranges)?
5. **Lineage**: What upstream sources and downstream dashboards are affected by an outage?""",
        key_concepts=[
            "Data Quality testing frameworks (Great Expectations, dbt tests)",
            "Data Contracts between producers and consumers",
            "SLAs, SLOs, and SLIs for data pipelines",
            "Automated anomaly detection for metric drift"
        ],
        practical_example="""```python
# Great Expectations Expectation Suite Example
import great_expectations as gx

context = gx.get_context()
validator = context.sources.pandas_default.read_parquet("s3://analytics/fact_completions.parquet")

validator.expect_column_values_to_not_be_null(column="student_id")
validator.expect_column_values_to_be_between(column="score_percentage", min_value=0.0, max_value=100.0)
validator.expect_column_values_to_be_in_set(column="completion_status", value_set=["PASSED", "FAILED", "IN_PROGRESS"])

results = validator.validate()
assert results.success, "Data quality checks failed!"
```""",
        completion_req="Create data test assertions using Great Expectations or dbt tests."
    )
]

MODULE_2_LESSONS = [
    make_lesson(
        title="Distributed Systems Fundamentals: CAP Theorem and Consensus",
        slug="distributed-systems-fundamentals-cap-consensus",
        order_index=1,
        duration_minutes=60,
        description="Theoretical foundations of distributed systems: network partitions, CAP Theorem, PACELC, distributed consensus (Raft, Paxos), and vector clocks.",
        objectives=[
            "Apply the CAP Theorem and PACELC model to distributed database trade-offs",
            "Understand distributed consensus algorithms (Raft leader election and log replication)",
            "Explain causal consistency and vector clocks in distributed replication"
        ],
        content_body="""A distributed system is a collection of autonomous computing nodes that communicate over a network to coordinate actions and share state.

### The CAP Theorem (Brewer)
In the presence of a **Network Partition (P)**, a distributed system must choose between:
- **Consistency (C)**: Every read receives the most recent write or an error.
- **Availability (A)**: Every non-failing node returns a response without guarantee that it contains the most recent write.

### PACELC Theorem
Expands CAP by addressing normal operation: If there is a **Partition (P)**, choose between **Availability (A)** and **Consistency (C)**; **Else (E)**, choose between **Latency (L)** and **Consistency (C)**.""",
        key_concepts=[
            "CAP Theorem (CP vs AP systems)",
            "PACELC Theorem for normal vs partitioned operations",
            "Raft consensus protocol (Leader Election, Log Replication, Safety)",
            "Split-brain scenarios and Quorum calculations (`N/2 + 1`)"
        ],
        practical_example="""```python
# Calculating Quorum for a Distributed Cluster
def has_quorum(total_nodes: int, active_nodes: int) -> bool:
    required_quorum = (total_nodes // 2) + 1
    return active_nodes >= required_quorum

print("5 nodes, 3 active -> Quorum:", has_quorum(5, 3)) # True
print("5 nodes, 2 active -> Quorum:", has_quorum(5, 2)) # False (prevents split-brain)
```""",
        completion_req="Analyze distributed consensus and quorum requirements.",
        is_free_preview=True
    ),
    make_lesson(
        title="Distributed Storage Systems (HDFS, Object Storage)",
        slug="distributed-storage-systems-hdfs-object-storage",
        order_index=2,
        duration_minutes=55,
        description="Scalable storage architectures: HDFS NameNodes and DataNodes, Cloud Object Storage (S3/GCS) architecture, consistency models, and columnar Parquet/ORC file formats.",
        objectives=[
            "Compare HDFS block-level storage with Cloud Object Storage REST architectures",
            "Understand columnar Parquet file structures (row groups, column chunks, page headers)",
            "Optimize I/O efficiency using predicate pushdown and dictionary encoding"
        ],
        content_body="""Modern big data analytics relies on distributed file systems and cloud object stores capable of storing petabytes of structured and unstructured data.

### HDFS vs Cloud Object Storage
- **HDFS**: Block-based (128MB/256MB blocks) across local cluster disks with 3x replication. High locality for MapReduce, but requires managing NameNodes and physical servers.
- **Cloud Object Storage (AWS S3, Google Cloud Storage)**: Key-value object store with strong consistency, virtually infinite scaling, and 11 9s durability without cluster maintenance.

### Apache Parquet Columnar File Format
Parquet is the standard storage format for analytical engines. It organizes data into **Row Groups**, which contain **Column Chunks** divided into **Pages**, storing min/max statistics for efficient metadata-based skip scans (Predicate Pushdown).""",
        key_concepts=[
            "HDFS NameNode metadata and DataNode block replication",
            "S3 Strong Read-After-Write Consistency",
            "Parquet file internals: Row Groups, Pages, and Footer Metadata",
            "Predicate Pushdown and Projection Pruning"
        ],
        practical_example="""```python
# Reading Parquet Metadata and Schema with pyarrow
import pyarrow.parquet as pq

parquet_file = pq.ParquetFile('s3_data.parquet')
print("Number of Row Groups:", parquet_file.num_row_groups)
print("Schema:\n", parquet_file.schema)
print("Column Metadata (Min/Max stats):", parquet_file.metadata.row_group(0).column(0))
```""",
        completion_req="Inspect Parquet internal metadata and evaluate object storage performance."
    ),
    make_lesson(
        title="Distributed Computing with Apache Spark Architecture",
        slug="distributed-computing-apache-spark-architecture",
        order_index=3,
        duration_minutes=65,
        description="Apache Spark internals: Driver, Cluster Manager, Executors, RDDs, DAG execution graph, Catalyst Optimizer, and Tungsten engine.",
        objectives=[
            "Explain the Spark distributed execution model (Driver, Executors, Tasks, Stages)",
            "Understand the Catalyst Optimizer (logical plan, optimized logical plan, physical plan)",
            "Analyze Spark DAG scheduling and shuffle operations across nodes"
        ],
        content_body="""Apache Spark is a unified multi-language engine for executing large-scale data analytics and machine learning on distributed computer clusters.

### Spark Architecture Components
- **Driver Program**: Runs the main application code, creates the `SparkSession`, translates user code into execution DAGs, and schedules tasks.
- **Cluster Manager**: Allocates cluster resources (Kubernetes, YARN, Standalone).
- **Executors**: Worker processes running on cluster nodes responsible for executing tasks and holding in-memory data partitions.

### Catalyst Optimizer Pipeline
1. **Unresolved Logical Plan**: Validates relation and column names.
2. **Logical Plan**: Applies rule-based optimizations (constant folding, predicate pushdown).
3. **Physical Plans**: Generates multiple execution strategies and selects the lowest-cost physical plan based on cost modeling.
4. **Tungsten Code Generation**: Emits optimized JVM bytecode for cache-aware, CPU-efficient execution.""",
        key_concepts=[
            "Spark Driver vs Worker Executor architecture",
            "Transformations (Lazy) vs Actions (Eager execution)",
            "Narrow dependencies (map, filter) vs Wide dependencies (groupBy, join requiring Shuffle)",
            "Catalyst Optimizer and Whole-Stage Code Generation"
        ],
        practical_example="""```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \\
    .appName("SparkInternalsDemo") \\
    .config("spark.executor.memory", "4g") \\
    .config("spark.executor.cores", "2") \\
    .getOrCreate()

df = spark.range(1, 1000000).filter("id % 2 == 0").groupBy("id").count()
# View execution plan
df.explain(True)
```""",
        completion_req="Run a Spark job and inspect its execution plan with `explain()`."
    ),
    make_lesson(
        title="Spark DataFrames, SQL, and Transformations",
        slug="spark-dataframes-sql-and-transformations",
        order_index=4,
        duration_minutes=60,
        description="Data manipulation in Spark: DataFrames API, Spark SQL, Window functions, Broadcast Joins, UDFs, and avoiding skew.",
        objectives=[
            "Write complex analytical transformations using Spark DataFrames and SQL",
            "Optimize joins using Broadcast Hash Joins (`broadcast()`)",
            "Implement Spark SQL analytical Window functions (Rank, DenseRank, Lead/Lag)"
        ],
        content_body="""Spark DataFrames provide a structured, strongly-typed API with rich SQL capabilities executed directly over Catalyst and Tungsten.

### Join Optimization Strategies
- **Shuffle Hash Join / Sort-Merge Join**: Standard join for two large tables. High network overhead due to data repartitioning (shuffle).
- **Broadcast Hash Join (Map-Side Join)**: When joining a large DataFrame with a small dimension table (<10MB default), Spark broadcasts the small table to all executors, completely eliminating the expensive network shuffle.""",
        key_concepts=[
            "DataFrame transformations and PySpark functions",
            "Broadcast Hash Join vs Sort Merge Join",
            "Window specs for cumulative metrics and rankings",
            "Data skew mitigation using Salting techniques"
        ],
        practical_example="""```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Broadcast Join and Window Function Example
large_events_df = spark.read.parquet("s3://events/")
small_courses_df = spark.read.parquet("s3://courses/")

# Broadcast join eliminating shuffle
enriched_df = large_events_df.join(
    F.broadcast(small_courses_df), 
    on="course_id", 
    how="inner"
)

# Window Function: Calculate student rank per course
window_spec = Window.partitionBy("course_id").orderBy(F.col("total_score").desc())
ranked_df = enriched_df.withColumn("rank", F.dense_rank().over(window_spec))
```""",
        completion_req="Execute a Spark broadcast join and calculate rankings with Window functions."
    ),
    make_lesson(
        title="Spark Streaming and Real-Time Data Processing",
        slug="spark-streaming-and-real-time-data-processing",
        order_index=5,
        duration_minutes=65,
        description="Continuous stream computing: Spark Structured Streaming, Kafka integration, trigger intervals, checkpointing, and stateful streaming.",
        objectives=[
            "Build real-time streaming pipelines with Spark Structured Streaming and Kafka",
            "Configure streaming triggers, micro-batching, and continuous processing",
            "Implement stateful stream aggregations with checkpoint directories"
        ],
        content_body="""Spark Structured Streaming provides a stream processing engine built on the Spark SQL engine, treating streaming data as an incrementally appended unbound table.

### Core Features
- **Kafka Source/Sink**: Native high-throughput ingestion from Kafka topics and writing to downstream stores.
- **Checkpointing & Write-Ahead Logs**: Stores stream offsets and state metadata to persistent storage (S3/HDFS) ensuring exactly-once processing guarantees on restart.
- **Output Modes**:
  - `Append`: Only new rows added to the result table are output.
  - `Complete`: The entire updated result table is written to sink.
  - `Update`: Only modified rows are output.""",
        key_concepts=[
            "Unbounded table streaming abstraction",
            "Structured Streaming Kafka integration",
            "Streaming Checkpointing for disaster recovery and exactly-once semantics",
            "Output modes: Append, Update, Complete"
        ],
        practical_example="""```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

spark = SparkSession.builder.appName("LmsKafkaStream").getOrCreate()

schema = StructType().add("student_id", StringType()).add("course_id", StringType()).add("score", IntegerType())

kafka_stream = spark.readStream \\
    .format("kafka") \\
    .option("kafka.bootstrap.servers", "localhost:9092") \\
    .option("subscribe", "lms.quizzes") \\
    .load()

parsed_stream = kafka_stream.selectExpr("CAST(value AS STRING) as json_payload") \\
    .select(from_json(col("json_payload"), schema).alias("data")) \\
    .select("data.*")

query = parsed_stream.writeStream \\
    .format("parquet") \\
    .option("path", "s3://lakehouse/quizzes/") \\
    .option("checkpointLocation", "s3://lakehouse/_checkpoints/quizzes/") \\
    .outputMode("append") \\
    .start()
```""",
        completion_req="Build a streaming ingestion job from Kafka to persistent storage."
    ),
    make_lesson(
        title="Data Lakehouses: Delta Lake, Apache Iceberg, and Hudi",
        slug="data-lakehouses-delta-lake-apache-iceberg-hudi",
        order_index=6,
        duration_minutes=65,
        description="The Lakehouse paradigm: ACID transactions on object storage, metadata layers, snapshot isolation, time travel, compaction, and schema evolution with Iceberg and Delta Lake.",
        objectives=[
            "Explain how Lakehouse table formats bring ACID transactions to Cloud Object Storage",
            "Compare metadata architectures: Apache Iceberg vs Delta Lake vs Apache Hudi",
            "Perform ACID UPSERTs, Time Travel, and file compaction (OPTIMIZE/Z-ORDER)"
        ],
        content_body="""The **Data Lakehouse** architecture combines the low cost, open formats, and scalability of Data Lakes (S3/GCS) with the ACID transactional consistency and governance of Data Warehouses.

### How Table Formats Work
Table formats like **Apache Iceberg** and **Delta Lake** add a metadata transaction log on top of raw Parquet data files:
- **ACID Transactions**: Multiple writers can update data concurrently with serializable/snapshot isolation.
- **Time Travel**: Query previous snapshots of data using log commit timestamps.
- **Schema Evolution**: Add, drop, or rename columns without rewriting multi-terabyte underlying data files.
- **Compaction**: Merge small files into optimal large files asynchronously.""",
        key_concepts=[
            "The Data Lakehouse paradigm",
            "ACID transaction logs on object storage",
            "Apache Iceberg metadata tree (Catalog -> Metadata -> Manifest List -> Manifests -> Data files)",
            "Z-Ordering and partition compaction"
        ],
        practical_example="""```sql
-- Delta Lake / Iceberg ACID Merge (Upsert) and Time Travel Example
MERGE INTO lakehouse.students target
USING staged_students source
ON target.id = source.id
WHEN MATCHED THEN
  UPDATE SET target.email = source.email, target.updated_at = source.updated_at
WHEN NOT MATCHED THEN
  INSERT (id, email, updated_at) VALUES (source.id, source.email, source.updated_at);

-- Time Travel Query on Lakehouse Table
SELECT * FROM lakehouse.students VERSION AS OF 5;
```""",
        completion_req="Perform an ACID UPSERT and Time Travel query on a Lakehouse table."
    ),
    make_lesson(
        title="Workflow Orchestration with Apache Airflow",
        slug="workflow-orchestration-with-apache-airflow",
        order_index=7,
        duration_minutes=60,
        description="Data pipeline orchestration: Apache Airflow architecture (Webserver, Scheduler, Celery Workers), DAG authoring, Operators, Sensors, XComs, and backfills.",
        objectives=[
            "Design idempotent Directed Acyclic Graphs (DAGs) in Apache Airflow",
            "Utilize Airflow Operators, TaskFlow API (`@task`), and Sensors",
            "Configure scheduling, retry policies, SLAs, and execution dates"
        ],
        content_body="""Apache Airflow is the industry-standard platform to programmatically author, schedule, and monitor complex data engineering workflows as code.

### Core Airflow Architecture
- **Scheduler**: Continuously evaluates DAG definitions, monitors task dependencies, and queues runnable task instances.
- **Executor / Workers (Celery/Kubernetes)**: Pulls tasks from the queue and executes them across distributed compute nodes.
- **Metadata Database (PostgreSQL)**: Authoritative state store for all DAGs, task runs, variables, and connections.
- **Webserver**: Rich UI for monitoring pipeline runs, DAG lineage, and task logs.""",
        key_concepts=[
            "Workflows as Code (DAGs in Python)",
            "Airflow 2.0 TaskFlow API (`@task` and `@dag` decorators)",
            "Execution Date (`data_interval_start`) vs Start Date",
            "Sensors, Branching, and Dynamic Task Mapping"
        ],
        practical_example="""```python
from datetime import datetime, timedelta
from airflow.decorators import dag, task

default_args = {
    'owner': 'data-engineering',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id="daily_lms_analytics_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args
)
def lms_etl_pipeline():

    @task
    def extract_postgres_data():
        return "s3://raw/postgres_export.parquet"

    @task
    def transform_spark_job(raw_path: str):
        print(f"Triggering Spark job on {raw_path}")
        return "s3://analytics/daily_marts.parquet"

    @task
    def load_to_warehouse(transformed_path: str):
        print(f"Loading {transformed_path} to Snowflake")

    raw_data = extract_postgres_data()
    analytics_data = transform_spark_job(raw_data)
    load_to_warehouse(analytics_data)

daily_dag = lms_etl_pipeline()
```""",
        completion_req="Author and trigger an idempotent Apache Airflow DAG."
    ),
    make_lesson(
        title="Distributed Database Internals: Partitioning and Replication",
        slug="distributed-database-internals-partitioning-replication",
        order_index=8,
        duration_minutes=60,
        description="Distributed database internals: Sharding strategies (Hash, Range, Consistent Hashing), Replication topologies (Leader-Follower, Multi-Leader, Leaderless), and Gossip protocols.",
        objectives=[
            "Evaluate Hash Partitioning vs Range Partitioning and Consistent Hashing",
            "Analyze Leader-Follower, Multi-Leader, and Leaderless (Dynamo-style) replication",
            "Understand read repair, anti-entropy (Merkle trees), and write quorums"
        ],
        content_body="""Distributed databases horizontally scale storage and compute across multiple nodes using **Partitioning (Sharding)** and **Replication**.

### Partitioning Strategies
- **Range Partitioning**: Assigns contiguous key ranges to nodes. Supports efficient range queries, but prone to hotspots.
- **Hash Partitioning**: Computes a cryptographic hash of the key to evenly distribute rows across nodes.
- **Consistent Hashing**: Minimizes data movement when nodes join or leave the cluster (used in DynamoDB, Cassandra).

### Replication Models
- **Single-Leader (PostgreSQL, MySQL)**: Writes go to leader; followers replicate asynchronously/synchronously.
- **Leaderless (Cassandra, DynamoDB)**: Clients write to and read from multiple replicas concurrently using tunable Quorums (`R + W > N`).""",
        key_concepts=[
            "Consistent Hashing and virtual nodes (vnodes)",
            "Synchronous vs Asynchronous replication lag",
            "Tunable Quorum reads and writes (`R + W > N`)",
            "Anti-entropy with Merkle trees and Read Repair"
        ],
        practical_example="""```python
import hashlib

class ConsistentHashRing:
    def __init__(self, nodes: list, replicas: int = 3):
        self.replicas = replicas
        self.ring = {}
        for node in nodes:
            for i in range(replicas):
                h = int(hashlib.md5(f"{node}:{i}".encode()).hexdigest(), 16)
                self.ring[h] = node
        self.sorted_keys = sorted(self.ring.keys())

    def get_node(self, key: str) -> str:
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        for ring_key in self.sorted_keys:
            if h <= ring_key:
                return self.ring[ring_key]
        return self.ring[self.sorted_keys[0]]
```""",
        completion_req="Understand consistent hashing and quorum replication models."
    ),
    make_lesson(
        title="Query Optimization and Distributed Indexing",
        slug="query-optimization-and-distributed-indexing",
        order_index=9,
        duration_minutes=55,
        description="Query engine performance: Distributed indexing (LSM Trees vs B-Trees), query compilation, cost-based optimizers, and partition pruning.",
        objectives=[
            "Understand LSM-Trees (Log-Structured Merge-trees) vs B-Trees for high write throughput",
            "Analyze query execution plans and cost-based query optimization (CBO)",
            "Apply distributed indexing and materialized view acceleration"
        ],
        content_body="""Database index structures determine read and write throughput tradeoffs in distributed storage engines.

### B-Trees vs LSM-Trees
- **B-Trees / B+ Trees (PostgreSQL, Traditional RDBMS)**: In-place page updates. Exceptional random read performance, but random disk writes cause write amplification.
- **LSM-Trees (Cassandra, RocksDB, Bigtable, ClickHouse)**: All writes are sequential appends to an in-memory **MemTable** and flushed to immutable **SSTables** on disk. Periodic background **Compaction** merges SSTables and purges deleted records. Incredible write throughput.""",
        key_concepts=[
            "LSM-Tree architecture (MemTable, WAL, SSTables, Bloom Filters)",
            "B-Tree index leaf nodes and write amplification",
            "Bloom filters for eliminating unnecessary disk lookups",
            "Materialized views and automated query rewrite"
        ],
        practical_example="""```python
# Conceptual Bloom Filter Lookup in an LSM-Tree SSTable
class BloomFilterSimulator:
    def contains(self, key: str) -> bool:
        # If Bloom filter says NO, the key is 100% NOT in the SSTable (skip disk read!)
        # If Bloom filter says YES, key MIGHT be present (read SSTable from disk)
        return True
```""",
        completion_req="Compare LSM-Trees and B-Trees and analyze query plans."
    ),
    make_lesson(
        title="Enterprise Data Architecture and Governance",
        slug="enterprise-data-architecture-governance",
        order_index=10,
        duration_minutes=60,
        description="Enterprise data strategy: Data Mesh decentralized ownership, Data Fabric, Data Catalogs, Data Lineage, RBAC/ABAC access policies, and regulatory compliance (GDPR, CCPA).",
        objectives=[
            "Evaluate centralized Data Lakes vs decentralized Data Mesh domain-driven architectures",
            "Implement automated data catalogs and metadata tracking with Apache Atlas / DataHub",
            "Enforce role-based (RBAC) and attribute-based (ABAC) row/column level security"
        ],
        content_body="""As organizations scale, monolithic centralized data teams become bottlenecks. Modern enterprise architectures introduce decentralized domain ownership and automated governance.

### Data Mesh Principles (Zhamak Dehghani)
1. **Domain-Oriented Decentralized Ownership**: Business domains (e.g., LMS Learning Domain, Billing Domain) own and manage their analytical data.
2. **Data as a Product**: Data assets are treated as first-class products with discoverability, documentation, and SLAs.
3. **Self-Serve Data Platform**: Platform teams provide automated infrastructure tooling (storage, compute, CI/CD).
4. **Federated Computational Governance**: Global standards for interoperability, privacy, and access control executed automatically.""",
        key_concepts=[
            "Data Mesh 4 core principles vs Centralized Data Lake",
            "Data as a Product and Data Product Contracts",
            "Column-level masking and Row-Level Security (RLS)",
            "Automated data catalogs and end-to-end lineage"
        ],
        practical_example="""```sql
-- PostgreSQL / Snowflake Row-Level Security (RLS) Policy Example
-- Restrict tenant access dynamically based on session context
CREATE POLICY tenant_isolation_policy ON fact_enrollments
    FOR ALL
    USING (tenant_id = CURRENT_SETTING('app.current_tenant_id')::UUID);

ALTER TABLE fact_enrollments ENABLE ROW LEVEL SECURITY;
```""",
        completion_req="Understand Data Mesh paradigms and implement Row-Level Security policies."
    )
]

# 10 Questions for Module 1 Quiz
MODULE_1_QUIZ_QUESTIONS = [
    make_question(1, "What are the five core stages of the Data Engineering Lifecycle?", "Generation, Storage, Ingestion, Transformation, and Serving", ["Extraction, Validation, Deletion, Testing, and Production", "Planning, Coding, Building, Testing, and Deploying", "Scraping, Cleaning, Compacting, Archiving, and Deleting"], "The Data Engineering Lifecycle spans Generation, Storage, Ingestion, Transformation, and Serving."),
    make_question(2, "In dimensional modeling, what type of table contains numerical metrics and foreign keys?", "Fact Table", ["Dimension Table", "Bridge Table", "Lookup Table"], "Fact tables contain quantitative business measurements and foreign keys referencing dimensions."),
    make_question(3, "What is a Slowly Changing Dimension (SCD) Type 2?", "Tracks historical changes by inserting a new row with valid_from and valid_to timestamp columns", ["Overwrites the existing record in place, losing history", "Creates a new column for each historical change", "Never updates any data"], "SCD Type 2 preserves historical state changes by creating new versioned rows with validity date ranges."),
    make_question(4, "Why are Columnar databases significantly faster than Row-oriented databases for analytical queries?", "They read only the specific columns requested in the query from disk, avoiding reading unused data", ["They do not store data on physical disks", "They only allow single-threaded operations", "They disable all data compression"], "Columnar storage stores columns contiguously, drastically reducing I/O by reading only required query columns."),
    make_question(5, "What major architecture shift enabled the widespread adoption of ELT over traditional ETL?", "The decoupling of scalable compute and storage in cloud data warehouses", ["The deprecation of SQL", "The invention of CSV files", "The elimination of data transformations"], "Cloud data warehouses provide on-demand massive parallel processing, enabling transforming raw data directly in-warehouse."),
    make_question(6, "What is the primary benefit of partition pruning in batch processing systems?", "The query engine skips reading entire file directories that do not match the filter predicates", ["It automatically deletes corrupted files", "It prevents duplicate user signups", "It converts JSON to HTML"], "Partition pruning uses directory partitioning (e.g. `year=2026/month=09/`) to eliminate scanning irrelevant data files."),
    make_question(7, "In stream processing, what is Event Time?", "The timestamp when the event was originally generated at the source device", ["The timestamp when the stream engine processed the message", "The timestamp when the database was backed up", "The server's current system clock time"], "Event Time is the exact time the event occurred at the client/source, regardless of network delays."),
    make_question(8, "What is the function of a Watermark in stream processing frameworks like Apache Flink and Spark?", "Defines a threshold of event-time lateness after which time windows are finalized and closed", ["Encrypts the Kafka stream", "Increases the network bandwidth", "Forces all streams to run synchronously"], "Watermarks tell the streaming engine how long to wait for late-arriving out-of-order events before closing a window."),
    make_question(9, "In Apache Kafka, what happens if messages are published with a consistent message key?", "All messages with the same key are guaranteed to be routed to the same partition and consumed in order", ["The messages are broadcast to all partitions simultaneously", "The messages are immediately deleted", "Kafka throws a runtime serialization exception"], "Kafka hashes the message key to assign partitions; identical keys always land on the same partition, preserving strict FIFO ordering."),
    make_question(10, "What is Change Data Capture (CDC)?", "A pattern that extracts insert, update, and delete events directly from database transaction logs (WAL)", ["Manually running hourly SELECT queries against production tables", "A technique to change column data types in SQL", "A method for caching HTTP API responses"], "CDC captures row-level changes from database transaction logs in real time with near-zero overhead on operational databases.")
]

# 10 Questions for Module 2 Quiz
MODULE_2_QUIZ_QUESTIONS = [
    make_question(1, "According to the CAP theorem, what trade-off must be made when a network partition occurs?", "Choose between Consistency (C) and Availability (A)", ["Choose between Performance and Security", "Choose between SQL and NoSQL", "Choose between CPU and Memory"], "When a network partition (P) is inevitable, a distributed system can either guarantee Consistency or Availability, but not both."),
    make_question(2, "In Apache Spark, what is the component responsible for converting user code into execution DAGs and managing tasks?", "Driver", ["Executor", "Worker Node", "Zookeeper"], "The Spark Driver initializes the SparkSession, builds the execution DAG, and assigns task partitions to Executors."),
    make_question(3, "What is a Broadcast Hash Join in Apache Spark?", "Spark sends a small lookup table to all worker nodes to perform local joins without a network shuffle", ["Spark shuffles all data across all cluster nodes", "Spark writes all join results to disk before proceeding", "Spark executes the join on the client machine only"], "Broadcast joins copy a small dimension table to every executor, completely bypassing the expensive data shuffle."),
    make_question(4, "How do Lakehouse table formats (e.g., Delta Lake, Apache Iceberg) achieve ACID transactions on Object Storage?", "By maintaining an immutable transaction metadata log that tracks atomic commit snapshots", ["By locking the entire cloud bucket on every write", "By converting object storage into an NFS mount", "By disabling concurrent reads"], "Lakehouse formats maintain transactional metadata logs that point to versioned Parquet data files, enabling snapshot isolation."),
    make_question(5, "In Apache Airflow, what does it mean for a data pipeline DAG to be idempotent?", "Running the DAG multiple times for the same execution date produces the exact same result without duplicate data", ["The DAG can only be executed once in history", "The DAG does not require any database", "The DAG runs in less than 1 second"], "Idempotency ensures that rerunning or backfilling a pipeline for any given time slice yields consistent, identical results."),
    make_question(6, "What is Consistent Hashing primarily used for in distributed database systems?", "Minimizing data re-distribution across cluster nodes when nodes are added or removed", ["Encrypting sensitive passwords", "Generating sequential integer primary keys", "Sorting analytical query results"], "Consistent Hashing maps data and nodes to a circular hash ring, re-routing only `K/N` keys when nodes scale."),
    make_question(7, "What is the write path mechanism in Log-Structured Merge-tree (LSM-tree) storage engines?", "Writes append sequentially to an in-memory MemTable and WAL, then flush to immutable SSTables on disk", ["Writes directly update random disk pages in place", "Writes are sent to an external Redis server", "Writes bypass disk and remain solely in RAM"], "LSM-trees write sequentially to RAM (MemTable) and a sequential WAL, achieving extremely high write throughput."),
    make_question(8, "What is the primary role of a Bloom Filter in an LSM-tree SSTable read path?", "Quickly tests if a key is definitely NOT present in an SSTable, skipping expensive disk I/O", ["Sorts strings alphabetically", "Calculates table row counts", "Encrypts SSTable files on disk"], "Bloom filters are probabilistic data structures that prevent unnecessary disk reads for non-existent keys."),
    make_question(9, "What are the four core principles of the Data Mesh architectural paradigm?", "Domain ownership, Data as a product, Self-serve data platform, and Federated computational governance", ["Centralized data lake, Monolithic ETL team, Manual Excel reporting, and Shared passwords", "Microservices, Containers, Kubernetes, and Helm", "Extraction, Loading, Transforming, and Deleting"], "Data Mesh decentralizes data ownership to domain teams while treating data as a product supported by a self-serve platform."),
    make_question(10, "What is the purpose of Checkpointing in Spark Structured Streaming?", "Saves streaming offsets and state data to fault-tolerant storage to ensure exactly-once recovery after failure", ["Stops the streaming job automatically after 100 records", "Deletes old Kafka topics", "Formats output JSON files"], "Checkpointing persists stream progress and state stores, enabling seamless recovery without message duplication.")
]

# 20 Questions for Final Assessment Quiz
FINAL_QUIZ_QUESTIONS = [
    make_question(1, "What is the key difference between OLTP and OLAP systems?", "OLTP handles high-concurrency row transactions; OLAP executes complex analytical queries over millions of rows", ["OLTP uses column storage; OLAP uses row storage", "OLTP is only for machine learning", "There is no difference"], "OLTP systems optimize low-latency row operations; OLAP systems optimize high-throughput column aggregations."),
    make_question(2, "In Kimball dimensional modeling, what is a Conformed Dimension?", "A dimension table that has the exact same meaning and structure across multiple fact tables and domains", ["A dimension that contains only numbers", "A temporary table created during ETL", "A dimension with no primary key"], "Conformed dimensions (e.g., `dim_date`, `dim_customer`) provide consistent enterprise context across diverse business facts."),
    make_question(3, "What does the PACELC theorem state about distributed systems when there is NO network partition?", "Else (E), the system must trade off between Latency (L) and Consistency (C)", ["Else (E), the system automatically becomes a single server", "Else (E), all network traffic is paused", "PACELC only applies during partitions"], "PACELC states: If Partition (P), choose Availability (A) or Consistency (C); Else (E), choose Latency (L) or Consistency (C)."),
    make_question(4, "Why are Parquet files ideal for big data analytical queries?", "Columnar layout, snappy compression, and footer metadata with min/max statistics for predicate pushdown", ["They are plain text files editable in notepad", "They execute JavaScript code natively", "They only allow sequential reading from line 1"], "Parquet's columnar design, compression, and rich metadata statistics enable high query speeds and storage efficiency."),
    make_question(5, "What causes a Wide Dependency (Shuffle) in Apache Spark?", "Operations that require data from multiple partitions across worker nodes (e.g., `groupByKey`, `join`)", ["Simple operations like `map` and `filter`", "Setting a small executor memory limit", "Reading a single CSV file"], "Wide transformations require redistributing data across executors over the network (a shuffle)."),
    make_question(6, "What is the purpose of Spark's Catalyst Optimizer?", "Automatically optimizes execution plans through rule-based and cost-based logical/physical transformations", ["Compiles Python code to C++", "Monitors server fan speeds", "Manages user login passwords"], "Catalyst analyzes query expressions to generate optimized physical execution plans and native JVM bytecode."),
    make_question(7, "What delivery guarantee does Kafka provide when producers use `enable.idempotence=True` and `acks=all`?", "Exactly-Once Semantics (EOS) within a partition without duplicate messages", ["At-Most-Once delivery", "Best-effort delivery with 50% packet drop", "No delivery guarantees"], "Idempotent Kafka producers assign sequence IDs to messages to prevent duplicate delivery even across retries."),
    make_question(8, "How does Apache Iceberg organize its metadata hierarchy?", "Iceberg Catalog -> Metadata File -> Manifest List -> Manifest Files -> Data Files", ["Single flat JSON file on the local machine", "PostgreSQL database table only", "Directly inside the Parquet file header"], "Iceberg uses a tree-like metadata hierarchy to track snapshots and data files without directory listing operations."),
    make_question(9, "What is Data Lineage in enterprise data governance?", "The complete historical trace of how data flows, transforms, and moves from source systems to downstream consumers", ["The list of employees who have access to a database", "The date when the database server was purchased", "The git commit history of the frontend app"], "Data Lineage provides end-to-end visibility into data origins, transformations, and downstream dependencies."),
    make_question(10, "In Apache Airflow, what does `catchup=False` prevent?", "Prevents running past historical DAG runs when a DAG is turned on or unpaused", ["Prevents the DAG from executing in parallel", "Disables all logging", "Deletes the metadata database"], "With catchup=False, Airflow only executes the most recent schedule interval rather than backfilling all past intervals."),
    make_question(11, "What is a Dead Letter Queue (DLQ) in data ingestion pipelines?", "A dedicated queue for isolating and inspecting malformed or unprocessable messages without halting the pipeline", ["A queue that deletes all incoming messages", "A queue that operates without network access", "A queue used only for server shutdowns"], "DLQs capture failed or invalid messages for debugging and reprocessing without blocking valid data streams."),
    make_question(12, "In distributed databases, what condition must be met to ensure Strong Consistency in a Quorum system?", "`R + W > N` (Read Quorum + Write Quorum > Total Replicas)", ["`R + W < N`", "`R * W = N`", "`R = W = 1` regardless of N"], "When `R + W > N`, the read quorum and write quorum are guaranteed to overlap on at least one up-to-date replica node."),
    make_question(13, "What is Data Skew in distributed computing, and why is it problematic?", "When one partition contains significantly more data than others, causing single worker stragglers that slow the entire job", ["When data types are converted from string to integer", "When clocks on worker nodes are out of sync", "When all data is deleted from the cluster"], "Data skew concentrates work on a single executor, bottlenecking the entire distributed pipeline on that single straggler."),
    make_question(14, "What technique can mitigate data skew during distributed Spark joins on skewed keys?", "Salting (appending random prefixes to skewed join keys to distribute records evenly across partitions)", ["Increasing network latency", "Deleting all null values", "Converting the join into a cross join"], "Salting appends random integers to keys, distributing skewed keys across multiple partition buckets."),
    make_question(15, "What is the primary benefit of dbt (Data Build Tool) in modern data platforms?", "Enables modular SQL transformations with version control, automated testing, documentation, and lineage graphs", ["Serves as a high-speed NoSQL database", "Builds React user interfaces", "Manages physical server cooling"], "dbt applies software engineering best practices (testing, version control, CI/CD, modularity) to SQL data modeling."),
    make_question(16, "What is Reverse ETL?", "Syncing enriched data from the analytical data warehouse back into operational business tools (Salesforce, CRM)", ["Restoring database backups from tape drives", "Converting Parquet files into raw CSVs", "Extracting data from frontend React state into backend APIs"], "Reverse ETL pushes modeled analytical data back into SaaS and operational tools to drive business workflows."),
    make_question(17, "What is Time Travel in modern Lakehouses and Cloud Data Warehouses?", "The ability to query or restore table data as it existed at a specific point in time or snapshot version", ["Running queries faster than the speed of light", "Predicting future data values with ML", "Simulating future database migrations"], "Time Travel leverages transaction log snapshots to query historical states or rollback accidental deletions."),
    make_question(18, "How does Debezium capture database changes for CDC without impacting application performance?", "By reading the database Write-Ahead Log (WAL) or transaction log files directly", ["By executing continuous `SELECT *` polls every 10 milliseconds", "By installing triggers on every table that block transactions", "By intercepting incoming HTTP requests at the firewall"], "Debezium taps into database replication stream WALs, capturing mutations asynchronously without locking application tables."),
    make_question(19, "What is the purpose of Row-Level Security (RLS) in analytical databases?", "Restricts which rows a user or tenant can view based on security context attributes", ["Compresses database rows to save disk space", "Prevents duplicate rows from being inserted", "Limits the maximum number of columns in a table"], "RLS transparently filters returned rows based on user identity or tenant context, enforcing multi-tenant isolation."),
    make_question(20, "What is a Data Contract in modern enterprise data architecture?", "An explicit agreement between data producers and data consumers defining schema, SLA, and semantics", ["A legal document signed with cloud storage providers", "The monthly invoice for cloud data warehouse usage", "The database user license agreement"], "Data contracts define expectations for schemas, update frequencies, and quality thresholds between producing and consuming teams.")
]

COURSE_3_DATA = {
    "title": "Data Engineering & Distributed Systems",
    "slug": "data-engineering-distributed-systems",
    "level": "ADVANCED",
    "short_description": "Architect scalable data pipelines, distributed computing systems, Lakehouses, and enterprise data platforms.",
    "description": "Comprehensive advanced data engineering course covering the Data Engineering Lifecycle, dimensional data modeling, batch and stream processing, Apache Kafka event streaming, Apache Spark distributed architecture, Delta Lake/Iceberg Lakehouses, Airflow orchestration, and distributed database internals.",
    "modules": [
        {
            "title": "Data Engineering Foundations",
            "slug": "data-engineering-foundations",
            "order_index": 1,
            "description": "Foundational data engineering principles, dimensional modeling (Star/Snowflake), ETL vs ELT, batch processing, Kafka event streaming, and data quality.",
            "lessons": MODULE_1_LESSONS,
            "quiz": {
                "title": "Module 1 Quiz: Data Engineering Foundations",
                "description": "Test your knowledge of data lifecycles, dimensional modeling, row vs columnar stores, ELT pipelines, and Kafka event streaming.",
                "passing_score": 70,
                "questions": MODULE_1_QUIZ_QUESTIONS
            }
        },
        {
            "title": "Distributed Data Systems",
            "slug": "distributed-data-systems",
            "order_index": 2,
            "description": "Distributed systems theory (CAP/consensus), Parquet storage internals, Apache Spark architecture, Data Lakehouses, Airflow orchestration, and distributed indexing.",
            "lessons": MODULE_2_LESSONS,
            "quiz": {
                "title": "Module 2 Quiz: Distributed Data Systems",
                "description": "Assess your understanding of distributed consensus, Apache Spark execution engines, Lakehouse ACID table formats, and Airflow orchestration.",
                "passing_score": 70,
                "questions": MODULE_2_QUIZ_QUESTIONS
            }
        }
    ],
    "final_quiz": {
        "title": "Final Assessment: Data Engineering & Distributed Systems",
        "description": "Comprehensive 20-question certification assessment covering the entire Data Engineering and Distributed Systems curriculum.",
        "passing_score": 80,
        "questions": FINAL_QUIZ_QUESTIONS
    }
}
