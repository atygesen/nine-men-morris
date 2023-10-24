#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <iostream>
#include <string>
#include <vector>

#include "connections.cpp"
#include "utils.cpp"

namespace py = pybind11;

const int EMPTY = -1;
const int FIELDS = 24;

class Board {
   public:
    Board() {
        this->reset();
    }

    void reset() {
        this->board.resize(FIELDS);
        for (int i = 0; i < FIELDS; i++) {
            this->board[i] = EMPTY;
        }
        playerOnePieces = 9;
        playerTwoPieces = 9;
    }

    int pieces_on_board(int player) {
        int sum = 0;
        for (size_t i = 0; i < board.size(); i++) {
            if (board[i] == player) ++sum;
        }
        return sum;
    }

    void place_piece(int position, int player) {
        if (position < 24) {
            if (board[position] == EMPTY) {
                board[position] = player;
                if (player == 0) {
                    playerOnePieces--;
                } else {
                    playerTwoPieces--;
                }
            } else {
                throw std::invalid_argument("Position already occupied!");
            }
        } else {
            throw std::out_of_range("Invalid position!");
        }
    }

    void temp_place_piece(int position, int player) {
        if (position < 24) {
            if (board[position] == EMPTY) {
                board[position] = player;
            } else {
                throw std::invalid_argument("Position already occupied!");
            }
        } else {
            throw std::out_of_range("Invalid position!");
        }
    }

    void remove_piece(int position, int player) {
        if (position >= FIELDS || position < 0) {
            throw std::out_of_range("Invalid position!");
        }
        int owned_by = board[position];
        if (owned_by == EMPTY) {
            throw std::invalid_argument("Position not owned by anyone.");
        } else if (owned_by == player) {
            throw std::invalid_argument("Position is owned by self.");
        }

        board[position] = EMPTY;
    }

    bool can_delete(int pos, int player) {
        int owned_by = board[pos];
        return owned_by != EMPTY && owned_by != player;
    }

    void give_piece(int player) {
        if (player == 0) {
            playerOnePieces++;
        } else if (player == 1) {
            playerTwoPieces++;
        } else {
            throw std::invalid_argument("Invalid player.");
        }
    }

    void move_piece(int from, int to, int player) {
        if (from < FIELDS && to < FIELDS) {
            if (board[from] == player && board[to] == EMPTY) {
                board[from] = EMPTY;
                board[to] = player;
            } else {
                throw std::invalid_argument("Invalid move!");
            }
        } else {
            throw std::out_of_range("Invalid position!");
        }
    }

    inline bool is_connected(int pos1, int pos2) {
        if (pos1 > pos2) {
            int tmp = pos2;
            pos2 = pos1;
            pos1 = tmp;
        }
        for (auto &c : ALL_CONNECTIONS) {
            if (c.pos1 == pos1 && c.pos2 == pos2) return true;
        }
        return false;
    }

    bool is_mill(int a, int b, int c) {
        // Get the three numbers in order
        if (a > c) swap(a, c);
        if (a > b) swap(a, b);
        if (b > c) swap(b, c);

        for (auto &con : ALL_LINE_CONNECTIONS) {
            if (a == con.pos1 && b == con.pos2 && c == con.pos3) return true;
        }
        return false;
    }

    bool check_mill(int position, int player) {
        if (player == EMPTY) return false;

        auto &checks = SPOT_TO_LINE_CONNECTION[position];

        for (auto &mill : checks) {
            if (board[mill.pos1] == player && board[mill.pos2] == player &&
                board[mill.pos3] == player)
                return true;
        }
        return false;
    }

    int getPlayerOnePieces() {
        return playerOnePieces;
    }

    int getPlayerTwoPieces() {
        return playerTwoPieces;
    }

    std::vector<int> &getBoard() {
        return board;
    }

    bool is_available(int pos) {
        if (pos >= 0 && pos < 24) {
            return board[pos] == EMPTY;
        } else {
            throw std::out_of_range("Out of range");
        }
    }

    inline int get_owner(int pos) {
        return board[pos];
    }

    int get_board_hash() {
        // Inspired by https://stackoverflow.com/a/22430045
        int hash = 0;

        hash = 31 * hash + playerOnePieces;
        hash = 31 * hash + playerTwoPieces;

        for (int i : board) {
            hash = ((31 * hash) + i);
        }
        return hash;
    }

    void toggle_turn() {
        this->turn_index ^= 1;
        this->ply += 1;
    }

    void reverse_turn() {
        this->turn_index ^= 1;
        this->ply -= 1;
    }

    unsigned int turn_index = 0;
    unsigned int ply = 0;

   private:
    std::vector<int> board;
    int playerOnePieces;
    int playerTwoPieces;
};

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

class MoveFinder {
   public:
    MoveFinder(Board *board) : m_board_ptr(board) {
    }

    std::vector<std::pair<int, int>> get_phase_one_moves(int player) {
        std::vector<std::pair<int, int>> moves;

        for (int pos = 0; pos < FIELDS; pos++) {
            int owner = this->m_board_ptr->get_owner(pos);
            if (owner != EMPTY) continue;
            m_board_ptr->temp_place_piece(pos, player);
            moves.emplace_back(pos, EMPTY);
            if (m_board_ptr->check_mill(pos, player)) {
                // We can delete
                int other_player = player ^ 1;
                for (int to_delete = 0; to_delete < FIELDS; to_delete++) {
                    if (m_board_ptr->get_owner(to_delete) == other_player) {
                        moves.emplace_back(pos, to_delete);
                    }
                }
            }
            m_board_ptr->remove_piece(pos, EMPTY);  // Trick, we are removing our own piece.
        }
        return moves;
    }

    std::vector<CandidateMove> get_movement_phase_moves(int player, bool is_flying) {
        std::vector<CandidateMove> moves;

        for (int from_pos = 0; from_pos < FIELDS; from_pos++) {
            if (m_board_ptr->get_owner(from_pos) != player) continue;
            for (int to_pos = 0; to_pos < FIELDS; to_pos++) {
                // Either not empty, or unconnected phase 2
                if (m_board_ptr->get_owner(to_pos) != EMPTY ||
                    (!is_flying && !m_board_ptr->is_connected(from_pos, to_pos)))
                    continue;
                m_board_ptr->move_piece(from_pos, to_pos, player);
                moves.emplace_back(from_pos, to_pos);
                if (m_board_ptr->check_mill(to_pos, player)) {
                    // Check deletion
                    int other_player = player ^ 1;
                    for (int to_delete = 0; to_delete < FIELDS; to_delete++) {
                        if (m_board_ptr->get_owner(to_delete) == other_player) {
                            moves.emplace_back(from_pos, to_pos, to_delete);
                        }
                    }
                }
                m_board_ptr->move_piece(to_pos, from_pos, player);
            }
        }
        return moves;
    }

   private:
    Board *m_board_ptr;
};

PYBIND11_MODULE(nnm_board, m) {
    py::class_<Board>(m, "Board")
        .def(py::init<>())
        // Attributes
        .def_readonly("turn_index", &Board::turn_index)
        .def_readonly("ply", &Board::ply)
        // Methods
        .def("toggle_turn", &Board::toggle_turn)
        .def("reverse_turn", &Board::reverse_turn)
        .def("pieces_on_board", &Board::pieces_on_board)
        .def("reset", &Board::reset)
        .def("place_piece", &Board::place_piece)
        .def("temp_place_piece", &Board::temp_place_piece)
        .def("get_owner", &Board::get_owner)
        .def("move_piece", &Board::move_piece)
        .def("can_delete", &Board::can_delete)
        .def("remove_piece", &Board::remove_piece)
        .def("give_piece", &Board::give_piece)
        .def("get_player_one_pieces", &Board::getPlayerOnePieces)
        .def("get_player_two_pieces", &Board::getPlayerTwoPieces)
        .def("is_available", &Board::is_available)
        .def("is_connected", &Board::is_connected)
        .def("is_mill", &Board::is_mill)
        .def("check_mill", &Board::check_mill)
        .def("get_board_hash", &Board::get_board_hash)
        .def("get_board", &Board::getBoard);

    py::class_<MoveFinder>(m, "MoveFinder")
        .def(py::init<Board *>())
        .def("get_movement_phase_moves", &MoveFinder::get_movement_phase_moves)
        .def("get_phase_one_moves", &MoveFinder::get_phase_one_moves);

    py::class_<CandidateMove>(m, "CppCandidateMove")
        .def_readonly("from_pos", &CandidateMove::from_pos)
        .def_readonly("to_pos", &CandidateMove::to_pos)
        .def_readonly("delete_pos", &CandidateMove::delete_pos);
}
