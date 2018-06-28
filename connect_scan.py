#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import socket


def scan(dst_ip, dst_port, open_port):
    # dst_ip = scan_info[0]
    # dst_port = scan_info[1]
    # open_port = scan_info[2]
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        c.settimeout(1.5)
        c.connect((dst_ip, dst_port))
        c.close()
        print(f'{dst_ip}:{dst_port} connect success')
        open_port.append(f'{dst_ip}:{dst_port}')
        # print(id(open_port), 'value_conn:', open_port)
        return True
    except Exception as e:
        print(f'{dst_ip}:{dst_port} connect failure, error:', type(e))
        return False
    # print('dist ip:', dst_ip, ' dst_port:', dst_port)


if __name__ == "__main__":
    import time
    spend = time.time()
    dst_ip0 = "192.168.0.106"
    dst_port0 = 80
    open_port = []
    scan(dst_ip0, dst_port0, open_port)
    spend = time.time() - spend
    print('消耗时间为', spend)
