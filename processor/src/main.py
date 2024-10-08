import os
import pika
import time

def do_work(id):
    print(" [x] Received %r" % id)
    time.sleep(0.25)

def get_work_queue_channel(queue_name):
    work_queue_host = os.environ['WORK_QUEUE_HOST']
    work_queue_port = int(os.environ.get('WORK_QUEUE_PORT', "5672"))
    print("connecting to work queue ", work_queue_host, str(work_queue_port))
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(work_queue_host, work_queue_port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    print("connected to work queue")
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel


def main():

    user = os.environ['JOB_USER']
    pwd = os.environ['JOB_PASS']
    print("credentials:", user, pwd)

    channel=get_work_queue_channel("ids")

    # loop over every message until it's exhausted the work
    method_frame, header_frame, id = channel.basic_get("ids")
    while method_frame:
        print("got id", id)
        channel.basic_ack(method_frame.delivery_tag)
        print("acknowledged", id)
        do_work(id)
        method_frame, header_frame, id = channel.basic_get('ids')

    print("processed all work")

main()