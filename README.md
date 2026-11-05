# InkJam

鼓谱与手绘演奏视频的公开预览。

[![Caravan 演奏预览](site/output/caravan-performance/poster.jpg)](https://ternencect.github.io/InkJam/)

[播放 Caravan · 同步跟谱](https://ternencect.github.io/InkJam/) · [作品资料库](https://ternencect.github.io/InkJam/output/library/) · [下载完整视频](https://github.com/ternencect/InkJam/releases/tag/caravan-preview-v1)

Caravan 全片 5 分 36.55 秒，1080p / 60 fps。视频关联 v2 的 396 小节鼓谱，支持连续跟谱、点击音符定位、逐帧检查和 MIDI / MusicXML 下载。声音为同谱合成鼓声。历史 381 小节谱单独归档。

`site/library/catalog.json` 记录作品、谱子版本和演奏视频之间的关系。页面及谱子保存在 Git，完整 MP4 保存在固定版本的 Release；发布时检查文件 SHA-256，再一起部署到 GitHub Pages。

## 发布

1. 仓库 Settings → Pages → Source 选择 **GitHub Actions**。
2. 在 `caravan-preview-v1` Release 上传 `Caravan-full-1080p60.mp4` 并发布。
3. 在 Actions → **Publish InkJam preview** → **Run workflow** 选择 `main` 运行，等待成功。首次部署成功后，上方链接生效。

发布只从 `main` 执行，以符合默认 Pages 环境保护规则。后续页面更新推送到 `main` 即自动部署；更换视频时保留旧 Release，新建版本并同步更新关联清单与文件校验清单。

## 本地检查

需要 Python 3.11+ 和 GitHub CLI。视频不随 `git clone` 下载。

```sh
python3 scripts/build_site.py --download-release
python3 -m http.server 8000 --directory _site
```

也可使用 `--video /absolute/path/Caravan-full-1080p60.mp4` 指定已有视频。构建输出目录须为空。
