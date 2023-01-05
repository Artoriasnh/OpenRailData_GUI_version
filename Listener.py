import stomp
import json


class Listener_(stomp.ConnectionListener):
    _mq: stomp.Connection

    def __init__(self, msg_to_sql, mq: stomp.Connection, durable=False):
        self._mq = mq
        self.is_durable = durable
        self.mts = msg_to_sql

    def on_message(self, frame):
        pass

    def on_error(self, frame):
        print('received an error {}'.format(frame.body))

    def on_disconnected(self):
        print('disconnected')


class TD_Listener(Listener_):
    def __init__(self, msg_to_sql,mq: stomp.Connection,msg_print,sts):
        self.msg_print = msg_print
        self.sts = sts
        self._mq = mq
        super().__init__(msg_to_sql,mq)

    def on_message(self, frame):
        headers, message_raw = frame.headers, frame.body
        parsed_body = json.loads(message_raw)

        if self.sts:
            if self.mts.area_id == 'Derby':
                self.mts.insert_td_DY_frame(parsed_body,self.msg_print)
            else:
                self.mts.print_td(parsed_body)
                self.mts.insert_td_frame(parsed_body)
        else:
            if self.msg_print:
                if self.mts.area_id == 'Derby':
                    self.mts.print_td_DY(parsed_body)
                else:
                    self.mts.print_td(parsed_body)



class TM_MVT_Listener(Listener_):
    def __init__(self, msg_to_sql, mq: stomp.Connection, msg_print, sts):
        self.msg_print = msg_print
        self.sts = sts
        super().__init__(msg_to_sql,mq)

    def on_message(self, frame):
        headers, message_raw = frame.headers, frame.body
        parsed_body = json.loads(message_raw)

        if self.sts:
            if self.msg_print:
                self.mts.print_MVT_msg(parsed_body)
                self.mts.insert_MVT_frame(parsed_body)
                print('MVT_data saving to sql .........')
            else:
                self.mts.insert_MVT_frame(parsed_body)
                print('MVT_data saving to sql .........')

        else:
            if self.msg_print:
                self.mts.print_MVT_msg(parsed_body)




class VSTP_Listener(Listener_):
    def __init__(self, msg_to_sql, mq: stomp.Connection, msg_print, sts):
        self.msg_print = msg_print
        self.sts = sts
        super().__init__(msg_to_sql,mq)

    def on_message(self, frame):
        headers, message_raw = frame.headers, frame.body
        parsed_body = json.loads(message_raw)

        if self.sts:
            if self.msg_print:
                self.mts.print_VSTP_msg(parsed_body)
                self.mts.insert_VSTP_frame(parsed_body)
                print('VSTP_data saving to sql .........')
            else:
                self.mts.insert_VSTP_frame(parsed_body)
                print('VSTP_data saving to sql .........')

        else:
            if self.msg_print:
                self.mts.print_VSTP_msg(parsed_body)


class RTPPM_Listener(Listener_):
    def __init__(self, msg_to_sql, mq: stomp.Connection, msg_print, sts):
        self.msg_print = msg_print
        self.sts = sts
        super().__init__(msg_to_sql,mq)

    def on_message(self, frame):
        headers, message_raw = frame.headers, frame.body
        parsed_body = json.loads(message_raw)

        if self.sts:
            if self.msg_print:
                self.mts.print_RTPPM_msg(parsed_body)
                self.mts.insert_RTPPM_frame(parsed_body)
                print('RTPPM_data saving to sql .........')
            else:
                self.mts.insert_RTPPM_frame(parsed_body)
                print('RTPPM_data saving to sql .........')

        else:
            if self.msg_print:
                self.mts.print_RTPPM_msg(parsed_body)