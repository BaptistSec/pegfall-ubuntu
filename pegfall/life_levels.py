import math
from .levels import BLUE as B, ORANGE as O, GREEN as G
from .levels import _arc, _ring, _row, _col, _grid, _mk, Block

def life_boards():
    out = []

    def add(name, sub, pts, balls=11, blocks=(), bumpers=(), hint=''):
        lv = _mk(name, sub, pts, balls, 26000, 52000, hint, bumpers)

        def near_block(p, block, margin=10):
            return math.hypot(max(abs(p.x - block.x) - block.w / 2, 0), max(abs(p.y - block.y) - block.h / 2, 0)) < margin
        blocks = [block for block in blocks if not any((near_block(p, block, 12) for p in lv.pegs if p.kind in (O, G)))]
        lv.pegs = [p for p in lv.pegs if p.kind != B or not any((near_block(p, block, 11) for block in blocks))]
        lv.pegs.extend(blocks)
        for p in lv.pegs:
            p.r = 7.0
        out.append(lv)
    p = _col(300, 180, 8, B, 42) + _col(660, 180, 8, B, 42)
    p += _row(342, 180, 7, B, 46) + _row(342, 516, 7, B, 46)
    p += [(360, 285, O), (600, 285, O), (480, 465, O), (480, 340, G)]
    add('Window Trade', 'Let the work be seen', p, hint='the side lanes reach the window corners')
    p = _arc(480, 345, 185, 15, B, math.pi, 2 * math.pi)
    p += _row(225, 430, 4, B, 40) + _row(615, 430, 4, B, 40)
    p += [(270, 540, O), (480, 390, O), (690, 540, O), (480, 540, G)]
    add('Across the Counter', 'One dependable repair at a time', p, blocks=[Block(x, 465, 32, 12) for x in (260, 302, 658, 700)], hint='break the short counter links or take the open centre')
    p = []
    for sign in (-1, 1):
        for i in range(8):
            p += [(480 + sign * (30 + i * 27), 180 + i * 26, B), (480 + sign * (30 + i * 27), 560 - i * 26, B)]
    p += [(480, 235, O), (355, 370, O), (605, 370, O), (480, 505, O), (480, 370, G)]
    add('A Name for the Work', 'Make a modest mark', p, hint='the diamond has four open faces')
    p = []
    for (row, (x, n)) in enumerate(((190, 5), (430, 5), (190, 5), (430, 5))):
        p += _row(x, 210 + row * 100, n, B, 58)
    p += [(570, 210, O), (335, 310, O), (570, 410, O), (335, 510, O), (480, 590, G)]
    add('Sound Shelves', 'Give each order a place', p, hint='follow the open ends down the shelves')
    p = []
    for (cx, cy) in ((280, 255), (680, 255), (480, 470)):
        p += _ring(cx, cy, 70, 10, B, 0.15) + [(cx, cy - 20, O)]
    p += [(480, 200, G), (480, 580, O)]
    add('Parts and Patience', 'Reinvest in useful stock', p, hint='each drawer is a separate choice, not a sealed box')
    p = _ring(310, 380, 115, 16, B, 0.2) + _ring(650, 380, 115, 16, B, -0.2)
    p += [(310, 285, O), (650, 285, O), (310, 470, O), (650, 470, O), (480, 290, G)]
    add('Second-hand Treadle', 'Earn capacity before comfort', p, blocks=[Block(x, 540, 30, 12) for x in (390, 432, 528, 570)], hint='the paired wheels leave a useful centre lane')
    p = []
    for (cx, cy) in ((240, 310), (480, 250), (720, 310)):
        p += _col(cx - 42, cy - 70, 5, B, 35) + _col(cx + 42, cy - 70, 5, B, 35)
        p += [(cx, cy, O), (cx, cy + 145, O)]
    p += [(480, 540, G)]
    add('City-bound', 'The last order begins', p, balls=12, hint='the open stack centres lead to the lower dispatch pegs')
    p = _grid(210, 180, 8, 4, B, gx=72, gy=65, skip=lambda c, r: (c + r) % 3 == 0)
    p += [(260, 480, O), (480, 430, O), (700, 480, O), (480, 590, O), (480, 280, G)]
    add('The Last Packing', 'Finish the order, pack your life', p, balls=12, blocks=[Block(x, 535, 28, 12) for x in (300, 342, 618, 660)], hint='open a packing bay, then reach the low orange pegs')
    p = []
    for (r, n) in ((295, 23), (230, 18), (165, 13)):
        p += _arc(480, 460, r, n, B, math.pi * 1.05, math.pi * 1.95)
    p += [(480, 200, O), (265, 380, O), (695, 380, O), (365, 500, O), (595, 500, O), (480, 590, O)]
    p += [(205, 540, G), (755, 540, G)]
    add('The Price of Leaving', 'One last order. Then the city.', p, balls=13, blocks=[Block(x, 555, 28, 12) for x in (300, 340, 380, 580, 620, 660)], hint='clear the final order in sections - the side lanes stay open')
    p = _arc(480, 420, 165, 11, B, math.pi, 2 * math.pi)
    p += [(350, 390, O), (480, 320, O), (610, 390, O), (480, 520, G)]
    add('A Bare Room', 'The move bought a chance, not a fortune', p, balls=12, hint='start small again - clear the three open orange pegs')
    p = []
    for i in range(7):
        p += [(240 + i * 31, 410 - i * 29, B), (720 - i * 31, 410 - i * 29, B)]
    p += _row(280, 540, 9, B, 50)
    p += [(320, 460, O), (480, 400, O), (640, 460, O), (480, 550, G)]
    add('A Dry Night', 'Yard wages mend the roof', p, hint='a gap under the roof leaves more than one approach')
    p = []
    for (cx, cy) in ((330, 270), (630, 270), (330, 470), (630, 470)):
        p += _arc(cx, cy, 65, 7, B, math.pi * 0.1, math.pi * 1.9)
        p += [(cx, cy, O)]
    p += [(480, 370, G)]
    add('Borrowed Daylight', 'Glass for the rented room', p, hint='take the windows one pane at a time')
    p = _row(220, 260, 5, B, 48) + _row(390, 370, 5, B, 48) + _row(560, 480, 5, B, 48)
    p += [(280, 340, O), (480, 450, O), (680, 560, O), (480, 260, G)]
    add('The Threshold', 'Keep the hard-won room dry', p, blocks=[Block(310, 410, 40, 12), Block(650, 590, 40, 12)], hint='use the edges of the steps rather than the whole staircase')
    p = _col(280, 310, 7, B, 38) + _col(680, 310, 7, B, 38)
    p += _arc(480, 360, 130, 10, B, math.pi, 2 * math.pi)
    p += [(340, 425, O), (620, 425, O), (480, 540, O), (480, 350, G)]
    add('After Hours', 'Repair a bench, earn a corner', p, blocks=[Block(x, 445, 42, 12) for x in (400, 480, 560)], hint='the borrowed bench top clears like any other blue peg')
    p = []
    for (cx, cy) in ((280, 300), (480, 380), (680, 300)):
        p += _arc(cx, cy, 75, 8, B, math.pi, 2 * math.pi) + [(cx, cy + 40, O)]
    p += [(480, 560, O), (480, 200, G)]
    add('One Tool of Your Own', 'The first city asset', p, hint='the tool roll fans out into open orange pockets')
    p = _col(290, 200, 8, B, 45) + _col(670, 200, 8, B, 45)
    p += _row(350, 260, 6, B, 52) + _row(350, 440, 6, B, 52)
    p += [(340, 350, O), (620, 350, O), (480, 540, O), (480, 350, G)]
    add('A Place for Tools', 'Look after what belongs to you', p, hint='the rack has no solid wall; bank through either side')
    p = _arc(310, 340, 100, 9, B, math.pi, 2 * math.pi) + _arc(650, 340, 100, 9, B, math.pi, 2 * math.pi)
    p += _row(260, 530, 10, B, 49)
    p += [(310, 400, O), (650, 400, O), (480, 590, O), (480, 300, G)]
    add('A Little Stock', 'Keep enough for the next repair', p, hint='leave a lane to the low shelf until you need it')
    p = []
    for (cx, cy) in ((250, 300), (480, 450), (710, 300)):
        p += _arc(cx, cy, 72, 10, B, 0, math.pi) + [(cx, cy - 25, O)]
    p += [(480, 200, G), (480, 580, O)]
    add('Work Comes Back', 'A city reputation takes hold', p, hint='the open baskets reward a patient descending shot')
    p = _ring(480, 330, 100, 12, B, math.pi / 12)
    p += _row(280, 500, 4, B, 42) + _row(554, 500, 4, B, 42)
    p += [(480, 300, O), (340, 440, O), (620, 440, O), (480, 560, G)]
    add('Your Name Again', 'An independent work corner', p, balls=11, hint='the mark is small; the open side routes still matter')
    p = _col(350, 220, 7, B, 46) + _col(610, 220, 7, B, 46)
    p += _row(230, 570, 5, B, 48) + _row(538, 570, 5, B, 48)
    p += [(480, 250, O), (480, 400, O), (480, 540, O), (250, 330, G), (710, 330, G)]
    add('A Finer Grip', 'More precise work earns more trust', p, hint='choose the centre or a long wall bank')
    p = _arc(480, 400, 220, 17, B, math.pi, 2 * math.pi)
    p += _col(270, 435, 4, B, 42) + _col(690, 435, 4, B, 42)
    p += [(350, 510, O), (480, 540, O), (610, 510, O), (480, 360, G)]
    add('A Stronger Bench', 'Build for the orders you have', p, blocks=[Block(x, 445, 30, 12) for x in (330, 370, 460, 500, 590, 630)], hint='break a short link and let the ball into its pocket')
    p = []
    for (cx, cy) in ((270, 270), (690, 270), (270, 490), (690, 490)):
        p += _ring(cx, cy, 60, 8, B, 0.25) + [(cx, cy, O)]
    p += _col(480, 220, 7, B, 48) + [(480, 570, G)]
    add('Every Part Has a Place', 'Order saves time and waste', p, hint='work one drawer at a time or break the central chain')
    p = _ring(480, 370, 225, 18, B, 0.12) + _ring(480, 370, 120, 10, B, 0.18)
    p += [(480, 210, O), (320, 370, O), (640, 370, O), (480, 530, O), (480, 370, G)]
    add('A Sound Machine', 'Retained earnings buy capacity', p, balls=12, hint='use the spaces between the two wheel rims')
    p = []
    for (cx, cy) in ((270, 250), (670, 270), (360, 490), (710, 510)):
        p += _row(cx - 48, cy - 45, 3, B, 48) + _row(cx - 48, cy + 45, 3, B, 48)
        p += [(cx - 48, cy, B), (cx + 48, cy, B), (cx, cy, O)]
    p += [(480, 360, G), (480, 580, O)]
    add('Beyond the Yard', 'Dependable work travels further', p, hint='the dispatch boxes have no solid lids')
    p = _arc(480, 330, 165, 13, B, math.pi, 2 * math.pi)
    p += _col(315, 360, 6, B, 40) + _col(645, 360, 6, B, 40)
    p += [(480, 250, O), (380, 460, O), (580, 460, O), (480, 580, O), (480, 380, G)]
    add('A Door of Your Own', 'One leased workshop room', p, balls=12, hint='the doorway is open below the arch')
    p = []
    for i in range(9):
        p += [(200 + i * 29, 430 - i * 27, B), (760 - i * 29, 430 - i * 27, B)]
    p += _row(240, 560, 5, B, 48) + _row(530, 560, 5, B, 48)
    p += [(330, 450, O), (630, 450, O), (480, 330, O), (480, 580, G)]
    add('Under Cover', 'Protect what the work has earned', p, hint='clear a rafter or take the open central drop')
    p = _ring(480, 245, 85, 10, B, 0.2) + _ring(480, 475, 100, 12, B, 0.2)
    p += _col(250, 230, 7, B, 49) + _col(710, 230, 7, B, 49)
    p += [(480, 245, O), (480, 475, O), (300, 590, O), (660, 590, O), (480, 360, G)]
    add('A Room Above', 'A steady home beside the work', p, hint='the two windows offer separate approaches')
    p = _arc(480, 420, 210, 15, B, math.pi, 2 * math.pi)
    p += _arc(480, 420, 140, 10, B, 0, math.pi)
    p += [(310, 375, O), (480, 300, O), (650, 375, O), (480, 530, O), (480, 420, G)]
    add('Room for Care', 'A small planter, not a palace', p, hint='the planter leaves wide sky between its branches')
    p = _arc(480, 430, 230, 19, B, math.pi, 2 * math.pi)
    p += _arc(480, 430, 150, 13, B, math.pi, 2 * math.pi)
    p += _arc(480, 430, 85, 7, B, math.pi, 2 * math.pi)
    p += [(480, 310, O), (365, 410, O), (595, 410, O), (280, 560, O), (680, 560, O)]
    p += [(480, 535, G)]
    add('Ground of Your Own', 'The same small hopes, a life rebuilt', p, balls=13, blocks=[Block(x, 585, 28, 12) for x in (360, 400, 560, 600)], hint='a familiar sunrise, earned again in the city')
    assert len(out) == 29
    return out
