"""Convert the downloader's CSV files (ticks/USA500_YYYY-MM-DD.csv) into compact .bin files for the app.

Usage: py make_data.py ticks data
File layout (little endian): uint32 n, then n x uint32 ms since 09:30:00 ET, n x int32 bid*1000, n x int32 ask*1000.
Also writes data/index.json listing the days.
"""
import csv, glob, json, os, struct, sys, datetime as dt

src = sys.argv[1] if len(sys.argv) > 1 else "ticks"
dst = sys.argv[2] if len(sys.argv) > 2 else "data"
os.makedirs(dst, exist_ok=True)
days = []
for p in sorted(glob.glob(os.path.join(src, "USA500_*.csv"))):
    date = os.path.basename(p)[7:17]
    ms, bid, ask = [], [], []
    for r in list(csv.reader(open(p)))[1:]:
        t = dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S.%f")
        ms.append(((t.hour * 60 + t.minute) * 60 - 34200) * 1000 + t.microsecond // 1000)
        bid.append(round(float(r[1]) * 1000)); ask.append(round(float(r[2]) * 1000))
    n = len(ms)
    with open(os.path.join(dst, date + ".bin"), "wb") as f:
        f.write(struct.pack("<I", n))
        f.write(struct.pack("<%dI" % n, *ms)); f.write(struct.pack("<%di" % n, *bid)); f.write(struct.pack("<%di" % n, *ask))
    days.append({"date": date, "file": date + ".bin", "ticks": n})
    print(date, n)
json.dump({"symbol": "USA500.IDX", "days": days}, open(os.path.join(dst, "index.json"), "w"))
