import psycopg2 as pg
from datetime import datetime
from pytz import timezone
from MSG import TD
from SOP_con.DY_SOP import DY_SOP
from SOP_con.DY_state_container import DY_state_container
from SOP_con.DY_address_update_state_container import DY_address_update_state_container
import re

TIMEZONE_LONDON: timezone = timezone("Europe/London")
state_container = DY_state_container
address_update_state_container = DY_address_update_state_container


class msg_to_sql(object):

    def __init__(self,
                 schema_name,
                 data_type,
                 database_name,
                 sql_username,
                 sql_password,
                 sql_host,
                 port,
                 table_format,
                 ):

        self.schema_name = schema_name
        self.data_type = data_type
        self.table_format = table_format
        self.conn = pg.connect(database=database_name, user=sql_username, password=sql_password, host=sql_host,
                               port=port)
        print("database connect successful")
        self.dbTable = '"{}"."{}"'.format(self.schema_name, self.data_type)
        self.cur = self.conn.cursor()
        self.cur.connection.commit()

    def creat_table(self):

        self.conn.rollback()
        self.cur.execute('create table if not exists {} ()'.format(self.dbTable))
        self.conn.commit()

        for col in self.table_format:
            self.conn.rollback()
            self.cur.execute(
                'alter table {} add column if not exists {} {}'.format(self.dbTable, col, self.table_format[col]))
            self.conn.commit()

    def set_timestamp(self, time_message):
        timestamp = time_message / 1000
        utc_datetime = datetime.utcfromtimestamp(timestamp)
        uk_datetime = TIMEZONE_LONDON.fromutc(utc_datetime)
        return uk_datetime

    def dic_flatten(self, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            try:
                items.extend(self.dic_flatten(v, new_key, sep=sep).items())
            except:
                items.append((new_key, v))
        return dict(items)

    def close(self):
        self.conn.close()


class TD_msg(msg_to_sql):
    def __init__(self, schema_name, data_type, database_name, sql_username, sql_password, sql_host, port, table_format,
                 area_id):
        self.area_id = area_id
        super().__init__(schema_name, data_type, database_name, sql_username, sql_password, sql_host, port,
                         table_format)

    def insert_data(self, data):
        if data["time"].isdigit() != True:
            pass
        else:
            uk_datetime = self.set_timestamp(int(data["time"]))
            data["time"] = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")

        replace_dict = {'to': "to_berth", "from": "from_berth"}
        new_data = [replace_dict[i] if i in replace_dict else i for i in list(data.keys())]
        col = ','.join(new_data)
        val = tuple(data.values())
        self.conn.rollback()
        self.cur.execute("insert into {} ({}) VALUES{}".format(self.dbTable, col, val))
        self.conn.commit()

    def insert_td_frame(self, parsed_body):
        self.creat_table()
        for outer_message in parsed_body:
            message = list(outer_message.values())[0]
            area_id = message["area_id"]
            message_type = message["msg_type"]
            if area_id == 'DY':
                if message["time"].isdigit() != True:
                    pass
                else:
                    uk_datetime = self.set_timestamp(int(message["time"]))
                    message["time"] = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")

                replace_dict = {'to': "to_berth", "from": "from_berth"}
                new_data = [replace_dict[i] if i in replace_dict else i for i in list(message.keys())]
                col = ','.join(new_data)
                val = tuple(message.values())
                self.conn.rollback()
                self.cur.execute("insert into {} ({}) VALUES{}".format(self.dbTable, col, val))
                self.conn.commit()
            print('TD_data saving to sql .........')

    def decode_S_class(self, address, data):
        NUM_OF_BITS = 8
        SCALE = 16
        SOP = DY_SOP
        address_dec = int(address, SCALE)
        data_bin = bin(int(data, SCALE))[2:].zfill(NUM_OF_BITS)
        data_MSB = data_bin[::-1]

        # 0-15 signal 16-50 route  51-53 TRTS  54-84 TRTS
        def get_changed_type(address_dec) -> str:
            changed_type = ('Signal' if (0 <= address_dec <= 15) else
                            'Route' if (16 <= address_dec <= 50) else
                            'TRTS' if (51 <= address_dec <= 53) else
                            'Track')
            return changed_type

        s_msg = []
        change_list = list(SOP[str(address_dec)].values())
        for j in range(0, len(change_list)):
            s_msg.append([get_changed_type(address_dec), change_list[j], data_MSB[j]])
        return s_msg

    def update_container(self, s_msg, address_dec):
        for j in range(0, len(s_msg)):
            if s_msg[j][1] == '':
                continue
            else:
                state_container[str(address_dec)][s_msg[j][1]] = s_msg[j][2]

    def get_changed_msg(self, s_msg, address_dec):
        changed_msg = []
        for j in range(0, len(s_msg)):
            if state_container[str(address_dec)][s_msg[j][1]] != s_msg[j][2]:
                changed_msg.append([s_msg[j][0], s_msg[j][1], s_msg[j][2]])
        return changed_msg

    def print_td(self, parsed_body):
        for outer_message in parsed_body:
            message = list(outer_message.values())[0]
            message_type = message["msg_type"]
            area_id = message["area_id"]
            if area_id == 'DY':
                if message_type in [TD['C_BERTH_STEP'], TD['C_BERTH_CANCEL'], TD['C_BERTH_INTERPOSE']]:
                    area_id = message["area_id"]
                    description = message.get("descr", "")
                    from_berth = message.get("from", "")
                    to_berth = message.get("to", "")
                    uk_datetime = self.set_timestamp(int(message["time"]))
                    print("{} [{}] {} {} {} -> {}".format(
                        uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        message_type, area_id, description, from_berth, to_berth, ))

                if message_type in [TD['S_SIGNALLING_UDPATE'], TD['S_SIGNALLING_REFRESH'],
                                    TD['S_SIGNALLING_REFRESH_FINISHED']]:
                    area_id = message["area_id"]
                    address = message.get("address", "")
                    data = message.get("data", "")
                    uk_datetime = self.set_timestamp(int(message["time"]))
                    print("{} [{}] {} {} {}".format(
                        uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        message_type, area_id, address, data, ))

                if message_type in [TD['C_HEARTBEAT']]:
                    area_id = message["area_id"]
                    report_time = message.get("report_time", "")
                    description = message.get("descr", "")
                    uk_datetime = self.set_timestamp(int(message["time"]))
                    print("{} [{:2}] {} {} {}".format(
                        uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        message_type, area_id, description, report_time, ))

    def print_td_DY(self, parsed_body):

        for outer_message in parsed_body:
            message = list(outer_message.values())[0]
            message_type = message["msg_type"]
            area_id = message["area_id"]
            uk_datetime = self.set_timestamp(int(message["time"]))

            if area_id == 'DY':
                if message_type in [TD['C_BERTH_STEP'], TD['C_BERTH_CANCEL'], TD['C_BERTH_INTERPOSE']]:
                    description = message.get("descr", "")
                    from_berth = message.get("from", "")
                    to_berth = message.get("to", "")
                    print("{} [{}] {} {} {} -> {}".format(
                        uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        message_type, area_id, description, from_berth, to_berth, ))

                if message_type == TD['S_SIGNALLING_UDPATE']:
                    address = message.get("address", "")
                    data = message.get("data", "")
                    s_msg = self.decode_S_class(address, data)

                    address_dec = int(address, 16)
                    if address_update_state_container[str(address_dec)] == 0:
                        address_update_state_container[str(address_dec)] = 1
                        self.update_container(s_msg, address_dec)
                        if len(set(list(address_update_state_container.values()))) == 1:
                            print("Full initial state acquisition successful")
                    else:
                        changed_msg = self.get_changed_msg(s_msg, address_dec)
                        self.update_container(s_msg, address_dec)
                        if changed_msg != []:
                            for j in changed_msg:
                                print("{} [{}] {} {} {} {}".format(
                                    uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                    message_type, area_id, j[0], j[1], j[2]))

                if message_type in [TD['S_SIGNALLING_REFRESH'],
                                    TD['S_SIGNALLING_REFRESH_FINISHED']]:
                    address = message.get("address", "")
                    data = message.get("data", "")
                    hex_data = re.findall("..", data)
                    for i in range(0, 4):
                        address_ = str(hex(int(address, 16) + i)[2:]).zfill(2).upper()
                        data_ = hex_data[i]
                        s_msg = self.decode_S_class(address_, data_)

                        address_dec = int(address_, 16)
                        if address_update_state_container[str(address_dec)] == 0:
                            address_update_state_container[str(address_dec)] = 1
                            self.update_container(s_msg, address_dec)
                            if len(set(list(address_update_state_container.values()))) == 1:
                                print("Full initial state acquisition successful")
                        else:
                            changed_msg = self.get_changed_msg(s_msg, address_dec)
                            self.update_container(s_msg, address_dec)
                            if changed_msg != []:
                                for j in changed_msg:
                                    print("{} [{}] {} {} {} {}".format(
                                        uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                        message_type, area_id, j[0], j[1], j[2]))

                if message_type == TD['C_HEARTBEAT']:
                    report_time = message.get("report_time", "")
                    description = message.get("descr", "")
                    print("{} [{:2}] {} {} {}".format(
                        uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        message_type, area_id, description, report_time, ))

    def creat_insert_initial_state(self, state_container, time):
        # creat table
        dbTable_initial_state = '"{}"."{}"'.format(self.schema_name, self.data_type + '_initial_state')
        self.conn.rollback()
        self.cur.execute('create table if not exists {} ()'.format(dbTable_initial_state))
        self.conn.commit()
        initial_state_table_format = {
            'time': 'TEXT',
            'Type': 'TEXT',
            'ID': 'TEXT',
            'State': 'TEXT',
        }
        for col in initial_state_table_format:
            self.conn.rollback()
            self.cur.execute(
                'alter table {} add column if not exists {} {}'.format(dbTable_initial_state, col,
                                                                       initial_state_table_format[col]))
            self.conn.commit()
        ini_col = ','.join(['time', 'Type', 'ID', 'State'])
        # insert table
        for i in range(len(state_container)):
            for j in state_container[str(i)]:
                val_ini = (time,) + (self.get_changed_type(i),) + (j,) + (state_container[str(i)][j],)
                self.conn.rollback()
                self.cur.execute(
                    "insert into {} ({}) VALUES{}".format(dbTable_initial_state, ini_col, val_ini))
                self.conn.commit()

    def insert_td_DY_frame(self, parsed_body, msg_print):
        self.creat_table()
        for outer_message in parsed_body:
            message = list(outer_message.values())[0]
            area_id = message["area_id"]
            message_type = message["msg_type"]
            if area_id == 'DY':

                uk_datetime = self.set_timestamp(int(message["time"]))
                message["time"] = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")
                replace_dict = {'to': "to_berth", "from": "from_berth"}
                new_data = [replace_dict[i] if i in replace_dict else i for i in list(message.keys())]
                col = ','.join(new_data)
                val = tuple(message.values())

                # SF  SH/SG

                if message_type in [TD['S_SIGNALLING_REFRESH'],
                                    TD['S_SIGNALLING_REFRESH_FINISHED'], TD['S_SIGNALLING_UDPATE']]:
                    address = message.get("address", "")
                    data = message.get("data", "")
                    new_data.extend(['Type', 'ID', 'State'])
                    col = ','.join(new_data)
                    # SF
                    if message_type == TD['S_SIGNALLING_UDPATE']:
                        s_msg = self.decode_S_class(address, data)
                        address_dec = int(address, 16)

                        # If the address container has not been updated, then store it in the container first
                        # If it has been updated, then compare the changes in the container and output the state information for the state change

                        if address_update_state_container[str(address_dec)] == 0:
                            address_update_state_container[str(address_dec)] = 1
                            self.update_container(s_msg, address_dec)
                            if len(set(list(address_update_state_container.values()))) == 1:
                                print("Full initial state acquisition successful")
                                self.creat_insert_initial_state(self, state_container, message["time"])
                        else:
                            changed_msg = self.get_changed_msg(s_msg, address_dec)
                            self.update_container(s_msg, address_dec)
                            if changed_msg != []:
                                for j in changed_msg:
                                    if msg_print == True:
                                        print("{} [{}] {} {} {} {}".format(
                                            uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                            message_type, area_id, j[0], j[1], j[2]))

                                    val_s = val + (j[0],) + (j[1],) + (j[2],)
                                    self.conn.rollback()
                                    self.cur.execute("insert into {} ({}) VALUES{}".format(self.dbTable, col, val_s))
                                    self.conn.commit()
                                    print('Derby_data saving to sql .........')

                    # SH/SG
                    else:
                        hex_data = re.findall("..", data)
                        for i in range(0, 4):
                            address_ = str(hex(int(address, 16) + i)[2:]).zfill(2).upper()
                            data_ = hex_data[i]
                            s_msg = self.decode_S_class(address_, data_)

                            address_dec = int(address, 16)
                            if address_update_state_container[str(address_dec)] == 0:
                                address_update_state_container[str(address_dec)] = 1
                                self.update_container(s_msg, address_dec)
                                if len(set(list(address_update_state_container.values()))) == 1:
                                    print("Full initial state acquisition successful")
                                    self.creat_insert_initial_state(self, state_container, message["time"])
                            else:
                                changed_msg = self.get_changed_msg(s_msg, address_dec)
                                self.update_container(s_msg, address_dec)
                                if changed_msg != []:
                                    for j in changed_msg:
                                        if msg_print == True:
                                            print("{} [{}] {} {} {} {}".format(
                                                uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                                message_type, area_id, j[0], j[1], j[2]))

                                        val_s = val + (j[0],) + (j[1],) + (j[2],)
                                        self.conn.rollback()
                                        self.cur.execute(
                                            "insert into {} ({}) VALUES{}".format(self.dbTable, col, val_s))
                                        self.conn.commit()
                                        print('Derby_data saving to sql .........')
                else:
                    if msg_print == True:
                        description = message.get("descr", "")
                        from_berth = message.get("from", "")
                        to_berth = message.get("to", "")
                        print("{} [{}] {} {} {} -> {}".format(
                            uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                            message_type, area_id, description, from_berth, to_berth, ))
                    self.conn.rollback()
                    self.cur.execute("insert into {} ({}) VALUES{}".format(self.dbTable, col, val))
                    self.conn.commit()


class TM_MVT_msg(msg_to_sql):
    def __init__(self, schema_name, data_type, database_name, sql_username, sql_password, sql_host, port, table_format,
                 MVT_type):
        self.MVT_type = MVT_type
        super().__init__(schema_name, data_type, database_name, sql_username, sql_password, sql_host, port,
                         table_format)

    def print_MVT_msg(self, parsed_body):
        for i in parsed_body:
            head = list(i.values())[0]
            body = list(i.values())[1]
            if head['msg_type'] == self.MVT_type:
                uk_datetime = self.set_timestamp(int(head['msg_queue_timestamp']))
                body['msg_queue_timestamp'] = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")
                val = ()
                for values in body.values():
                    val = val + (str(values),)
                print(val)

    def insert_MVT_data(self, data):
        head = list(data.values())[0]
        body = list(data.values())[1]

        if head['msg_type'] == self.MVT_type:
            uk_datetime = self.set_timestamp(int(head['msg_queue_timestamp']))
            body['msg_queue_timestamp'] = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")
            col = ','.join(list(body.keys()))
            val = ()
            for values in body.values():
                val = val + (str(values),)
            self.conn.rollback()
            self.cur.execute("insert into {} ({}) VALUES{}".format(self.dbTable, col, val))

            self.conn.commit()

    def insert_MVT_frame(self, parsed_body):
        self.creat_table()
        for outer_message in parsed_body:
            self.insert_MVT_data(outer_message)


class VSTP_msg(msg_to_sql):
    def __init__(self, schema_name, data_type, database_name, sql_username, sql_password, sql_host, port, table_format):
        super().__init__(schema_name, data_type, database_name, sql_username, sql_password, sql_host, port,
                         table_format)

    def print_VSTP_msg(self, parsed_body):
        msg = parsed_body
        uk_datetime = self.set_timestamp(int(msg[list(msg.keys())[0]]['timestamp']))
        msg_timestamp = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")
        col = list(msg[list(msg.keys())[0]]['schedule'].keys())
        col = col[:10]
        val = []
        for i in col:
            val.append(msg[list(msg.keys())[0]]['schedule'][i])
        val.append(msg_timestamp)
        print(val)

    def insert_VSTP_frame(self, parsed_body):
        self.creat_table()
        msg = parsed_body
        uk_datetime = self.set_timestamp(int(msg[list(msg.keys())[0]]['timestamp']))
        msg_timestamp = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")
        col = list(msg[list(msg.keys())[0]]['schedule'].keys())
        col = col[:10]
        val = []
        for i in col:
            val.append(msg[list(msg.keys())[0]]['schedule'][i])
        col.append('timestamp')
        val.append(msg_timestamp)
        col = ','.join(col)
        val = tuple(val)
        self.conn.rollback()
        self.cur.execute("insert into {} ({}) VALUES{}".format(self.dbTable, col, val))
        self.conn.commit()


class RTPPM_msg(msg_to_sql):
    def __init__(self, schema_name, data_type, database_name, sql_username, sql_password, sql_host, port, table_format,
                 rtppm_list):
        self.rtppm_list = rtppm_list
        super().__init__(schema_name, data_type, database_name, sql_username, sql_password, sql_host, port,
                         table_format)

    def print_RTPPM_msg(self, parsed_body):
        if 'OperatorPage' in self.rtppm_list:
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['OperatorPage']:
                items = self.dic_flatten(i['Operator'])
                print(items)
        if 'OOCPage' in self.rtppm_list:
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['OOCPage']['Operator']:
                items = self.dic_flatten(i)
                print(items)
        if 'NationalPage_Sector' in self.rtppm_list:
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['NationalPage']['Sector']:
                items = self.dic_flatten(i)
                print(items)
        if 'NationalPage_Operator' in self.rtppm_list:
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['NationalPage']['Operator']:
                items = self.dic_flatten(i)
                print(items)

    def insert_RTPPM_frame(self, parsed_body):
        uk_datetime = self.set_timestamp(int(parsed_body['RTPPMDataMsgV1']['timestamp']))
        msg_timestamp = uk_datetime.strftime("%Y-%m-%d %H:%M:%S")

        for i in self.rtppm_list:
            dbTable = '"{}"."{}"'.format(self.schema_name, self.data_type + '_' + i)
            self.conn.rollback()
            self.cur.execute('create table if not exists {} ()'.format(dbTable))
            self.conn.commit()
            for col in self.table_format[i]:
                self.conn.rollback()
                self.cur.execute(
                    'alter table {} add column if not exists {} {}'.format(dbTable, col, self.table_format[i][col]))
                self.conn.commit()

        if 'OperatorPage' in self.rtppm_list:
            dt = '"{}"."{}"'.format(self.schema_name, self.data_type + '_' + 'OperatorPage')
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['OperatorPage']:
                items = self.dic_flatten(i['Operator'])
                col = list(items.keys())
                col.append('timestamp')
                col = ','.join(col)
                val = list(items.values())
                val.append(msg_timestamp)
                val = tuple(val)
                self.conn.rollback()
                self.cur.execute("insert into {} ({}) VALUES{}".format(dt, col, val))
                self.conn.commit()

        if 'OOCPage' in self.rtppm_list:
            dt = '"{}"."{}"'.format(self.schema_name, self.data_type + '_' + 'OOCPage')
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['OOCPage']['Operator']:
                items = self.dic_flatten(i)
                col = list(items.keys())
                col.append('timestamp')
                col = ','.join(col)
                val = list(items.values())
                val.append(msg_timestamp)
                val = tuple(val)
                self.conn.rollback()
                self.cur.execute("insert into {} ({}) VALUES{}".format(dt, col, val))
                self.conn.commit()

        if 'NationalPage_Sector' in self.rtppm_list:
            dt = '"{}"."{}"'.format(self.schema_name, self.data_type + '_' + 'NationalPage_Sector')
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['NationalPage']['Sector']:
                items = self.dic_flatten(i)
                col = list(items.keys())
                col.append('timestamp')
                col = ','.join(col)
                val = list(items.values())
                val.append(msg_timestamp)
                val = tuple(val)
                self.conn.rollback()
                self.cur.execute("insert into {} ({}) VALUES{}".format(dt, col, val))
                self.conn.commit()

        if 'NationalPage_Operator' in self.rtppm_list:
            dt = '"{}"."{}"'.format(self.schema_name, self.data_type + '_' + 'NationalPage_Operator')
            for i in parsed_body['RTPPMDataMsgV1']['RTPPMData']['NationalPage']['Operator']:
                items = self.dic_flatten(i)
                col = list(items.keys())
                col.append('timestamp')
                col = ','.join(col)
                val = list(items.values())
                val.append(msg_timestamp)
                val = tuple(val)
                self.conn.rollback()
                self.cur.execute("insert into {} ({}) VALUES{}".format(dt, col, val))
                self.conn.commit()
