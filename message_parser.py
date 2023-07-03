# message_parser.py
import os
import argparse
import datetime as dt
import json

FPATHS = {
    "KAKAO_WIN": [],
    "KAKAO_MAC": [],
    "KAKAO_AND": [],
    "KAKAO_IOS": [],
}

class MessageParser:
    pass


def kakao_win(lines):
    messages = []
    title, saved_time, chat_date = "", "", ""
    name, time, message = "", "", ""
    for idx, line in enumerate(lines):
        line = line.rstrip('\n')
        if line=="":
            continue
        elif idx == 0 and line.endswith("님과 카카오톡 대화"):
            title = line.rstrip("님과 카카오톡 대화").rstrip()
            #print(idx, title)
        elif idx == 1 and line.startswith("저장한 날짜 : "):
            saved_time = line.lstrip("저장한 날짜 : ")
            saved_time = dt.datetime.strptime(saved_time, "%Y-%m-%d %H:%M:%S")
            #print(idx, saved_time)
        elif line.startswith("---------------") and line.endswith("---------------"):
            date = line.strip("---------------").strip()
            try:
                date = dt.datetime.strptime(date[:-4], "%Y년 %m월 %d일")
                #print(date)
            except:
                if all(x != "" for x in [name, time, message]):
                    message += "\n"+line
                    continue
            chat_date = date
        elif line.endswith("님이 들어왔습니다.") or line.endswith("님이 나갔습니다."):
            continue
        elif line.startswith("["):
            sep1 = line[1:line.index("]")]
            temp = line[line.index("]")+2:]
            if not temp.startswith("["):
                print(line)
                continue
            sep2 = temp[1:temp.index("]")]
            sep3 = temp[temp.index("]")+2:]

            if all(x != "" for x in [name, time, message]):
                obj = {
                    'name': name,
                    'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'message': message
                }
                messages.append(obj)

            try:
                ap, hours, minutes = sep2.split()[0], int(sep2.split()[1].split(':')[0]), int(sep2.split()[1].split(':')[1])
            except ValueError:
                if all(x != "" for x in [line, name, time, message]):
                    message += "\n"+line
                    continue
            if ap == "오후":
                hours += 12
            elif ap != "오전":
                print("time parse error")
                if all(x != "" for x in [line, name, time, message]):
                    message += "\n"+line
                continue
            if chat_date == "":
                print("no chat_date")
                continue
            #print(chat_date)
            time = chat_date + dt.timedelta(minutes=minutes, hours=hours)
            
            name, time, message = sep1, time, sep3
        elif all(x != "" for x in [line, name, time, message]):
            message += "\n"+line
    if all(x != "" for x in [name, time, message]):
        obj = {
            'name': name,
            'time': time.strftime("%Y-%m-%d %H:%M:%S"),
            'message': message
        }
        messages.append(obj)

    res = {
        'title': title,
        'saved_time': saved_time.strftime("%Y-%m-%d %H:%M:%S"),
        'messages': messages,
    }
    return res



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='모바일 메신저 서비스의 내보내기 파일을 파싱합니다.'
    )
    parser.add_argument('-p', '--platform', type=str, default='ios', help='select platform in ["win", "mac", "and", "ios"]')
    parser.add_argument('filename', type=str, help='filename to parse')
    args = parser.parse_args()
    print(args.platform, args.filename)

    try:
        with open(args.filename, "r", encoding='utf-8') as fin:
            lines = fin.readlines()

            res = kakao_win(lines)

            fpath = "./result/"
            fname = res["title"]+"_"+res["saved_time"].split()[0]+".json"
            if not os.path.exists(fpath):
                os.mkdir(fpath)
            try:
                with open(os.path.join(fpath, fname), "w", encoding='utf-8') as fout:
                    json.dump(res, fout, ensure_ascii=False)
            except IOError:
                print("No such file or directory", os.path.join(fpath, fname))
                
    except IOError:
        print("No such file :", args.filename)