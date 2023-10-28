#include <iostream>
#include <vector>

#include "board.hpp"
#include "connections.hpp"
#include "unordered_map"

class Evaluator {
   public:
    Evaluator(Board *board, int me) : m_board_ptr(board), me(me) {
        this->other = me ^ 1;
    };

    float evaluate();

    int brain_size() const {
        return this->m_coeffs.size();
    };

    void set_brain(const std::vector<float> &brain) {
        if (brain.size() != m_coeffs.size()) {
            throw std::invalid_argument("Invalid size of brain!");
        }
        for (size_t i=0; i<brain.size(); i++){
            m_coeffs[i] = brain[i];
        }
    };

    std::vector<float> get_brain() const {
        return this->m_coeffs;
    }

    void reset() {
    }

   private:
    Board *m_board_ptr = nullptr;
    int me;
    int other;
    std::vector<float> m_coeffs = {9.0, 2.0, 2.0, 0.2, 1.0, 1.0};

    inline float get_piece_diff() const {
        int p1 = m_board_ptr->pieces_on_board(me);
        int p2 = m_board_ptr->pieces_on_board(other);
        return p1 - p2;
    };

    int get_blocked_pieces(int player) const;

    int get_central_pieces() const;

    int get_two_piece_config(int player) const;
};
