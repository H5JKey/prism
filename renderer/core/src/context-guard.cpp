#include "context-guard.hpp"

#include "render-target.hpp"

std::stack<std::reference_wrapper<const RenderTarget>> ContextGuard::stack;

ContextGuard::ContextGuard(const RenderTarget& target) {
    target.makeCurrent();
    stack.push(std::ref(target));
}

ContextGuard::~ContextGuard() {
    if (stack.empty()) return;
    if (stack.size() == 1) {
        stack.top().get().release();
        stack.pop();
    } else {
        stack.pop();
        stack.top().get().makeCurrent();
    }
}