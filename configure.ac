AC_INIT([piFS], [1.0], [philipl@overt.org], [pifs])
AC_CONFIG_AUX_DIR(build)
AC_CONFIG_SRCDIR(src/pifs.c)
AM_CONFIG_HEADER(config.h)
AM_INIT_AUTOMAKE

# Checks for programs
AC_PROG_CC

# Set language to C++
AC_LANG_C

# Checks for header files
AC_HEADER_DIRENT
AC_HEADER_STDC
AC_CHECK_HEADERS([fcntl.h string.h unistd.h])

PKG_CHECK_MODULES([FUSE], [fuse >= 2.8])

# Checks for typedefs, structures, and compiler characteristics
AC_HEADER_STDBOOL
AC_C_CONST
AC_TYPE_UID_T
AC_C_INLINE
AC_TYPE_MODE_T
AC_TYPE_OFF_T
AC_TYPE_SIZE_T

# Check for functions
AC_FUNC_CLOSEDIR_VOID
AC_FUNC_LSTAT
AC_FUNC_LSTAT_FOLLOWS_SLASHED_SYMLINK
AC_FUNC_UTIME_NULL
AC_CHECK_FUNCS([fchdir fdatasync fork ftruncate lchown memset mkdir mkfifo rmdir setxattr strdup strerror utime])

AC_CONFIG_FILES([Makefile
 src/Makefile
 ])
AC_OUTPUT
