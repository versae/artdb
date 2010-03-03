# -*- coding: utf-8 -*-
f = open("initial_data2.xml", "r")
lines = f.readlines()
p = 0
res = []
for k, l in enumerate(lines):
    if l.find("POINT (") >= 0:
        l = l.replace(",", " ")
        l = l.replace("  ", " ")
        if l.find("&quot;") >= 0:
            l = l.replace("&quot;", "\"")
        else:
            l = l.replace("º", "")
            l = l.replace("°", "")
        l = l.replace("^M", "")
        p += 1
    res.append(l)
print "".join(res)
