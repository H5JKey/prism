#pragma once
#include <functional>
#include <stack>

#include "render-target.hpp"

class ContextGuard {
    static std::stack<std::reference_wrapper<const RenderTarget>> stack;

   public:
    ContextGuard(const ContextGuard&) = delete;
    ContextGuard(ContextGuard&&) = delete;
    ContextGuard& operator=(const ContextGuard&) = delete;
    ContextGuard& operator=(ContextGuard&&) = delete;

    ContextGuard(const RenderTarget& target);

    ~ContextGuard();
};