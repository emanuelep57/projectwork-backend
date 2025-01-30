from dataclasses import dataclass


@dataclass
class PostoDTO:
    id: int
    fila: str
    numero: int

    @classmethod
    def from_model(cls, posto):
        return cls(
            id=posto.id,
            fila=posto.fila,
            numero=posto.numero
        )

    def to_dict(self):
        return {
            'id': self.id,
            'fila': self.fila,
            'numero': self.numero
        }


@dataclass
class PostoOccupatoDTO:
    fila: str
    numero: int

    @classmethod
    def from_model(cls, posto):
        return cls(
            fila=posto.fila,
            numero=posto.numero
        )

    def to_dict(self):
        return {
            'fila': self.fila,
            'numero': self.numero
        }
