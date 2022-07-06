# Use gcc image.
FROM gcc:latest

# Copy main.c from local file system to the container.
COPY main.c main.c

# Compile hello-world program using gcc.
RUN gcc -o hello-world main.c

# Run the program.
CMD ["./hello-world"]
