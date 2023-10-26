#pragma once
#include <unordered_map>
#include <vector>

struct Connection {
    int pos1;
    int pos2;
};

struct LineConnection {
    int pos1;
    int pos2;
    int pos3;

public:
    bool contains(int val) const {
        return val == pos1 || val == pos2 || val == pos3;
    };

    bool contains(Connection val) const {
        return contains(val.pos1) && contains(val.pos2);
    };
};

const static std::vector<Connection> ALL_CONNECTIONS = {
    {0, 1},   {0, 9},   {1, 2},   {1, 4},   {2, 14},  {3, 4},   {3, 10},  {4, 5},
    {4, 7},   {5, 13},  {6, 7},   {6, 11},  {7, 8},   {8, 12},  {9, 10},  {9, 21},
    {10, 11}, {10, 18}, {11, 15}, {12, 13}, {12, 17}, {13, 14}, {13, 20}, {14, 23},
    {15, 16}, {16, 17}, {16, 19}, {18, 19}, {19, 20}, {19, 22}, {21, 22}, {22, 23},
};

const static std::vector<LineConnection> ALL_LINE_CONNECTIONS = {
    {0, 1, 2},    {0, 9, 21},   {1, 4, 7},    {2, 14, 23},  {3, 4, 5},   {3, 10, 18},
    {5, 13, 20},  {6, 7, 8},    {6, 11, 15},  {8, 12, 17},  {9, 10, 11}, {12, 13, 14},
    {15, 16, 17}, {16, 19, 22}, {18, 19, 20}, {21, 22, 23},
};

const static std::unordered_map<int, std::vector<LineConnection>> SPOT_TO_LINE_CONNECTION = {
    {0, {{0, 1, 2}, {0, 9, 21}}},       {1, {{0, 1, 2}, {1, 4, 7}}},
    {2, {{0, 1, 2}, {2, 14, 23}}},      {3, {{3, 4, 5}, {3, 10, 18}}},
    {4, {{1, 4, 7}, {3, 4, 5}}},        {5, {{3, 4, 5}, {5, 13, 20}}},
    {6, {{6, 7, 8}, {6, 11, 15}}},      {7, {{1, 4, 7}, {6, 7, 8}}},
    {8, {{6, 7, 8}, {8, 12, 17}}},      {9, {{0, 9, 21}, {9, 10, 11}}},
    {10, {{3, 10, 18}, {9, 10, 11}}},   {11, {{6, 11, 15}, {9, 10, 11}}},
    {12, {{8, 12, 17}, {12, 13, 14}}},  {13, {{5, 13, 20}, {12, 13, 14}}},
    {14, {{2, 14, 23}, {12, 13, 14}}},  {15, {{6, 11, 15}, {15, 16, 17}}},
    {16, {{15, 16, 17}, {16, 19, 22}}}, {17, {{8, 12, 17}, {15, 16, 17}}},
    {18, {{3, 10, 18}, {18, 19, 20}}},  {19, {{16, 19, 22}, {18, 19, 20}}},
    {20, {{5, 13, 20}, {18, 19, 20}}},  {21, {{0, 9, 21}, {21, 22, 23}}},
    {22, {{16, 19, 22}, {21, 22, 23}}}, {23, {{2, 14, 23}, {21, 22, 23}}},

};

/* Connections are ordered by index, to index 0 means 0 connects to 1 and 9, etc. */
const static std::vector<std::vector<int>> INDEX_CONNECTIONS = {
    {1, 9},            //
    {0, 2, 4},         //
    {1, 14},           //
    {4, 10},           //
    {1, 3, 5, 7},      //
    {4, 13},           //
    {7, 11},           //
    {4, 6, 8},         //
    {7, 12},           //
    {0, 10, 21},       //
    {3, 9, 11, 18},    //
    {6, 10, 15},       //
    {8, 13, 17},       //
    {5, 12, 14, 20},   //
    {2, 13, 23},       //
    {11, 16},          //
    {15, 17, 19},      //
    {12, 16},          //
    {10, 19},          //
    {16, 18, 20, 22},  //
    {13, 19},          //
    {9, 22},           //
    {19, 21, 23},      //
    {14, 22},          //
};