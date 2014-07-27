/*  
    This program implements the BBP algorithm to generate a few hexadecimal
    digits beginning immediately after a given position id, or in other words
    beginning at position id + 1.  On most systems using IEEE 64-bit floating-
    point arithmetic, this code works correctly so long as d is less than
    approximately 1.18 x 10^7.  If 80-bit arithmetic can be employed, this limit
    is significantly higher.  Whatever arithmetic is used, results for a given
    position id can be checked by repeating with id-1 or id+1, and verifying 
    that the hex digits perfectly overlap with an offset of one, except possibly
    for a few trailing digits.  The resulting fractions are typically accurate 
    to at least 11 decimal digits, and to at least 9 hex digits.  
*/

/*  David H. Bailey     2006-09-08 */

#include <stdio.h>
#include <math.h>
#include <limits.h>

static double expm (double p, double ak, int i, double pt)

/*  expm = 16^p mod ak.  This routine uses the left-to-right binary 
    exponentiation scheme. */

{
  int j;
  double r;

  r = 1.;

/*  Perform binary exponentiation algorithm modulo ak. */

  for (j = 1; j <= i; j++){
    if (p >= pt){
      r = 16. * r;
      r = r - (int) (r / ak) * ak;
      p = p - pt;
    }
    pt = 0.5 * pt;
    if (pt >= 1.){
      r = r * r;
      r = r - (int) (r / ak) * ak;
    }
  }

  return r;
}

static double series (int m, int id, int i, double pt)

/*  This routine evaluates the series  sum_k 16^(id-k)/(8*k+m) 
    using the modular exponentiation technique. */

{
  int k;
  double ak, p, s, t;
#define eps 1e-17

  s = 0.;

/*  Sum the series up to id. */

  for (k = 0; k < id; k++){
    ak = 8 * k + m;
    if ((int) ak == 1) continue;
    p = id - k;
    if(! ((int) pt & (int) p)){
      i--;
      pt = 1 << (i - 1);
    }
    t = expm (p, ak, i, pt);
    s = s + t / ak;
    s = s - (int) s;
  }

/*  Compute a few terms where k >= id. */

  for (k = id; k <= id + 100; k++){
    ak = 8 * k + m;
    t = pow (16., (double) (id - k)) / ak;
    if (t < eps) break;
    s = s + t;
    s = s - (int) s;
  }
  return s;
}

unsigned char get_byte(int id)
{
  int id_pow2;
  double id_val2;

  #if defined(__GNUC__)
    id_pow2 = CHAR_BIT * sizeof (int) - __builtin_clz (id);
  #else
    {
      int tid = id;
      id_pow2 = 1;
      while (tid >>= 1) id_pow2++;
    }
  #endif
  id_val2 = 1 << (id_pow2 - 1);

  double s1 = series (1, id, id_pow2, id_val2);
  double s2 = series (4, id, id_pow2, id_val2);
  double s3 = series (5, id, id_pow2, id_val2);
  double s4 = series (6, id, id_pow2, id_val2);
  double pid = 4. * s1 - 2. * s2 - s3 - s4;
  pid = pid - (int) pid + 1.;

  double y = fabs(pid);
  y = 16. * (y - floor (y));
  unsigned char first = y;
  y = 16. * (y - floor (y));
  unsigned char second = y;
  return (first << 4) | second;
}


