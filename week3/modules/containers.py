import docker
import tempfile
import os

# Initialize Docker client
client = docker.from_env()

def execute_code_in_container(code):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the code to a file
        code_file_path = os.path.join(temp_dir, "script.py")
        with open(code_file_path, "w") as f:
            f.write(code)

        # Run the code in a Docker container
        result = client.containers.run(
            image="python:slim",  # Use a minimal Python image
            command=f"python /app/script.py",
            volumes={temp_dir: {"bind": "/app", "mode": "rw"}},
            mem_limit="100m",  # Limit memory usage
            cpu_period=100000,
            cpu_quota=50000,  # Limit CPU usage
            remove=True,  # Remove the container after execution
        )

        return result.decode("utf-8")

# Example usage
code = """
print("Hello, World!")
"""
output = execute_code_in_container(code)
print(output)