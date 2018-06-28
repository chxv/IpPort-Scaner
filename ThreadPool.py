from threading import Thread
import threading
from queue import Queue


class ThreadPoolManager():
    """线程池管理器"""
    def __init__(self, thread_num):
        # 初始化参数
        self.work_queue = Queue()
        self.thread_num = thread_num
        self.thread_list = []
        self.__init_threading_pool(self.thread_num)  # 这句应放在最后，先让前面的变量初始化

    def __init_threading_pool(self, thread_num):
        # 初始化线程池，创建指定数量的线程池
        try:
            for i in range(thread_num):
                # thread = HandleThread(self.work_queue)
                # l.append(thread)
                # l[i].start()
                # self.threads = l
                thread = HandleThread(self.work_queue)
                self.thread_list.append(thread)
                self.thread_list[i].start()
                # print(thread.isAlive(), type(thread))

        except Exception as e:
            print("initial thread error:", type(e))

    def add_job(self, func, *args):
        # 将任务放入队列，等待线程池阻塞读取，参数是被执行的函数和函数的参数
        self.work_queue.put((func, args))

    def stop(self):
        pass
    # def wait_all_complete(self):
    #     # print(self.thread_list)
    #     for i in range(len(self.thread_list)):
    #         if self.thread_list[i].isAlive():
    #             print('wait for', self.thread_list[i].name())
    #             # i.join()
    #


class HandleThread(Thread):
    """定义线程类，继承threading.Thread"""
    def __init__(self, work_queue):
        Thread.__init__(self)
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        # 启动线程
        while True:
            try:
                target, args = self.work_queue.get()
                target(*args)  # 执行任务
                self.work_queue.task_done()
            except Exception as e:
                print('error:', type(e), 'target:', target, 'args', args, 'in thread', self.name)


if __name__ == "__main__":
    import socket
    host = ''
    port = 8888
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(3)

    # 创建一个有4个线程的线程池
    thread_pool = ThreadPoolManager(4)

    # 处理http请求，这里简单返回200 hello world
    def handle_request(conn_socket):
        recv_data = conn_socket.recv(1024)
        reply = 'HTTP/1.1 200 OK \r\n\r\n'
        reply += 'hello world'
        print('thread %s is running ' % threading.current_thread().name)
        conn_socket.send(reply)
        conn_socket.close()

    # 循环等待接收客户端请求
    while True:
        # 阻塞等待请求
        conn_socket, addr = s.accept()
        # 一旦有请求了，把socket扔到我们指定处理函数handle_request处理，等待线程池分配线程处理
        thread_pool.add_job(handle_request, *(conn_socket, ))

    s.close()
