# === STAGE 1 ===
# Use gcc image. Name this stage as "build".
FROM gcc:latest AS build

WORKDIR /build

# Copy main.c from local file system to the container.
COPY main.c main.c

# Compile hello-world program using gcc.
# Statically link libc in order to run in the "scratch" image.
RUN gcc -static -o hello-world main.c

# === STAGE 2 ===
# Use the minimum "scratch" image.
FROM scratch

# Copy executable from the previous stage (in /build) to the container (.).
COPY --from=build /build/hello-world ./hello-world

# Run the program.
CMD ["./hello-world"]
