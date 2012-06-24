./manage.py runserver --host 0.0.0.0 --port 8000

Как компилять CSS
-----------------

Тестирование
------------

Под чистым gunicorn
-------------------

### sync worker

CPU 68%
Памяти 10M

Concurrency Level:      10
Time taken for tests:   25.486 seconds
Complete requests:      10000
Failed requests:        0
Write errors:           0
Total transferred:      13660000 bytes
HTML transferred:       12040000 bytes
Requests per second:    392.38 [#/sec] (mean)
Time per request:       25.486 [ms] (mean)
Time per request:       2.549 [ms] (mean, across all concurrent requests)
Transfer rate:          523.42 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       1
Processing:     5   25   1.0     25      35
Waiting:        5   25   1.0     25      34
Total:          6   25   1.0     25      35

-----------------------------------

CPU 65%

Concurrency Level:      100
Time taken for tests:   25.550 seconds
Complete requests:      10000
Failed requests:        0
Write errors:           0
Total transferred:      13660000 bytes
HTML transferred:       12040000 bytes
Requests per second:    391.39 [#/sec] (mean)
Time per request:       255.497 [ms] (mean)
Time per request:       2.555 [ms] (mean, across all concurrent requests)
Transfer rate:          522.11 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.5      0       6
Processing:     4  254  15.1    254     281
Waiting:        4  254  15.1    254     281
Total:         10  254  14.7    254     281


### gevent worker

CPU 78%
Памяти 16M

Concurrency Level:      10
Time taken for tests:   25.857 seconds
Complete requests:      10000
Failed requests:        0
Write errors:           0
Total transferred:      13660000 bytes
HTML transferred:       12040000 bytes
Requests per second:    386.75 [#/sec] (mean)
Time per request:       25.857 [ms] (mean)
Time per request:       2.586 [ms] (mean, across all concurrent requests)
Transfer rate:          515.91 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       1
Processing:    19   26   1.4     26      52
Waiting:       19   26   1.4     25      52
Total:         19   26   1.4     26      53


----------------------------------

CPU 80%

Concurrency Level:      100
Time taken for tests:   26.149 seconds
Complete requests:      10000
Failed requests:        0
Write errors:           0
Total transferred:      13660000 bytes
HTML transferred:       12040000 bytes
Requests per second:    382.43 [#/sec] (mean)
Time per request:       261.488 [ms] (mean)
Time per request:       2.615 [ms] (mean, across all concurrent requests)
Transfer rate:          510.15 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.5      0       7
Processing:    99  260  11.2    260     288
Waiting:       99  260  11.2    260     288
Total:        102  261  10.9    260     288


Под flup + NGINX
----------------

CPU 172%

Concurrency Level:      10
Time taken for tests:   39.323 seconds
Complete requests:      10000
Failed requests:        0
Write errors:           0
Total transferred:      13620000 bytes
HTML transferred:       12040000 bytes
Requests per second:    254.30 [#/sec] (mean)Time per request:       39.323 [ms] (mean)
Time per request:       3.932 [ms] (mean, across all concurrent requests)
Transfer rate:          338.24 [Kbytes/sec] received

Connection Times (ms)              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       5
Processing:    20   39   7.6     39      84
Waiting:       20   39   7.6     38      84
Total:         20   39   7.6     39      84

--------------------------------

CPU 170%

Concurrency Level:      100
Time taken for tests:   41.125 seconds
Complete requests:      10000
Failed requests:        0
Write errors:           0
Total transferred:      13620000 bytes
HTML transferred:       12040000 bytes
Requests per second:    243.16 [#/sec] (mean)
Time per request:       411.248 [ms] (mean)
Time per request:       4.112 [ms] (mean, across all concurrent requests)
Transfer rate:          323.42 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.6      0       9
Processing:    21  409  55.7    399     982
Waiting:       21  409  55.6    399     982
Total:         30  409  55.5    400     982

