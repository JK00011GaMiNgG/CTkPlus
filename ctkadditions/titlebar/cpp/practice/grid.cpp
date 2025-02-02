#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <utility>
#include <tuple>
#include <algorithm>

#include "shape.cpp"

using namespace std;

class Grid {
    public:
        void init(int width, int height, bool small) {
            vector<vector<int>> grid = generate(width, height);
            this->width = width;
            this->height = height;
            this->small = small;
            this->grid = grid;
            this->oddrows = (this->height % 2 != 0);
        }

        void createPoint(int x, int y) {
            drawPoint(x, y);
            refresh();
        }

        void createLine(int x1, int y1, int x2, int y2) {
            drawLine(x1, y1, x2, y2);
            refresh();
        }

        void createShape(Shape* shape, int x, int y) {
            drawShape(shape, x, y);
            refresh();
        }

    private:
        int width, height;
        bool small;
        bool oddrows;
        vector<vector<int>> grid;

        string os() {
            #ifdef _WIN32
                return "windows";
            #elif defined(__linux__)
                return "linux";
            #elif defined(__APPLE__)
                return "mac";
            #else
                return "unknown";
            #endif
        }

        vector<vector<int>> generate(int width, int height) {
            vector<vector<int>> grid(width, vector<int>(height, 0));
            return grid;
        }

        void print() {
            if (!this->small) {
                for (int i = 0; i < this->height; i++) {
                    for (int j = 0; j < this->width; j++) {
                        cout << (this->grid[i][j] == 0 ? "██" : "  ");
                    }
                    cout << "\n";
                }
            } else {
                int numRows = this->height;
                int rowPairs = numRows / 2;
                bool odd = (numRows % 2 != 0);
                for (int i = 0; i < rowPairs; i++) {
                    int top = 2 * i;
                    int bottom = 2 * i + 1;
                    for (int j = 0; j < this->width; j++) {
                        if (this->grid[top][j] == 0 && this->grid[bottom][j] == 0)
                            cout << "█";
                        else if (this->grid[top][j] == 0 && this->grid[bottom][j] == 1)
                            cout << "▀";
                        else if (this->grid[top][j] == 1 && this->grid[bottom][j] == 0)
                            cout << "▄";
                        else
                            cout << " ";
                    }
                    cout << "\n";
                }
                if (odd) {
                    int last = numRows - 1;
                    for (int j = 0; j < this->width; j++) {
                        cout << (this->grid[last][j] == 0 ? "▀" : " ");
                    }
                    cout << "\n";
                }
            }
        }

        void clear() {
            string current_os = os();
            if (current_os == "windows") {
                system("cls");
            } else if (current_os == "linux" || current_os == "mac") {
                system("clear");
            }
        }

        void refresh() {
            clear();
            print();
        }

        void drawPoint(int x, int y) {
            if (x >= 0 && x < this->width && y >= 0 && y < this->height) {
                this->grid[y][x] = 1;
            } else {
                cout << "Point out of bounds: (" << x << ", " << y << ")\n";
            }
        }

        void drawLine(int x1, int y1, int x2, int y2) {
            vector<pair<int, int>> points;
            bool isSteep = abs(y2 - y1) > abs(x2 - x1);

            if (isSteep) {
                swap(x1, y1);
                swap(x2, y2);
            }

            bool rev = false;
            if (x1 > x2) {
                swap(x1, x2);
                swap(y1, y2);
                rev = true;
            }

            int deltax = x2 - x1;
            int deltay = abs(y2 - y1);
            int error = deltax / 2;
            int y = y1;
            int ystep = (y1 < y2) ? 1 : -1;

            for (int x = x1; x <= x2; ++x) {
                if (isSteep) {
                    points.emplace_back(y, x);
                } else {
                    points.emplace_back(x, y);
                }

                error -= deltay;
                if (error < 0) {
                    y += ystep;
                    error += deltax;
                }
            }

            if (rev) {
                reverse(points.begin(), points.end());
            }
            for (int i = 0; i < points.size() - 1; ++i) {
                drawPoint(points[i].first, points[i].second);
            }
        }

        void drawShape(Shape* shape, int x, int y) {
            int vertex_amount = shape->get_vertex_amount();
            int n = 0;
            int m = 1;
            for (int i = 0; i < vertex_amount - 1; i++) {
                pair<int, int> a = shape->get_points(i);
                pair<int, int> b = shape->get_points(i+1);
                int x1 = a.first + x;
                int y1 = a.second + y;
                int x2 = b.first + x;
                int y2 = b.second + y;
                drawLine(x1, y1, x2, y2);
            }
        }
};