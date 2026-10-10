# SPDX-License-Identifier: MIT
#include <os/arch/arm64.h>
#include <sys/sysctl.h>
#include <spawn.h>
#include <sys/wait.h>
#include <mach/mach_traps.h>
#include <pthread.h>
#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

extern char **environ;

struct tso_result
{
    kern_return_t enable;
    kern_return_t disable;
};

static void *probe_tso_on_new_thread(void *arg)
{
    struct tso_result *result = arg;
    result->enable = thread_set_x86_64_compat(1);
    result->disable = result->enable ? -1 : thread_set_x86_64_compat(0);
    return NULL;
}

static void report(const char *mode, int spawnattr_result, int spawn_result,
                   int child_exit, int child_signal)
{
    int translated = -1;
    size_t translated_size = sizeof(translated);
    int translated_result = sysctlbyname("sysctl.proc_translated", &translated,
                                         &translated_size, NULL, 0);

    printf("{\"mode\":\"%s\",\"pid\":%ld,\"compiled_arch\":\"arm64\","
           "\"page_size\":%ld,\"translated_query_rc\":%d,"
           "\"translated_value\":%d,\"cross_arch_x86_64\":%s,"
           "\"custom_x18_enabled\":%s,\"spawnattr_4k_rc\":%d,"
           "\"spawn_4k_rc\":%d,\"child_exit\":%d,"
           "\"child_signal\":%d}\n",
           mode, (long)getpid(), sysconf(_SC_PAGESIZE), translated_result,
           translated,
           os_cross_arch_is_supported(OS_CROSS_ARCH_X86_64) ? "true" : "false",
           os_custom_x18_abi_enabled() ? "true" : "false",
           spawnattr_result, spawn_result, child_exit, child_signal);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "--probe-child"))
    {
        report("4k_child", -1, -1, -1, -1);
        return 0;
    }

    posix_spawnattr_t attr;
    int attr_rc = posix_spawnattr_init(&attr);
    if (attr_rc)
    {
        report("parent", attr_rc, -1, -1, -1);
        return 0;
    }

    int set_4k_rc = posix_spawnattr_set_4k_page_size_np(&attr);
    pid_t child_pid = -1;
    char *child_argv[] = { argv[0], "--probe-child", NULL };
    int spawn_rc = set_4k_rc ? set_4k_rc :
        posix_spawn(&child_pid, argv[0], NULL, &attr, child_argv, environ);
    int child_exit = -1;
    int child_signal = -1;

    if (!spawn_rc)
    {
        int status;
        if (waitpid(child_pid, &status, 0) >= 0)
        {
            if (WIFEXITED(status)) child_exit = WEXITSTATUS(status);
            if (WIFSIGNALED(status)) child_signal = WTERMSIG(status);
        }
    }

    posix_spawnattr_destroy(&attr);
    report("parent", set_4k_rc, spawn_rc, child_exit, child_signal);

    if (argc > 1 && !strcmp(argv[1], "--test-x18-transitions"))
    {
        os_set_custom_x18_abi_enabled(true);
        int entered = os_custom_x18_abi_enabled();
        os_set_custom_x18_abi_enabled(false);
        int returned = !os_custom_x18_abi_enabled();
        printf("{\"mode\":\"x18_transitions\",\"entered_custom_mode\":%s,"
               "\"returned_to_macos_mode\":%s}\n",
               entered ? "true" : "false", returned ? "true" : "false");
        fflush(stdout);
    }

    if (argc > 1 && !strcmp(argv[1], "--test-tso"))
    {
        kern_return_t current_enable = thread_set_x86_64_compat(1);
        kern_return_t current_disable = current_enable ? -1 : thread_set_x86_64_compat(0);
        struct tso_result worker = { -1, -1 };
        pthread_t thread;
        int thread_create = pthread_create(&thread, NULL, probe_tso_on_new_thread, &worker);
        int thread_join = thread_create ? -1 : pthread_join(thread, NULL);
        printf("{\"mode\":\"tso_api\",\"current_thread_enable\":%d,"
               "\"current_thread_disable\":%d,\"worker_create\":%d,"
               "\"worker_enable\":%d,\"worker_disable\":%d,"
               "\"worker_join\":%d}\n",
               current_enable, current_disable, thread_create,
               worker.enable, worker.disable, thread_join);
        fflush(stdout);
    }

    return 0;
}
