#pragma once
#include <iostream>
#include <string>
#include <vector>

#include "connections.hpp"

const int EMPTY = -1;
const int FIELDS = 24;

struct CandidateMove {
    int from_pos;
    int to_pos;
    int delete_pos = EMPTY;

    CandidateMove(int from_pos, int to_pos, int delete_pos)
        : from_pos(from_pos), to_pos(to_pos), delete_pos(delete_pos) {
    }
    CandidateMove(int from_pos, int to_pos) : from_pos(from_pos), to_pos(to_pos) {
    }
};

struct CandidatePlacement {
    int pos;
    int delete_pos = EMPTY;

    CandidatePlacement(int pos, int delete_pos) : pos(pos), delete_pos(delete_pos) {
    }
    CandidatePlacement(int pos) : pos(pos) {
    }
};
class Board {
   public:
    Board() {
        this->reset();
    }

    void reset();

    int pieces_on_board(int player) const;

    void place_piece(int position) {
        this->place_piece(position, (int)this->turn_index);
    }

    void place_piece(int position, int player);

    void temp_place_piece(int position, int player);

    void remove_piece(int position) {
        remove_piece(position, this->turn_index);
    };

    void remove_piece(int position, int player);

    bool can_delete(int pos, int player);

    void give_piece() {
        if (this->turn_index == 0) {
            playerOnePieces++;
        } else {
            playerTwoPieces++;
        }
    };

    void move_piece(int from, int to) {
        move_piece(from, to, this->turn_index);
    };

    void move_piece(int from, int to, int player);

    void move_piece_flying(int from, int to) {
        move_piece_flying(from, to, this->turn_index);
    }

    void move_piece_flying(int from, int to, int player);

    bool is_connected(int pos1, int pos2);

    bool is_mill(int a, int b, int c);

    bool check_mill(int position, int player);

    int getPlayerOnePieces() {
        return playerOnePieces;
    };

    int getPlayerTwoPieces() {
        return playerTwoPieces;
    };

    int get_player_pieces_on_hand(int player) const;

    inline std::vector<int> &getBoard() {
        return board;
    };

    bool is_available(int pos);

    inline int get_owner(int pos) {
        return board[pos];
    };

    int get_board_hash();

    void toggle_turn() {
        this->turn_index ^= 1;
        this->ply += 1;
    };

    void reverse_turn() {
        this->turn_index ^= 1;
        this->ply -= 1;
    };

    void execute_move(CandidateMove move);
    void execute_move(CandidatePlacement move);
    void undo_move(CandidateMove move);
    void undo_move(CandidatePlacement move);

    int get_turn_index() const {
        return turn_index;
    };
    int get_ply() const {
        return ply;
    };

   private:
    std::vector<int> board;
    int playerOnePieces;
    int playerTwoPieces;
    unsigned int turn_index = 0;
    unsigned int ply = 0;
};

class MoveFinder {
   public:
    MoveFinder(Board *board) : m_board_ptr(board) {
    }

    std::vector<CandidatePlacement> get_phase_one_moves(int player) const {
        std::vector<CandidatePlacement> moves;

        for (int pos = 0; pos < FIELDS; pos++) {
            int owner = this->m_board_ptr->get_owner(pos);
            if (owner != EMPTY) continue;
            m_board_ptr->temp_place_piece(pos, player);
            if (m_board_ptr->check_mill(pos, player)) {
                // We can delete
                int other_player = player ^ 1;
                for (int to_delete = 0; to_delete < FIELDS; to_delete++) {
                    if (m_board_ptr->get_owner(to_delete) == other_player) {
                        moves.emplace_back(pos, to_delete);
                    }
                }
            } else {
                moves.emplace_back(pos, EMPTY);
            }
            m_board_ptr->remove_piece(pos, EMPTY);  // Trick, we are removing our own piece.
        }
        return moves;
    }

    std::vector<CandidateMove> get_movement_phase_moves(int player, bool is_flying) const {
        std::vector<CandidateMove> moves;

        for (int from_pos = 0; from_pos < FIELDS; from_pos++) {
            if (m_board_ptr->get_owner(from_pos) != player) continue;
            for (int to_pos = 0; to_pos < FIELDS; to_pos++) {
                // Either not empty, or unconnected phase 2
                if (m_board_ptr->get_owner(to_pos) != EMPTY ||
                    (!is_flying && !m_board_ptr->is_connected(from_pos, to_pos)))
                    continue;
                // No need to check for connections at this stage anymore.
                m_board_ptr->move_piece_flying(from_pos, to_pos, player);
                if (m_board_ptr->check_mill(to_pos, player)) {
                    // Check deletion
                    for (int to_delete = 0; to_delete < FIELDS; to_delete++) {
                        if (m_board_ptr->can_delete(to_delete, player)) {
                            moves.emplace_back(from_pos, to_pos, to_delete);
                        }
                    }
                } else {
                    moves.emplace_back(from_pos, to_pos);
                }
                m_board_ptr->move_piece_flying(to_pos, from_pos, player);  // Undo movement
            }
        }
        return moves;
    }

    int get_phase() const {
        // Cannot determine draws!
        int player = m_board_ptr->get_turn_index();
        if (m_board_ptr->get_player_pieces_on_hand(player) > 0) {
            return 1;
        }
        // No valid moves, game is over!
        if (!has_available_move(player)) return -1;

        // Check win condition for both players
        int piece_cnt = m_board_ptr->pieces_on_board(player);
        int piece_other = m_board_ptr->pieces_on_board(player ^ 1);
        if (piece_cnt < 3 || piece_other < 3) {
            // Done, either we or the other play has insufficient pieces.
            return -1;
        }
        if (piece_cnt == 3) {
            return 3;
        }
        return 2;
    }

    bool has_available_move(int player) const {
        if (m_board_ptr->get_player_pieces_on_hand(player) > 0) {
            // Can still place pieces on the board
            return true;
        }
        int piece_cnt = m_board_ptr->pieces_on_board(player);
        if (piece_cnt < 0) {
            // Game is over
            return false;
        }
        // In phase 3, there is always a move!
        if (piece_cnt == 3) return true;
        // Phase 2
        for (int i = 0; i < FIELDS; i++) {
            int owner = m_board_ptr->get_owner(i);
            if (owner != player) continue;
            // Check posslbe valid moves from i->j
            for (int j : INDEX_CONNECTIONS[i]) {
                if (m_board_ptr->get_owner(j) == EMPTY) {
                    // Found a possible move for the player
                    return true;
                }
            }
        }
        return false;
    }

   private:
    Board *m_board_ptr = nullptr;
};
