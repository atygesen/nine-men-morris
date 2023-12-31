#include "board.hpp"
#include "utils.hpp"


#include <sstream>

void Board::reset() {
    this->board.resize(FIELDS);
    for (int i = 0; i < FIELDS; i++) {
        this->board[i] = EMPTY;
    }
    playerOnePieces = 9;
    playerTwoPieces = 9;
    this->ply = 0;
    this->turn_index = 0;
}

int Board::pieces_on_board(int player) const {
    int sum = 0;
    for (size_t i = 0; i < FIELDS; i++) {
        if (board[i] == player) ++sum;
    }
    return sum;
}

void Board::place_piece(int position, int player) {
    if (is_available(position)) {
        board[position] = player;
        if (player == 0) {
            playerOnePieces--;
        } else {
            playerTwoPieces--;
        }
    } else {
        throw std::invalid_argument("Position already occupied!");
    }
}

void Board::temp_place_piece(int position, int player) {
    if (is_available(position)) {
        board[position] = player;
    } else {
        throw std::invalid_argument("Position already occupied!");
    }
}

void Board::remove_piece(int position, int player) {
#ifdef DEBUG_MODE
    int owned_by = board.at(position);
#else
    int owned_by = board[position];
#endif
    if (owned_by == EMPTY) {
        throw std::invalid_argument("Position not owned by anyone.");
    } else if (owned_by == player) {
        throw std::invalid_argument("Position is owned by self.");
    }

    board[position] = EMPTY;
}

bool Board::can_delete(int pos, int player) {
    int owned_by = get_owner(pos);
    if (owned_by == EMPTY || owned_by == player) {
        // Cannot delete own or empty
        return false;
    }
    // Check if it's in a mill
    int other_player = player ^ 1;
    if (check_mill(pos, other_player)) {
        // Check if all of the players pieces are in a mill
        for (int i = 0; i < FIELDS; i++) {
            if (i != pos && get_owner(i) == other_player && !check_mill(i, other_player)) {
                // We found a valid deletion which isn't this spot, but this spot is in a mill
                return false;
            }
        }
    }
    return true;
}

void Board::move_piece(int from, int to, int player) {
#ifdef DEBUG_MODE
    if (from >= FIELDS || from < 0 || to >= FIELDS || to < 0) {
        throw std::out_of_range("Invalid position!");
    }
#endif
    if (board[from] == player && board[to] == EMPTY && is_connected(from, to)) {
        board[from] = EMPTY;
        board[to] = player;
    } else {
        throw std::invalid_argument("Invalid move!");
    }
}

void Board::move_piece_flying(int from, int to, int player) {
#ifdef DEBUG_MODE
    if (board.at(from) == player && board.at(to) == EMPTY)
#else
    if (board[from] == player && board[to] == EMPTY)
#endif
    {
        board[from] = EMPTY;
        board[to] = player;
    } else {
        std::stringstream ss;
        ss << "Invalid move from " << from << " to " << to;
        throw std::invalid_argument(ss.str());
    }
}

bool Board::is_connected(int pos1, int pos2) {
    if (pos1 > pos2) {
        std::swap(pos1, pos2);
    }
    for (auto &c : ALL_CONNECTIONS) {
        if (c.pos1 == pos1 && c.pos2 == pos2) return true;
    }
    return false;
}

bool Board::is_mill(int a, int b, int c) {
    // Get the three numbers in order
    if (a > c) std::swap(a, c);
    if (a > b) std::swap(a, b);
    if (b > c) std::swap(b, c);

    for (auto &con : ALL_LINE_CONNECTIONS) {
        if (a == con.pos1 && b == con.pos2 && c == con.pos3) return true;
    }
    return false;
}

bool Board::check_mill(int position, int player) {
    if (player == EMPTY) return false;

    auto &checks = SPOT_TO_LINE_CONNECTION.at(position);

    for (auto &mill : checks) {
        if (board[mill.pos1] == player && board[mill.pos2] == player && board[mill.pos3] == player)
            return true;
    }
    return false;
}

int Board::get_player_pieces_on_hand(int player) const {
    if (player == 0) {
        return playerOnePieces;
    } else if (player == 1) {
        return playerTwoPieces;
    }
    throw std::invalid_argument("Invalid player");
}


std::size_t Board::get_board_hash() const {
     // Inspired by https://stackoverflow.com/a/39269304

    std::size_t seed = 0;
    hash_combine(seed, turn_index);
    hash_combine(seed, playerOnePieces);
    hash_combine(seed, playerTwoPieces);

    for (const int val : board){
        hash_combine(seed, val);
    }
    return seed;
}

void Board::execute_move(CandidateMove move) {
    // Assume it's from a generated list, no need to check mills. :)
    move_piece_flying(move.from_pos, move.to_pos);
    if (move.delete_pos != EMPTY) {
        remove_piece(move.delete_pos, -1);
    }
    toggle_turn();
}

void Board::execute_move(CandidatePlacement move) {
    place_piece(move.pos);
    if (move.delete_pos != EMPTY) {
        remove_piece(move.delete_pos, -1);
    }
    toggle_turn();
}

void Board::undo_move(CandidatePlacement move) {
    reverse_turn();
    remove_piece(move.pos, -1);
    give_piece();
    if (move.delete_pos != EMPTY) {
        temp_place_piece(move.delete_pos, this->turn_index ^ 1);
    }
}

void Board::undo_move(CandidateMove move) {
    reverse_turn();
    move_piece_flying(move.to_pos, move.from_pos);
    if (move.delete_pos != EMPTY) {
        temp_place_piece(move.delete_pos, this->turn_index ^ 1);
    }
}
