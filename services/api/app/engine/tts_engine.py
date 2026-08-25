import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

import edge_tts
import imageio_ffmpeg

logger = logging.getLogger("framescout.engine.tts")

SUPPORTED_VOICES: Dict[str, str] = {
    "pt-BR-AntonioNeural": "Antonio (Masculino, Natural)",
    "pt-BR-FranciscaNeural": "Francisca (Feminino, Expressivo)",
    "pt-BR-ThalitaNeural": "Thalita (Feminino, Jovem)",
    "en-US-GuyNeural": "Guy (English, US)",
    "en-US-JennyNeural": "Jenny (English, US)",
}


class TTSEngine:
    @staticmethod
    def list_voices() -> List[Dict[str, str]]:
        return [
            {"id": voice_id, "name": label}
            for voice_id, label in SUPPORTED_VOICES.items()
        ]

    @staticmethod
    async def synthesize(
        text: str,
        voice: str = "pt-BR-AntonioNeural",
        output_path: str = "/tmp/scene_audio.mp3",
    ) -> float:
        """
        Sintetiza a narração da cena em arquivo MP3 e retorna a duração exata em segundos.
        Recorre ao gerador de áudio sintético determinístico se a conexão Edge-TTS falhar.
        """
        clean_text = text.strip()
        if not clean_text:
            clean_text = "..."

        if voice not in SUPPORTED_VOICES:
            voice = "pt-BR-AntonioNeural"

        out_p = Path(output_path).resolve()  # noqa: ASYNC240
        out_p.parent.mkdir(parents=True, exist_ok=True)  # noqa: ASYNC240

        try:
            communicate = edge_tts.Communicate(clean_text, voice)
            await asyncio.wait_for(communicate.save(str(out_p)), timeout=25.0)
            duration = TTSEngine.get_audio_duration(str(out_p))
            if duration > 0.1:
                return duration
            return TTSEngine._generate_fallback_audio(clean_text, str(out_p))
        except Exception as exc:
            logger.warning(
                f"Edge-TTS indisponível ({exc}). Gerando áudio de contingência."
            )
            return TTSEngine._generate_fallback_audio(clean_text, str(out_p))

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Obtém a duração exata do arquivo de áudio utilizando o binário do FFmpeg."""
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_bin,
            "-i",
            file_path,
            "-f",
            "null",
            "-",
        ]
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            for line in res.stderr.splitlines():
                if "time=" in line:
                    parts = line.split("time=")[1].split()[0]
                    h, m, s = parts.split(":")
                    return float(h) * 3600 + float(m) * 60 + float(s)
            return 3.0
        except Exception:
            return 3.0

    @staticmethod
    def _generate_fallback_audio(text: str, output_path: str) -> float:
        """Gera um arquivo de áudio de silêncio proporcional ao número de palavras."""
        words = len(text.split())
        est_duration = max(2.0, round((words / 2.5), 1))

        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_bin,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            str(est_duration),
            "-q:a",
            "9",
            "-acodec",
            "libmp3lame",
            output_path,
        ]
        try:
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return est_duration
        except Exception:
            with open(output_path, "wb") as f:
                f.write(b"ID3" + b"\x00" * 1024)
            return est_duration
