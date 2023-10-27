#include "evaluator.hpp"

float Evaluator::evaluate() const {
    float score = 0.0;

    score += get_piece_diff() * m_coeffs[0];

    score -= get_blocked_pieces(me) * m_coeffs[1];
    score += get_blocked_pieces(other) * m_coeffs[2];

    score += get_central_pieces() * m_coeffs[3];

    score += get_two_piece_config(this->me) * m_coeffs[4];
    score -= get_two_piece_config(this->other) * m_coeffs[5];

    return score;
}

int Evaluator::get_blocked_pieces(int player) const {
    int n_blocked = 0;
    int other_player = player ^ 1;
    for (int i = 0; i < FIELDS; i++) {
        if (m_board_ptr->get_owner(i) != player) continue;
        bool is_surrounded = true;
        for (auto j : INDEX_CONNECTIONS[i]) {
            if (m_board_ptr->get_owner(j) != other_player) {
                is_surrounded = false;
                break;
            }
        }
        if (is_surrounded) ++n_blocked;
    }
    return n_blocked;
}

int Evaluator::get_central_pieces() const {
    int n_central = 0;
    for (int i = 0; i < FIELDS; i++) {
        if (m_board_ptr->get_owner(i) == this->me && INDEX_CONNECTIONS.at(i).size() == 4)
            n_central++;
    }
    return n_central;
}

int Evaluator::get_two_piece_config(int player) const {
    int n_config = 0;

    for (const auto &con : ALL_CONNECTIONS) {
        if (m_board_ptr->get_owner(con.pos1) != player ||
            m_board_ptr->get_owner(con.pos2) != player)
            continue;
        // Get the third spot
        for (const auto &line : ALL_LINE_CONNECTIONS) {
            if (line.contains(con)) {
                int n_empty =
                    (m_board_ptr->get_owner(line.pos1) + m_board_ptr->get_owner(line.pos2) +
                     m_board_ptr->get_owner(line.pos3));
                if (n_empty == 1) n_config++;
            }
        }
    }

    return n_config;
}
