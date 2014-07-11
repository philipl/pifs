πfs: Never worry about data again!
==================================

πfs is a revolutionary new file system that, instead of wasting space storing
your data on your hard drive, stores your data in π! You'll never run out of
space again - π holds every file that could possibly exist! They said 100%
compression was impossible? You're looking at it!

πfs is dead simple to build:

```sh
./configure
make
make install
```

πfs is dead simple to use:

```sh
πfs -o mdd=<metadata directory> <mountpoint>
```

where the _metadata directory_ is where πfs should store its metadata (such
as filenames or the locations of your files in π) and _mountpoint_ is your
usual filesystem mountpoint.

What does π have to do with my data?
------------------------------------

π (or pi) is one of the most important constants in mathematics and has a
variety of interesting properties (which you can read about at [wikipedia](http://en.wikipedia.org/wiki/Pi))

One of the properties that π is conjectured to have is that it is _normal_,
which is to say that its digits are all distributed evenly, with the
implication that it is a _disjunctive sequence_, meaning that all possible
finite sequences of digits will be present somewhere in it. If we consider
π in base 16 (hexadecimal) , it is trivial to see that if this conjecture
is true, then all possible finite files must exist within π. The first
record of this observation dates back to [2001](http://www.netfunny.com/rhf/jokes/01/Jun/pi.html).

From here, it is a small leap to see that if π contains all possible files,
why are we wasting exabytes of space storing those files, when we could just
look them up in π!

Every file that could possibly exist?
-------------------------------------

That's right! Every file you've ever created, or anyone else has created or
will create! Copyright infringement? It's just a few digits of π! They were
always there!

But how do I look up my data in π?
----------------------------------

As long as you know the index into π of your file and its length, its a
simple task to extract the file using the [Bailey–Borwein–Plouffe formula](http://en.wikipedia.org/wiki/BBP-type_formula)
Similarly, you can use the formula to initially find the index of your file

Now, we all know that it can take a while to find a long sequence of digits
in π, so for practical reasons, we should break the files up into smaller
chunks that can be more readily found.

In this implementation, to maximise performance, we consider each individual byte
of the file separately, and look it up in π.

So I've looked up my bytes in π, but how do I remember where they are?
----------------------------------------------------------------------

Well, you've obviously got to write them down somewhere; you could use a piece of
paper, but remember all that storage space we saved by moving our data into π? Why
don't we store our file locations there!?! Even better, the location of our files in
π is metadata and as [we all know](http://datatechnologytoday.wordpress.com/2010/09/07/on-the-importance-of-metadata/)
metadata is becoming more and more important in everything we do. Doesn't it feel
great to have generated so much metadata? Why waste time with old fashioned data
when you can just deal with metadata, and lots of it!

Yeah, but what happens if lose my file locations?
-------------------------------------------------

No problem, the locations are just metadata! Your files are still there, sitting
in π - they're never going away, are they?

Why is this thing so slow? It took me five minutes to store a 400 line text file!
---------------------------------------------------------------------------------

Well, this is just an initial prototype, and don't worry, there's always Moore's law!

Where do we go from here?
-------------------------

There's lots of potential for the future!

* Variable run length search and lookup!
* Arithmetic Coding!
* Parallelizable lookup!
* Cloud based π lookup!
* πfs for Hadoop!

