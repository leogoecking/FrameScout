import logging
import os
import subprocess
from typing import List, Tuple

import imageio_ffmpeg

logger = logging.getLogger("framescout.engine.video")


class VideoComposer:
    @staticmethod
    def get_dimensions(aspect_ratio: str) -> Tuple[int, int]:
        if aspect_ratio == "9:16":
            return 1080, 1920
        return 1920, 1080

    @staticmethod
    def render_scene_clip(
        media_path: str,
        audio_path: str,
        output_clip_path: str,
        duration: float,
        framing_mode: str = "FILL",
        aspect_ratio: str = "16:9",
        narration_text: str = "",
    ) -> str:
        """
        Renderiza o clipe visual de uma cena única combinando imagem/vídeo,
        enquadramento (FILL, FIT, PAN_AND_ZOOM) e narração em áudio.
        """
        w, h = VideoComposer.get_dimensions(aspect_ratio)
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        os.makedirs(os.path.dirname(os.path.abspath(output_clip_path)), exist_ok=True)

        is_video = media_path.lower().endswith((".mp4", ".mov", ".webm", ".mkv"))
        has_media = os.path.exists(media_path) and os.path.getsize(media_path) > 0

        if not has_media:
            return VideoComposer._render_fallback_card(
                audio_path, output_clip_path, duration, w, h, narration_text
            )

        fps = 30
        total_frames = max(30, int(duration * fps))

        if is_video:
            filter_str = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
            cmd = [
                ffmpeg_bin,
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                media_path,
                "-i",
                audio_path,
                "-t",
                str(duration),
                "-vf",
                filter_str,
                "-r",
                str(fps),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                output_clip_path,
            ]
        else:
            if framing_mode == "PAN_AND_ZOOM":
                z_expr = "min(zoom+0.0015,1.25)"
                filter_str = (
                    f"zoompan=z='{z_expr}':d={total_frames}:fps={fps}:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h},scale={w}:{h}"
                )
            elif framing_mode == "FIT":
                filter_str = (
                    f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                    f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black"
                )
            else:  # FILL
                filter_str = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"

            cmd = [
                ffmpeg_bin,
                "-y",
                "-loop",
                "1",
                "-i",
                media_path,
                "-i",
                audio_path,
                "-t",
                str(duration),
                "-vf",
                filter_str,
                "-r",
                str(fps),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-tune",
                "stillimage",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                output_clip_path,
            ]

        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if res.returncode != 0:
                err_msg = res.stderr.decode("utf-8", "ignore")
                logger.warning(f"Falha ao renderizar clipe visual ({err_msg}). Usando fallback.")
                return VideoComposer._render_fallback_card(
                    audio_path, output_clip_path, duration, w, h, narration_text
                )
            return output_clip_path
        except Exception as exc:
            logger.warning(f"Erro no FFmpeg: {exc}. Recorrendo ao fallback.")
            return VideoComposer._render_fallback_card(
                audio_path, output_clip_path, duration, w, h, narration_text
            )

    @staticmethod
    def _render_fallback_card(
        audio_path: str,
        output_clip_path: str,
        duration: float,
        w: int,
        h: int,
        narration_text: str,
    ) -> str:
        """Gera um clipe de fallback com fundo cinemático escuro."""
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_bin,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x0f172a:s={w}x{h}:r=30",
            "-i",
            audio_path,
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            output_clip_path,
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return output_clip_path

    @staticmethod
    def render_credits_card(
        attributions: List[str],
        duration: float,
        output_path: str,
        aspect_ratio: str = "16:9",
    ) -> str:
        """Renderiza um slide final de créditos legais com fundo escuro."""
        w, h = VideoComposer.get_dimensions(aspect_ratio)
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cmd = [
            ffmpeg_bin,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x020617:s={w}x{h}:r=30",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            output_path,
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return output_path

    @staticmethod
    def concatenate_clips(
        clip_paths: List[str],
        final_output_path: str,
    ) -> str:
        """Concatena múltiplos clipes MP4 em um arquivo final de vídeo."""
        if not clip_paths:
            raise ValueError("Nenhum clipe disponível para concatenação.")

        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        os.makedirs(os.path.dirname(os.path.abspath(final_output_path)), exist_ok=True)

        concat_txt_path = final_output_path + ".txt"
        with open(concat_txt_path, "w", encoding="utf-8") as f:
            for p in clip_paths:
                # Escape single quotes properly for FFmpeg concat format
                safe_path = os.path.abspath(p).replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

        cmd = [
            ffmpeg_bin,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_txt_path,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            final_output_path,
        ]

        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if res.returncode != 0:
                err_msg = res.stderr.decode("utf-8", "ignore")
                raise RuntimeError(f"Falha ao concatenar vídeo: {err_msg}")
            return final_output_path
        finally:
            if os.path.exists(concat_txt_path):
                try:
                    os.remove(concat_txt_path)
                except Exception:
                    pass
