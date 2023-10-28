#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "board.hpp"
#include "evaluator.hpp"

namespace py = pybind11;

PYBIND11_MODULE(nnm_board, m) {
    py::class_<Board>(m, "Board")
        .def(py::init<>())
        // Attributes
        .def_property_readonly("turn_index", &Board::get_turn_index)
        .def_property_readonly("ply", &Board::get_ply)
        // Methods
        .def("toggle_turn", &Board::toggle_turn)
        .def("reverse_turn", &Board::reverse_turn)
        .def("pieces_on_board", &Board::pieces_on_board)
        .def("reset", &Board::reset)
        .def("temp_place_piece", &Board::temp_place_piece)
        .def("get_owner", &Board::get_owner)
        // Board manipulation
        .def("place_piece", py::overload_cast<int, int>(&Board::place_piece))
        .def("place_piece", py::overload_cast<int>(&Board::place_piece))
        .def("move_piece", py::overload_cast<int, int>(&Board::move_piece))
        .def("move_piece", py::overload_cast<int, int, int>(&Board::move_piece))
        .def("move_piece_flying", py::overload_cast<int, int, int>(&Board::move_piece_flying))
        .def("move_piece_flying", py::overload_cast<int, int>(&Board::move_piece_flying))
        .def("remove_piece", py::overload_cast<int, int>(&Board::remove_piece))
        .def("remove_piece", py::overload_cast<int>(&Board::remove_piece))

        .def("execute_move", py::overload_cast<CandidateMove>(&Board::execute_move))
        .def("execute_move", py::overload_cast<CandidatePlacement>(&Board::execute_move))

        .def("undo_move", py::overload_cast<CandidatePlacement>(&Board::undo_move))
        .def("undo_move", py::overload_cast<CandidateMove>(&Board::undo_move))


        // Helper stuff
        .def("can_delete", &Board::can_delete)
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
        .def("get_phase", &MoveFinder::get_phase)
        .def("get_movement_phase_moves", &MoveFinder::get_movement_phase_moves)
        .def("get_phase_one_moves", &MoveFinder::get_phase_one_moves);

    py::class_<CandidateMove>(m, "CppCandidateMove")
        .def_readonly("from_pos", &CandidateMove::from_pos)
        .def_readonly("to_pos", &CandidateMove::to_pos)
        .def_readonly("delete_pos", &CandidateMove::delete_pos);

    py::class_<CandidatePlacement>(m, "CppCandidatePlacement")
        .def_readonly("pos", &CandidatePlacement::pos)
        .def_readonly("delete_pos", &CandidatePlacement::delete_pos);

    py::class_<Evaluator>(m, "Evaluator")
        .def(py::init<Board *, int>())
        .def("evaluate", &Evaluator::evaluate)
        .def("brain_size", &Evaluator::brain_size)
        .def("reset", &Evaluator::reset)
        .def("get_brain", &Evaluator::get_brain)
        .def("set_brain", &Evaluator::set_brain);
}
