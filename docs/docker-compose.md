---
title: Docker Compose 的使用
---

我们在[前一节](dockerfile-2.md)介绍了使用 Docker 同时运行数据库和后端的方法。如果你亲自尝试过一遍的话，你会发现这种方法是极其繁琐的。繁琐之处在于：

- 涉及到不同 Docker 容器间网络的连接
- 需要手动创建和挂载数据卷、挂载配置文件、设置环境变量等
- `docker run` 命令较为复杂，不利于快速一键运行

Docker compose 是一个可以解决这些问题的工具。官方对 Docker compose 的介绍是“一个定义并运行多容器应用的工具”，当然，对于单容器也有其方便之处。

## 描述容器运行的配置

Dockerfile 用来描述**容器构建的方法**，而 Docker compose 使用的 `docker-compose.yml` 配置文件用来描述**容器运行的方法**。Docker compose 实际上调用 Docker 服务提供的 API 来对容器进行管理。

`docker-compose.yml` 文件一般放置在项目的根目录。我们直接给出运行后端和数据库所用的 [`docker-compose.yml`]({{ code_base }}/external/django-backend/docker-compose.yml)：

```yaml
volumes:
  db-vol:

services:
  backend:
    build: .
    ports:
      - "9000:80"
    volumes:
      - "${PWD}/config.json:/config/config.json"
    restart: unless-stopped

  mysql:
    image: mysql:latest
    volumes:
      - "db-vol:/var/lib/mysql"
    environment:
        MYSQL_ROOT_PASSWORD: "my-secret-pw"
        MYSQL_DATABASE: leaderboard
```

`volumes` 用来创建数据卷，在这里我们提供一个名称为 `db-vol` 的**空词典**，表示用默认配置创建一个名为 `db-vol` 的数据卷。

一个 Docker 容器为一个服务（Service），在 `services` 中定义。

- 对于需要构建镜像的后端，我们用 `build` 指定 `docker build` 的上下文（即 Dockerfile 所在目录）；而对于不需要构建镜像的 MySQL 服务，我们用 `image` 指定所用的镜像。
- `ports` 是发布的端口，与 `docker run` 命令中 `-p` 一致。
- `volumes` 用于挂载数据卷或绑定宿主机上的目录。挂载数据卷用数据卷名称，而挂载宿主机目录时需要对应目录的绝对路径或用 `.` 开头的相对路径（一般用 `${PWD}` 表示工作目录，在这里我们的 `config.json` 直接放在项目根目录下）。与 `docker run -v` 不同，这时我们**可以挂载单个文件**了。
- `environment` 用于设置容器的环境变量。因为我们不再手动进入 MySQL 容器来创建数据库，因此额外增加 `MYSQL_DATABASE` 环境变量来完成这件事。

需要注意的是，我们的后端需要等待 MySQL 初始化完成之后才能够开始运行，否则将因连接不上数据库而运行失败。然而，Docker compose 中的服务的启动顺序是不确定的。尽管 Docker compose 提供了一些字段（如 `depends_on`）来控制容器启动的顺序，但只能控制一个容器在另一个容器启动完成（Started），而不是初始化结束（Ready）后启动另一个容器。这仍可能导致运行失败。

一种简单粗暴但有效的方法是：如果后端因为数据库的问题运行失败，就重新启动，直到成功。我们在 `backend` 服务中添加一项 `restart: unless-stopped` 来实现这样的作用。这一项的意思是：不断重启，直到手动停止。一旦后端运行成功，它将一直运行直到我们手动停止，因此可以达到我们的目的。

!!! note "一些更加优雅的方法"
    利用一些第三方的工具，可以实现不需要重启容器，保证在数据库初始化完成、可以接受请求时再启动服务。[wait-for-it](https://github.com/vishnubob/wait-for-it) 是一个这样的工具。

## 运行服务

在运行之前，我们先修改一下我们的配置文件（放置在项目根目录）。在前面我们使用 `bridge` 网络连接两个服务，而 Docker compose 的一大好处在于它自动创建一个连接所有服务的网络，并且可以以**服务名**作为 hostname 访问，这样就不需要手动在配置文件中填入 IP 地址了。因此，我们将 `config.json` 的 `db_host` 改成 `mysql`。

在 `docker-compose.yml` 所在目录下，执行

```bash
docker compose up -d
```

即可根据 `docker-compose.yml` 一键运行所有服务。同样地，访问 `127.0.0.1:9000`，检查是否运行成功。

!!! info "docker-compose 与 docker compose"
    `docker-compose` 是 Python 脚本，而 `docker compose` 是 Docker cli 的一个子命令。后者根据前者的 `v2` 版本开发，其功能基本一致，但因为其整合入 Docker cli 中，我们无需安装额外的 `docker-compose` 工具。可以认为二者基本上是等同的。

## 一些常用的命令

除了 `docker compose up` 外，还有一些常用的命令：

- `docker compose down`：停止所有容器，删除由 `docker compose up` 创建的网络、数据卷、镜像等。
- `docker compose logs <服务名>`：查看某一容器内的日志。
- `docker compose exec <服务名> <命令>`：在某一容器中执行命令。
