# -*- coding: utf-8 -*-
"""《黎凡特口语》批量配音（edge-tts，黎凡特男女声）。

用法：python tools/levantine/gen_audio.py
- 断点续传：已存在且非空的 mp3 直接跳过，可反复运行补漏。
- 音频写入站点共享的 audio/ 目录；清单**合并**写入 tools/audio_map.json，
  保留埃及册已有键，不覆盖整份文件。
- 失败条目写 tools/audio_map.json.levantine.fails.json。
"""
import asyncio
import json
import sys
import time
from pathlib import Path

import edge_tts

import audio_spec as A

sys.stdout.reconfigure(encoding="utf-8")
CONCURRENCY = 16
MIN_SIZE = 1024


async def one(text, key, sem, counter):
    rel = A.relpath(text, key)
    out = A.ROOT / rel
    if out.exists() and out.stat().st_size >= MIN_SIZE:
        return "skip", rel, key, text
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp%d.mp3" % (time.time_ns() % 100000))
    p = A.profile(key)
    err = ""
    for attempt in range(3):
        try:
            async with sem:
                comm = edge_tts.Communicate(text, p["voice"], rate=p["rate"], pitch=p["pitch"])
                await comm.save(str(tmp))
            if tmp.exists() and tmp.stat().st_size >= MIN_SIZE:
                tmp.replace(out)
                counter[0] += 1
                return "ok", rel, key, text
            err = "empty output"
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:120])
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        await asyncio.sleep(0.8 * (attempt + 1))
    return "fail:%s" % err, rel, key, text


async def main():
    items = list(A.collect_tasks().values())
    print("黎凡特待配音条目:", len(items), "并发:", CONCURRENCY, flush=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    counter = [0]
    done = [0]
    t0 = time.time()

    async def wrapped(text, key):
        r = await one(text, key, sem, counter)
        done[0] += 1
        if done[0] % 100 == 0 or done[0] == len(items):
            print("进度 %d/%d | 新合成 %d | 耗时 %.0fs" %
                  (done[0], len(items), counter[0], time.time() - t0), flush=True)
        return r

    results = await asyncio.gather(*(wrapped(t, k) for t, k in items))
    ok = sum(1 for r in results if r[0] == "ok")
    skip = sum(1 for r in results if r[0] == "skip")
    fail = sum(1 for r in results if r[0].startswith("fail"))
    print("汇总 | 新生成 %d | 跳过 %d | 失败 %d | 耗时 %.0fs" %
          (ok, skip, fail, time.time() - t0), flush=True)

    mp = {}
    for status, rel, key, text in results:
        if status in ("ok", "skip"):
            mp[A.map_key(text, key)] = rel
    total = A.merge_map(mp)
    print("合并后共享清单共 %d 条（本册新增 %d 条，埃及册键保留）" %
          (total, len(mp)), flush=True)

    fails = [(text, key, status) for status, rel, key, text in results
             if status.startswith("fail")]
    Path(str(A.MAP_PATH) + ".levantine.fails.json").write_text(
        json.dumps(fails, ensure_ascii=False, indent=1), encoding="utf-8")
    print("完成：本册可用音频 %d / %d，失败 %d，总耗时 %.0fs" %
          (len(mp), len(items), len(fails), time.time() - t0), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
