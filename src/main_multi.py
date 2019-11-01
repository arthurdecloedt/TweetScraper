import multiprocessing
from multiprocessing.pool import Pool

import imageParser
import image_downloader
import json_parser
from queue import *

file_name = "../data/aapl.json"


if __name__ == '__main__':

    manager = multiprocessing.Manager()
    url_queue = manager.Queue(60000)

    proxy_queue = manager.Queue(60000)
    trash_queue = manager.Queue(60000)
    img_queue = manager.Queue(60000)
    pJson = multiprocessing.Process(target=json_parser.get_tweet_queue,args=[file_name,url_queue])

    pJson.start()

    pool = Pool(100)

    # start first url before entering loop
    counter = multiprocessing.Value('i', 0)
    no_meta_c = multiprocessing.Value('i', 0)
    img_c = multiprocessing.Value('i', 0)
    c_lock = multiprocessing.Lock()
    nm_lock = multiprocessing.Lock()
    img_lock = multiprocessing.Lock()
    url = url_queue.get(block=True)
    pool.apply_async(imageParser.enqueue_image_url,(url,img_queue))
    n = 0
    while n < 7000:
        url = url_queue.get(block=True)
        # a new url needs to be processed
        n+=1
        with c_lock:
            counter.value += 1
        ap_as = pool.apply_async(imageParser.enqueue_image_url, (url,))
        if counter.value >= 1000:
            ap_as.get()
            counter.value = 0
            print('scrapes:{0}'.format(str(n)))
    pool.close()
    pJson.terminate()
    pool.join()
