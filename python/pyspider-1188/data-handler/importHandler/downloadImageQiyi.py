#!/usr/bin/python
## -*- encoding: utf-8 -*-
import re, datetime, urllib, os, threading, time, random, errno, MySQLdb, math, logger, logging
from urlparse import urljoin, urlparse, urlunparse, urlsplit, urlunsplit

myLogger = logging.getLogger('v1188ys.download.image_qiyi')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise exc

def downloadImage(url):
    #start_time = time.time()
    baseDir = "/home/jason/shared/image-qiyi"
    #baseDir = "/root/image"
    parsed = urlparse(url)
    path = parsed[2]
    fullPath = baseDir+path
    fullDir = os.path.dirname(fullPath)
    if not os.path.exists(fullDir):
        mkdir_p(fullDir)

    fileExists = os.path.exists(fullPath)
    try:
        if not fileExists:
            result = urllib.urlretrieve(url, fullPath)
            #print "execution time: %f s" % (time.time()-start_time) 
    except IOError, e:
        myLogger.error("io error: %s, url: %s" % (e,url))
    except Exception, e:
        raise e

# url = "http://img3.2345.com/dianyingimg/zongyi/img/f/5/sup15012_223x310.jpg?1419516249"

# def printTime(name):
#     for x in xrange(1,3):
#         print "Thread %s : time is %s" % (name, time.ctime(time.time()))
#         time.sleep(random.random())

# threads = []
# for x in xrange(1,100):
#     if len(threads)>10:
#         for t in threads:
#             t.join()
#         del threads[:] # empty the list
#     t1 = threading.Thread(target = printTime, args=("No%d" % (x),) )
#     threads.append(t1)
#     t1.start()


def partitionDownload(fetchResult):
    for x in fetchResult:
        small = x[0]
        downloadImage(small)
    #     if x[1]%100 == 0:
    #         print "printing id %d" % (x[1])
    # print "time: %f s" % (time.time()) 


def start():
    pass
    start_time = time.time()
    threads = []
    limit  =1000.0
    workerNum = 10
    try:
        db = MySQLdb.connect('172.16.1.19', 'test', 'test', '1188test')
        cursor = db.cursor()
        cursor.execute("SELECT count(1) from variety_source where api_name='qiyi'")
        rowCount = cursor.fetchone()[0]
        #print 'total row count is %d' % (rowCount,)
        runtimes = math.ceil(rowCount/limit)
        for x in xrange(0, int(runtimes)):
            while True:
                #if not alive, delete it
                for t in threads:
                    if not t.isAlive():
                        threads.remove(t)
                # if <10, then go to get more from DB 
                if len(threads) < workerNum:
                    #print 'current threads num is %d' % (len(threads),)
                    break
                #sleep for 1s, waiting for the next check
                time.sleep(1)

            sql = "SELECT small_image, id from variety_source where api_name='qiyi' limit %d, %d" % (int(x*limit ), int(limit))
            cursor.execute(sql)
            result = cursor.fetchall()
            #if result is empty?
            if len(result) == 0:
                #print 'result is empty, ready to exit main process'
                break 
            t1 = threading.Thread(target = partitionDownload, args=(result,) )
            threads.append(t1)
            t1.start()
    except Exception, e:
        myLogger.error(e)

