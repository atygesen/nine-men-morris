#pragma once

#include <functional>
#include <vector>

inline void hash_combine(std::size_t& seed, const int v)
{
    // Copied from https://stackoverflow.com/a/2595226
    seed ^= v + 0x9e3779b9 + (seed<<6) + (seed>>2);
};
