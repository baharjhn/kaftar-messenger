import os
import datetime

import mysql.connector
import elasticsearch

# Connection settings come from environment variables (see .env.example).
es = elasticsearch.Elasticsearch(os.environ.get("KAFTAR_ES_URL", "http://localhost:9200"))

cnx = mysql.connector.connect(user=os.environ.get("KAFTAR_DB_USER", "root"),
                              password=os.environ.get("KAFTAR_DB_PASSWORD", ""),
                              host=os.environ.get("KAFTAR_DB_HOST", "127.0.0.1"),
                              port=int(os.environ.get("KAFTAR_DB_PORT", "3306")),
                              database=os.environ.get("KAFTAR_DB_NAME", "Kaftar"))
cursor = cnx.cursor(buffered=True)

phone_num = None
request = None
system = False

es.indices.delete(index='message', ignore=[400, 404])
es.indices.delete(index='membership', ignore=[400, 404])


def insert_message_elastic(dic):
    es.index(index="message", doc_type='tweet', body=dic)
def insert_membership_elastic(dic):
    es.index(index="membership", doc_type='tweet', body=dic)
def handle_output(str):
    if (str == "NULL"):
        return "NULL"
    else:
        if str == 'System' or str == 'Me': return str
        return ("\"" + str + "\"")


# TODO
def get_session_ip():
    return 'XX1'


# TODO
def get_device():
    return 'GALAXY S8'


# TODO
def get_date():
    return str(datetime.datetime.now())


# TODO
def get_OS():
    return 'Windows'


def get_message_id():
    sum = 0
    cursor.execute("SELECT COUNT(*) From PvMessage")
    sum += int(cursor.fetchall()[0][0])
    cursor.execute("SELECT COUNT(*) From GroupMessage")
    sum += int(cursor.fetchall()[0][0])
    cursor.execute("SELECT COUNT(*) From ChannelMessage")
    sum += int(cursor.fetchall()[0][0])
    return str(sum + 1)


def login():
    global phone_num, request
    cursor.execute(
        "SELECT PhoneNo, UserPassword "
        "FROM KaftarUser "
        "WHERE PhoneNo = '" + request[1] + "' ;")

    result = cursor.fetchall()

    if phone_num == request[1]:
        print("You've already logged in with this number!")
        return

    elif phone_num != None:
        print("Please first log out")
        return

    elif result != []:
        if result[0][1] != 'NULL':
            print("Enter your password:")
            password = str(input())
            if password != result[0][1]:
                print("Access denied.")
                return

        phone_num = request[1]

        cursor.execute("SELECT SessionIP "
                       "FROM UserSession "
                       "WHERE SessionIP = '" + get_session_ip() + "' AND  PhoneNo = '" + phone_num + "';")

        result = cursor.fetchall()

        if result == []:
            cursor.execute(
                "INSERT INTO UserSession (PhoneNo , FirstAccess , Device , LastAccess , SessionIP , OS)  VALUES "
                "('" + request[
                    1] + "', '" + get_date() + "', '" + get_device() + "', NULL, '" + get_session_ip() + "', ' "
                                                                                                         "" + get_OS() + "');"
            )
        else:
            cursor.execute("UPDATE UserSession "
                           "SET LastAccess = NULL "
                           "WHERE SessionIP = '" + get_session_ip() + "' AND  PhoneNo = '" + phone_num + "';")

        cnx.commit()
        return

    elif result == []:
        print("ID is not found.")
        return


def create_user():
    global phone_num, request

    cursor.execute(
        "SELECT PhoneNo "
        "FROM KaftarUser "
        "WHERE PhoneNo = '" + request[1] + "' ;")

    result = cursor.fetchall()
    if result == []:
        cursor.execute(
            "INSERT INTO KaftarUser (UserName , PhoneNo , Bio , UserPassword , SelfDestruct) VALUES "
            "('NULL' , '" + request[1] + "', 'NULL', 'NULL', '0');"
        )
        cnx.commit()

    else:
        print("You've already registered, Please sign in.")

    return


def set_bio():
    global phone_num
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute(
        "UPDATE KaftarUser "
        "SET Bio = '" + ' '.join(request[1:]) + "' "
                                                "WHERE PhoneNo = '" + phone_num + "';"
    )
    cnx.commit()
    return


def set_self_destruct():
    global phone_num
    if phone_num == None:
        print("Please first log in")
        return

    if int(request[1]) < 0 or int(request[1]) > 3:
        print("Self destruct value is not valid")
        return

    cursor.execute(
        "UPDATE KaftarUser "
        "SET SelfDestruct = '" + request[1] + "' "
                                              "WHERE PhoneNo = '" + phone_num + "';"
    )
    cnx.commit()
    return


def set_password():
    global phone_num
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute(
        "UPDATE KaftarUser "
        "SET UserPassword = '" + ' '.join(request[1:]) + "' "
                                                         "WHERE PhoneNo = '" + phone_num + "';"
    )
    cnx.commit()
    return


def set_name():
    global phone_num
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute(
        "UPDATE KaftarUser "
        "SET UserName = '" + ' '.join(request[1:]) + "' "
                                                     "WHERE PhoneNo = '" + phone_num + "';"
    )
    cnx.commit()
    return


def create_channel():
    global phone_num, request, system
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT ChannelID "
                   "FROM KaftarChannel "
                   "WHERE ChannelID = '" + request[1] + "' ;")
    result = cursor.fetchall()

    if (result == []):
        cursor.execute(
            "INSERT INTO KaftarChannel (ChannelID , ChannelName , ChannelLink , ChannelAdminPhoneNo , Bio ) "
            " VALUES ('" + request[1] + "', '" + ' '.join(request[2:]) + "', 'NULL', '" + phone_num + "', 'NULL');")
        cnx.commit()

        request = ["join_channel", request[1]]
        join_channel()

        request = ['send_message_channel', request[1], 'channel created']
        system = True
        send_message_channel()
        system = False

    else:
        print("This ID has been taken. Please choose another ID")

    return


def create_group():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT GroupID "
                   "FROM KaftarGroup "
                   "WHERE GroupID = '" + request[1] + "' ;")
    result = cursor.fetchall()

    if (result == []):
        cursor.execute(
            "INSERT INTO KaftarGroup (GroupID , GroupName , GroupLink, GroupAdminPhoneNo , Bio ) "
            " VALUES ('" + request[1] + "', '" + ' '.join(request[2:]) + "', 'NULL', '" + phone_num + "', 'NULL');")
        cnx.commit()
        request = ["join_group", request[1]]
        join_group()

    else:
        print("This ID has been taken. Please choose another ID")

    return


def set_channel_link():
    global phone_num
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT ChannelID "
                   "FROM KaftarChannel "
                   "WHERE ChannelID = '" + request[1] + "' AND ChannelAdminPhoneNo = '" + phone_num + "' ;")
    result = cursor.fetchall()
    if result == []:
        print("Access denied.")
        return

    # Making sure the link is not taken.
    cursor.execute("SELECT ChannelID "
                   "FROM KaftarChannel "
                   "WHERE ChannelLink = '" + request[2] + "' ;")
    result = cursor.fetchall()

    cursor.execute("SELECT GroupID "
                   "FROM KaftarGroup "
                   "WHERE GroupLink = '" + request[2] + "' ;")
    new_result = cursor.fetchall()

    if result != [] or new_result != []:
        print("The link is already taken. Please choose another link.")
        return

    cursor.execute("UPDATE KaftarChannel "
                   "SET ChannelLink = '" + request[2] + "' "
                                                        "WHERE ChannelID = '" + request[1] + "';")

    cnx.commit()
    return


def set_group_link():
    global phone_num
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT GroupID "
                   "FROM KaftarGroup "
                   "WHERE GroupID = '" + request[1] + "' AND GroupID IN (SELECT GID "
                                                      "FROM GroupMembership "
                                                      "WHERE UserPhoneNo = '" + phone_num + "');")
    result = cursor.fetchall()

    if result == []:
        print("Access denied.")
        return

    # Making sure the link is not taken.
    cursor.execute("SELECT ChannelID "
                   "FROM KaftarChannel "
                   "WHERE ChannelLink = '" + request[2] + "' ;")
    result = cursor.fetchall()

    cursor.execute("SELECT GroupID "
                   "FROM KaftarGroup "
                   "WHERE GroupLink = '" + request[2] + "' ;")
    new_result = cursor.fetchall()

    if result != [] or new_result != []:
        print("The link is already taken. Please choose another link.")
        return

    cursor.execute("UPDATE KaftarGroup "
                   "SET GroupLink = '" + request[2] + "' "
                                                      "WHERE GroupID = '" + request[1] + "';")

    cnx.commit()
    return


def logout():
    global phone_num
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute(
        "SELECT SessionIp "
        "FROM UserSession "
        "WHERE PhoneNo = '" + phone_num + "' "
                                          "AND SessionIp='" + get_session_ip() + "' ;")
    result = cursor.fetchall()
    cursor.execute(
        "UPDATE UserSession "
        "SET lastAccess= '" + get_date() + "'"
                                           "WHERE SessionIp='" + result[0][0] + "'"
                                                                                "AND PhoneNo = '" + phone_num + "';")

    phone_num = None
    cnx.commit()


def block_user():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT PhoneNo FROM KaftarUser Where PhoneNo='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("ID is not found.")
    else:
        cursor.execute("INSERT INTO BlockedUser (BlockerPhoneNo, BlockedPhoneNo ,BlockedDate) VALUES "
                       "('" + phone_num + "' , '" + request[1] + "','" + get_date() + "')")
        cnx.commit()


def unblock_user():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute(
        "DELETE FROM BlockedUser WHERE BlockerPhoneNo='" + phone_num + "'AND " + "BlockedPhoneNo='" + request[1] + "';")
    cnx.commit()


def join_group():
    global phone_num, request, system
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT GroupID "
                   "FROM kaftarGroup "
                   "WHERE GroupID = '" + request[1] + "';")
    result = cursor.fetchall()

    if result == []:
        print("This group Doesn't exist")
        return

    cursor.execute("SELECT GID "
                   "FROM GroupMembership "
                   "WHERE GID = '" + request[1] + "' AND "
                                                  "UserPhoneNo = '" + phone_num + "'; ")
    result = cursor.fetchall()

    if result != []:
        print("You've already joined this group")
        return

    cursor.execute("INSERT INTO GroupMembership (GID , UserPhoneNo , LastAccess ) VALUES "
                   "('" + request[1] + "', '" + phone_num + "', '" + get_date() + "' );")
    cnx.commit()
    dict = {
        'member': phone_num,
        'GroupID': request[1],
        'ChannelID': "None"

    }
    insert_membership_elastic(dict)

    cursor.execute("SELECT UserName "
                   "FROM kaftarUser "
                   "WHERE PhoneNO = '" + phone_num + "'; ")
    name = cursor.fetchall()[0][0]
    if name == 'NULL': name = phone_num
    content = name + " joined group"

    cursor.execute("SELECT GroupAdminPhoneNo "
                   "FROM kaftarGroup "
                   "WHERE GroupID = '" + request[1] + "'; ")
    admin_phone_no = cursor.fetchall()[0][0]

    if admin_phone_no == phone_num: content = "group created"

    request = ['send_message_group', request[1], content]
    system = True
    send_message_group()
    system = False
    return


def join_channel():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT ChannelID "
                   "FROM kaftarChannel "
                   "WHERE ChannelID = '" + request[1] + "';")
    result = cursor.fetchall()

    if result == []:
        print("This channel Doesn't exist")
        return

    cursor.execute("SELECT CID "
                   "FROM ChannelMembership "
                   "WHERE CID = '" + request[1] + "' AND "
                                                  "UserPhoneNo = '" + phone_num + "'; ")
    result = cursor.fetchall()

    if result != []:
        print("You've already joined this Channel")
        return

    cursor.execute("INSERT INTO ChannelMembership (CID , UserPhoneNo , LastAccess ) VALUES "
                   "('" + request[1] + "', '" + phone_num + "', '" + get_date() + "' );")
    cnx.commit()
    dict = {
        'member': phone_num,
        'GroupID': "None",
        'ChannelID': request[1]

    }
    insert_membership_elastic(dict)
    return


def send_message():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute("SELECT PhoneNo FROM KaftarUser Where PhoneNo='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("ID is not found.")
    else:
        cursor.execute(
            "SELECT BlockedPhoneNo From BlockedUser Where BlockerPhoneNo='" + phone_num + "' AND BlockedPhoneNo ='"
            + request[1] + "';")
        result = cursor.fetchall()
        if (len(result) != 0):
            print("This User is in your blackList")
            result = None
        else:
            cursor.execute(
                "SELECT BlockedPhoneNo From BlockedUser Where BlockerPhoneNo='" + request[1] + "' AND BlockedPhoneNo ='"
                + phone_num + "';")
            result = cursor.fetchall()
            if (len(result) != 0):
                print("You are blocked by this User")
                result = None
            else:
                cursor.execute(
                    "INSERT INTO PvMessage (MessageID , ReceiverPhoneNo ,SenderPhoneNo ,Content ,SentTime) VALUES "
                    "('" + get_message_id() + "' , '" + request[1] + "','" + phone_num + "','" + ' '.join(request[2:])
                    + "','" + get_date() + "');")

                cnx.commit()

                cursor.execute("SELECT LastAccess "
                               "FROM PVMembership "
                               "WHERE OwnerPhoneNo = '" + phone_num + "' "
                                                                      "AND PersonPhoneNo = '" + request[1] + "' ;")
                exist = cursor.fetchall()

                if exist == []:
                    cursor.execute("INSERT INTO PVMembership (OwnerPhoneNo, PersonPhoneno, LastAccess) VALUES "
                                   "('" + phone_num + "', '" + request[1] + "', '" + get_date() + "');")
                else:
                    cursor.execute("UPDATE PVMembership "
                                   "SET LastAccess = '" + get_date() + "' "
                                                                       "WHERE OwnerPhoneNo = '" + phone_num + "' "
                                                                                                              "AND PersonPhoneNo = '" +
                                   request[1] + "' ;")
                cnx.commit()

                cursor.execute("SELECT LastAccess "
                               "FROM PVMembership "
                               "WHERE OwnerPhoneNo = '" + request[1] + "' "
                                                                       "AND PersonPhoneNo = '" + phone_num + "' ;")
                exist = cursor.fetchall()

                if exist == []:
                    cursor.execute("INSERT INTO PVMembership (OwnerPhoneNo, PersonPhoneno, LastAccess) VALUES "
                                   "('" + request[1] + "', '" + phone_num + "', '0001-01-01 01:01:01') ;")

                    cnx.commit()

                dict = {
                    'Content': ' '.join(request[2:]),
                    'SentTime': get_date()[:10],
                    'ReceiverPhoneNo': request[1],
                    'SenderPhoneNo': phone_num,
                    'ReceiverChannelID': "None",
                    'ReceiverGroupID': "None"
                }
                insert_message_elastic(dict)

    return


def join_link():
    global phone_num, request, system
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT ChannelID "
                   "FROM kaftarChannel "
                   "WHERE ChannelLink = '" + request[1] + "';")
    result = cursor.fetchall()

    if result == []:
        cursor.execute("SELECT GroupID "
                       "FROM kaftarGroup "
                       "WHERE GroupLink = '" + request[1] + "';")
        result = cursor.fetchall()

        if result == []:
            print("This group or channel Doesn't exist")
            return

        cursor.execute("SELECT GID "
                       "FROM GroupMembership "
                       "WHERE GID = '" + result[0][0] + "' AND "
                                                        "UserPhoneNo = '" + phone_num + "'; ")
        new_result = cursor.fetchall()
        if new_result != []:
            print("You've already joined this group")
            return

        cursor.execute("INSERT INTO GroupMembership (GID , UserPhoneNo , LastAccess ) VALUES "
                       "('" + result[0][0] + "', '" + phone_num + "', '" + get_date() + "' );")
        cnx.commit()

        cursor.execute("SELECT UserName "
                       "FROM kaftarUser "
                       "WHERE PhoneNO = '" + phone_num + "'; ")
        name = cursor.fetchall()[0][0]
        if name == 'NULL': name = phone_num
        content = name + " joined group"

        request = ['send_message_group', result[0][0], content]
        system = True
        send_message_group()
        system = False

        return

    cursor.execute("SELECT CID "
                   "FROM ChannelMembership "
                   "WHERE CID = '" + result[0][0] + "' AND "
                                                    "UserPhoneNo = '" + phone_num + "'; ")
    new_result = cursor.fetchall()

    if new_result != []:
        print("You've already joined this Channel")
        return

    cursor.execute("INSERT INTO ChannelMembership (CID , UserPhoneNo , LastAccess ) VALUES "
                   "('" + result[0][0] + "', '" + phone_num + "', '" + get_date() + "' );")
    cnx.commit()
    return


def send_message_channel():
    global phone_num, request
    if phone_num == None and system == False:
        print("Please first log in")
        return
    cursor.execute("SELECT ChannelID FROM KaftarChannel Where ChannelID='" + request[1] + "';")
    result = cursor.fetchall()
    if len(result) == 0 and system == False:
        print("ID is not found.")
    else:
        cursor.execute(
            "SELECT ChannelAdminPhoneNo From KaftarChannel Where ChannelId='" + request[
                1] + "' AND ChannelAdminPhoneNo ='"
            + phone_num + "';")
        result = cursor.fetchall()
        if len(result) == 0 and system == False:
            print("Access denied.")
            result = None
        else:
            phone_number = phone_num
            if system: phone_number = str(-1)

            cursor.execute(
                "INSERT INTO ChannelMessage (MessageID , ReceiverChannelID ,SenderPhoneNo ,Content ,SentTime) VALUES "
                "('" + get_message_id() + "' , '" + request[1] + "','" + phone_number + "','" + ' '.join(request[2:])
                + "','" + get_date() + "');")
            cnx.commit()
            if not system:
                cursor.execute("UPDATE ChannelMembership "
                               "SET LastAccess =  '" + get_date() + "' "
                                                                    "WHERE UserPhoneNo = '" + phone_num + "' "
                                                                                                          "AND CID= '" +
                               request[1] + "'")
                cnx.commit()

            dict = {
                'Content': ' '.join(request[2:]),
                'SentTime': get_date()[:10],
                'ReceiverPhoneNo': "None",
                'SenderPhoneNo': phone_number,
                'ReceiverChannelID': request[1],
                'ReceiverGroupID': "None"
            }
            insert_message_elastic(dict)

    return


def send_message_group():
    global phone_num, request, system
    if phone_num == None and system == False:
        print("Please first log in")
        return
    cursor.execute("SELECT GroupID FROM KaftarGroup Where GroupID='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0 and system == False):
        print("ID is not found.")
    else:

        cursor.execute(
            "SELECT GID From GroupMemberShip Where GID='" + request[1] + "' AND UserPhoneNo ='"
            + phone_num + "';")
        result = cursor.fetchall()
        if (len(result) == 0 and system == False):
            print("you are not a member of this group")
            result = None
        else:
            phone_number = phone_num
            if system: phone_number = str(-1)
            cursor.execute(
                "INSERT INTO GroupMessage (MessageID , ReceiverGroupID ,SenderPhoneNo ,Content ,SentTime) VALUES "
                "('" + get_message_id() + "' , '" + request[1] + "','" + phone_number + "','" + ' '.join(request[2:])
                + "','" + get_date() + "');")
            cnx.commit()

            if not system:
                cursor.execute("UPDATE GroupMembership "
                               "SET LastAccess =  '" + get_date() + "' "
                                                                    "WHERE UserPhoneNo = '" + phone_num + "' "
                                                                                                          "AND GID= '" +
                               request[1] + "'")
                cnx.commit()
            dict = {
                'Content': ' '.join(request[2:]),
                'SentTime': get_date()[:10],
                'ReceiverPhoneNo': "None",
                'SenderPhoneNo': phone_num,
                'ReceiverChannelID': "None",
                'ReceiverGroupID': request[1]
            }
            insert_message_elastic(dict)

    return


def leave_group():
    global phone_num, request, system
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute("SELECT GroupID FROM KaftarGroup Where GroupID='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("ID is not found.")
    else:

        cursor.execute(
            "SELECT GID From GroupMemberShip Where GID='" + request[1] + "' AND UserPhoneNo ='"
            + phone_num + "';")
        result = cursor.fetchall()
        if (len(result) == 0):
            print("you are already out of this Group")
            result = None
        else:

            cursor.execute("SELECT UserName "
                           "FROM kaftarUser "
                           "WHERE PhoneNO = '" + phone_num + "'; ")
            name = cursor.fetchall()[0][0]
            if name == 'NULL': name = phone_num

            request = ["send_group_message", request[1], name + " left group"]
            system = True
            send_message_group()
            system = False

            cursor.execute(
                "DELETE FROM GroupMemberShip WHERE GID='" + request[1] + "' AND  UserPhoneNo='" + phone_num + "';")
            cnx.commit()

    return


def leave_channel():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute("SELECT ChannelID FROM KaftarChannel Where ChannelID='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("ID is not found.")
    else:

        cursor.execute(
            "SELECT CID From ChannelMemberShip Where CID='" + request[1] + "' AND UserPhoneNo ='"
            + phone_num + "';")
        result = cursor.fetchall()
        if (len(result) == 0):
            print("you are already out of this Channel")
            result = None
        else:
            cursor.execute(
                "DELETE FROM ChannelMemberShip WHERE CID='" + request[1] + "'AND UserPhoneNo='" + phone_num + "';")
            cnx.commit()


# TODO not sure if working
def count_unread():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return

    unread = 0
    cursor.execute("SELECT count(pm.MessageID) "
                   "FROM PVMessage AS pm, PVMembership AS pms "
                   "WHERE pm.SenderPhoneNo = pms.PersonPhoneNo "
                   "AND pms.OwnerPhoneNo = '" + phone_num + "' "
                                                            "AND pm.SentTime > pms.LastAccess ;")
    result = cursor.fetchall()
    unread += result[0][0]

    cursor.execute("SELECT count(gm.MessageID) "
                   "FROM GroupMessage AS gm, GroupMembership AS gms "
                   "WHERE gm.ReceiverGroupID = gms.GID "
                   "AND gms.UserPhoneNo = '" + phone_num + "' "
                                                           "AND gm.SentTime > gms.LastAccess;")
    result = cursor.fetchall()
    unread += result[0][0]

    cursor.execute("SELECT count(cm.MessageID) "
                   "FROM ChannelMessage AS cm, ChannelMembership AS cms "
                   "WHERE cm.ReceiverChannelID = cms.CID "
                   "AND cms.UserPhoneNo = '" + phone_num + "' "
                                                           "AND cm.SentTime > cms.LastAccess;")
    result = cursor.fetchall()
    unread += result[0][0]

    print(unread)
    result


def view_user_profile():
    cursor.execute("SELECT PhoneNo FROM KaftarUser Where PhoneNo='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("ID is not found.")
    else:

        cursor.execute("SELECT PhoneNo,UserName,Bio FROM KaftarUser Where PhoneNo='" + request[1] + "'")
        result = cursor.fetchall()

        print("Name:" + handle_output(result[0][1]), "Bio:" + handle_output(result[0][2]))


def view_channel_profile():
    cursor.execute("SELECT ChannelID FROM KaftarChannel WHERE ChannelID='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("ID is not found.")

    else:

        cursor.execute(

            "SELECT ChannelID,ChannelName,ChannelLink,ChannelAdminPhoneNo FROM KaftarChannel,ChannelMemberShip Where KaftarChannel.ChannelID =ChannelMemberShip.CID AND "

            "ChannelID='" +

            request[1] + "' "

                         "AND UserPhoneNo= '" + phone_num + "'")

        result = cursor.fetchall()

        if (len(result) == 0):
            print("Access denied.")

            return

        print("Name:" + handle_output(result[0][1]), end=" ")

        cursor.execute("SELECT COUNT(CID) FROM ChannelMemberShip WHERE CID ='" + request[1] + "';")

        numOfMembers = cursor.fetchall()[0][0]

        print("MembersCount:" + str(numOfMembers), end=" ")

        print("Link:" + handle_output(result[0][2]), end=" ")

        if (phone_num == result[0][3]):

            cursor.execute(

                "SELECT KaftarUser.UserName,KaftarUser.PhoneNo FROM ChannelMemberShip,KaftarUser WHERE ChannelMemberShip.UserPhoneNo=KaftarUser.PhoneNo")

            result = cursor.fetchall()

            cursor.execute(

                "SELECT KaftarUser.UserName FROM KaftarUser WHERE KaftarUser.PhoneNo='" + phone_num + "'")

            result1 = cursor.fetchall()
            if (result1[0][0] == "NULL"):

                out = phone_num

            else:

                out = result1[0][0]

            print("Creator:" + handle_output(out), end=" ")

            print("Members:" + handle_output(out), end=" ,")

            for i in range(len(result)):

                if (result[i][1] != phone_num):

                    if (result[i][0] == "NULL"):

                        out = result[i][1]

                    else:

                        out = result[i][0]

                    if (i == len(result) - 1):

                        print(handle_output(out))

                    else:
                        if (i == len(result) - 2 and result[i + 1][1] == phone_num):
                            print(handle_output(out))
                        else:
                            print(handle_output(out), end=" ,")


                else:

                    continue



        else:

            print()

    return


def view_group_profile():
    cursor.execute("SELECT GroupID FROM KaftarGroup WHERE GroupID='" + request[1] + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("ID is not found.")

    else:
        cursor.execute(
            "SELECT GroupID,GroupName,GroupLink,GroupAdminPhoneNo FROM KaftarGroup,GroupMemberShip Where KaftarGroup.GroupID=GroupMemberShip.GID "
            "AND GroupID='" + request[1] + "' "
                                           "AND UserPhoneNo='" + phone_num + "'")
        result = cursor.fetchall()
        if (len(result) == 0):
            print("Access denied")
            return
        print("Name:" + handle_output(result[0][1]), end=" ")
        cursor.execute("SELECT COUNT(GID) FROM GroupMemberShip WHERE GID ='" + request[1] + "';")
        numOfMembers = cursor.fetchall()[0][0]

        print("MembersCount:" + str(numOfMembers), end=" ")
        print("Link:" + handle_output(result[0][2]), end=" ")
        print("Creator:" + handle_output(result[0][3]), end=" ")
        cursor.execute(
            "SELECT KaftarUser.UserName,KaftarUser.PhoneNo "
            "FROM GroupMemberShip,KaftarUser "
            "WHERE GroupMemberShip.UserPhoneNo=KaftarUser.PhoneNo "
            "AND GID = '" + request[1] + "' "
                                         "ORDER BY GroupMembership.LastAccess DESC")
        result = cursor.fetchall()
        print("Members:", end="")
        for i in range(len(result) - 1):
            out = result[i][0]
            if (result[i][0] == 'NULL'):
                out = result[i][1]
            print(handle_output(out), end=", ")

        i = len(result) - 1
        out = result[i][0]
        if (result[i][0] == 'NULL'):
            out = result[i][1]
        print(handle_output(out))


def view_chat():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute("SELECT SenderPhoneNo,ReceiverPhoneNo,Content,SentTime,UserName "
                   "FROM PVMessage,KaftarUser "
                   "WHERE SenderPhoneNo=PhoneNo "
                   "AND ((SenderPhoneNo ='" + phone_num + "' AND ReceiverPhoneNo= '" + request[1] + "') or "
                                                                                                    "(SenderPhoneNo ='" +
                   request[1] + "' AND ReceiverPhoneNo= '" + phone_num + "') )  "
                                                                         "order by SentTime"
                                                                         " LIMIT 20 ")

    result = cursor.fetchall()

    for i in result:
        name = i[4]
        if i[4] == 'NULL': name = i[0]
        if i[0] == phone_num: name = 'Me'

        print("Sender:" + handle_output(name), "Time:" + handle_output(str(i[3])), end=" ")
        print("Message:" + handle_output(i[2]))

    cursor.execute("UPDATE PVMembership "
                   "SET LastAccess =  '" + get_date() + "' "
                                                        "WHERE OwnerPhoneNo = '" + phone_num + "' "
                                                                                               "AND PersonPhoneNo= '" +
                   request[1] + "'")
    cnx.commit()
    return


def view_channel():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute(
        "SELECT CID From ChannelMemberShip Where CID='" + request[1] + "' AND UserPhoneNo ='"
        + phone_num + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("Access denied.")
        result = None
    else:
        cursor.execute("SELECT UserName,Content,SentTime, phoneNo "
                       "FROM ChannelMessage, KaftarUser "

                       "WHERE SenderPhoneNo=PhoneNo "
                       "AND ReceiverChannelID ='" + request[1] + "'"
                                                                 "ORDER BY SentTime  "
                                                                 " LIMIT 20"
                       )

        result = cursor.fetchall()

        for i in result:
            name = i[0]
            if i[0] == 'NULL': name = i[3]
            if i[3] == phone_num: name = 'Me'

            print("Sender:" + handle_output(name), "Time:" + handle_output(str(i[2])), end=" ")
            print("Message:" + handle_output(i[1]))
        cursor.execute("UPDATE ChannelMembership "
                       "SET LastAccess =  '" + get_date() + "' "
                                                            "WHERE UserPhoneNo = '" + phone_num + "' "
                                                                                                  "AND CID= '" +
                       request[1] + "'")
        cnx.commit()
    return


def view_group():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return
    cursor.execute(
        "SELECT GID From GroupMemberShip Where GID='" + request[1] + "' AND UserPhoneNo ='"
        + phone_num + "';")
    result = cursor.fetchall()
    if (len(result) == 0):
        print("Access denied.")
        result = None
    else:
        cursor.execute("SELECT UserName,Content,SentTime, phoneNo "
                       "FROM GroupMessage ,KaftarUser "
                       "WHERE SenderPhoneNo = phoneNo "
                       "AND ReceiverGroupID='" + request[1] + "'"
                                                              "ORDER BY SentTime  "
                                                              " LIMIT 20"
                       )

        result = cursor.fetchall()

    for i in result:
        name = i[0]
        if i[0] == 'NULL': name = i[3]
        if i[3] == phone_num: name = 'Me'

        print("Sender:" + handle_output(name), "Time:" + handle_output(str(i[2])), end=" ")
        print("Message:" + handle_output(i[1]))

    cursor.execute("UPDATE GroupMembership "
                   "SET LastAccess =  '" + get_date() + "' "
                                                        "WHERE UserPhoneNo = '" + phone_num + "' "
                                                                                              "AND GID= '" +
                   request[1] + "'")
    cnx.commit()
    return


def home():
    global phone_num, request
    if phone_num == None:
        print("Please first log in")
        return

    cursor.execute("SELECT answer.Type, answer.Chat, answer.MaxSentTime "
                   "FROM ( "
                   "SELECT 'pv' AS Type, sub_ans.Person AS chat, max(sub_ans.SentTime) AS MaxSentTime "
                   "FROM ( "
                   "SELECT pvm.SenderPhoneNo AS Person, pvm.SentTime AS SentTime "
                   "FROM PVMessage AS pvm "
                   "WHERE pvm.ReceiverPhoneNo = '" + phone_num + "' "

                                                                 "UNION "
                                                                 "SELECT pvm.ReceiverPhoneNo AS person, pvm.SentTime AS SentTime "
                                                                 "FROM PVMessage AS pvm "
                                                                 "WHERE pvm.senderPhoneNo = '" + phone_num + "' "
                                                                                                             ") AS sub_ans "


                                                                                                             "GROUP BY sub_ans.Person "

                                                                                                             "UNION "
                                                                                                             "SELECT 'group' AS Type, gms.GID AS chat, max(gm.SentTime) AS MaxSentTime "
                                                                                                             "FROM GroupMessage AS gm, GroupMembership AS gms "
                                                                                                             "WHERE gm.ReceiverGroupID = gms.GID "
                                                                                                             "AND gms.UserPhoneNo = '" + phone_num + "' "
                                                                                                                                                     "GROUP BY gms.GID "

                                                                                                                                                     "UNION "
                                                                                                                                                     "SELECT 'channel' AS Type, cms.CID AS chat, max(cm.SentTime) AS MaxSentTime "
                                                                                                                                                     "FROM ChannelMessage AS cm, ChannelMembership AS cms "
                                                                                                                                                     "WHERE cm.ReceiverChannelID = cms.CID "
                                                                                                                                                     "AND cms.UserPhoneNo = '" + phone_num + "' "
                                                                                                                                                                                             "GROUP BY cms.CID "

                                                                                                                                                                                             ")as answer "
                                                                                                                                                                                             "ORDER BY MaxSentTime DESC ;")

    result = cursor.fetchall()
    for i in range(len(result)):
        if result[i][0] == 'channel':
            cursor.execute("SELECT LastAccess "
                           "FROM ChannelMembership "
                           "WHERE UserPhoneNo = '" + phone_num + "' "
                                                                 "    AND CID = '" + result[i][1] + "' ;")
            last_access = cursor.fetchall()[0][0]

            cursor.execute("SELECT count(cm.MessageID) "
                           "FROM ChannelMessage as cm "
                           "WHERE cm.ReceiverChannelId = '" + result[i][1] + "' "
                                                                             "AND cm.SentTime > '" + str(
                last_access) + "';")

            count = cursor.fetchall()[0][0]

            cursor.execute("SELECT ChannelName "
                           "FROM KaftarChannel "
                           "WHERE ChannelID = '" + result[i][1] + "' ;")
            channel_name = cursor.fetchall()[0][0]

            print('channel ' + channel_name + ', unread_count=' + str(count))

        if result[i][0] == 'group':
            cursor.execute("SELECT LastAccess "
                           "FROM GroupMembership "
                           "WHERE UserPhoneNo = '" + phone_num + "' "
                                                                 "    AND GID = '" + result[i][1] + "' ;")
            last_access = cursor.fetchall()[0][0]

            cursor.execute("SELECT count(gm.MessageID) "
                           "FROM GroupMessage as gm "
                           "WHERE gm.ReceiverGroupId = '" + result[i][1] + "' "
                                                                           "AND gm.SentTime > '" + str(
                last_access) + "';")

            count = cursor.fetchall()[0][0]

            cursor.execute("SELECT GroupName "
                           "FROM KaftarGroup "
                           "WHERE GroupID = '" + result[i][1] + "' ;")
            group_name = cursor.fetchall()[0][0]

            print('group ' + group_name + ', unread_count=' + str(count))

        if result[i][0] == 'pv':
            cursor.execute("SELECT LastAccess "
                           "FROM PVMembership "
                           "WHERE OwnerPhoneNo = '" + phone_num + "' "
                                                                  "    AND PersonPhoneNo = '" + result[i][1] + "' ;")

            last_access = cursor.fetchall()[0][0]

            cursor.execute("SELECT count(pm.MessageID) "
                           "FROM PVMessage as pm "
                           "WHERE pm.SenderPhoneNo = '" + result[i][1] + "' "
                                                                         "AND pm.ReceiverPhoneNo = '" + phone_num + "' "
                                                                                                                    "AND pm.SentTime > '" + str(
                last_access) + "' ;")
            count = cursor.fetchall()[0][0]

            cursor.execute("SELECT UserName "
                           "FROM KaftarUser "
                           "WHERE PhoneNo = '" + result[i][1] + "' ;")
            user_name = cursor.fetchall()[0][0]
            if user_name == 'NULL': user_name = result[i][1]

            print('chat with ' + user_name + ', unread_count=' + str(count))

    return


def search_all():
    words = ' '.join(request[1:])


    groups_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"ChannelID": "None"}}

                ]}}
    })
    groups = []
    for i in groups_results['hits']['hits']:
        groups.append(i['_source']['GroupID'])

    channels_results = es.search(index="membership", doc_type="tweet", body={
         "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"GroupID": "None"}}

                ]}}
    })
    channels = []
    for i in channels_results['hits']['hits']:
        channels.append(i['_source']['ChannelID'])

    result = es.search(index="message", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"bool": {
                        "should": [{"bool": {
                            "must": [{"match": {"ReceiverPhoneNo": phone_num}}, {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}] + [{"bool": {
                            "must": [{"match": {"SenderPhoneNo": phone_num}}, {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}] + [{"match": {"ReceiverGroupID": x}} for x in groups] + [
                                      {"match": {"ReceiverChannelID": x}} for x in channels]

                    }
                    },
                    {"bool": {
                        "must": [{ "match": {"Content": words } }]

                    }
                    }

                ]
            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source'])

def search_all_fuzzy():
    words = ' '.join(request[1:])

    groups_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"ChannelID": "None"}}

                ]}}
    })
    groups = []
    for i in groups_results['hits']['hits']:
        groups.append(i['_source']['GroupID'])

    channels_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"GroupID": "None"}}

                ]}}
    })
    channels = []
    for i in channels_results['hits']['hits']:
        channels.append(i['_source']['ChannelID'])

    result = es.search(index="message", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"bool": {
                        "should": [{"bool": {
                            "must": [{"match": {"ReceiverPhoneNo": phone_num}},
                                     {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}] + [{"bool": {
                            "must": [{"match": {"SenderPhoneNo": phone_num}}, {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}] + [{"match": {"ReceiverGroupID": x}} for x in groups] + [
                                      {"match": {"ReceiverChannelID": x}} for x in channels]

                    }
                    },
                    {"bool": {
                        "must": [{"match": {"Content": {"query": words, "fuzziness": 3}}}]

                    }
                    }

                ]
            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source'])

def search_chat():
    words = ' '.join(request[2:])
    Rnumber = request[1]

    result = es.search(index="message", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"ReceiverPhoneNo": Rnumber}},
                    {"match": {"SenderPhoneNo": phone_num}},
                    {"fuzzy": {"Content": {"value": words, "fuzziness": 3}}}]
            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source']['Content'])


def search_group():
    words = ' '.join(request[2:])
    groupID = request[1]

    result = es.search(index="message", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"ReceiverGroupID": groupID}}
                        ,
                    {"fuzzy": {"Content": {"value": words, "fuzziness": 3}}}]

            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source']['Content'])

def search_group_by_sender():
    words = ' '.join(request[3:])
    sender_phone_number=request[2]
    groupID = request[1]



    result = es.search(index="message", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"ReceiverGroupID": groupID}},
                    {"match": {"SenderPhoneNo": sender_phone_number}},
                    {"fuzzy": {"Content": {"value": words, "fuzziness": 2}}}]
            }
        }
    })

    for i in result['hits']['hits']:
        print(i['_source']['Content'])


def search_channel():
    words = ' '.join(request[2:])
    channelID = request[1]

    result = es.search(index="message", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"ReceiverChannelID": channelID}}

                    ,{"fuzzy": {"Content": {"value": words, "fuzziness": 3}}}]

            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source']['Content'])
def view_messages_by_date():

    date=request[1]
    groups_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"ChannelID": "None"}}

                ]}}
    })
    groups = []
    for i in groups_results['hits']['hits']:
        groups.append(i['_source']['GroupID'])

    channels_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"GroupID": "None"}}

                ]}}
    })
    channels = []
    for i in channels_results['hits']['hits']:
        channels.append(i['_source']['ChannelID'])

    result = es.search(index="message", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"bool": {
                        "should": [{"bool": {
                            "must": [{"match": {"ReceiverPhoneNo": phone_num}},
                                     {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}] + [{"bool": {
                            "must": [{"match": {"SenderPhoneNo": phone_num}}, {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}] + [{"match": {"ReceiverGroupID": x}} for x in groups] + [
                                      {"match": {"ReceiverChannelID": x}} for x in channels]

                    }
                    },
                    {"bool": {
                        "must": [{"match": {"SentTime":date}}]

                    }
                    }


                ]
            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source'])

def view_messages_by_date_chat():
    phone_num_chat=request[1]
    date=request[2]
    groups_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"ChannelID": "None"}}

                ]}}
    })
    groups = []
    for i in groups_results['hits']['hits']:
        groups.append(i['_source']['GroupID'])

    channels_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"GroupID": "None"}}

                ]}}
    })
    channels = []
    for i in channels_results['hits']['hits']:
        channels.append(i['_source']['ChannelID'])

    result = es.search(index="message", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"bool": {
                        "should": [{"bool": {
                            "must": [{"match": {"ReceiverPhoneNo": phone_num}},
                                     {"match": {"SenderPhoneNo": phone_num_chat}},
                                     {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}] + [{"bool": {
                            "must": [{"match": {"SenderPhoneNo": phone_num}},
                                     {"match": {"ReceiverPhoneNo": phone_num_chat}},
                                     {"match": {"ReceiverChannelID": "None"}},
                                     {"match": {"ReceiverGroupID": "None"}}]
                        }}]

                    }
                    },
                    {"bool": {
                        "must": [{"match": {"SentTime":date}}]

                    }
                    }


                ]
            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source'])

def view_messages_by_date_group():
    groupID=request[1]
    date=request[2]
    groups_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"ChannelID": "None"}}
                    ,
                    {"match": {"GroupID": groupID}}

                ]}}
    })
    groups = []
    for i in groups_results['hits']['hits']:
        groups.append(i['_source']['GroupID'])

    channels_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"GroupID": "None"}}

                ]}}
    })
    channels = []
    for i in channels_results['hits']['hits']:
        channels.append(i['_source']['ChannelID'])
    if(not len(groups)):
        print("access denied")
        return
    result = es.search(index="message", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"bool": {
                        "must":[{"match": {"ReceiverGroupID": groups[0]}}]


                    }
                    },
                    {"bool": {
                        "must": [{"match": {"SentTime": date}}]

                    }
                    }

                ]
            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source'])



def view_messages_by_date_channel():
    channelID=request[1]
    date=request[2]
    groups_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"ChannelID": "None"}}


                ]}}
    })
    groups = []
    for i in groups_results['hits']['hits']:
        groups.append(i['_source']['GroupID'])

    channels_results = es.search(index="membership", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"member": phone_num}}
                    ,
                    {"match": {"ChannelID": channelID}}
                    ,
                    {"match": {"GroupID": "None"}}

                ]}}
    })
    channels = []
    for i in channels_results['hits']['hits']:
        channels.append(i['_source']['ChannelID'])
    if(not len(channels)):
        print("access denied")
        return
    result = es.search(index="message", doc_type="tweet", body={
        "query": {
            "bool": {
                "must": [
                    {"bool": {
                        "must":[{"match": {"ReceiverChannelID": channels[0]}}]


                    }
                    },
                    {"bool": {
                        "must": [{"match": {"SentTime": date}}]

                    }
                    }

                ]
            }
        }
    })
    for i in result['hits']['hits']:
        print(i['_source'])


# Commands a user can type at the prompt (first word = command name).
COMMANDS = {name: globals()[name] for name in [
    "login", "create_user", "logout", "set_bio", "set_self_destruct", "set_password", "set_name",
    "create_channel", "create_group", "set_channel_link", "set_group_link",
    "block_user", "unblock_user", "join_group", "join_channel", "join_link", "leave_group", "leave_channel",
    "send_message", "send_message_channel", "send_message_group", "count_unread",
    "view_user_profile", "view_channel_profile", "view_group_profile",
    "view_chat", "view_channel", "view_group", "home",
    "search_all", "search_all_fuzzy", "search_chat", "search_group", "search_group_by_sender", "search_channel",
    "view_messages_by_date", "view_messages_by_date_chat", "view_messages_by_date_group",
    "view_messages_by_date_channel",
]}

if __name__ == "__main__":
    while True:
        request = input().split()
        if not request:
            continue
        command = COMMANDS.get(request[0])
        if command is None:
            print("Request is not valid")
            continue
        command()

