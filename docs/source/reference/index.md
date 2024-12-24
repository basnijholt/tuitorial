# 📜 API Documentation

```{admonition} tl;dr
The API documentation is comprehensive and can be overwhelming.
The most important parts are:

- {class}`tuitorial.tuitorial`: the ``@tuitorial`` decorator
- {class}`tuitorial.tuitorial`: the class that is returned by the ``@tuitorial`` decorator
- {class}`tuitorial.Pipeline`: the class containing the ``tuitorial`` instances
- {class}`tuitorial.Pipeline.run`: run functions inline sequentially
- {class}`tuitorial.Pipeline.map`: run functions that *may* contain map-reduce operations in parallel

```

```{toctree}
tuitorial
tuitorial.map
tuitorial.map.adaptive
tuitorial.map.xarray
tuitorial.map.adaptive_scheduler
tuitorial.cache
tuitorial.helpers
tuitorial.resources
tuitorial.lazy
tuitorial.sweep
tuitorial.testing
tuitorial.typing
```
