class GameState():
    def __init__(self) -> None:
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],]

        self.moveFunctions = {
            'p': self.getPawnMoves, 'R':self.getRookMoves, 'N':self.getKnightMoves,
            'B':self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves 
        }   
        self.whiteToMove =  True
        self.moveLog = []

        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)

        self.checkMate = False
        self.staleMate = False

        self.enpassantPossible = ()

        self.currentCastlingRight = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                    self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
       
       

    def makeMove(self, move):
        # making the startSq empty
        self.board[move.startRow][move.startCol] = '--'
        # moving the piece
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # appending move to the movelog
        self.moveLog.append(move)
        # changes turn
        self.whiteToMove = not self.whiteToMove
        # checking if the kings were moved to update there locations
        if move.pieceMoved == 'wK':
            self.whiteKingLoc = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLoc = (move.endRow, move.endCol)

        # promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'

        # update castling rights - whenever king or rook move is played
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

        
                

    def undoMove(self):
        if len(self.moveLog) != 0:
            # removing move form log
            move = self.moveLog.pop()
            # reversing make move
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # changing turn
            self.whiteToMove = not self.whiteToMove
            # checking if the kings were moved to update there locations
            if move.pieceMoved == 'wK':
                self.whiteKingLoc = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLoc = (move.startRow, move.startCol)

            # undoing enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
                
            # undoing castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
            
            # undoing castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]
            


    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
                

                

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # gets all move
        moves = self.getAllMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLoc[0], self.whiteKingLoc[1], moves)
        else:
            self.getCastleMoves(self.blackKingLoc[0], self.blackKingLoc[1], moves)
        # goes backwords through the list
        for i in range(len(moves)-1,-1,-1):
            # makes the move and changes turn
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # sees if that previous move puts the player in check
                moves.remove(moves[i])
            # changes turn back and undoes the move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        # checks if there are no valid moves (either: stalemate or checkmate)
        if len(moves) == 0:
            # sees if in check or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.stalemate = True
        
        # all the valid moves
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    def inCheck(self):
        # checks which turn
        if self.whiteToMove:
            # returns a bool and checks if the whiite king is under attack
            return self.squareUnderAttack(self.whiteKingLoc[0], self.whiteKingLoc[1])
        else:
            # then checks black king
            return self.squareUnderAttack(self.blackKingLoc[0], self.blackKingLoc[1])

    def squareUnderAttack(self, r, c):
        # sees opponent moves by changing turn gets all there moves and changes back turn
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllMoves()
        self.whiteToMove = not self.whiteToMove
        # checks all moves and sees if the end square is the square entered in the function
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False 


    def getAllMoves(self):
        # initialising the move list
        moves = []
        # going through each element in the list
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                # checking piece colour
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    # using dictionary to reduce if statements
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves





    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r,c), (r-1,c), self.board, legalMove = True))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c), (r-2,c), self.board, legalMove = True))
            if c-1 > 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board,legalMove = True))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board,isEnpassantMove=True,legalMove = True))

            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board, legalMove = True))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board,isEnpassantMove=True, legalMove = True))

        if not self.whiteToMove:
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c), (r+1,c), self.board, legalMove = True))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c), (r+2,c), self.board, legalMove = True))
            if c-1 > 0:
                if self.board[r+1][c-1][0] == 'w':
                   moves.append(Move((r, c), (r+1, c-1), self.board, legalMove = True))

                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board,isEnpassantMove=True, legalMove = True))
                
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board, legalMove = True))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board,isEnpassantMove=True, legalMove = True))

    def getRookMoves(self,r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemypiece = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0  <= (r + d[0] * i) < 8 and 0 <= endCol < 8:
                    endpiece = self.board[(r + d[0] * i)][endCol]
                    if endpiece == "--":
                        moves.append(Move((r, c), (r + d[0] * i, endCol), self.board, legalMove = True))
                    elif endpiece[0] == enemypiece:
                        moves.append(Move((r, c), (r + d[0] * i, endCol), self.board, legalMove = True))
                        break
                    else: 
                        break
                else:
                    break

    def getBishopMoves(self,r,c,moves):
        directions = ((-1, 1), (1, -1), (-1, -1), (1, 1))
        enemypiece = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0  <= endRow < 8 and 0 <= endCol < 8:
                    endpiece = self.board[endRow][endCol]
                    if endpiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board, legalMove = True))
                    elif endpiece[0] == enemypiece:
                        moves.append(Move((r, c), (endRow, endCol), self.board, legalMove = True))
                        break
                    else: 
                        break
                else:
                    break

    def getKnightMoves(self,r,c,moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),(1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
                endRow = r + m[0] 
                endCol = c + m[1]
                if 0  <= endRow < 8 and 0 <= endCol < 8:
                    endpiece = self.board[endRow][endCol]
                    if endpiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board, legalMove = True))

    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self,r,c,moves):
        directions = ((-1,-1), (1,-1), (1,1), (-1,1), (-1,0), (0,-1), (1,0), (0,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board, legalMove = True))

    def getCastleMoves(self, r, c, moves):
        # cant castle if a aquare a is under attack
        if self.squareUnderAttack(r, c):
            return
        # can move there
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove = True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))




class CastleRights():
    def __init__(self, wks, bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}



    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False, legalMove = False):
        # start location/square
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        # end location/square
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        # piece moved/captured
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # bool to see if either black or white pawn has been moved to the end row
        self.isPawnPromotion = ((self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))
        
        self.isEnpassantMove = isEnpassantMove
        
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCastleMove = isCastleMove
        self.legalMove = legalMove

        # to compare the moves
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol




    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        startSquare = self.getRankFile(self.startRow, self.startCol)
        endSquare = self.getRankFile(self.endRow, self.endCol)
            
        if (self.pieceMoved[1] != 'p' or self.pieceMoved[1] != '-') and self.pieceCaptured != '--':
            return self.pieceMoved[1] + 'x' + endSquare
        elif self.pieceMoved[1] == 'p' and self.pieceCaptured != '--' or self.isEnpassantMove:
            return startSquare[0] + 'x' + endSquare
        elif self.pieceMoved[1] != 'p':
            return self.pieceMoved[1] + endSquare
        elif self.pieceMoved[1] == 'p':
            return endSquare
        else:
            pass


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]












