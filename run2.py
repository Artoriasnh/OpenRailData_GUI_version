from Message_to_sql import *
from get_data import get_data
from MSG import *

Email='925884246@qq.com'
password = 'Esperando-0259'
feeds_list=['TD']
td_list=['All_Derby','Derby']
rtppm_list = ['NationalPage_Sector','NationalPage_Operator','OOCPage','OperatorPage']
mvt_list = ['"0001": "activation"',
            '"0002": "cancellation"',
            '"0003": "movement"'
            '"0004": "_unidentified"',
            '"0005": "reinstatement"',
            '"0007": "identity change"',
            '"0008": "_location change"'
            ]

get_options={'Save_to_SQL': True, 'View': True, 'Durable': False}

sql_info = {
    'sql_username' : 'postgres', #postgres
    'sql_password' : '1997513nihao', #1997513nihao
    'schema_name' : 'test4',
    'database_name' : 'postgres',
    'sql_host' : 'localhost',
    'port' : '5432'
}

for i in feeds_list:

    if i == 'TD':
        for j in td_list:
            area_id = j
            if j == 'All_Derby':
                _table_format = table_format['TD_All']
            else:
                _table_format = table_format['TD']

            TD_mts = TD_msg(
                schema_name=sql_info['schema_name'],
                data_type='TD_'+area_id,
                database_name=sql_info['database_name'],
                sql_username=sql_info['sql_username'],
                sql_password=sql_info['sql_password'],
                sql_host=sql_info['sql_host'],
                port=sql_info['port'],
                table_format = _table_format,
                area_id = area_id
            )
            TD_getdata=get_data(
                mts=TD_mts,
                username=Email,
                password=password,
                topic=topic_dict['TD'],
                listener=Listener_dict['TD'],
                msg_print = get_options['View'],
                sts = get_options['Save_to_SQL'],
                isdurable =  get_options['Durable']
            )
            TD_getdata.start()

    if i =='MVT':
        for j in mvt_list:
            MVT_mts = TM_MVT_msg(
                schema_name=sql_info['schema_name'],
                data_type=TM_MESSAGES[j[1:5]],
                database_name=sql_info['database_name'],
                sql_username=sql_info['sql_username'],
                sql_password=sql_info['sql_password'],
                sql_host=sql_info['sql_host'],
                port=sql_info['port'],
                table_format=table_format['MVT'][j[1:5]],
                MVT_type=j[1:5]
            )
            MVT_getdata = get_data(
                mts=MVT_mts,
                username=Email,
                password=password,
                topic=topic_dict['MVT'],
                listener=Listener_dict['MVT'],
                msg_print=get_options['View'],
                sts = get_options['Save_to_SQL'],
                isdurable=get_options['Durable']
            )
            MVT_getdata.start()


    if i =='VSTP':

        VSTP_mts = VSTP_msg(
            schema_name=sql_info['schema_name'],
            data_type='VSTP',
            database_name=sql_info['database_name'],
            sql_username=sql_info['sql_username'],
            sql_password=sql_info['sql_password'],
            sql_host=sql_info['sql_host'],
            port=sql_info['port'],
            table_format=table_format['VSTP'],
        )
        VSTP_getdata = get_data(
            mts=VSTP_mts,
            username=Email,
            password=password,
            topic=topic_dict['VSTP'],
            listener=Listener_dict['VSTP'],
            msg_print=get_options['View'],
            sts=get_options['Save_to_SQL'],
            isdurable=get_options['Durable']
        )

        VSTP_getdata.start()




    if i =='RTPPM':

        RTPPM_mts = RTPPM_msg(
            schema_name=sql_info['schema_name'],
            data_type='RTPPM',
            database_name=sql_info['database_name'],
            sql_username=sql_info['sql_username'],
            sql_password=sql_info['sql_password'],
            sql_host=sql_info['sql_host'],
            port=sql_info['port'],
            table_format= table_format['RTPPM'],
            rtppm_list = rtppm_list,
        )
        RTPPM_getdata = get_data(
            mts=RTPPM_mts,
            username=Email,
            password=password,
            topic=topic_dict['RTPPM'],
            listener=Listener_dict['RTPPM'],
            msg_print=get_options['View'],
            sts=get_options['Save_to_SQL'],
            isdurable=get_options['Durable']
        )

        RTPPM_getdata.start()






