from nnm.colors import WHITE, BLACK, GREEN, RED
from nnm.board import Board
from nnm.rules.rules import Rules, Phase
from nnm.ai.rand_ai import RandomAI
from nnm.ai.minimax import MinimaxAI
from nnm.ai.ai import AI

from pygame.draw import circle, line
import pygame

import time

PIECE_SIZE = 15


class NineMenMorris:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background = WHITE
        w, h = self.screen.get_size()
        self.w = w
        self.h = h

        self.board = Board(self.w, self.h)
        self.delete_spot_state = False
        self.selected_pos = None

        self.rules = Rules(self.board)

        # ai = RandomAI()
        ai = MinimaxAI(self.board.players[1], self.board.players[0], self.rules, max_depth=2)
        self.board.players[1].ai = ai

    def event_handler(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_game_over():
                print("Game is over")
                return
            pass_turn = False
            if not self.current_player.ai:
                pass_turn = self._do_player_move()

            if pass_turn and self.current_player.ai and not self.is_game_over():
                # Instantaneously execute the AI turn.
                ai: AI = self.current_player.ai
                moves = self.rules.get_current_player_moves()
                choice = ai.select_move(moves)
                print("AI choice:", choice)
                self.rules.execute_move(choice)

    def _do_player_move(self) -> bool:
        """Returns whether the turn should be passed."""
        x, y = pygame.mouse.get_pos()

        phase = self.get_phase()
        spot = self.board.get_closest_spot(x, y)
        pass_turn = False

        # Player logic
        if self.delete_spot_state:
            success = self.board.delete_spot(spot)
            if success:
                self.delete_spot_state = False
                pass_turn = True
        elif phase is Phase.ONE:
            if self.board.is_available(spot):
                success = self.board.place_piece(spot)
                if success:
                    # Was able to place a piece
                    if self.board.has_three_in_a_line(must_contain=spot):
                        self.delete_spot_state = True
                    else:
                        pass_turn = True
        else:
            # Movement phase
            if not self.selected_pos and self.board.is_own_piece(spot):
                self.selected_pos = spot
            elif self.selected_pos == spot:
                self.selected_pos = None
            elif self.selected_pos:
                is_flying = phase is Phase.THREE
                success = self.board.move_piece(
                    self.selected_pos, spot, flying=is_flying
                )
                if success:
                    self.selected_pos = None
                    if self.board.has_three_in_a_line(must_contain=spot):
                        self.delete_spot_state = True
                    else:
                        pass_turn = True
        if pass_turn:
            self.board.toggle_player()
        return pass_turn

    @property
    def turn(self) -> int:
        return self.board.ply // 2

    @property
    def current_player(self):
        return self.board.player

    def get_phase(self) -> Phase:
        return self.rules.get_phase()

    def is_game_over(self) -> bool:
        return self.rules.is_game_over()

    def get_winner(self):
        counts = self.board.get_player_piece_counts()
        counts.pop(None)
        return max(((k, v) for k, v in counts.items()), key=lambda tup: tup[1])[0]

    def draw(self) -> None:
        self.screen.fill(self.background)

        my_font = pygame.font.SysFont("arial", 20)
        title = my_font.render(
            f"Ply: {self.board.ply}, Turn: {self.turn}, Phase: {self.get_phase()}, player: {self.board.player.name}, deletion: {self.delete_spot_state}",
            True,
            BLACK,
        )
        text_rect = title.get_rect(center=(self.w / 2, 15))
        self.screen.blit(title, text_rect)

        counts = [p.pieces_on_hand for p in self.board.players]
        cnt = my_font.render(f"Counts: {counts}", True, BLACK)
        text_rect = title.get_rect(center=(self.w / 2, 35))
        self.screen.blit(cnt, text_rect)

        for coord in self.board.spot_coordinates:
            circle(self.screen, BLACK, coord.as_tuple(), 6)

        for pos1, pos2 in self.board.connections_coordinates:
            line(self.screen, BLACK, pos1.as_tuple(), pos2.as_tuple())

        for pos, player in self.board.pieces.items():
            if player is not None:
                # Check if it's a "selected" piece
                color = player.color if pos != self.selected_pos else GREEN
                circle(
                    self.screen,
                    color,
                    self.board.as_coord(pos).as_tuple(),
                    PIECE_SIZE,
                )

        if self.is_game_over():
            winner = self.get_winner()
            title = my_font.render(f"GAME OVER, {winner.name} WON", True, RED)
            text_rect = title.get_rect(center=(self.w / 2, self.h / 2))
            self.screen.blit(title, text_rect)
