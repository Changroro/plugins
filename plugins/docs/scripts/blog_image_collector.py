#!/usr/bin/env python3
"""블로그 본문 이미지 로컬 수집기.

외부 이미지 URL을 받아 글 슬러그 폴더 안에 `img-NN.{ext}` 형식으로 저장한다.

설계 원칙:
- 외부 의존 최소화: `requests`만 필수. Pillow는 선택 (포맷 감지 보조용).
- R2 / 오브젝트 스토리지 미사용. 영구 호스팅은 발행 단계의 티스토리 에디터가 담당.
- 저장된 로컬 경로를 stdout으로 반환 → blog-writer agent가 본문 임베드에 사용.

CLI:
    python blog_image_collector.py <url> <dest_dir> <index>

예시:
    python blog_image_collector.py https://example.com/foo.png ./my-post-images 1
    # -> ./my-post-images/img-01.png 가 생성되고 stdout에 같은 경로 출력
"""
from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

# 브라우저 위장 헤더 (일부 CDN이 기본 python-requests UA 차단)
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Content-Type → 확장자 매핑
_CT_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/avif": ".avif",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
}


def _guess_ext(url: str, content_type: str) -> str:
    """URL 경로 → Content-Type → fallback 순으로 확장자 추정."""
    # 1) URL path에 확장자가 있으면 우선
    path = urlparse(url).path.split("?")[0]
    suffix = Path(path).suffix.lower()
    if suffix and 2 <= len(suffix) <= 6:
        return suffix
    # 2) Content-Type 매핑
    ct = (content_type or "").lower().split(";")[0].strip()
    if ct in _CT_TO_EXT:
        return _CT_TO_EXT[ct]
    # 3) mimetypes 표준 가이드
    guess = mimetypes.guess_extension(ct) if ct else None
    if guess:
        return guess
    # 4) 알 수 없으면 .png (티스토리 본문에서 가장 흔한 기본값)
    return ".png"


def _download(url: str, timeout: int = 60) -> tuple[bytes, str]:
    """URL에서 바이너리와 Content-Type을 받아온다.

    기본 requests로 실패하면 curl_cffi(있을 때)로 브라우저 임퍼소네이션 재시도.
    """
    try:
        resp = requests.get(url, headers=_BROWSER_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.content, resp.headers.get("Content-Type", "")
    except Exception as primary_err:
        try:
            from curl_cffi import requests as curl_requests  # type: ignore

            resp = curl_requests.get(
                url,
                headers=_BROWSER_HEADERS,
                timeout=timeout,
                impersonate="chrome124",
            )
            resp.raise_for_status()
            return resp.content, resp.headers.get("Content-Type", "")
        except ImportError:
            raise RuntimeError(
                f"이미지 다운로드 실패: {primary_err}. "
                "curl_cffi 미설치 — 필요 시 `pip install curl_cffi` 후 재시도."
            ) from primary_err
        except Exception as fallback_err:
            raise RuntimeError(
                f"이미지 다운로드 실패 (기본+impersonation 둘 다): "
                f"primary={primary_err}; fallback={fallback_err}"
            ) from fallback_err


def download_url(url: str, dest_dir: str | Path, index: int) -> Path:
    """외부 이미지 URL → 로컬 파일 저장 → 저장 경로 반환.

    Args:
        url: 외부 이미지 URL
        dest_dir: 저장할 디렉토리 (없으면 자동 생성)
        index: 글 내 이미지 순서 (1-based)

    Returns:
        저장된 파일의 절대 경로 (Path)

    Raises:
        RuntimeError: 다운로드 실패 시
        ValueError: index < 1 또는 url 누락
    """
    if not url:
        raise ValueError("url이 비어있습니다.")
    if index < 1:
        raise ValueError(f"index는 1 이상이어야 합니다. 받은 값: {index}")

    dest = Path(dest_dir).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    data, content_type = _download(url)
    ext = _guess_ext(url, content_type)
    filename = f"img-{index:02d}{ext}"
    out_path = dest / filename
    out_path.write_bytes(data)
    return out_path


def download_local(src_path: str | Path, dest_dir: str | Path, index: int) -> Path:
    """이미 로컬에 있는 이미지를 글 폴더로 복사하여 `img-NN.ext` 정규 이름으로 저장.

    URL이 아니라 사용자가 직접 제공한 로컬 파일을 같은 폴더 구조로 정렬하기 위함.
    """
    if index < 1:
        raise ValueError(f"index는 1 이상이어야 합니다. 받은 값: {index}")

    src = Path(src_path).expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(f"원본 이미지를 찾을 수 없습니다: {src}")

    dest = Path(dest_dir).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    ext = src.suffix.lower() or ".png"
    out_path = dest / f"img-{index:02d}{ext}"
    out_path.write_bytes(src.read_bytes())
    return out_path


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="블로그 본문 이미지를 글 폴더에 img-NN.ext 형태로 저장한다.",
    )
    parser.add_argument(
        "source",
        help="외부 이미지 URL (http/https) 또는 로컬 파일 경로.",
    )
    parser.add_argument(
        "dest_dir",
        help="저장할 폴더. 예: ./my-post-images",
    )
    parser.add_argument(
        "index",
        type=int,
        help="글 내 이미지 순서 (1-based).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    source: str = args.source
    is_url = source.startswith("http://") or source.startswith("https://")
    try:
        if is_url:
            out_path = download_url(source, args.dest_dir, args.index)
        else:
            out_path = download_local(source, args.dest_dir, args.index)
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"[blog_image_collector] 오류: {e}", file=sys.stderr)
        return 1

    # 호출부(agent)가 stdout으로 경로를 읽어 본문에 임베드하므로 줄 끝 newline만 출력
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
