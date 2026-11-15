# -*- coding: utf-8 -*-
"""批量生成站点配音 mp3（edge-tts 微软在线 TTS）。

用法：python tools/gen_audio.py
- 断点续传：已存在且非空的 mp3 直接跳过，可反复运行补漏。
- 并发 6，失败自动重试 4 次；失败的条目不会写入 audio_map.json。
- 产出：audio/<桶>/<hash>.mp3 与 tools/audio_map.json。
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


async def one(text, key, sem, counter, total):
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
    print("待配音条目:", len(items), "并发:", CONCURRENCY, flush=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    counter = [0]
    done = [0]
    t0 = time.time()

    async def wrapped(text, key):
        r = await one(text, key, sem, counter, len(items))
        done[0] += 1
        if done[0] % 100 == 0 or done[0] == len(items):
            print("进度 %d/%d | 已完成 %d | 耗时 %.0fs" %
                  (done[0], len(items), counter[0], time.time() - t0), flush=True)
        return r

    results = await asyncio.gather(*(wrapped(t, k) for t, k in items))
    ok = sum(1 for r in results if r[0] == "ok")
    skip = sum(1 for r in results if r[0] == "skip")
    fail = sum(1 for r in results if r[0].startswith("fail"))
    print("汇总 | 新生成 %d | 跳过 %d | 失败 %d | 耗时 %.0fs" %
          (ok, skip, fail, time.time() - t0), flush=True)

    # 本脚本只重建埃及册的音频键；共享清单里黎凡特册的键（含 |lev: 前缀）必须保留，
    # 否则重跑第 01 册配音会把第 02 册的 2574 条映射整份抹掉。
    mp = {k: v for k, v in (A.read_map() or {}).items() if "|lev:" in k}
    for status, rel, key, text in results:
        if status in ("ok", "skip"):
            mp[A.map_key(text, key)] = rel
    A.MAP_PATH.write_text(json.dumps(mp, ensure_ascii=False, indent=0), encoding="utf-8")

    fails = [(text, key, status) for status, rel, key, text in results if status.startswith("fail")]
    if fails:
        Path(str(A.MAP_PATH) + ".fails.json").write_text(
            json.dumps(fails, ensure_ascii=False, indent=1), encoding="utf-8")
    print("完成：可用音频 %d / %d，失败 %d，总耗时 %.0fs" %
          (len(mp), len(items), len(fails), time.time() - t0), flush=True)
    print("音频清单:", A.MAP_PATH, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
