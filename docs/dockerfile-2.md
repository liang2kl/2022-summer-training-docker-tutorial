---
title: "Dockerfile 的编写（下）"
---

接下来，我们完成一个实际的任务：将暑培后端作业打包为 Docker 镜像。我们将以 Django 作业示例代码为例，Golang 作业仅提供 [Dockerfile 样例]({{ code_base }}/external/golang-backend)。

!!! question "为什么选择讲解 Django"
    Golang 是编译型语言，我们只需要编译得到可执行文件就可以了（与之前使用 gcc 编译类似）；而 Python 是动态语言，与之前的例子不同，而且 Django 的部署一般需要用到 uWSGI，相对麻烦。

    如果没有学习 Django 也没有关系，重点是掌握**如何根据部署过程写 Dockerfile、运行容器**。

!!! info "Django 后端样例"
    本课程使用的代码位于 [/external/django-backend]({{ code_base }}/external/django-backend)，基于 [Django 作业官方示例](https://github.com/Btlmd/sast2022-django-training/tree/impl)修改而成。具体的修改有：

    - 将 `uwsgi.ini.bak` 中的 `socket` 改为 `http`
    - 将 `uwsgi.ini.bak` 更名为 `uwsgi.ini`
    - 将数据库配置文件 `LeaderBoard/my.cnf` 用 `config/config.json` 代替
    
    为方便与本教程同步，建议使用本教程仓库下的代码而非原始的样例代码。

## 从部署过程到 Dockerfile

写 Dockerfile 其实就是在容器中进行一遍部署（即配置环境、运行程序）的工作。我们先看 Django 部署的步骤：

1. 配置环境
    1. 安装特定版本的 Python（在这里我们使用 3.8）
    2. 安装项目依赖（`requirements.txt`）
    3. 安装 uWSGI
    4. 创建/编辑配置文件 `config/config.json`（原来是 `LeaderBoard/my.cnf`）
2. 运行程序
    1. 运行 `python3 manage.py makemigrations`
    2. 运行 `python3 manage.py migrate`
    3. 启动 uWSGI

接下来，我们根据这个流程写 Dockerfile。

**安装特定版本的 Python：**通过指定基础镜像，我们获得了特定版本的 Python 环境：

```dockerfile
FROM python:3.8
```

在继续进行之前，我们需要先将所有文件拷贝到容器内部：

```dockerfile
COPY . .
```

!!! note "使用 .dockerignore"
    在向容器内部拷贝时可以通过在 Dockerfile 同一目录下新建 `.dockerignore` 文件排除无关文件，如 git 目录、虚拟环境等，以缩小容器体积。

**安装项目依赖：**使用 `RUN` 安装依赖：

```dockerfile
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt
```

!!! note "关于此命令的一些解释"
    `-i https://pypi.tuna.tsinghua.edu.cn/simple` 使用 TUNA 源；`--no-cache-dir` 禁用缓存，以缩小容器体积。

**安装 uWSGI：**同样地，使用 `RUN`。在这里我们使用 pip 安装：

```dockerfile
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir uwsgi
```

在构建镜像的过程中，对于每一条指令，镜像会相应地加上一层。如果每一条 bash 命令都写一条 `RUN` 的话，镜像层数将非常多，构建时间和镜像大小都会受到影响。因此，一般使用一条 `RUN` 利用 `&& \` 连接多条命令，而不是使用多条 `RUN`：

```dockerfile
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir uwsgi
```

**创建/编辑配置文件 `config/config.json`：**配置文件一般包含敏感信息（如数据库的用户名与密码等），**不能**放入镜像中，因此这一步**不能**在构建镜像的过程中完成。我们稍后会介绍通过挂载目录完成此步骤的方法。

**运行程序**：运行 Django 程序包含几个步骤，这些步骤都在**容器运行**而不是容器构建时进行，因此应成为 `CMD`。一种较为简便的在启动时执行多条命令的方法为：将它们写到一个 shell 脚本中。在我们的例子中，我们将三个步骤写到 `start.sh` 中：

```sh
#!/bin/sh
python3 manage.py makemigrations &&
python3 manage.py migrate &&
uwsgi --ini uwsgi.ini
```

然后，使用 `CMD` 执行脚本：

```dockerfile
CMD ["/bin/sh", "start.sh"]
```

这样，我们的 Docker 镜像就写好了。最终的 Dockerfile 见 [/external/django-backend/Dockerfile]({{ code_base }}/external/django-backend/Dockerfile)。

构建镜像：

```bash
docker build . --tag leaderboard-backend
```

## 运行容器

!!! info "关于此部分内容"
    此部分内容介绍的方法稍显复杂，但对于理解 Docker 有较大的帮助。之后我们会使用 [Docker Compose](docker-compose.md) 来简化这一流程。

### 运行数据库

在运行后端之前，我们首先使用 Docker 运行一个 MySQL 服务器。

Docker 容器内的数据随着容器的销毁而消失，因此数据库的数据**不能保存在容器内部**。我们使用 Docker 的数据卷（Volume）功能。

!!! note "什么是数据卷"
    数据卷是一个可供一个或多个容器使用的特殊目录，可以提供很多有用的特性，如：

    - 数据卷可以在容器之间共享和重用
    - 对数据卷的修改会立马生效
    - 对数据卷的更新，不会影响镜像
    - 数据卷默认会一直存在，即使容器被删除

首先，创建一个数据卷：

```bash
docker volume create db-vol
```

然后，启动 `mysql` 容器，并将此数据卷挂载到 `/var/lib/mysql`，即数据库数据文件存放的目录：

```bash
docker run \
    -d \
    --name db \
    --mount source=db-vol,target=/var/lib/mysql \
    -e MYSQL_ROOT_PASSWORD=my-secret-pw \
    mysql
```

其中，`my-secret-pw` 改为你想要设置的 `root` 账户的密码。

接下来，进入 MySQL：

```
docker exec -it db mysql -p
```

然后，为后端创建一个数据库 `leaderboard`：

```
mysql> CREATE DATABASE leaderboard;
Query OK, 1 row affected (0.01 sec)
```

### 关于数据库的访问

每一个 Docker 容器都有自己的网络命名空间（Namespace），容器的网络是与其他容器/宿主机的网络隔离的，因此在数据库容器的 `0.0.0.0:3306` 上监听的 MySQL 服务是无法在后端容器中通过 `127.0.0.1:3306` 访问的。

`docker run` 创建容器时默认使用 Docker 的网桥模式（Bridge）创建网络，在这种模式下，除了分配隔离的网络命名空间之外，Docker 还会为所有的容器设置 IP 地址。当 Docker 服务器在主机上启动之后会创建新的虚拟网桥 `docker0`，随后在该主机上启动的全部服务在默认情况下都与该网桥相连。

因此，一种简单的访问数据库容器的办法是通过它在 `bridge` 网络（Docker 为 bridge 模式的容器创建的默认网络）上的 IP 地址进行访问。我们通过如下命令查看 IP 地址的分配：

```
docker network inspect bridge
```

查看其中打印出的 JSON 的 `Containers` 查看所连接容器的网络信息，查找 `Name` 为 `db` 的一项：

```
...
"Containers": {
    "7dd1830526a7196c1d1751dcbbd38a756949306995062e33b12ebcb294f2d672": {
        "Name": "db",
        "EndpointID": "1c4ab5928e6ba0864c775637b55f200a8699b3700d8c9d6f346035ca12ff1eaf",
        "MacAddress": "02:42:ac:11:00:03",
        "IPv4Address": "172.17.0.3/16",
        "IPv6Address": ""
    },
    ...
},
...
```

其中的 `IPv4Address` 就是数据库容器被分配到的 IPv4 地址，在后端容器中通过 `172.17.0.3` 即可访问数据库。

!!! info "看不懂？"
    这一部分看不懂没关系，只需要了解到通过 `docker network inspect bridge` 可以查询容器被分配到的、可以被其他容器访问到的 IP 地址就可以了。

### 运行后端

前面提到，数据库访问信息是不能放在镜像中的。我们通过挂载**宿主机上**的目录来解决。

在宿主机上某个位置创建一个新目录作为存放配置文件的目录，在其中新建一个名为 `config.json` 的文件，并将数据库访问信息写入。注意修改 `db_host` 和 `db_pass` 为数据库容器的 IP 地址和数据库 `root` 账户的密码：

```json
{
    "db_host": "172.17.0.3",
    "db_port": 3306,
    "db_user": "root",
    "db_pass": "my-secret-pass",
    "db_name": "leaderboard",
    "db_charset": "utf8mb4"
}
```

!!! warning "真实环境下不要使用 root 账户"
    数据库 root 账户具有一切权限，不应当用于后端访问。在这里我们为了方便直接使用 root 账户，真实情况下应当创建一个新的账户并授予相应的权限。

最后，运行后端容器：

```bash
docker run \
    -d
    --name backend \
    -p 9000:80 \
    -v /abs_path/to/lb_config:/config \
    backend-django
```

注意 `/abs_path/to/lb_config` 需要改为之前创建的本机上的配置文件目录的**绝对**地址，`9000` 改为任意一个在本机上没有被占用的端口（一般 `9000` 就可以）。

!!! note
    初次运行时可以不加 `-d`，方便检查运行是否有问题。

我们通过 `-v 本机配置文件目录绝对地址:/config` 来将本机上的配置文件目录映射到容器内的 `/config`，从而使得容器内可以通过 `/config/config.json` 访问到本机上的配置文件，这样就在不将配置文件放入镜像的情况下在容器中访问到配置文件。

`-p 9000:80` 选项的作用在[前面](commands.md#linux)提到过，其作用是将容器的 80 端口发布到宿主机的 9000 端口，从而能够通过宿主机的 9000 端口访问容器的 80 端口。

运行容器后，在宿主机上访问 `GET http://127.0.0.1:9000/`，如果正常返回响应即运行成功：

```
curl http://127.0.0.1:9000
{"code": 0, "msg": "hello"}
```

---

因为涉及到两个容器的运行及访问以及目录和数据卷的挂载，以上方法较为繁琐。接下来，我们介绍使用 Docker Compose 简化这一流程的方法。
