# 2022 年酒井科协暑培 Docker 课程

此仓库包含 2022 年酒井科协暑培 Docker 课程文档及源码。

本文档参考了汪子涵的 [2021 年暑培讲义](https://www.xuetangx.com/learn/THUSAST08091234567890/THUSAST08091234567890/8571842/video/13167567)，在此表示感谢。

## 课前准备

### 安装 Docker

**macOS 和 Windows 系统**

[安装 Docker Desktop](https://www.docker.com/products/docker-desktop/)。

**Linux 系统**

官方提供了自动安装脚本：

```
curl -fsSL get.docker.com -o get-docker.sh
sudo sh get-docker.sh --mirror Aliyun
```

好处是方便，并且可以直接使用国内镜像加速，但 `sudo sh` 意味着这个脚本可以对你的系统做任何事，如果不放心可以参考[官方文档](https://docs.docker.com/engine/install/ubuntu/)手动安装。

### 运行 hello-world

安装完成后，运行 hello-world 进行测试：

```bash
# Linux
sudo docker run hello-world:latest

# macOS / Windows
docker run --rm hello-world:latest
```

当运行容器时，使用的镜像如果在本地中不存在，Docker 就会自动从 Docker 镜像仓库中下载，默认是从 Docker Hub 公共镜像源下载。

这里的 `hello-world` 实际来自 Docker Hub 中的 [hello-world](https://hub.docker.com/_/hello-world)，`latest` 为版本标签。

当看到如下输出时，表明 Docker 安装成功：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
......
```

一般情况下，Docker 拉取镜像的速度非常慢（如上面的命令可能卡在 `Unable to find image 'hello-world:latest' locally`），我们需要更换镜像源以加速访问。

国内可访问的公共镜像源的可用情况可以在 [docker-registry-cn-mirror-test](https://github.com/docker-practice/docker-registry-cn-mirror-test)
的 Actions 下查看（各云服务平台有供内部使用的镜像源，一般会更加稳定，可以查询平台文档）。这里我们以 `https://docker.mirrors.ustc.edu.cn` 为例：

Linux：编辑 `/etc/docker/daemon.json`

macOS 或 Windows：打开 Docker Desktop 的设置 - Docker Engine

```
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

## 课程内容

以下是 Docker 课程的几大部分，请点击链接前往各自的文档。

- [Docker 介绍](#docker-介绍)
- [Docker 基本命令及 Dockerfile 基础](./docker)
- [docker-compose 使用](./docker-compose)

## Docker 介绍

TODO
