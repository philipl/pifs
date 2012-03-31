/*  Copyright (C) 2012 Philip Langdale
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Library General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

#define FUSE_USE_VERSION 26
#include <dirent.h>
#include <errno.h>
#include <libgen.h>
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/statvfs.h>
#include <sys/xattr.h>
#include <unistd.h>
#include <config.h>
#include <fuse/fuse.h>

unsigned char get_byte(int id);

struct options {
  char *mdd;
} options;

/** macro to define options */
#define PIFS_OPT_KEY(t, p, v) { t, offsetof(struct options, p), v }

static struct fuse_opt pifs_opts[] =
{
  PIFS_OPT_KEY("mdd=%s", mdd, 0),
};

#define FULL_PATH(path) \
  char full_path[PATH_MAX]; \
  snprintf(full_path, PATH_MAX, "%s%s", options.mdd, path); \
  printf("full_path: %s\n", full_path);

static int pifs_getattr(const char *path, struct stat *buf)
{
  FULL_PATH(path);
  int ret = lstat(full_path, buf);
  buf->st_size /= 2;
  return ret == -1 ? -errno : ret;
}

static int pifs_readlink(const char *path, char *buf, size_t bufsiz)
{
  FULL_PATH(path);
  int ret = readlink(full_path, buf, bufsiz - 1);
  if (ret == -1) {
    return -errno;
  }

  buf[ret] = '\0';
  return 0;
}

static int pifs_mknod(const char *path, mode_t mode, dev_t dev)
{
  FULL_PATH(path);
  int ret = mknod(full_path, mode, dev);
  return ret == -1 ? -errno : ret;
}

static int pifs_mkdir(const char *path, mode_t mode)
{
  FULL_PATH(path);
  int ret = mkdir(full_path, mode | S_IFDIR);
  return ret == -1 ? -errno : ret;
}

static int pifs_unlink(const char *path)
{
  FULL_PATH(path);
  int ret = unlink(full_path);
  return ret == -1 ? -errno : ret;
}

static int pifs_rmdir(const char *path)
{
  FULL_PATH(path);
  int ret = rmdir(full_path);
  return ret == -1 ? -errno : ret;
}

static int pifs_symlink(const char *oldpath, const char *newpath)
{
  FULL_PATH(newpath);
  int ret = symlink(oldpath, full_path);
  return ret == -1 ? -errno : ret;
}

static int pifs_rename(const char *oldpath, const char *newpath)
{
  FULL_PATH(newpath);
  int ret = rename(oldpath, full_path);
  return ret == -1 ? -errno : ret;
}

static int pifs_link(const char *oldpath, const char *newpath)
{
  FULL_PATH(newpath);
  int ret = link(oldpath, full_path);
  return ret == -1 ? -errno : ret;
}

static int pifs_chmod(const char *path, mode_t mode)
{
  FULL_PATH(path);
  int ret = chmod(full_path, mode);
  return ret == -1 ? -errno : ret;
}

static int pifs_chown(const char *path, uid_t owner, gid_t group)
{
  FULL_PATH(path);
  int ret = chown(full_path, owner, group);
  return ret == -1 ? -errno : ret;
}

static int pifs_truncate(const char *path, off_t length)
{
  FULL_PATH(path);
  int ret = truncate(full_path, length * 2);
  return ret == -1 ? -errno : ret;
}

static int pifs_utime(const char *path, struct utimbuf *times)
{
  FULL_PATH(path);
  int ret = utime(full_path, times);
  return ret == -1 ? -errno : ret;
}

static int pifs_open(const char *path, struct fuse_file_info *info)
{
  FULL_PATH(path);
  int ret = open(full_path, info->flags);
  info->fh = ret;
  return ret == -1 ? -errno : 0;
}

static int pifs_read(const char *path, char *buf, size_t count, off_t offset,
                     struct fuse_file_info *info)
{
  int ret = lseek(info->fh, offset * 2, SEEK_SET);
  if (ret == -1) {
    return -errno;
  }

  for (size_t i = 0; i < count; i++) {
    short index;
    ret = read(info->fh, &index, sizeof index);
    if (ret == -1) {
      return -errno;
    } else if (ret == 0) {
      return i;
    }
    *buf = (char) get_byte(index);
    buf++;
  }

  return count;
}

static int pifs_write(const char *path, const char *buf, size_t count,
                      off_t offset, struct fuse_file_info *info)
{
  int ret = lseek(info->fh, offset * 2, SEEK_SET);
  if (ret == -1) {
    return -errno;
  }

  for (size_t i = 0; i < count; i++) {
    short index;
    for (index = 0; index < SHRT_MAX; index++) {
      if (get_byte(index) == *buf) {
        break;
      }
    }
    ret = write(info->fh, &index, sizeof index);
    if (ret == -1) {
      return -errno;
    }
    buf++;
  }

  return count;
}

static int pifs_statfs(const char *path, struct statvfs *buf)
{
  FULL_PATH(path);
  int ret = statvfs(full_path, buf);
  return ret == -1 ? -errno : ret;
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
  FULL_PATH(path);
  int ret = setxattr(full_path, name, value, size, flags);
  return ret == -1 ? -errno : ret;
}

static int pifs_getxattr(const char *path, const char *name, char *value,
                         size_t size)
{
  FULL_PATH(path);
  int ret = getxattr(full_path, name, value, size);
  return ret == -1 ? -errno : ret;
}

static int pifs_listxattr(const char *path, char *list, size_t size)
{
  FULL_PATH(path);
  int ret = listxattr(full_path, list, size);
  return ret == -1 ? -errno : ret;
}

static int pifs_removexattr(const char *path, const char *name)
{
  FULL_PATH(path);
  int ret = removexattr(full_path, name);
  return ret == -1 ? -errno : ret;
}

static int pifs_opendir(const char *path, struct fuse_file_info *info)
{
  FULL_PATH(path);
  DIR *dir = opendir(full_path);
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
  FULL_PATH(path);
  int ret = access(full_path, mode);
  return ret == -1 ? -errno : ret;
}

static int pifs_create(const char *path, mode_t mode,
                       struct fuse_file_info *info)
{
  FULL_PATH(path);
  int ret = creat(full_path, mode);
  info->fh = ret;
  return ret == -1 ? -errno : 0;
}

static int pifs_ftruncate(const char *path, off_t length,
                          struct fuse_file_info *info)
{
  int ret = ftruncate(info->fh, length * 2);
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
  DIR *dir = opendir(options.mdd);
  if (!dir) {
    return -errno;
  }
  int ret = utimensat(dirfd(dir), basename((char *) path), times, 0);
  closedir(dir);
  return ret == -1 ? -errno : ret;
}

static struct fuse_operations pifs_ops = {
  .getattr = pifs_getattr,
  .readlink = pifs_readlink,
  .mknod = pifs_mknod,
  .mkdir = pifs_mkdir,
  .rmdir = pifs_rmdir,
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
  int ret;
  struct fuse_args args = FUSE_ARGS_INIT(argc, argv);

  memset(&options, 0, sizeof(struct options));
  if (fuse_opt_parse(&args, &options, pifs_opts, NULL) == -1) {
    return -1;
  }

  if (!options.mdd) {
    fprintf(stderr,
            "%s: Metadata directory must be specified with -o mdd=<directory>\n",
            argv[0]);
    return -1;
  }

  if (access(options.mdd, R_OK | W_OK | X_OK) == -1) {
    fprintf(stderr, "%s: Cannot access metadata directory '%s': %s\n",
            argv[0], options.mdd, strerror(errno));
    return -1;
  }

  ret = fuse_main(args.argc, args.argv, &pifs_ops, NULL);
  fuse_opt_free_args(&args);
  return ret;
}
