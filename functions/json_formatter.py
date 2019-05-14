def Json_formatter(header, data):
    text='['
    for d in data:
        temp=list(map(str, d))
        text+='{'
        temp_text=[]
        for h in range(len(header)):
            text+='"'+header[h]+'":'+temp[h]+','
        text=text.rstrip(',')
        text+="},"
    text=text.rstrip(',')
    text+=']'
    return text