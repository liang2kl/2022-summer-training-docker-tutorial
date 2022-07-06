#include "stdlib.h"
#include "stdio.h"

int main(int argc, char *argv[]) {
    const char * user_name = getenv("USER");
    printf("Hello, %s!\n", user_name);
    return 0;
}
