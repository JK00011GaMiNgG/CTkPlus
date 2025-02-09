#include <vector>

#include "grid.cpp"

int main() {
    Grid grid;
    grid.init(20, 20, true);

//    VertexShape vshape;
//    vshape.init({0, 0, 0, 10, 10, 10}, false);
//    grid.createShape(&vshape, 4, 4);

    EllipseShape eshape;
    eshape.init(10, 10);
    grid.createShape(&eshape, 10, 4);

    return 0;
}