# test

**The project implements 
a service for managing mailing
lists API for administration and obtaining statistics.**

Used tools:

**Python3.10**
**Django4.1.3 (+DRF)**
**Postgresql**
**Celery (+Redis)**


SECRET_KEY='django-insecure-7k595kjux6640w&=p*6+qa_#pc_69nobs+yp7%_irnqx&7-=$-'



1 - Tests written

2 - Prepared by docker-compose

3 - We send a request to a remote server, wait 60 seconds and in
in case of any failure, we will put the sending of the message at the end of the queue after 2 hours, so until the date
end of distribution.


