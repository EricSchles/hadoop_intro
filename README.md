#Intro

The hadoop framework is a powerful tool for processing large amounts of data.  By making use of Hadoop we can scale our resources exponentially, rather than linearly.  In other words, every time you add another computer to your cluster, you get more than the power of the first computer in computational resources.  So let's say you start with one computer, and you are trying to computer all the primes less than a billion.  By adding a second computer, you'd get there more than twice as fast!  In order to understand this framework, we'll need to understand the underlying design pattern first: MapReduce.  

##MapReduce In Python

The MapReduce pattern is actually quiet simple.  Below are examples of map and reduce in python, as well as their function definitions.

###Map
```
def f(x):
	return x*x

print map(f,[1,2,3]) # result is [1,4,9]
```

So the map function applies the function f, to each element in the list.

Here we see it's implementation:

```
def mapper(f,listing):
	return [f(elem) for elem in listing]
```

In general we may think of the mapping step as the transformation step, preparing or processing our data, one element at a time.

###Reduce
```
def g(x,y):
	return x+y
print reduce(g,[1,2,3]) # result is 6
```

So the reduce function applies the function g, to each element in the list in succession, accumulating them down to a single element.

Here we see it's implementation:

```
def reducer(g,listing):
     accumulation = 0
     for i in listing:
             accumulation = f(accumulation,i)
     return accumulation
```

In general we may think of the reducing step as the accumulation step, joining together all the processed information.

##A worked example

Say we want to know the frequency of a given word across several pieces of text.  We can use MapReduce to first count all the occurrences of the words across the texts, and then reduce them down to find the total count.

example.py:
```
from glob import glob

def word_freq(text):
    return text.count("the")

def word_count(current,new):
    return current+new

books = glob("books/*")
book_text = [open(book,"r").read() for book in books]

print reduce(word_count,map(word_freq,book_text))
```

Notice how we structured the code - in the map step we transformed the data, in this case from text to a number; then in the reduce step we added all the numbers up.

You may be thinking to yourself.  Okay, so what?  I don't need MapReduce to do all that.  Well, if you are trying to do this across multiple machines, you absolutely do.  

##Understanding Hadoop

Now that we understand the basics of the underlying algorithm, how do we understand Hadoop?  Notice that we are dealing with an array of values, where the same operation is happening to all of them.  Let's say we had two computers now, how might we make use of MapReduce and Hadoop to do the same thing?

In a simplified way, here's what happens:

Say we have the following data:

`arr = [1,2,3,4,5,6]`

We have the following map:

```
def f(x):
	return x*x
```

And we have the following reduce:

```
def g(x,y):
	return x+y
```

What happens first is, the data is split across the two machines.  Since there are 6 elements, the first three go to machine one, and the second three go to machine two.  Then the map function is applied, in both machines.  Then the results would be sent to a single machine (in this case) and the reduce step would be used to combine all the results.

Now say we had 20 machines and 1 million elements in our array, but the map and reduce steps stay the same.  Now 1,000,000/20 is 50,000.  So each server will get that many.  Next in the reduce step we send pairs of 50,000 element arrays to a single machine.  So we move from computing on 20 machines to 10 machines, combining to arrays of 100,000 elements.  Then we combine all 100,000 array pairs on 5 machines, and so on and so forth, until we get down to one final number on one machine.  

Please note, this was a worked example and probably not terribly efficient.  There is a lot of work that goes into tunning Hadoop clusters so that they act optimally on data.  The simple scheme I worked out above, is simply to explain how one _could_ do things with Hadoop.

##Building your own cluster

Now that we know, approximately, how to use hadoop and MapReduce, we are finally in a position to install our own cluster!  

These instructions require OSX or Linux (preferred).  Hadoop will not work on windows.  But fortunately, VMware (or virtual box) and ubuntu are easy to install :)

Installation:

First we run the following setup commands (these are all the prerequistes):

```
 sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9

sudo sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"

sudo apt-get update

sudo apt-get install lxc lxc-docker
```

Next we'll create a docker group:

```
$ sudo groupadd docker
$ sudo usermod -a -G docker $USER
```

Now we are in a place to install ferry:

```
sudo pip install -U ferry
export FERRY_DIR=/var/lib/ferry
ferry-dust install
```

Finally, run:

```
ferry-dust start
sudo ferry server
ferry info
```

To quit run:

`sudo ferry quit`

##Getting started with Hadoop

Now that we have our very own Hadoop cluster (albeit on one machine) we are ready to start using hadoop.

You begin by starting up ferry:

`sudo ferry server`

Then you'll start hadoop:

`ferry start hadoop`

Notice the returned value (it should be sa-[some number].  Copy paste this number, you'll need it (and the sa part).

Now we wait for our hadoop cluster to be built (exciting).  We can check the progress of this with:

`ferry ps`

Once the hadoop cluster is up and running, simply type:

`sudo ferry ssh sa-[some number]` (the docs are wrong here)

This will allow you to ssh into your Hadoop instance (exciting).

Next we type:

```
su ferry
source /etc/profile
```

##Running our first real hadoop example

mapper.py:

```
import sys

# input comes from STDIN (standard input)
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()
    # split the line into words
    words = line.split()
    # increase counters
    for word in words:
        # write the results to STDOUT (standard output);
        # what we output here will be the input for the
        # Reduce step, i.e. the input for reducer.py
        #
        # tab-delimited; the trivial word count is 1
        print '%s\t%s' % (word, 1)
```

Please make sure mapper.py has execute permissions:

`chmod +x mapper.py`

reducer.py:

```
from operator import itemgetter
import sys

current_word = None
current_count = 0
word = None

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    word, count = line.split('\t', 1)

    # convert count (currently a string) to int
    try:
        count = int(count)
    except ValueError:
        # count was not a number, so silently
        # ignore/discard this line
        continue

    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_word == word:
        current_count += count
    else:
        if current_word:
            # write result to STDOUT
            print '%s\t%s' % (current_word, current_count)
        current_count = count
        current_word = word

# do not forget to output the last word if needed!
if current_word == word:
    print '%s\t%s' % (current_word, current_count)
```

also, this code will need to be able to execute:

`chmod +x reducer.py`

Running the code on Hadoop:
```
bin/hadoop jar contrib/streaming/hadoop-*streaming*.jar \
-file /home/hduser/mapper.py    -mapper /home/hduser/mapper.py \
-file /home/hduser/reducer.py   -reducer /home/hduser/reducer.py \
-input /user/hduser/gutenberg/* -output /user/hduser/gutenberg-output
```

##Alternative installation

[installing Hadoop 2.6 on ubuntu](http://www.bogotobogo.com/Hadoop/BigData_hadoop_Install_on_ubuntu_single_node_cluster.php)
[installing Hadoop 2.4 on ubuntu](http://dogdogfish.com/2014/04/26/installing-hadoop-2-4-on-ubuntu-14-04/)
##References:

* [How Hadoop works](https://www.cs.duke.edu/courses/fall11/cps216/Lectures/how_hadoop_works.pdf)
* [Setting up Ferry](http://ferry.opencore.io/en/latest/install/client.html)
* [Hadoop and Ferry](http://ferry.opencore.io/en/latest/examples/hadoop.html)
* [Hadoop and Python](http://www.michael-noll.com/tutorials/writing-an-hadoop-mapreduce-program-in-python/)
