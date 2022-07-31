# 使用 golang 镜像
FROM golang:1.18 AS build

# 设置 Go 代理服务器
ENV GOPROXY=https://goproxy.cn,direct

# 静态链接动态库
ENV CGO_ENABLED=0

WORKDIR /build

COPY . .

# 下载依赖
RUN go mod download

# 编译
RUN go build -o ./server

# 与 scratch 类似，不过具有包管理器
FROM alpine:latest

WORKDIR /app

# 可选：安装 bash，方便进入容器进行调试
RUN apk add --no-cache bash

# 将可执行文件拷贝到此容器中
COPY --from=build /build/server ./server

EXPOSE 80

CMD ["./server"]
