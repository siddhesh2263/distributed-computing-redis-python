# Distributed computing using a Redis queue and Python

## Table of contents

- [Why We Need Distributed Computing](#why-we-need-distributed-computing)
- [System Architecture](#system-architecture)
- [Redis Setup](#redis-setup)
- [Initiating Computation via HTTP Request](#initiating-computation-via-http-request)
- [Simulation and Results](#simulation-and-results)
- [Future Enhancements](#future-enhancements)
- [References](#references)

<br>

## Why we need distributed computing

Python, due to the Global Interpreter Lock (GIL), is inherently single-threaded. This makes it difficult to scale CPU-bound tasks efficiently using threads or basic multiprocessing alone. While the `multiprocessing` module allows parallelism up to the number of CPU cores on a single machine, it hits a hard limit when trying to scale beyond that.

I used to mistakenly assume that threading improves performance for all workloads, but that only holds true for I/O-bound tasks. For CPU-intensive operations, threading in Python offers no real performance gain because of the GIL. Although `asyncio` is a better fit for I/O-bound concurrency, it doesn’t solve the problem of parallel computation across machines.

This project is built to address these limitations from the ground up:
* It offloads processing work to distributed worker pods running on a cluster.
* It uses Redis as a shared queue to decouple task submission from task execution.
* Each unit of work is pushed into the queue and processed concurrently by multiple workers—across pods, cores, or machines.

By embracing this approach early, rather than retrofitting multiprocessing later, the system becomes more scalable.

This architecture also makes it easier to:
* Add or remove workers on the fly (horizontal scaling)
* Distribute tasks without managing local process pools
* Build toward a cloud-native model using containers and Kubernetes

<br>

## System architecture

In this system, a Dispatcher App pushes tasks into a Redis queue, and multiple Worker Apps across different nodes pull and process these tasks concurrently. This setup enables scalable and decoupled processing.

![alt text](https://github.com/siddhesh2263/distributed-computing-redis-python/blob/main/assets/architecture.png?raw=true)

<br>

## Redis setup

Redis is deployed as a single pod inside the Kubernetes cluster, exposed via a ClusterIP service named `redis-svc`. A ConfigMap stores non-sensitive connection details like host, port, and queue name, while a Secret can optionally store the Redis password. Both the dispatcher and worker apps read these environment variables to connect to Redis and communicate through a shared queue. No manual queue creation is needed—Redis creates it automatically on the first push.

<br>

## Initiating computation via HTTP request

The Dispatcher App exposes a `/dispatch` endpoint that allows users to trigger message generation through an HTTP POST request. The request body includes the number of messages to generate and the delay between each. When this endpoint is called, the dispatcher pushes the specified number of messages into the Redis queue, which are then picked up by the worker apps for processing.

Below is an example curl command:
```
curl -X POST http://10.0.0.191:8000/dispatch \
     -H "Content-Type: application/json" \
     -d '{"num_messages": 10, "delay": 0.1}'
```

<br>

## Simulation and results

Once the system is deployed, a POST request is sent to the Dispatcher App to simulate the workload. The Dispatcher generates the specified number of messages and pushes them to the Redis queue. Multiple Worker Apps, running across different nodes, pull these messages concurrently and process them.

![alt text](https://github.com/siddhesh2263/distributed-computing-redis-python/blob/main/assets/simulation.gif?raw=true)

Live logs from each worker pod show messages being processed independently, confirming that the system is working as a distributed, decoupled, and scalable setup.

<br>

## Future enhancements

Possible enhancements include using a separate Redis database to track processed message IDs and prevent accidental duplicates due to rare race conditions. A dedicated dead-letter queue (DLQ) can also be added to capture messages that consistently fail processing. To handle potential message loss (e.g., if a worker crashes after popping but before finishing), an intermediate "in-process" queue can be introduced following Redis’s Reliable Queue pattern. For more robust reliability, solutions like RabbitMQ or AWS SQS can be considered.

<br>

## References

[Distributed Computing using a Redis Queue](https://www.youtube.com/watch?v=XCSARhkRg7g)