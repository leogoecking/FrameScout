import asyncio
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("framescout.worker")


class FrameScoutWorker:
    def __init__(self):
        self._running = True

    def stop(self, *args):
        logger.info("Encerrando worker...")
        self._running = False

    async def run(self):
        logger.info("Iniciando FrameScout Background Worker (Sprint 0 Scaffold)...")
        logger.info("Worker pronto para processar filas assíncronas (Redis/Celery/SigLIP em sprints futuros).")

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.stop)

        while self._running:
            # Heartbeat do worker
            logger.debug("Worker heartbeat: aguardando tarefas...")
            await asyncio.sleep(5)

        logger.info("Worker finalizado com sucesso.")


def main():
    worker = FrameScoutWorker()
    try:
        asyncio.run(worker.run())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker interrompido.")
        sys.exit(0)


if __name__ == "__main__":
    main()
