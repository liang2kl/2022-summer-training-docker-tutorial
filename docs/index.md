---
title: 主页
---

[本仓库](https://github.com/liang2kl/2022-summer-training-docker-tutorial/)包含 2022 年酒井科协暑培 Docker 课程文档及源码。

本课程的内容包括：

- [Docker 介绍](introduction.md)：介绍 Docker 的用处及有关概念
- [Docker 基本命令](commands.md)：介绍 Docker 常用的命令，并给出一些运行 Docker 的例子
- [Dockerfile 的编写（上）](dockerfile-1.md)：介绍通过 Dockerfile 构建 hello world 镜像的几种方法
- [Dockerfile 的编写（下）](dockerfile-2.md)：打包并运行暑培后端作业
- [Docker Compose 的使用](docker-compose.md)：介绍使用 Docker Compose 简化运行多个容器的步骤
- [Docker 的原理](behind-the-scene.md)：简单介绍 Docker 背后的原理

课前只需完成下面“课前准备”的内容。其余内容为课程讲义，在课上均会涉及。在完成课前准备的基础上，可以提前浏览 [Docker 介绍](introduction.md)的内容。

## 课前准备

### 安装 Docker

**macOS 和 Windows 系统**

安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

**Linux 系统**

官方提供了自动安装脚本：

```
curl -fsSL get.docker.com -o get-docker.sh
sudo sh get-docker.sh --mirror Aliyun
```

好处是方便，并且可以直接使用国内镜像加速，但 `sudo sh` 意味着这个脚本可以对你的系统做任何事，如果不放心可以参考[官方文档](https://docs.docker.com/engine/install/ubuntu/)手动安装。

### 运行 hello-world

安装完成后，运行 hello-world 进行测试，注意 Linux 需要 root 权限：

```bash
# Linux
sudo docker run --rm hello-world:latest

# macOS / Windows
docker run --rm hello-world:latest
```

!!! info "关于 docker 用户组"
    准确来说，只有在 `docker` 用户组内的用户才能执行 `docker` 命令，而默认只有 `root` 用户在此用户组中。macOS 和 Windows 的 Docker 实际上是 Linux 虚拟机，`root` 为唯一的用户。

    在之后的文档中，为简洁起见我们在 `docker` 命令前不加 `sudo`，如有需要请自行添加。Linux 下输入此命令并重新登录即可省去 `sudo`：

    ```bash
    sudo usermod -aG docker $USER
    ```

当运行容器时，使用的镜像如果在本地中不存在，Docker 就会自动从 Docker 镜像仓库中下载，默认是从 Docker Hub 公共镜像源下载。

!!! note
    这里的 `hello-world` 实际来自 Docker Hub 中的 [hello-world](https://hub.docker.com/_/hello-world)，`latest` 为版本标签。

当看到如下输出时，表明 Docker 安装成功：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
......
```

!!! info "更换镜像源"
    一般情况下，Docker 拉取镜像的速度非常慢（如上面的命令可能卡在 `Unable to find image 'hello-world:latest' locally`），我们需要更换镜像源以加速访问。

    国内可访问的公共镜像源的可用情况可以在 [docker-registry-cn-mirror-test](https://github.com/docker-practice/docker-registry-cn-mirror-test)
    的 Actions 下查看。这里我们以 `https://docker.mirrors.ustc.edu.cn` 为例：

    Linux：编辑 `/etc/docker/daemon.json`；

    macOS 或 Windows：打开 Docker Desktop 的 `设置 - Docker Engine`。

    ```json
    {
        "registry-mirrors": [
            "https://docker.mirrors.ustc.edu.cn"
        ]
    } 
    ```

    Linux 系统下，在更改后，输入：

    ```
    sudo systemctl restart docker
    ```

    各云服务平台有供内部使用的镜像源，一般会更加稳定，可以查询平台文档。
