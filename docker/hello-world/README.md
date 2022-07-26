# 用 Docker 运行 Hello World

本部分目标：运行 docker 容器时在屏幕打印 `Hello, world`（或类似内容）。

以下部分镜像使用 GitHub Actions 自动构建并上传至 Docker Hub，可直接使用：

- 使用 echo：`liang2kl/2022-sast-hello:echo`
- 使用 gcc 编译 C 程序：`liang2kl/2022-sast-hello:basic`
- 缩小镜像体积：`liang2kl/2022-sast-hello:slim`
- 进阶版 echo：`liang2kl/2022-sast-echo`

## 使用官方 hello-world 镜像

Docker 官方提供了一个 `hello-world` 镜像，通常用于检测 docker 环境是否正常。

使用命令行输入：

```
docker run --rm hello-world:latest
```

即可看到输出：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

## 使用 echo

建议你自己新建一个文件夹并动手写 Dockerfile。此部分内容源码见 [./echo](./echo) 目录，供参考。

首先，新建一个名为 `Dockerfile` 的文本文件，用来描述如何构建你的 docker 镜像。

在 Dockerfile 中，我们首先需要指定使用的基础镜像。这里，我们使用 `ubuntu`，这个镜像包含了 `echo`，可以用来进行输出。

用 `FROM` 指定基础镜像：

```dockerfile
FROM ubuntu:latest
```

最后，我们使用 `ENTRYPOINT` 来指定容器运行（即 `docker run`）时在**容器内部**执行的命令，命令行参数用逗号隔开：

```dockerfile
CMD ["echo", "Hello, world!"]
```

这样，我们的 Dockerfile 就编写好了。接下来，我们使用 `docker build` 命令来构建镜像，并将镜像的标签设为 `hello:echo`：

```
docker build . --tag hello:echo
```

然后，使用此镜像运行容器：

```
docker run --rm hello:echo
```

你应当能看到 `Hello, world!` 的输出。

## 使用 gcc 编译 C 程序

我们使用 `gcc` 来编译一个 hello world 程序，源码见 [./build-basic](./build-basic) 目录。

本部分所用的 C 程序 [`main.c`](build-basic/main.c) 如下：

```c
#include "stdio.h"

int main() {
    printf("Hello, world!\n");
    return 0;
}
```

在 `main.c` 同一目录下，创建 Dockerfile 如下：

```dockerfile
# Use "gcc" image.
FROM gcc:latest

# Copy main.c from local file system to the container.
COPY main.c main.c

# Compile hello-world program using gcc.
RUN gcc -o hello-world main.c

# Run the program.
CMD ["./hello-world"]
```

与之前例子相比，有几个不同点：

- 因为需要使用 `gcc`，因此使用官方的 `gcc` 镜像。
- 因为编译在 `gcc` 镜像内部进行，而我们的源文件在宿主机（即你的电脑）的文件系统中，我们需要将其拷贝到镜像内部。使用 `COPY /local/path /container/path` 进行拷贝。
- 在镜像中执行命令，使用 `RUN`。注意，`RUN` 在**镜像构建**时运行，而 `ENTRYPOINT` 在**容器启动**时运行。在这里，我们使用 `gcc` 编译程序，得到可执行文件 `hello-world`。

与之前类似，构建镜像并运行容器：

```
docker build . --tag hello:basic
docker run --rm hello:basic
```

## 缩小镜像体积

此部分源码见 [./build-slim](./build-slim) 目录。

在完成上一部分之后，执行如下命令，查看你所构建的镜像的体积：

```
> docker image ls hello:basic
REPOSITORY   TAG       IMAGE ID       CREATED             SIZE
hello        basic     3304cef3f3ee   About an hour ago   1.16GB
```

可以看到，`hello` 镜像的体积非常庞大，超过了 1GB。这是因为，我们使用了 `gcc` 镜像，而 `gcc` 镜像本身体积就达到了 1.16GB。

然而，`gcc` 只是用来进行编译的，在编译完成之后就不需要用到 `gcc` 了。为此，我们使用 Dockerfile 的 [multi-stage build](https://docs.docker.com/develop/develop-images/multistage-build/) 功能，以将用于编译与运行的镜像分离。

Dockerfile 如下：

```dockerfile
# === STAGE 1 ===
# Use "gcc" image. Name this stage as "build".
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
# This also works:
# COPY --from=0 /build/hello-world ./hello-world

# Run the program.
CMD ["./hello-world"]
```

每一个 `FROM` 语句直到下一个 `FROM` 语句的内容均为一个“阶段”（stage），每个阶段之间相互独立。在这里，我们有两个阶段：

**第一个阶段**：和上一个例子类似，使用 `gcc` 容器编译二进制文件。不同的是：

- 在 `FROM` 语句中增加了 `AS build`，以将此阶段命名为 `build`。这是为了方便在后续阶段中表示此阶段。
- 将工作目录设置为 `/build`，方便在后续阶段中进行拷贝。这一步可以省略（默认的工作目录为 `/`）。
- 在编译时，加上了 `-static`，以将动态库（在这里是 `libc`）静态地链接到可执行文件。因为我们后续使用（几乎什么都没有的）`scratch` 镜像来运行程序，而 `scratch` 中没有 `libc`，因此需要静态链接。

**第二个阶段**：使用 `scratch` 镜像，占用空间接近于 0。

我们使用 `COPY` 语句从第一个阶段 `build` 中将编译得到的二进制文件 `hello-world` 复制到这个镜像中。与之前不同，我们使用 `--from=build` 以从 `build` 阶段的镜像，而非宿主机上拷贝文件。你也可以使用 `--from=0` 表示从第一个阶段拷贝，从而省略 `AS build`，当然这不如上面的表示直观。

同样地，构建镜像并运行容器：

```
docker build . --tag hello:slim
docker run --rm hello:slim
```

查看此镜像的大小：

```
> docker image ls hello:slim
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
hello        slim      5ea5ccb25a54   3 hours ago   723kB
```

镜像只有 723kB，基本上就是程序本身的大小。

## 进阶版 echo

此部分源码见 [./echo-advanced](./echo-advanced) 目录。

我们之前写的 hello world 镜像都仅支持固定的输出。我们接下来使用 Docker 输出任意的字符串。

[之前提到](../README.md#ubuntu)，在 `docker run` 命令中，镜像名后面的参数的作用为覆盖镜像所定义的默认命令。因此，一种输出任意字符串的方法为：

```
docker run --rm ubuntu:22.04 echo Hello, world!
                |__________| |________________|
                    镜像名           CMD 
```

这个“默认命令”，就是我们上面所使用的 `CMD` 所定义的命令。你可以尝试覆盖[使用 echo](#使用-echo) 一节中构建的镜像所定义的命令：

```
docker run --rm hello:echo echo Hello, SAST!
```

此时，输出为 `Hello, SAST!`，而非 `Hello, world!`。

这其实违背了我们的初衷：我们上面写的 hello world 镜像只用于输出 `Hello, world!`，而不应当用于其他用途。为此，我们应当将 `CMD` 换成 `ENTRYPOINT`：

```dockerfile
FROM ubuntu:latest
ENTRYPOINT ["echo", "Hello, world!"]
```

`ENTRYPOINT` 与 `CMD` 的区别在于，`CMD` 可以通过简单地在 `docker run` 命令后追加参数来覆盖，而 `ENTRYPOINT` 不能[^1]。

另外，`ENTRYPOINT` 与 `CMD` 共同构成了容器运行时执行的命令：

```
ENTRYPOINT CMD
```

因此，我们可以这样来写一个默认输出 `Hello, world!`，但又可以输出任意字符串，且不需要像上面那样手动输入 `echo` 的镜像：

```dockerfile
FROM ubuntu:latest

# Set entry point as "echo".
ENTRYPOINT ["echo"]

# Provide the default arguments to the command ("echo").
CMD ["Hello, world!"]
```

构建、运行：

```bash
docker build . --tag echo
docker run --rm echo              # 输出为 Hello, world!
docker run --rm echo Hello, SAST! # 输出为 Hello, SAST!
```

怎么理解 `ENTRYPOINT` 和 `CMD` 的区别？不使用 `ENTRYPOINT` 的镜像像是一个运行环境，`CMD` 是在此环境中执行的程序（如 `ubuntu` 使用 `bash` 作为默认的 `CMD`），而使用 `ENTRYPOINT` 的镜像更像是一个程序，`CMD` 是这个程序的命令行参数（如上面的例子使用 `Hello, world` 作为默认的输出，但可以随时更改）。

最后，请你再仔细品味这几个命令的联系与区别：

```bash
docker run --rm ubuntu:22.04 echo Hello, SAST! # Ubuntu 镜像
docker run --rm hello:echo echo Hello, SAST! # 我们写的 echo - hello world 镜像，使用 CMD
docker run --rm echo Hello, SAST! # 我们写的改进版 echo - hello world 镜像，使用 ENTRYPOINT

echo Hello, SAST # 直接使用本地环境的 echo 程序
```

[^1]: `ENTRYPOINT` 可以通过 `docker run` 的 `--entrypoint` 选项覆盖，但一般不会使用。
