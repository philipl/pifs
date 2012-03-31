AC_INIT([πFS], [1.0], [philipl@overt.org], [πfs])
AC_CONFIG_AUX_DIR(build)
AC_CONFIG_SRCDIR(src/πfs.c)
AM_CONFIG_HEADER(config.h)
AM_INIT_AUTOMAKE

# Checks for programs
AC_PROG_CC_C99

# Set language to C
AC_LANG_C

# Checks for header files
AC_HEADER_DIRENT
AC_HEADER_STDC

PKG_CHECK_MODULES([FUSE], [fuse >= 2.8])

AC_SUBST([EXTRA_CFLAGS], ["-Wall -Werror -Wextra -Wno-unused-parameter"])

AC_CONFIG_FILES([Makefile
 src/Makefile
 ])
AC_OUTPUT
