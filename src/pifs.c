#define FUSE_USE_VERSION 26
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <config.h>
#include <fuse/fuse.h>

static int pifs_getattr(const char *path, struct stat *buf)
{
  int ret = stat(path, buf);
  return ret == -1 ? -errno : ret;
}

static int pifs_readlink(const char *path, char *buf, size_t bufsiz)
{
  int ret = readlink(path, buf, bufsiz);
  return ret == -1 ? -errno : ret;
}

static int pifs_mknod(const char *path, mode_t mode, dev_t dev)
{
  int ret = mknod(path, mode, dev);
  return ret == -1 ? -errno : ret;
}

static int pifs_mkdir(const char *path, mode_t mode)
{
  int ret = mkdir(path, mode | S_IFDIR);
  return ret == -1 ? -errno : ret;
}

static int pifs_unlink(const char *path)
{
  int ret = unlink(path);
  return ret == -1 ? -errno : ret;
}

static int pifs_rmdir(const char *path)
{
  int ret = rmdir(path);
  return ret == -1 ? -errno : ret;
}

static int pifs_symlink(const char *oldpath, const char *newpath)
{
  int ret = symlink(oldpath, newpath);
  return ret == -1 ? -errno : ret;
}

static int pifs_rename(const char *oldpath, const char *newpath)
{
  int ret = rename(oldpath, newpath);
  return ret == -1 ? -errno : ret;
}

static int pifs_link(const char *oldpath, const char *newpath)
{
  int ret = link(oldpath, newpath);
  return ret == -1 ? -errno : ret;
}

static int pifs_chmod(const char *path, mode_t mode)
{
  int ret = chmod(path, mode);
  return ret == -1 ? -errno : ret;
}

static int pifs_chown(const char *path, uid_t owner, gid_t group)
{
  int ret = chown(path, owner, group);
  return ret == -1 ? -errno : ret;
}

static int pifs_truncate(const char *path, off_t length)
{
  int ret = truncate(path, length);
  return ret == -1 ? -errno : ret;
}

static int pifs_utime(const char *path, struct utimbuf *times)
{
  int ret = utime(path, times);
  return ret == -1 ? -errno : ret;
}

static int pifs_open(const char *path, struct fuse_file_info *info)
{
  int ret = open(path, info->flags);
  info->fh = ret;
  return ret == -1 ? -errno : 0;
}

static int pifs_read(const char *path, char *buf, size_t count, off_t offset,
                     struct fuse_file_info *info)
{
  int ret = lseek(info->fh, offset, SEEK_SET);
  if (ret == -1) {
    return -errno;
  }

  ret = read(info->fh, buf, count);
  return ret == -1 ? -errno : ret;
}

static int pifs_write(const char *path, const char *buf, size_t count,
                      off_t offset, struct fuse_file_info *info)
{
  int ret = lseek(info->fh, offset, SEEK_SET);
  if (ret == -1) {
    return -errno;
  }

  ret = write(info->fh, buf, count);
  return ret == -1 ? -errno : ret;
}

static int pifs_statfs(const char *path, struct statvfs *buf)
{
  int ret = statfs(path, buf);
  return ret == -1 ? -errno : ret;
}

static int pifs_flush(const char *path, struct fuse_file_info *info)
{
  return 0;
}

static int pifs_release(const char *path, struct fuse_file_info *info)
{
  int ret = close(info->fh);
  return ret == -1 ? -errno : ret;
}

static int pifs_fsync(const char *path, int datasync,
                      struct fuse_file_info *info)
{
  int ret = datasync ? fdatasync(info->fh) : fsync(info->fh);
  return ret == -1 ? -errno : ret;
}

static int pifs_setxattr(const char *path, const char *name, const char *value,
                         size_t size, int flags)
{
  int ret = setxattr(path, name, value, size, flags);
  return ret == -1 ? -errno : ret;
}

static int pifs_getxattr(const char *path, const char *name, char *value,
                         size_t size)
{
  int ret = getxattr(path, name, value, size);
  return ret == -1 ? -errno : ret;
}

static int pifs_listxattr(const char *path, char *list, size_t size)
{
  int ret = listxattr(path, list, size);
  return ret == -1 ? -errno : ret;
}

static int pifs_removexattr(const char *path, const char *name)
{
  int ret = removexattr(path, name);
  return ret == -1 ? -errno : ret;
}

static int pifs_opendir(const char *path, struct fuse_file_info *info)
{
  DIR *dir = opendir(path);
  info->fh = (uint64_t) dir;
  return !dir ? -errno : 0;
}

static int pifs_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
                       off_t offset, struct fuse_file_info *info)
{
  DIR *dir = (DIR *) info->fh;
  if (offset) {
    seekdir(dir, offset);
  }

  int ret;
  do {
    errno = 0;
    struct dirent *de = readdir(dir);
    if (!de) { 
      if (errno) {
        return -errno;
      } else {
        break;
      }
    }

    ret = filler(buf, de->d_name, NULL, de->d_off);
  } while (ret == 0);

  return 0;
}

static int pifs_releasedir(const char *path, struct fuse_file_info *info)
{
  int ret = closedir((DIR *)info->fh);
  return ret == -1 ? -errno : ret;
}

static int pifs_fsyncdir(const char *path, int datasync,
                         struct fuse_file_info *info)
{
  int fd = dirfd((DIR *)info->fh);
  if (fd == -1) {
    return -errno;
  }

  int ret = datasync ? fdatasync(fd) : fsync(fd);
  return ret == -1 ? -errno : ret;
}

static int pifs_access(const char *path, int mode)
{
  int ret = access(path, mode);
  return ret == -1 ? -errno : ret;
}

static int pifs_create(const char *path, mode_t mode,
                       struct fuse_file_info *info)
{
  int ret = creat(path, mode);
  info->fh = ret;
  return ret == -1 ? -errno : 0;
}

static int pifs_ftruncate(const char *path, off_t length,
                          struct fuse_file_info *info)
{
  int ret = ftruncate(info->fh, length);
  return ret == -1 ? -errno : ret;
}

static int pifs_fgetattr(const char *path, struct stat *buf,
                        struct fuse_file_info *info)
{
  int ret = fstat(info->fh, buf);
  return ret == -1 ? -errno : ret;
}

static int pifs_lock(const char *path, struct fuse_file_info *info, int cmd,
                     struct flock *lock)
{
  int ret = fcntl(info->fh, cmd, lock);
  return ret == -1 ? -errno : ret;
}

static int pifs_utimens(const char *path, const struct timespec times[2])
{
  int ret = utimensat(0, path, times, 0);
  return ret == -1 ? -errno : ret;
}

static struct fuse_operations pifs_ops = {
  .getattr = pifs_getattr,
  .readlink = pifs_readlink,
  .mknod = pifs_mknod,
  .mkdir = pifs_mkdir,
  .unlink = pifs_unlink,
  .symlink = pifs_symlink,
  .rename = pifs_rename,
  .link = pifs_link,
  .chmod = pifs_chmod,
  .chown = pifs_chown,
  .truncate = pifs_truncate,
  .utime = pifs_utime,
  .open = pifs_open,
  .read = pifs_read,
  .write = pifs_write,
  .statfs = pifs_statfs,
  .flush = pifs_flush,
  .release = pifs_release,
  .fsync = pifs_fsync,
  .setxattr = pifs_setxattr,
  .getxattr = pifs_getxattr,
  .listxattr = pifs_listxattr,
  .removexattr = pifs_removexattr,
  .opendir = pifs_opendir,
  .readdir = pifs_readdir,
  .releasedir = pifs_releasedir,
  .fsyncdir = pifs_fsyncdir,
  .access = pifs_access,
  .create = pifs_create,
  .ftruncate = pifs_ftruncate,
  .fgetattr = pifs_fgetattr,
  .lock = pifs_lock,
  .utimens = pifs_utimens,
  .flag_nullpath_ok = 1,
};

int main (int argc, char *argv[])
{
  return fuse_main(argc, argv, &pifs_ops, NULL);
}
