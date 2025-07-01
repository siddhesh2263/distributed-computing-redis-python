Distributed computations with Python and redis

python is inherently single threaded.
some people thingk threwading is the answer to spreading work over multiple cores or multiple cpus. since python is single threaded, multithreading is not going to speed up your computation work.
if app is IO bound (like running API, waiting for database,) then threading will work, much simpler to use async, so the author doesn't use threading.
so it's either asynchrnouns processing, or the method with the author is going to show, aloows to distribute wor over more than