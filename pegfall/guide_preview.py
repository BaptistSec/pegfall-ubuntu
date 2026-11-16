from . import physics
_FIELDS = (('x', None), ('y', None), ('alive', True), ('kind', None), ('shape', 'circle'), ('r', physics.PEG_R), ('angle', 0.0), ('w', 0.0), ('h', 0.0), ('rest', physics.RESTITUTION), ('kick', 0.0), ('vx', 0.0), ('lit', False))

class GuidePreview:

    def __init__(self):
        self.clear()

    def clear(self):
        self._game = None
        self._key = None
        self._points = None

    def points(self, game, x, y):
        pegs = game.collision_pegs()
        geometry = tuple((tuple((getattr(peg, name, default) for (name, default) in _FIELDS)) for peg in pegs))
        board = game.board
        key = (x, y, game.aim, board.left, board.right, board.top, geometry)
        if self._game is not game or self._key != key:
            points = physics.predict_path(x, y, game.aim, pegs, board)
            self._game = game
            self._key = key
            self._points = points
        return self._points
