class Literal:
    def __init__(self,byte:int):
        self.byte = byte
    def __repr__(self):
        return f"Literal({self.byte})"
class Match:
    def __init__(self, length:int, distance:int):
        self.length = length
        self.distance = distance
    def __repr__(self):
        return f"Match(length={self.length}, distance={self.distance})"
class LiteralEvent:
    def __init__(self, symbol: int):
        self.symbol = symbol
    def __repr__(self):
        return f"LiteralEvent({self.symbol})"
class MatchEvent:
    def __init__(self, length_symbol:int, length_extra: str,
                 distance_symbol:int, distance_extra:str):
        self.length_symbol= length_symbol
        self.length_extra = length_extra
        self.distance_symbol= distance_symbol
        self.distance_extra = distance_extra
    def __repr__(self):
        return (f"MatchEvent({self.length_symbol}, \"{self.length_extra}\", "
                f"{self.distance_symbol}, \"{self.distance_extra}\")")
class EndEvent:
    def __init__(self):
        self.symbol= 256

    def __repr__(self):
        return "EndEvent(256)"