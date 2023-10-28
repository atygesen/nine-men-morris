from nnm.colors import WHITE, BLACK, GREEN, RED
from nnm.board import Board, Player
from nnm.board_screen import BoardScreen
from nnm.rules.rules import Rules, Phase
from nnm.ai.rand_ai import RandomAI
from nnm.ai.minimax import MinimaxAI
from nnm.ai.ai import AI

from pygame.draw import circle, line
import pygame

PIECE_SIZE = 15


class NineMenMorris:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background = WHITE
        w, h = self.screen.get_size()
        self.w = w
        self.h = h

        self.board = Board()
        self.board_screen = BoardScreen(w, h, self.board)
        self.delete_spot_state = False
        self.selected_pos = None

        self.rules = Rules(self.board)

        ai = RandomAI()
        ai = MinimaxAI(
            self.board.players[1], self.rules, max_depth=4
        )
        self.board.players[1].ai = ai
        # ai.evaluator.load_brain()

    def is_ai_turn(self):
        return self.current_player.ai is not None

    def play_ai(self) -> None:
        player = self.current_player
        ai: AI = player.ai
        if ai is None:
            raise RuntimeError("Player is not an AI")
        choice = ai.get_best_move()
        # print("AI choice:", choice)
        self.rules.execute_move(choice)
        # print("State", self.board.get_board_state())

        # print("Evaluation", player.name, ai.evaluator.evaluate())
        # print(ai.evaluator._get_blocked_pieces(player))
        self.rules.next_turn()
        # time.sleep(0.5)

    def event_handler(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_game_over():
                print("Game is over")
                return
            if not self.current_player.ai:
                self._do_player_move()

    def _do_player_move(self) -> bool:
        """Returns whether the turn should be passed."""
        x, y = pygame.mouse.get_pos()

        phase = self.get_phase()
        spot = self.board_screen.get_closest_index(x, y)
        pass_turn = False

        # print("Phase", phase)

        # Player logic
        if self.delete_spot_state:
            if self.board.can_delete(spot):
                try:
                    self.board.remove_piece(spot)
                except ValueError:
                    # Invalid
                    pass
                else:
                    self.delete_spot_state = False
                    pass_turn = True
        elif phase is Phase.ONE:
            if self.board.is_available(spot):
                is_mill = self.board.place_piece(
                    spot, self.current_player, check_mill=True
                )
                if is_mill:
                    self.delete_spot_state = True
                else:
                    pass_turn = True
        else:
            # Movement phase
            if self.selected_pos is None and self.board.is_own_piece(spot):
                self.selected_pos = spot
                # print("Selected", spot)
            elif self.selected_pos == spot:
                self.selected_pos = None
            elif self.selected_pos is not None:
                try:
                    self.board.move_piece(
                        self.selected_pos,
                        spot,
                        player=self.current_player,
                        flying=phase is Phase.THREE,
                    )
                except ValueError as e:
                    # Invalid move
                    print("Move error", e)
                else:
                    self.selected_pos = None
                    if self.board.is_in_mill(spot, self.current_player):
                        self.delete_spot_state = True
                    else:
                        pass_turn = True
        if pass_turn:
            self.board.toggle_player()
            self.rules.next_turn()
        # print("Closest index", spot, self.selected_pos)
        return pass_turn

    @property
    def turn(self) -> int:
        return self.board.ply // 2

    @property
    def current_player(self):
        return self.board.current_player

    def get_phase(self) -> Phase:
        return self.rules.get_phase()

    def is_game_over(self) -> bool:
        return self.rules.is_game_over()

    def get_winner(self) -> Player:
        players = self.board.players
        return max(players, key=lambda p: self.board.get_player_pieces_on_board(p))

    def draw(self) -> None:
        self.screen.fill(self.background)

        my_font = pygame.font.SysFont("arial", 20)
        title = my_font.render(
            f"Ply: {self.board.ply}, Turn: {self.turn}, Phase: {self.get_phase()}, player: {self.board.current_player.name}, deletion: {self.delete_spot_state}",
            True,
            BLACK,
        )
        text_rect = title.get_rect(center=(self.w / 2, 15))
        self.screen.blit(title, text_rect)

        counts = self.board.get_piece_counts()
        cnt = my_font.render(f"Counts: {counts}", True, BLACK)
        text_rect = title.get_rect(center=(self.w / 2, 35))
        self.screen.blit(cnt, text_rect)

        for coord in self.board_screen.spot_coordinates:
            circle(self.screen, BLACK, coord.as_tuple(), 6)

        for pos1, pos2 in self.board_screen.connections_coordinates:
            line(self.screen, BLACK, pos1.as_tuple(), pos2.as_tuple())

        for coord, player in self.board_screen.get_piece_coords():
            # Check if it's a "selected" piece
            color = player.color if coord.index != self.selected_pos else GREEN
            circle(
                self.screen,
                color,
                coord.as_tuple(),
                PIECE_SIZE,
            )

        if self.is_game_over():
            if self.rules.get_phase() is Phase.DRAW:
                title = my_font.render(f"GAME OVER, DRAW", True, RED)
            else:
                winner = self.get_winner()
                title = my_font.render(f"GAME OVER, {winner.name} WON", True, RED)
            text_rect = title.get_rect(center=(self.w / 2, self.h / 2))
            self.screen.blit(title, text_rect)

    def reset(self):
        self.board.reset()
        self.rules.reset()
