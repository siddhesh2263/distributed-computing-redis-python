# Distributed computing using Python and Redis

There are limitations to using multiprocessing for distributed computing. Python is inherently single threaded, which means the Python apps will run on a single thread, and that is not sufficient. There will be a need to distribute the computation work across multiple cores or multiple CPUs.

Some people think threading is an option to that, but no, because Python is single threaded. For computational work, multithreading is not going to speed up the app whatsoever.

If the app is IO bound, then yes threading can work. But it is much simpler to use Async.

Subprocesses can scale up to the number of cores on a single machine, but when we want to scale up more, we would need to rewrite the code to handle things differently. And it is not difficult to write code to start off with to be completely distributed, as opposed to be limited to a single computer using subprocesses.

Below is the high level architecture of the system:

IMAGE HERE

## Concurrent work

The operation is going to be concurrent. This will be defined by the messages in the Redis queue. The message will contain all the information it needs for another application to look at, and perform the work that is to be done.

This setup is scalable, compared to subprocessing on a single system.

When dealing with concurrency, the order of execution should not impact the final output. While the messages might be pulled in order from the Redis queue, it is not guarenteed the worker will finish processing them in the same order. As long as we have this behaviour, the above setup works.

## Handling errors

Redis is not 100% foolproof to certain types of error scenarios. Firstly, multiple workers should not be able to access the same message, and this is something Redis handles. However, if a message is pulled, and the worker crashes during processing it, we need to handle this explicitly. RabbitMQ handles this by itself, but this is something we will not cover in this setup.

<br>

## System architecture

![alt text](https://github.com/siddhesh2263/distributed-computing-redis-python/blob/main/assets/architecture.png?raw=true)

<br>

![alt text](https://github.com/siddhesh2263/distributed-computing-redis-python/blob/main/assets/simulation.gif?raw=true)