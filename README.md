Local claude UI via streamlit

> [!NOTE] Primarily intended for personal use while learning about function calling

We also give Claude some additional tool use, like:
 * Web browsing
 * (containerized) bash execution
 * (containerized) python execution 

Each session uses a persistent (for the duration of the session):
 * container
 * directory within that container

Note: This will later be abstracted out in a separate library.
