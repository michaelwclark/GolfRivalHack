from mitmproxy import http
import json
from random import randint


# Saves the chest JSON to a file for further debugging
def log_chest(box):
    with open(f"{box['box_info']['box_id']}_chest.json", "w+") as fp:
        json.dump(box, fp)


# Build a list of balls to keep. This works better than selecting a few since the server
#  removes balls periodically.
def get_balls():
    balls = []
    for i in range(1, 290):
        balls.append({"id": i, "count": randint(50, 500)})
    return balls


# Set each ball count to it's ID for in game documentation purposes
def document_balls():
    balls = []
    for i in range(1, 290):
        balls.append({"id": i, "count": i})
    return balls


# Failed attempt at keeping the balls despite server returning a different list.
# I think the logic is right here but the response modifier is a bit off.
# TODO: debug further to try and keep the balls.
def keep_balls(balls):
    balls = []
    for i in range(1, 290):
        balls.append({"id": i, "count": randint(50, 500)})
    return balls


# Upgrade clubs to max available levels.
def upgrade_club(club):
    commons = [43, 7, 56, 14, 34, 15, 17, 16, 11, 30, 24]
    rares = [98, 25, 19, 50, 28, 20, 57, 21, 9, 35, 29, 48, 22, 12, 49]
    epics = [55, 31, 13, 10, 62, 32, 26, 8, 27, 47, 23, 36]
    Legendary = [37, 64, 63, 38, 39, 45, 40, 41, 42, 60]
    wolfs = [101, 102, 103, 105, 106]

    club["count"] = club["id"]
    if club['id'] in commons:
        club["level"] = 15
    elif club['id'] in rares:
        club["level"] = 13
    elif club['id'] in epics:
        club["level"] = 12
    elif club['id'] in Legendary:
        club["level"] = 8
    elif club['id'] in wolfs:
        club["level"] = 21


# Runs before response gets to the client
def response(flow: http.HTTPFlow) -> None:
    flow_response = flow.response.get_text()
    try:
        flow_response = json.loads(flow.response.get_text())
    except json.decoder.JSONDecodeError:
        return

    # If the response is a chest log it for now.
    if "box/open" in flow.request.pretty_url:
        chest = flow_response["data"]
        log_chest(chest)

    # if the response is /me then update balls and clubs
    elif "user/me" in flow.request.pretty_url:
        flow_response['data']['user_prop']['ballList'] = get_balls()
        clubs = flow_response['data']['user_prop']['clubList']
        for club in clubs:
            upgrade_club(club)

        # Can trick the client into upgraded trophys but can't start new level.
        # flow_response['data']['user_info']['trophys'] = 55001

        # Can trick the client into glevel max but it breaks when trying to start new level.
        # flow_response['data']['user_info']['max_glevel'] = 19
        # flow_response['data']['user_info']['glevel'] = 19

        # Unsure what this actually does
        # flow_response['data']['user_info']['ulevel'] = 10
        # flow_response['data']['user_info']['u_stage_new'] = 1

    # Response from server that seems to remove certian balls.
    # This isn't working right yet.
    elif "userProp/getList" in flow.request.pretty_url:
        flow_response["data"]["ballList"] = keep_balls(flow_response["data"]["ballList"])
    flow.response.text = json.dumps(flow_response)


# Save the log actions for debugging.
def log_log_row(row):
    filename = f"{row['cmd']}_log_cmd.json"
    with open(filename, "w+") as fp:
        out = {**row}
        out['row'] = json.loads(out['row'])
        json.dump(out, fp)


# Failed attempt to trick server into updating diamonds and trophies.
def update_log_diaomonds(row):
    row_json = json.loads(row['row'])
    if row_json.get('diamond'):
        row_json['diamond'] = row_json['diamond'] + 100
        row_json['trophy'] = row_json['trophy'] + 10000
    row = {**row, "row": json.dumps(row_json)}
    return row


# Runs before request is sent to the server
def request(flow: http.HTTPFlow):
    if "uploadlogs" in flow.request.pretty_url:
        log_row = json.loads(flow.request.urlencoded_form["rows"])
        updated_rows = []
        for row in log_row['rows']:
            log_log_row(row)
            # This doesn't work, server is too smart.
            # updated_row = update_log_diaomonds(row)
            # updated_rows.append(updated_row)

        flow.request.urlencoded_form["rows"] = json.dumps({"rows": updated_rows})

# curl -H 'X-Unity-Version: 2018.4.36f1' -H 'Accept: */*' -H 'APP-VERSION: 1.59.293' -H 'GOLF-TOKEN: xxx' -H 'Accept-Language: en-us' --compressed -H 'Content-Type: application/x-www-form-urlencoded' -H 'OS-TYPE: ios' -H 'User-Agent: Golf%20Rival/4 CFNetwork/1240.0.4 Darwin/20.6.0' -H 'Connection: keep-alive' -X POST 'https://api.golfrival.net/box/open?ubox_id=2355737461&diamond_num=0'


# curl -H 'X-Unity-Version: 2018.4.36f1' -H 'Accept: */*' -H 'APP-VERSION: 1.59.293' -H 'GOLF-TOKEN: xxx' -H 'Accept-Language: en-us' --compressed -H 'Content-Type: application/x-www-form-urlencoded' -H 'OS-TYPE: ios' -H 'User-Agent: Golf%20Rival/4 CFNetwork/1240.0.4 Darwin/20.6.0' -H 'Connection: keep-alive' -X POST 'https://api.golfrival.net/luckyspin/spin?consume_type=3&consume_num=0&watch_ad=0'
# {"code": "0", "message": "\u6210\u529f", "data": {"user_lucky_spin_info": {"id": 6684, "uid": 33148368, "pid": 1, "spin_stage": 13, "spin_items": [{"prop": {"prop_id": 39, "prop_type": 45, "prop_color": 4, "prop_num": 100}, "status": 0}, {"prop": {"prop_id": 0, "prop_type": 3, "prop_color": 0, "prop_num": 650}, "status": 1}, {"prop": {"prop_id": 26, "prop_type": 4, "prop_color": 3, "prop_num": 4}, "status": 0}, {"prop": {"prop_id": 0, "prop_type": 2, "prop_color": 0, "prop_num": 30}, "status": 0}, {"prop": {"prop_id": 1, "prop_type": 5, "prop_color": 0, "prop_num": 3}, "status": 0}, {"prop": {"prop_id": 0, "prop_type": 7, "prop_color": 3, "prop_num": 3}, "status": 0}, {"prop": {"prop_id": 0, "prop_type": 2, "prop_color": 0, "prop_num": 200}, "status": 0}, {"prop": {"prop_id": 8, "prop_type": 5, "prop_color": 0, "prop_num": 3}, "status": 0}], "reset_times": 0, "refresh_at": 1659576486, "need_hole_num": 3, "hole_num": 0}, "box": {"need_spin_times": 8, "reward": {"prop_id": 0, "prop_num": 1, "prop_type": 6, "prop_color": 4, "chest_type": 3}, "spin_times": 2}, "spin_consume": {"consume_type": 3, "consume_num": 1200, "ad_enable": false}, "reset_consume": {"consume_type": 2, "consume_num": 120}, "reset_enable": false, "next_refresh_time": 1659596400, "conf": {"start_time": 1659423600, "end_time": 1660028400, "reset_pop_up_interval": 3600}, "spin_reward": {"prop_id": 0, "prop_type": 3, "prop_color": 0, "prop_num": 650, "item_index": 1}, "this_time_spin_consume": {"consume_type": 3, "consume_num": 0}}, "show_msg": ""}
#  can't replay, get code 37006