import pathlib

import docker


# TODO(bschoen): Do I want to make this wrap the function call handler
# TODO(bschoen): For now we're just running the whole thing in a docker container to test it out, in general though we don't want the tool to have the same permissions as the caller, wrapping a python function directly means we lose those customization points, unless we provide a wrapper (adapter) around them
# TODO(bschoen): Other tools could have arbitrary state, so as cool as the function call handler thing is, probably need to throw it away.
#                this probably needs to take in context manager tools and adapt them
# Note: If these act as command line applications (as an abstraction) will be tricky to manage state
# TODO(bschoen): Probably want a couple of different adapters.
# TODO(bschoen): We want the lightweight ones to play with them, but the containerized ones separately.
# TODO(bschoen): Speed of tool use probably isn't a limiting factor in compute by an order of magnitude, but may need to reuse something like a connection
# TODO(bschoen): Tools should probably be able to take in something like a docker container on context enter so can be shared between tools, same as other connections, but don't *HAVE* to
# TODO(bschoen): Tools should take a container provider on construction, that way they all have the same `__enter__` signature so a wrapping context manager doesn't have to know how to call `__enter__``
class DockerizedWorkspace:
    """Dockerized workspace for things which need sandboxing like code execution.

    Note that we want it to share between multiple tools

    Note:
        For most tools given to a model (for example web browsing), we don't need
        to sandbox and can just use the `schemas.generate_json_schema_for_function`
        to generate tool schemas for normal python functions.

    """

    # TODO(bschoen): Practice would likely want to give this it's own dockerfile
    DEFAULT_IMAGE_TAG = "python:3.12"

    def __init__(
        self,
        workspace_name: pathlib.Path,
        image_tag: str = DEFAULT_IMAGE_TAG,
    ) -> None:
        self.workspace_name = workspace_name
        self.image_tag = image_tag

    def __enter__(self) -> None:
        """Creates the container and working directory."""

        self.client = docker.from_env()

        self.container = self.client.containers.run(
            image=self.image_tag,
            command=["/bin/bash"],
            detach=True,
            tty=True,
            # TODO(bschoen): Make volumes persistent so can ssh into them after conversation
            # volumes={self.workspace_name: {"bind": "/workspace", "mode": "rw"}},
        )

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        print("Cleaning up container...")

        if self.container is not None:

            self.container.stop()

            # TODO(bschoen): We could always not remove
            self.container.remove()

        # return None, automatically propagating exceptions if any
        return None
