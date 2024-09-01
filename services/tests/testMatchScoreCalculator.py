# tests:
# 1. game doesn't end:
#   - game 0:0 set 0:0 p1
#   - game 30:30 set 0:0 p2
#   - game 40:40 set 0:0 p1
#   - game less:more set 0:0 p1
# 2. game ends:
#   - game 40:0 set 0:0 p1
#   - game less:more set 0:0 p2
# 3. set doesn't end:
#   - game 15:0 set 0:0 p1
#   - game 40:0 set 5:5 p1
#   - game 40:0 set 1:3 p1
#   - tiebreak 3:4 set 6:6 p1
#   - tiebreak 6:7 set 6:6 p1
# 4. set ends:
#   - game 30:40 set 4:5 p2
#   - tiebreak 5:6 set 6:6 p2
# 5. deuce starts:
#   - game 30:40 set 0:0 p1
# 6. tiebreak starts:
#   - game 0:40 set 6:5 p2
# 7. match ends:
#   - game more:less set 6:5 sets 1:1
#   - game 30:40 set 5:6 sets 0:1
#   - tiebreak 7:6 set 5:1 sets 1:1
