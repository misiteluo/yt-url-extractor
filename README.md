# YouTube 频道视频链接提取器

一个简单的 Python 脚本，用于提取指定 YouTube 频道下所有视频的链接。

## 功能特性

- 支持多种输入格式（完整 URL、`@用户名`、纯用户名）
- 自动获取频道真实名称并以此命名输出文件
- 提取结果保存到 `output/` 目录，每行一个链接
- 使用 `yt-dlp` 的 flat-playlist 模式，只获取链接不下载视频

## 安装

```bash
# 克隆项目
git clone <仓库地址>
cd yt-url-extractor

# 创建虚拟环境（可选）
python -m venv .venv
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

```bash
# 使用用户名
python extract_urls.py DanKoeTalks

# 使用 @ 格式（PowerShell 中需要加引号）
python extract_urls.py "@DanKoeTalks"

# 使用完整 URL
python extract_urls.py "https://www.youtube.com/@DanKoeTalks"
```

运行后会在 `output/` 目录下生成以频道名称命名的 `.txt` 文件，例如：

```
output/
  └── Dan Koe.txt
```

## 输出格式

每行一个视频链接：

```
https://www.youtube.com/watch?v=xxxxx
https://www.youtube.com/watch?v=yyyyy
https://www.youtube.com/watch?v=zzzzz
```

## 注意事项

- 需要能够访问 YouTube（可能需要代理）
- 在 PowerShell 中使用 `@` 开头的用户名时，请用引号包裹参数
- 频道视频数量较多时，提取过程可能需要一定时间
