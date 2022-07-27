---
title: Docker 基本命令
---

## Docker 基本命令

本课程中最常用到的命令有：

- `docker run`：基于给定镜像启动一个新容器
- `docker build`：使用 Dockerfile 构建镜像

另外，还有一些获取信息、对本地的容器/镜像进行操作的命令：

- `docker pull`：拉取给定镜像（但不启动容器）
- `docker ps`：列出当前正在运行（Up）的所有容器，使用 `-a` 可以列出所有容器
- `docker exec`：使用给定容器运行命令
- `docker logs`：打印容器的标准输出
- `docker stop`：停止正在运行的容器
- `docker rm`：删除容器
- `docker image ls`：列出本地所有镜像
- `docker rmi`：删除镜像

在这里，我们不详细介绍 Docker 的命令，在需要时查阅[文档](https://docs.docker.com/engine/reference/commandline/docker/)或使用搜索引擎搜索问题即可。

## 尝试使用 Docker 运行已有镜像

### Hello, world

之前，我们在安装 Docker 之后已经运行过官方的 `hello-world` 镜像：

```
docker run --rm hello-world
                |_________|
                   镜像名
```

这条命令具体做了什么呢？

- 首先，先后在本地和 Docker 镜像仓库（默认为 Docker Hub）中查找 `hello-world` 镜像，若在本地不存在，则拉取到本地
- 使用 `hello-world` 镜像创建一个新的容器并启动
- ...（一些资源分配）
- **在容器中**执行 `hello-world` 定义的启动时所执行的命令（在这里是打印出一些文字）
- 终止容器  

我们在 `docker run` 后加上了 `--rm`，其意思是在启动容器并执行完命令后，自动删除这个容器，否则此容器会保存在本地（终止，即 Exited
状态，可通过 `docker ps -a` 查看）。

### Ubuntu

我们尝试使用 Docker 运行 Ubuntu，并启动一个供我们交互的 bash 终端：

```
docker run -t -i ubuntu:22.04  bash
                 |__________| |____|
                     镜像       CMD
```

`-i` 即 `--interactive`，让容器的标准输入保持打开；`-t` 即 `--tty`，让 Docker 分配一个伪终端（pseudo-tty）并绑定到容器的标准输入上。在镜像名后的命令行参数 `bash` 覆盖了镜像所定义的默认命令，使得容器运行时执行 `bash`。

### 运行暑培 Linux 作业所用镜像

暑培的 Linux 作业（CTF）实际上是在一台服务器上使用同一个镜像运行了 `N = 分配到账户的同学数量` 个容器，并将宿主机上的不同端口映射到容器内 ssh 所用的 22 端口，从而可以通过宿主机的不同端口 ssh 到不同的容器。

通过如下命令使用暑培所用镜像运行一个容器：

```
docker run -p 127.0.0.1:20000:22 -d cc7w/linux-training:v10
```

`-p` 即 `--publish`，将容器内部的端口发布到宿主机上。`-p 127.0.0.1:20000:22` 将容器内部的 22 端口发布到宿主机的 `127.0.0.1:20000`；换句话说，我们可以通过宿主机的 `127.0.0.1:20000` 访问容器的 22 端口。

`-d` 即 `--detach`，使得容器启动后执行的命令在后台运行。你可以通过 `docker image inspect cc7w/linux-training:v10` 看看容器启动后执行了什么命令。

现在，我们就可以通过宿主机 ssh 到容器内部了：

```
ssh train@127.0.0.1 -p 20000
```

[/docker/run-linux-homework/configure.py]({{ code_base }}/docker/run-linux-homework/configure.py) 中模拟了在服务器上批量创建若干 Linux 作业所用容器的过程（并不完整），如果感兴趣可以参考。

---

上面的例子都是基于已有的镜像。当我们需要将应用及依赖打包并发布给其他人使用时，我们通过编写 Dockerfile 来构建镜像。保持兴趣，继续往下阅读吧！
