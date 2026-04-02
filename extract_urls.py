"""
YouTube 频道视频链接提取器
功能：提供一个 YouTube 频道链接或博主用户名，获取该频道下所有视频的 URL
依赖：yt-dlp (pip install yt-dlp)
用法：
    python extract_urls.py "https://www.youtube.com/@用户名"
    python extract_urls.py "@用户名"
    python extract_urls.py "用户名"
"""

import subprocess
import sys
import os
import re
import argparse


# 输出目录（脚本所在目录下的 output 文件夹）
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def get_channel_name(channel_url: str) -> str:
    """
    通过 yt-dlp 获取频道/博主的真实名称
    使用多种策略依次尝试：
      1. 获取频道页面的 playlist_title（频道名称）
      2. 获取第一个视频的 channel 或 uploader 字段
      3. 从 URL 中解析用户名作为兜底

    Args:
        channel_url: YouTube 频道的 URL

    Returns:
        频道名称字符串
    """
    # 策略1：直接从频道页面提取 playlist_title（即频道名）
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--playlist-items", "0",        # 不取任何视频，只要播放列表元数据
        "--print", "%(playlist_title)s", # 输出频道/播放列表标题
        "--no-warnings",
        channel_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode == 0 and result.stdout.strip():
            name = result.stdout.strip().split("\n")[0]
            if name and name != "NA" and name != "NA - Videos":
                name = re.sub(r' - Videos$', '', name)  # 去掉 " - Videos" 后缀
                name = re.sub(r'[\\/:*?"<>|]', '_', name)
                if name:
                    return name
    except Exception:
        pass

    # 策略2：取第一个视频的完整信息，提取 channel 或 uploader
    for field in ["%(channel)s", "%(uploader)s"]:
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--playlist-items", "1",    # 只取第一个视频
            "--print", field,
            "--no-download",            # 不下载视频
            "--no-warnings",
            channel_url
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if result.returncode == 0 and result.stdout.strip():
                name = result.stdout.strip().split("\n")[0]
                if name and name != "NA":
                    name = re.sub(r'[\\/:*?"<>|]', '_', name)
                    return name
        except Exception:
            pass

    # 策略3：从 URL 中提取用户名作为兜底方案
    match = re.search(r'youtube\.com/(?:@|c/|channel/|user/)([^/\s?]+)', channel_url)
    if match:
        return match.group(1)

    return None


def normalize_channel_url(input_str: str) -> str:
    """
    将用户输入标准化为完整的 YouTube 频道 URL
    支持以下输入格式：
      - 完整 URL: https://www.youtube.com/@用户名
      - 带 @ 的用户名: @用户名
      - 纯用户名: 用户名

    Args:
        input_str: 用户输入的频道链接或用户名

    Returns:
        标准化后的频道 URL
    """
    input_str = input_str.strip()

    # 已经是完整 URL
    if input_str.startswith("http://") or input_str.startswith("https://"):
        url = input_str.rstrip("/")
        # 确保指向 videos 页面
        if "/videos" not in url:
            url += "/videos"
        return url

    # 带 @ 前缀的用户名
    if input_str.startswith("@"):
        return f"https://www.youtube.com/{input_str}/videos"

    # 纯用户名，自动添加 @ 前缀
    return f"https://www.youtube.com/@{input_str}/videos"


def extract_video_urls(channel_input: str) -> list[str]:
    """
    从 YouTube 频道中提取所有视频链接并保存到 output 目录

    Args:
        channel_input: YouTube 频道的 URL 或用户名

    Returns:
        视频链接列表
    """
    # 标准化频道 URL
    channel_url = normalize_channel_url(channel_input)
    print(f"正在获取频道视频列表，请稍候...")
    print(f"频道地址: {channel_url}")

    # 先获取频道名称，用于命名输出文件
    print("正在获取频道名称...")
    channel_name = get_channel_name(channel_url)

    if not channel_name:
        print("警告: 无法获取频道名称，将使用默认名称")
        channel_name = "unknown_channel"

    print(f"频道名称: {channel_name}")

    # 使用 yt-dlp 的 --flat-playlist 模式，只获取视频 URL 而不下载
    print("正在提取所有视频链接...")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",          # 只解析播放列表，不下载
        "--print", "url",           # 只输出视频 URL
        "--no-warnings",            # 不显示警告
        channel_url
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        if result.returncode != 0:
            print(f"错误: {result.stderr.strip()}")
            return []

        # 解析输出，每行一个 URL
        urls = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        print(f"共找到 {len(urls)} 个视频")

        if not urls:
            print("未找到任何视频链接")
            return []

        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 以频道名称命名文件，保存到 output 目录
        output_file = os.path.join(OUTPUT_DIR, f"{channel_name}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(urls))

        print(f"结果已保存到: {output_file}")
        return urls

    except FileNotFoundError:
        print("错误: 未找到 yt-dlp，请先安装: pip install -r requirements.txt")
        return []
    except Exception as e:
        print(f"发生错误: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="YouTube 频道视频链接提取器")
    parser.add_argument(
        "channel",
        help="YouTube 频道的 URL 或用户名（如: @用户名 或 https://www.youtube.com/@用户名）"
    )

    args = parser.parse_args()
    extract_video_urls(args.channel)


if __name__ == "__main__":
    main()
