import stomp
import time
import threading

class get_data(threading.Thread):
    def __init__(self,
                 mts,
                 username,
                 password,
                 topic,
                 listener,
                 msg_print,
                 sts,
                 isdurable
                 ):

        super().__init__()
        self.mts = mts
        self.username = username
        self.password = password
        self.topic = topic
        self.listener = listener
        self.msg_print = msg_print
        self.sts = sts
        self.isdurable = isdurable

    def connect_open_rail_feed(self):
        if self.isdurable:
            connection = stomp.Connection([('localhost', 61613)], keepalive=True, heartbeats=(5000, 5000))
        else:
            connection = stomp.Connection([('datafeeds.networkrail.co.uk', 61618)], keepalive=True, heartbeats=(5000, 5000))
        connection.set_listener('', self.listener(self.mts, connection, self.msg_print,self.sts))

        connect_headers = {
            "username": self.username,
            "passcode": self.password,
            "wait": True,
        }
        connection.connect(**connect_headers)

        # Connect to feed
        subscribe_headers = {"destination": self.topic, "id": 1, "ack": "auto"}
        connection.subscribe(**subscribe_headers)

        return connection

    def run(self):
        conn = self.connect_open_rail_feed()

        while True:
            try:
                time.sleep(1)
                if not conn.is_connected():
                    print('re________________link')
                    print('re________________link')
                    print('re________________link')
                    conn = self.connect_open_rail_feed()
            except KeyboardInterrupt:
                break

        self.mts.close()
        conn.disconnect()



