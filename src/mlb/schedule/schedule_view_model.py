from mlb.models.game_detail import GameDetail

class ScheduleViewModel:
    def __init__(self, game1: GameDetail, game2: GameDetail, game3: GameDetail):
        self.game1 = game1
        self.game2 = game2
        self.game3 = game3

    def has_live_game(self):
        return (self._is_live(self.game1) or self._is_live(self.game2) or self._is_live(self.game3))

    def _is_live(self, game: GameDetail):
        return ((game is not None) and (game.isLive))

    def _is_preview(self, game: GameDetail):
        return ((game is not None) and (game.status == "Preview"))

    def get_next_game_start_utc(self):
        """Returns the start time of the next Preview game in the set. Returns None if there are none."""
        for g in [self.game1, self.game2, self.game3]:
            if self._is_preview(g):
                return g.dateTimeUtc
        return None
        
