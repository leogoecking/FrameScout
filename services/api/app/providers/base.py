from abc import ABC, abstractmethod
from typing import List

from app.domain.schemas import MediaCandidateBase, SearchQueryBase


class MediaProvider(ABC):
    """
    Interface abstrata obrigatória para qualquer provedor de mídia externo.
    Isola completamente o domínio de detalhes de chamadas de API externas.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Identificador único do provider (ex: 'pexels', 'wikimedia')."""
        pass

    @abstractmethod
    async def search(self, query: SearchQueryBase, limit: int = 10) -> List[MediaCandidateBase]:
        """
        Executa a busca de candidatos de mídia para uma determinada query.
        Deve preencher 'rights_status' com base em dados de licença e procedência.
        """
        pass
