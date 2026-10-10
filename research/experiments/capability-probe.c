#include <os/arch/arm64.h>
#include <sys/sysctl.h>
#include <spawn.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
extern char **environ;
int main(int argc, char **argv) {
  int translated=-1; size_t n=sizeof(translated);
  int rc=sysctlbyname("sysctl.proc_translated",&translated,&n,0,0);
  printf("compiled_arch=arm64 page_size=%ld translated_query=%d translated=%d cross_arch_x86_64=%d custom_x18=%d\n",sysconf(_SC_PAGESIZE),rc,translated,os_cross_arch_is_supported(OS_CROSS_ARCH_X86_64),os_custom_x18_abi_enabled());
  if(argc>1) return 0;
  posix_spawnattr_t attr; posix_spawnattr_init(&attr);
  int a=posix_spawnattr_set_4k_page_size_np(&attr);
  printf("set_4k_attribute=%d (%s)\n",a,strerror(a)); fflush(stdout);
  pid_t pid; char *args[]={argv[0],"child",0};
  int s=a?a:posix_spawn(&pid,argv[0],0,&attr,args,environ);
  printf("spawn_4k=%d (%s)\n",s,strerror(s));
  if(!s) { int status; waitpid(pid,&status,0); printf("child_wait_status=%d\n",status); }
  posix_spawnattr_destroy(&attr); return 0;
}
